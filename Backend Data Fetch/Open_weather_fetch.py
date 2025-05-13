import requests
import pandas as pd
from datetime import datetime, timedelta

# Your OpenWeather API key
API_KEY = "your_api_key_here"

# California bounding box
lat_min, lat_max = 32.0, 42.0
lon_min, lon_max = -125.0, -114.0

# How densely you want to tile the area
lat_step = 1.0  # degrees latitude
lon_step = 1.0  # degrees longitude

# How many past days to fetch (up to 5)
num_days = 5

# Los Angeles UTC offset is usually -7 hours (PDT)
utc_offset_hours = -7
utc_offset = timedelta(hours=utc_offset_hours)

# List to hold all weather records
weather_data = []

# Generate grid points inside California
lat_points = [lat_min + i * lat_step for i in range(int((lat_max - lat_min) / lat_step) + 1)]
lon_points = [lon_min + i * lon_step for i in range(int((lon_max - lon_min) / lon_step) + 1)]

print(f"Total points to fetch: {len(lat_points) * len(lon_points)}")

# Real current UTC time
now_utc = datetime.utcnow()

# Loop over grid points
for lat in lat_points:
    for lon in lon_points:
        print(f"\nFetching for point ({lat}, {lon})")

        for day_offset in range(1, num_days + 1):
            target_date_la = now_utc + utc_offset - timedelta(days=day_offset)
            target_date_utc = target_date_la - utc_offset
            timestamp = int(target_date_utc.timestamp())

            url = (
                f"https://api.openweathermap.org/data/3.0/onecall/timemachine?"
                f"lat={lat}&lon={lon}&dt={timestamp}&appid={API_KEY}&units=metric"
            )

            try:
                response = requests.get(url, timeout=10)
                if response.ok:
                    data = response.json()
                    records = data.get("data", [])
                    if not records:
                        print(f"  No data for {target_date_la.date()}")
                        continue

                    for record in records:
                        weather_entry = {
                            "lat": lat,
                            "lon": lon,
                            "datetime_utc": datetime.utcfromtimestamp(record["dt"]).isoformat(),
                            "datetime_local": (datetime.utcfromtimestamp(record["dt"]) + utc_offset).isoformat(),
                            "temperature_C": record["temp"],
                            "feels_like_C": record["feels_like"],
                            "humidity_%": record["humidity"],
                            "dew_point_C": record["dew_point"],
                            "pressure_hPa": record["pressure"],
                            "clouds_%": record["clouds"],
                            "visibility_m": record["visibility"],
                            "wind_speed_mps": record["wind_speed"],
                            "wind_deg": record["wind_deg"],
                            "wind_gust_mps": record.get("wind_gust", None),
                            "weather_main": record["weather"][0]["main"],
                            "weather_description": record["weather"][0]["description"],
                        }
                        weather_data.append(weather_entry)
                else:
                    print(f"  Error: {response.status_code} {response.text}")
            except Exception as e:
                print(f"  Exception fetching ({lat},{lon}) day_offset {day_offset}: {e}")

# Create DataFrame
if weather_data:
    df_weather = pd.DataFrame(weather_data)
    output_path = "california_weather_last_5_days.csv"
    df_weather.to_csv(output_path, index=False)
    print(f"\n✅ Weather data saved to {output_path}, total {len(df_weather)} records.")
else:
    print("\n❌ No weather data fetched.")
