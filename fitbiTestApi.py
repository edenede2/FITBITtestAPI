import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime

# Consolidated Function to Fetch Data
def fetch_data(access_token, data_type, start_date, end_date):
    base_url = "https://api.fitbit.com/1.2/user/-/"
    headers = {"Authorization": f"Bearer {access_token}"}
    url_dict = {
        'Sleep': f"{base_url}sleep/date/{start_date}/{end_date}.json",
        'Activity': f"{base_url}activities/steps/date/{start_date}/{end_date}.json",
        'Sleep Levels': f"{base_url}sleep/date/{start_date}/{end_date}.json",  # Assuming similar endpoint
        'Heart Rate': f"{base_url}activities/heart/date/{start_date}/{end_date}.json"  # Adjust as per actual endpoint
    }
    response = requests.get(url_dict[data_type], headers=headers)
    return response.json()

# Function to fetch sleep data
def get_sleep_data(access_token):
    url = "https://api.fitbit.com/1.2/user/-/sleep/date/2024-03-17.json"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# Function to fetch activity data
def get_activity_data(access_token):
    url = "https://api.fitbit.com/1/user/-/activities/date/2023-03-15.json"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# Function to fetch data
def fetch_data(access_token, data_type, start_date, end_date):
    base_url = "https://api.fitbit.com/1.2/user/-/"
    headers = {"Authorization": f"Bearer {access_token}"}
    if data_type == 'Sleep':
        url = f"{base_url}sleep/date/{start_date}/{end_date}.json"
    else:  # Activity
        url = f"{base_url}activities/steps/date/{start_date}/{end_date}.json"
    response = requests.get(url, headers=headers)
    return response.json()

# Load access tokens from a file
@st.cache_data
def load_tokens(file_path):
    tokens = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():
                try:
                    label, token = line.strip().split(' = ')
                    tokens[label] = token
                except ValueError:
                    continue
    return tokens

# UI
st.title('Fitbit Data Explorer')

# Load and select access token
token_file_path = 'access_tokens.txt'  # Ensure this file exists
tokens = load_tokens(token_file_path)
selected_label = st.selectbox('Select a Watch:', list(tokens.keys()))
selected_token = tokens[selected_label]

# Select data type
data_type = st.radio("Select Data Type:", ['Sleep', 'Activity', 'Sleep Levels', 'Heart Rate'])

# Initialize default start and end dates as today's date, or choose your own defaults
default_start_date = datetime.date.today() - datetime.timedelta(days=7)
default_end_date = datetime.date.today()

# Use st.date_input to allow users to select a date range. Provide a default range.
selected_date_range = st.date_input("Select Date Range:", [default_start_date, default_end_date])

# Ensure that two dates are always unpacked by checking the length of selected_date_range
if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
else:
    # If not, fall back to the default start and end dates
    start_date, end_date = default_start_date, default_end_date

# Ensure you adjust your data processing and plotting according to the corrected data type handling
if start_date and end_date:
    fetched_data = fetch_data(selected_token, data_type, start_date.isoformat(), end_date.isoformat())
    if data_type == 'Sleep':
        dates = [item['dateOfSleep'] for item in fetched_data.get('sleep', [])]
        durations = [item['duration']/3600000 for item in fetched_data.get('sleep', [])]  # Convert from milliseconds to hours
        df = pd.DataFrame({'Date': dates, 'Duration': durations})
        fig = px.bar(df, x='Date', y='Duration', title='Sleep Duration Over Time', labels={'Duration': 'Duration (hours)'})
        st.plotly_chart(fig)
    elif data_type == 'Activity':
        dates = [item['dateTime'] for item in fetched_data.get('activities-steps', [])]
        steps = [int(item['value']) for item in fetched_data.get('activities-steps', [])]
        df = pd.DataFrame({'Date': dates, 'Steps': steps})
        fig = px.line(df, x='Date', y='Steps', title='Activity Over Time')
        st.plotly_chart(fig)
    elif data_type == 'Sleep Levels':
        sleep_levels_data = fetch_data(selected_token, 'Sleep Levels', start_date.isoformat(), end_date.isoformat())
        # Initialize a dictionary to store aggregated sleep stage durations
        sleep_stages = {'Light': 0, 'Deep': 0, 'REM': 0, 'Awake': 0}
    
        # Loop through each night's data
        for night in sleep_levels_data['sleep']:
            for stage in night['levels']['data']:
                # Aggregate the durations by sleep stage
                if stage['level'] in sleep_stages:
                    sleep_stages[stage['level']] += stage['seconds'] / 60  # Convert seconds to minutes
    
        # Prepare the DataFrame for visualization
        df_sleep_levels = pd.DataFrame(list(sleep_stages.items()), columns=['Stage', 'Minutes'])
    
        # Plotting the data
        fig = px.bar(df_sleep_levels, x='Stage', y='Minutes', title='Distribution of Sleep Stages',
                     labels={'Minutes': 'Minutes Spent'}, color='Stage')
        st.plotly_chart(fig)
    elif data_type == 'Heart Rate':
        heart_rate_data = fetch_data(selected_token, 'Heart Rate', start_date.isoformat(), end_date.isoformat())
        # Assuming the structure includes 'activities-heart' with date-wise entries
        dates = []
        average_heart_rates = []
    
        for entry in heart_rate_data['activities-heart']:
            dates.append(entry['dateTime'])
            # Assuming 'restingHeartRate' is available; adapt as needed based on your data structure
            average_heart_rates.append(entry['value']['restingHeartRate'])
    
        # Prepare the DataFrame for visualization
        df_heart_rate = pd.DataFrame({
            'Date': dates,
            'Average Heart Rate': average_heart_rates
        })
    
        # Plotting the data
        fig = px.line(df_heart_rate, x='Date', y='Average Heart Rate', title='Average Heart Rate Over Time',
                      labels={'Average Heart Rate': 'BPM (Beats Per Minute)'})
        st.plotly_chart(fig)

    
    # Check if df is defined and not empty
    if not df.empty:
        # Proceed with Excel file creation and download functionality
        to_excel = BytesIO()
        with pd.ExcelWriter(to_excel, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1')
        # No need to call writer.save()
        to_excel.seek(0)  # Go to the beginning of the stream
    
        # Add a download button for the Excel file
        st.download_button(label="Download Excel file",
                           data=to_excel,
                           file_name="fitbit_data.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.write("No data to download.")
