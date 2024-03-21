import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime
from datetime import time
import json
import jwt 

from datetime import datetime, timedelta

# Consolidated Function to Fetch Data
def fetch_data(access_token, data_type, start_date, end_date, start_time, end_time, limit, offset):
    base_url = "https://api.fitbit.com/1.2/user/-/"
    base_urll = "https://api.fitbit.com/1/user/-/"
    headers = {"Accept": "application/json",
               "Authorization": f"Bearer {access_token}"}
    url_dict = {
        'Sleep': f"{base_url}sleep/date/{start_date}/{end_date}.json",
        'Steps': f"{base_url}activities/steps/date/{start_date}/{end_date}.json",
        'Steps Intraday': f"{base_url}activities/steps/date/{start_date}/1d/1min/time/{start_time}/{end_time}.json",
        'Sleep Levels': f"{base_url}sleep/date/{start_date}/{end_date}.json",
        'Heart Rate': f"{base_url}activities/heart/date/{start_date}/1d/1sec/time/{start_time}/{end_time}.json",
        'HRV Intraday by Interval': f"{base_url}hrv/date/{start_date}/{end_date}/all.json",
        'Daily RMSSD': f"{base_url}hrv/date/{start_date}/all.json",
        'ECG': f'{base_url}ecg/list.json?{start_date} asc {limit} {offset}',
        'Activity_Time_Series': f'{base_urll}spo2/date/2024-03-18/2024-03-19/all.json'
    }
    
    
    response = requests.get(url_dict[data_type], headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}, {response.text}")
        return None




print("Loading tokens...")
tokens = r'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1JTWDIiLCJzdWIiOiJCWUJSMlciLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcm94eSBybnV0IHJwcm8gcnNsZSByYWN0IHJyZXMgcmxvYyByd2VpIHJociBydGVtIiwiZXhwIjoxNzQyMjc0NjIzLCJpYXQiOjE3MTA3NjMwNjR9.Z3R3yaq6cUN3rn7KyQVLCs9VDG9_NYO16D4d51bWKWk'
print("Tokens loaded.")

# Print the data from each API call
start_date = datetime.now().strftime('%Y-%m-%d') # Get today's date
end_date = datetime.now().strftime('%Y-%m-%d')

start_time = '00:00'
end_time = '23:59'

limit = "1"
offset = "0"

# # Fetch Sleep Data
# sleep_data = fetch_data(tokens, 'Sleep', start_date, end_date, start_time, end_time, limit, offset)
# print(sleep_data)

# # Fetch Steps Data
# steps_data = fetch_data(tokens, 'Steps', start_date, end_date, start_time, end_time, limit, offset)
# print(steps_data)

# # Fetch Steps Intraday Data
# steps_intraday_data = fetch_data(tokens, 'Steps Intraday', start_date, end_date, start_time, end_time, limit, offset)
# print(steps_intraday_data)

# # Fetch Sleep Levels Data
# sleep_levels_data = fetch_data(tokens, 'Sleep Levels', start_date, end_date, start_time, end_time, limit, offset)
# print(sleep_levels_data)


# # Fetch Heart Rate Data
# heart_rate_data = fetch_data(tokens, 'Heart Rate', start_date, end_date, start_time, end_time, limit, offset)
# print(heart_rate_data)

# # Fetch HRV Intraday by Interval Data
# hrv_intraday_by_interval_data = fetch_data(tokens, 'HRV Intraday by Interval', start_date, end_date, start_time, end_time, limit, offset)
# print(hrv_intraday_by_interval_data)

# # Fetch Daily RMSSD Data
# daily_rmssd_data = fetch_data(tokens, 'Daily RMSSD', start_date, end_date, start_time, end_time, limit, offset)
# print(daily_rmssd_data)

# # Fetch ECG Data
# ecg_data = fetch_data(tokens, 'ECG', start_date, end_date, start_time, end_time, limit, offset)
# print(ecg_data)

# Fetch Activity Time Series Data
activity_time_series_data = fetch_data(tokens, 'Activity_Time_Series', start_date, end_date, start_time, end_time, limit, offset)
data= activity_time_series_data
#data = pd.DataFrame(data)
print(data)
