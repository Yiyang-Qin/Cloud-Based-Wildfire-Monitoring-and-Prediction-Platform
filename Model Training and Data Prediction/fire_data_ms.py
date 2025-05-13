import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sqlalchemy import create_engine, Column, Float, Integer, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from geopy.distance import geodesic
import pytz
import geopandas as gpd
from shapely.geometry import Point

# === PostgreSQL DB Credentials (Inline) ===
DB_USER = "firepredict"
DB_PASSWORD = "firepredict"
DB_HOST = "localhost"  
DB_PORT = "5432"
DB_NAME = "fire_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# === SQLAlchemy Setup ===
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class RegionalFireRisk(Base):
    __tablename__ = "regional_fire_risk"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float)
    longitude = Column(Float)
    probability = Column(Float)

Base.metadata.create_all(bind=engine)

# === Load Model and Features ===
model = joblib.load('fire_risk_model.joblib')
features = joblib.load('model_features.joblib')

weather_df = pd.read_csv("california_weather_data.csv")
weather_df.columns = weather_df.columns.str.strip()

# === Simulate Weather (replace with live feed) ===
def get_weather_for_grid(lat, lon, request_utc_dt=None):
    # Step 1: find closest weather grid point
    weather_df['distance'] = weather_df.apply(
        lambda row: geodesic((lat, lon), (row['Latitude'], row['Longitude'])).km,
        axis=1
    )
    nearest = weather_df.loc[weather_df['distance'].idxmin()]

    # Step 2: determine day/night in Pacific time
    if request_utc_dt is None:
        request_utc_dt = datetime.utcnow()
    local_time = request_utc_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("US/Pacific"))
    hour = local_time.hour
    daynight_encoded = 0 if 6 <= hour < 18 else 1

    return {
        'latitude': lat,
        'longitude': lon,
        'TEMP': nearest['Mean Temperature (.1 Fahrenheit)'] ,
        'DEWP': nearest['Mean Dew Point (.1 Fahrenheit)'] ,
        'SLP': nearest['Mean Sea Level Pressure (.1 mb)'] ,
        'WDSP': nearest['Mean Wind Speed (.1 knots)'] ,
        'GUST': nearest['Maximum Wind Gust (.1 knots)'] ,
        'PRCP': nearest['Precipitation Amount (.01 inches)'] ,
        'MAX': nearest['Maximum Temperature (.1 Fahrenheit)'] ,
        'MIN': nearest['Minimum Temperature (.1 Fahrenheit)'] ,
        'daynight_encoded': daynight_encoded
    }



def is_land_point(lat, lon):
    # Very simple exclusion for major ocean regions off California coast
    # Rough approximation — feel free to tune further
    return not (
        lon < -123.0 and lat < 38.0  # ocean west of CA
        or lon < -122.5 and lat < 36.0  # ocean southwest of central CA
        or lon < -121.5 and lat < 34.0  # southern ocean
        or lat < 32.5 or lat > 42.0 or lon < -124.4 or lon > -114.0  # outside CA
    )

# === Generate CA Grid ===
land_gdf = gpd.read_file("ne_50m_land.shp") 
lats = np.linspace(32.5, 42.0, 50)
lons = np.linspace(-124.4, -114.0, 50)

grid_inputs = []

for lat in lats:
    for lon in lons:
        point = Point(lon, lat)  # GeoPandas expects (lon, lat)
        if not land_gdf.contains(point).any():
            continue  # skip ocean points

        try:
            weather_features = get_weather_for_grid(lat, lon)
            grid_inputs.append(weather_features)
        except Exception as e:
            print(f"⚠️ Skipped point ({lat}, {lon}) due to error: {e}")

grid_df = pd.DataFrame(grid_inputs)
grid_df['probability'] = model.predict_proba(grid_df[features])[:, 1]
grid_df['timestamp'] = datetime.utcnow()

# === Write to PostgreSQL ===
session = SessionLocal()
session.query(RegionalFireRisk).delete()  # optional: clear existing grid

for _, row in grid_df.iterrows():
    session.add(RegionalFireRisk(
        timestamp=row['timestamp'],
        latitude=row['latitude'],
        longitude=row['longitude'],
        probability=row['probability']
    ))

session.commit()
session.close()
print("✅ PostgreSQL fire risk grid updated.")






