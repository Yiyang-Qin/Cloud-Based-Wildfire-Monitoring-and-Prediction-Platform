# Cloud-Based Wildfire Monitoring and Prediction Platform

## Overview
This project is a cloud-based wildfire monitoring and prediction platform, consisting of a backend service for data fetching and processing, and a frontend for visualization and real-time alerts.

## Setup Instructions

### 1️⃣ Backend Setup
```bash
cd Wildfire\ Monitor/wildfire-monitor-backend-main
npm install
```

#### Environment Variables
Create a `.env` file in `wildfire-monitor-backend-main`:
```
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
DB_HOST=localhost
DB_USER=username
DB_PASS=password
DB_NAME=wildfire_db
```

#### Start the Backend Server
```bash
node server.js
```

### 2️⃣ Frontend Setup
```bash
cd Wildfire\ Monitor/wildfire-monitor-frontend-main
npm install
npm start
```

Visit `http://localhost:3000` to view the application.

---

## Data Fetching Scripts
Located in `Backend Data Fetch/`:
- `NOAA_fetch.py`: Fetches NOAA weather data
- `Open_weather_fetch.py`: Fetches OpenWeatherMap data
- `Read_viirs.py`: Reads VIIRS satellite fire data
- `Schema_Inference.py`: Infers schema for database storage
- `training_data_fetch.py`: Collects training data for ML models

To execute any script:
```bash
python3 <script_name>.py
```

---

## API Endpoints
| Endpoint         | Method | Description                |
|------------------|--------|----------------------------|
| `/api/fetch`    | GET    | Fetch data from sources   |
| `/api/alert`    | POST   | Send alert notification   |
| `/api/weather`  | GET    | Get weather information   |

---

## Running Backend and Frontend Together

To run both the backend and frontend simultaneously, open two terminal windows:

**Terminal 1:**
```bash
cd Wildfire\ Monitor/wildfire-monitor-backend-main
node server.js
```

**Terminal 2:**
```bash
cd Wildfire\ Monitor/wildfire-monitor-frontend-main
npm start
```

Visit `http://localhost:3000` to view the live dashboard.

---

## Database Setup
To create and initialize the database:
```bash
python3 Backend\ Data\ Fetch/create_db.py
```

To check the database status:
```bash
python3 Backend\ Data\ Fetch/check_db.py
```

---

## Contributing
Please submit PRs for any improvements or bug fixes. Ensure all code is properly formatted and tested.

## License
This project is licensed under the MIT License.
