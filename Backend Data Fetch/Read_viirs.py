import requests
import pandas as pd
from datetime import datetime, timedelta

# Your NASA FIRMS API Key
API_KEY = "094ea417efad2049cf4e04ee47ff4951"
collection = "viirs-snpp-c2"

# Bounding box for Greater Los Angeles area
bbox = [-120.0, 32.5, -116.5, 35.0]

# How many days you want in total
total_days = 365

# Max days per API call (API limit is 10)
days_per_call = 10

# Calculate how many calls we need
num_calls = (total_days + days_per_call - 1) // days_per_call

# Container to store all dataframes
all_data = []

print("Fetching fire data...")

for i in range(num_calls):
    days = min(days_per_call, total_days - i * days_per_call)
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{API_KEY}/{collection}/{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}/{days}"
    print(f"Fetching chunk {i + 1}/{num_calls}: last {days} days...")

    response = requests.get(url)
    if response.ok and "latitude" in response.text:
        df = pd.read_csv(pd.compat.StringIO(response.text))
        all_data.append(df)
    else:
        print(f"❌ Error in chunk {i + 1}: {response.text}")

# Combine all chunks into one big dataframe
if all_data:
    full_df = pd.concat(all_data, ignore_index=True)
    full_df.to_csv("la_fire_data_full_year.csv", index=False)
    print(f"✅ All data saved to 'la_fire_data_full_year.csv', total {len(full_df)} records.")
else:
    print("❌ No data fetched.")
