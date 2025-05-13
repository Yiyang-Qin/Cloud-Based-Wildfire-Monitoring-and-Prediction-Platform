import psycopg2
from psycopg2 import sql

# ==== Configuration ====
DB_CONFIG = {
    "user": "weather_user",
    "password": "Weather",
    "host": "localhost",
    "dbname": "weather_db"
}
TABLE_NAME = "weather_data"

# ==== Connect and Inspect ====
def check_database():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print(f"✅ Connected to database: {DB_CONFIG['dbname']}")

        # Show all user tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        print("\n📄 Tables in database:")
        for t in tables:
            print(" -", t[0])

        # Show table schema
        print(f"\n📌 Schema of '{TABLE_NAME}':")
        cursor.execute(sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s;"), [TABLE_NAME])
        columns = cursor.fetchall()
        for col, dtype in columns:
            print(f" - {col}: {dtype}")

        # Preview some rows
        print(f"\n🔍 First 5 rows from '{TABLE_NAME}':")
        cursor.execute(sql.SQL("SELECT * FROM {} LIMIT 5").format(sql.Identifier(TABLE_NAME)))
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        # Close connection
        cursor.close()
        conn.close()
        print("\n🔒 Connection closed.")

    except Exception as e:
        print("❌ Error connecting to database:")
        print(e)

if __name__ == "__main__":
    check_database()
