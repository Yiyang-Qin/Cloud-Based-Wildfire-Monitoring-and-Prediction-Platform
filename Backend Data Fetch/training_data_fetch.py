# import requests
#
# API_KEY = '2b7ae474b526f2ea360758a527594dbb'
# LAT = 34.05
# LON = -118.25
#
# url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=hourly,minutely,current,alerts&units=imperial&appid={API_KEY}"
#
# response = requests.get(url)
# data = response.json()
#
# # print(data)
#
# # Extract the daily forecast (first element is today's data)
# daily_data = data['daily'][0]
#
# weather_summary = {
#     'Mean Temperature (.1 Fahrenheit)': round(daily_data['temp']['day'], 1),
#     'Mean Dew Point (.1 Fahrenheit)': round(daily_data['dew_point'], 1),
#     'Mean Sea Level Pressure (.1 mb)': round(daily_data['pressure'], 1),
#     'Mean Wind Speed (.1 knots)': round(daily_data['wind_speed'] *  0.868976, 1),
#     'Maximum Wind Gust (.1 knots)': round(daily_data.get('wind_gust', 0) *  0.868976, 1),
#     'Maximum Temperature (.1 Fahrenheit)': round(daily_data['temp']['max'], 1),
#     'Minimum Temperature (.1 Fahrenheit)': round(daily_data['temp']['min'], 1),
#     'Precipitation Amount (.01 inches)': round(daily_data.get('rain', 0) * 0.0393701, 2)
# }
#
#
# print(weather_summary)

import requests
import pandas as pd
from time import sleep
from datetime import datetime

API_KEY = '2b7ae474b526f2ea360758a527594dbb'

# California bounding box
lat_min, lat_max = 32.0, 42.0
lon_min, lon_max = -125.0, -114.0
lat_step = 0.5
lon_step = 0.5


# Define the floating range generator
def frange(start, stop, step):
    while start <= stop:
        yield round(start, 2)
        start += step


# List to collect all data
all_data = []

# Loop through the grid
for lat in frange(lat_min, lat_max, lat_step):
    for lon in frange(lon_min, lon_max, lon_step):
        print(f"Fetching data for {lat}, {lon}")
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=hourly,minutely,current,alerts&units=imperial&appid={API_KEY}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            daily_data = data['daily'][0]

            # Extract the date
            forecast_date = datetime.utcfromtimestamp(daily_data['dt']).strftime('%Y-%m-%d')

            weather_summary = {
                'Date': forecast_date,
                'Latitude': lat,
                'Longitude': lon,
                'Mean Temperature (.1 Fahrenheit)': round(daily_data['temp']['day'], 1),
                'Mean Dew Point (.1 Fahrenheit)': round(daily_data['dew_point'], 1),
                'Mean Sea Level Pressure (.1 mb)': round(daily_data['pressure'], 1),
                'Mean Wind Speed (.1 knots)': round(daily_data['wind_speed'] * 0.868976, 1),
                'Maximum Wind Gust (.1 knots)': round(daily_data.get('wind_gust', 0) * 0.868976, 1),
                'Maximum Temperature (.1 Fahrenheit)': round(daily_data['temp']['max'], 1),
                'Minimum Temperature (.1 Fahrenheit)': round(daily_data['temp']['min'], 1),
                'Precipitation Amount (.01 inches)': round(daily_data.get('rain', 0) * 0.0393701, 2)
            }
            all_data.append(weather_summary)
        else:
            print(f"Failed to fetch data for {lat}, {lon}")

        # Sleep to avoid rate limits
        sleep(1)

# Convert to DataFrame and save
df = pd.DataFrame(all_data)
df.to_csv("california_weather_data.csv", index=False)
print("Data saved to california_weather_data.csv")

