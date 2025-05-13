import pandas as pd
from sqlalchemy import create_engine

# === PostgreSQL Credentials ===
DB_USER = "firepredict"
DB_PASSWORD = "firepredict"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "fire_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# === Create SQLAlchemy engine ===
engine = create_engine(DATABASE_URL)

# === Define query: fetch recent records (default 100) ===
def fetch_latest_fire_risks(limit=100):
    query = f"""
    SELECT timestamp, latitude, longitude, probability
    FROM regional_fire_risk
    ORDER BY timestamp DESC
    LIMIT {limit};
    """
    df = pd.read_sql(query, con=engine)
    return df

# === Run and display ===
if __name__ == "__main__":
    df = fetch_latest_fire_risks(limit=50)
    print("✅ Latest Fire Risk Predictions:")
    print(df)



