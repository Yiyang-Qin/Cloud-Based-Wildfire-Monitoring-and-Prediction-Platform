import os
import requests

# Constants
BASE_URL = "https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/2023/"
OUTPUT_DIR = "noaa_data_2023"
FILENAME = "Temp.txt"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read station IDs from the text file and append .csv
with open(FILENAME, "r") as f:
    station_ids = [line.strip() + ".csv" for line in f if line.strip()]

# Download each file
for station_file in station_ids:
    url = BASE_URL + station_file
    local_path = os.path.join(OUTPUT_DIR, station_file)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(local_path, "wb") as out_file:
                out_file.write(response.content)
            print(f"Downloaded: {station_file}")
        else:
            print(f"Not found (HTTP {response.status_code}): {station_file}")
    except Exception as e:
        print(f"Failed to download {station_file}: {e}")
