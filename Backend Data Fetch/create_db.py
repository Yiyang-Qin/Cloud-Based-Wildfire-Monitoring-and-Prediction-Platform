import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# ====== Database Configuration ======
DB_CONFIG = {
    "user": "weather_user",
    "password": "securepassword",
    "host": "localhost",
    "dbname": "weather_db"
}
TABLE_NAME = "weather_data"
DATA_DIR = "/home/admin/Data/noaa_data_2023"

# ====== SQLAlchemy Engine Setup ======
engine = create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['dbname']}")

# ====== SQL Table Schema (safe with BIG values) ======
CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    "STATION" DOUBLE PRECISION,
    "DATE" TIMESTAMP,
    "LATITUDE" DOUBLE PRECISION,
    "LONGITUDE" DOUBLE PRECISION,
    "ELEVATION" DOUBLE PRECISION,
    "NAME" TEXT,
    "TEMP" DOUBLE PRECISION,
    "TEMP_ATTRIBUTES" DOUBLE PRECISION,
    "DEWP" DOUBLE PRECISION,
    "DEWP_ATTRIBUTES" DOUBLE PRECISION,
    "SLP" DOUBLE PRECISION,
    "SLP_ATTRIBUTES" DOUBLE PRECISION,
    "STP" DOUBLE PRECISION,
    "STP_ATTRIBUTES" DOUBLE PRECISION,
    "VISIB" DOUBLE PRECISION,
    "VISIB_ATTRIBUTES" DOUBLE PRECISION,
    "WDSP" DOUBLE PRECISION,
    "WDSP_ATTRIBUTES" DOUBLE PRECISION,
    "MXSPD" DOUBLE PRECISION,
    "GUST" DOUBLE PRECISION,
    "MAX" DOUBLE PRECISION,
    "MAX_ATTRIBUTES" TEXT,
    "MIN" DOUBLE PRECISION,
    "MIN_ATTRIBUTES" TEXT,
    "PRCP" DOUBLE PRECISION,
    "PRCP_ATTRIBUTES" TEXT,
    "SNDP" DOUBLE PRECISION,
    "FRSHTT" DOUBLE PRECISION
);
"""

# ====== Expected Column Types ======
dtype_str_cols = {
    "STATION": str,
    "DATE": str,
    "NAME": str,
    "MAX_ATTRIBUTES": str,
    "MIN_ATTRIBUTES": str,
    "PRCP_ATTRIBUTES": str
}

float_cols = [
    "STATION", "LATITUDE", "LONGITUDE", "ELEVATION", "TEMP", "TEMP_ATTRIBUTES", "DEWP",
    "DEWP_ATTRIBUTES", "SLP", "SLP_ATTRIBUTES", "STP", "STP_ATTRIBUTES", "VISIB", "VISIB_ATTRIBUTES",
    "WDSP", "WDSP_ATTRIBUTES", "MXSPD", "GUST", "MAX", "MIN", "PRCP", "SNDP", "FRSHTT"
]

# ====== Load One CSV File into DB ======
def load_csv_to_db(csv_path):
    print(f"🔄 Loading {csv_path}...")
    try:
        df = pd.read_csv(csv_path, dtype=dtype_str_cols)

        # Convert date and numeric fields
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        for col in float_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")

        # Insert into DB
        df.to_sql(TABLE_NAME, engine, if_exists="append", index=False)
        print(f"✅ {len(df)} rows inserted from {os.path.basename(csv_path)}")

    except (pd.errors.EmptyDataError, SQLAlchemyError, ValueError) as e:
        print(f"❌ Error in file: {csv_path}")
        print(f"   → {type(e).__name__}: {e}")

# ====== Main Control Flow ======
def main():
    # Ensure table is created
    try:
        with engine.begin() as conn:
            conn.execute(text(CREATE_TABLE_SQL))
        print(f"📐 Table `{TABLE_NAME}` ensured.")
    except SQLAlchemyError as e:
        print("❌ Failed to initialize table:")
        print(f"   → {e}")
        return

    # Scan directory and process all CSVs
    for filename in sorted(os.listdir(DATA_DIR)):
        if filename.endswith(".csv"):
            filepath = os.path.join(DATA_DIR, filename)
            load_csv_to_db(filepath)

if __name__ == "__main__":
    main()
