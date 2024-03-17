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
        'Sleep Levels': f"{base_url}sleep/date/{start_date}/{end_date}.json",
        'Heart Rate': f"{base_url}activities/heart/date/{start_date}/{end_date}.json"
    }
    response = requests.get(url_dict[data_type], headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}, {response.text}")
        return None
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

# Existing code to select the date range
selected_date_range = st.date_input("Select Date Range:", [default_start_date, default_end_date])
df = pf.DataFrame()

# Validate selected date range
if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    if start_date <= end_date:
        fetched_data = fetch_data(selected_token, data_type, start_date.isoformat(), end_date.isoformat())
        if not fetched_data:
            st.write("Failed to fetch data or no data available for the selected range.")
        else:
            if data_type == 'Sleep' or data_type == 'Sleep Levels':
                # Assuming fetched_data structure based on your provided sleep data example
                sleep_data = fetched_data.get('sleep', [])
                dates = [sd['dateOfSleep'] for sd in sleep_data]
                durations = [sd['duration']/3600000 for sd in sleep_data]  # Convert milliseconds to hours
                df = pd.DataFrame({'Date': dates, 'Duration': durations})
                if not df.empty:
                    fig = px.bar(df, x='Date', y='Duration', title='Sleep Duration Over Time', labels={'Duration': 'Duration (hours)'})
                    st.plotly_chart(fig)
                else:
                    st.write("No sleep data available for the selected date range.")
    
            elif data_type == 'Heart Rate':
                # Processing based on your provided heart rate data example
                heart_rate_data = fetched_data.get('activities-heart', [])
                dates = [hr['dateTime'] for hr in heart_rate_data]
                average_heart_rates = [hr['value'].get('restingHeartRate', 0) for hr in heart_rate_data]
                df = pd.DataFrame({'Date': dates, 'Average Heart Rate': average_heart_rates})
                if not df.empty:
                    fig = px.line(df, x='Date', y='Average Heart Rate', title='Daily Average Heart Rate')
                    st.plotly_chart(fig)
                else:
                    st.write("No heart rate data available for the selected date range.")

    
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
