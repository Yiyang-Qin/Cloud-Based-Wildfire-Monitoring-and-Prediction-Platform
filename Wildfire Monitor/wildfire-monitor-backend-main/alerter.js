// alerter.js
const { Pool } = require('pg');
const AWS = require('aws-sdk');
require('dotenv').config();

// ——— 1) AWS SES Configuration ———
AWS.config.update({
  region: 'us-west-2',
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,      // Recommended to use environment variables
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
});
const ses = new AWS.SES({ apiVersion: '2010-12-01' });

// ——— 2) Postgres Connection ———
// weather_db: stores regions & users
const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'weather_db',
  password: 'postgres',
  port: 5432,
});

// fire_db: stores regional_fire_risk
const firePool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'fire_db',
  password: 'postgres',
  port: 5432,
});

async function checkAndAlert() {
  // 1. First, retrieve all user regions (get WKT)
  const regionsRes = await pool.query(`
    SELECT
      r.id         AS region_id,
      u.email      AS user_email,
      r.name       AS region_name,
      ST_AsText(r.geom) AS wkt
    FROM regions r
    JOIN users u ON u.id = r.user_id
  `);

  for (let { region_id, user_email, region_name, wkt } of regionsRes.rows) {
    // 2. Query fire_db: probability ≥ 0.3 and falls within the polygon
    const fireRes = await firePool.query(
      `
      SELECT id, timestamp, latitude, longitude, probability
      FROM regional_fire_risk
      WHERE probability >= 0.21
        AND ST_Contains(
              ST_GeomFromText($1, 4326),
              ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
            )
      `,
      [wkt]
    );

    if (fireRes.rows.length > 0) {
      const firePoints = fireRes.rows.map(({ latitude, longitude, probability, timestamp }) => 
        `- Time: ${new Date(timestamp).toLocaleString()}, Latitude: ${latitude.toFixed(2)}, Longitude: ${longitude.toFixed(2)}, Probability: ${(probability * 100).toFixed(2)}%`
      ).join('\n');

      // 3. Construct and send SES alert email
      const params = {
      Source: 'kwang655@usc.edu',
      Destination: { ToAddresses: [user_email] },
      Message: {
        Subject: {
        Data: `【Wildfire Risk Alert】High-risk fire points detected in your region "${region_name}"`,
        Charset: 'UTF-8'
        },
        Body: {
        Text: {
          Data: `
  Hello,

  We have detected predicted fire points with the following details within your defined region "${region_name}" (ID: ${region_id}):

  ${firePoints}

  Please pay immediate attention to this area and take necessary safety precautions.

  —— Cloud Wildfire Monitoring Platform
          `.trim(),
          Charset: 'UTF-8'
        }
        }
      }
      };

      try {
        await ses.sendEmail(params).promise();
        console.log(`Alert sent to ${user_email} for region ${region_name}`);
      } catch (err) {
        console.error(`Failed to send alert to ${user_email}:`, err);
      }
    }
  }
}

// Run every minute, or adjust to your desired frequency
setInterval(() => {
  checkAndAlert().catch(console.error);
}, 60 * 1000);

// Execute once immediately on startup
checkAndAlert().catch(console.error);
