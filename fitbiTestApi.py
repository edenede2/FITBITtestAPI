import streamlit as st
import requests
import pandas as pd
import plotly.express as px



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
@st.cache
def load_tokens(file_path):
    with open(file_path, 'r') as file:
        tokens = file.readlines()
    return [token.strip() for token in tokens]

# UI
st.title('Fitbit Data Explorer')

# Load and select access token
token_file_path = 'access_tokens.txt'  # Ensure this file exists and contains access tokens, one per line
tokens = load_tokens(token_file_path)
selected_token = st.selectbox('Select a Watch:', tokens)

# Select data type
data_type = st.radio("Select Data Type:", ['Sleep', 'Activity'])

# Date range picker
start_date, end_date = st.date_input("Select Date Range:", [])

# Fetch and display data if dates are selected
if start_date and end_date:
    fetched_data = fetch_data(selected_token, data_type, start_date, end_date)
    if data_type == 'Sleep':
        # Example: Extract and plot sleep data
        # Adjust the extraction based on how the sleep data is structured in the fetched_data
        st.write(fetched_data)  # Placeholder to show raw data
    else:
        # Example: Extract and plot activity data
        # Convert to DataFrame for easier plotting
        dates = [item['dateTime'] for item in fetched_data['activities-steps']]
        steps = [int(item['value']) for item in fetched_data['activities-steps']]
        df = pd.DataFrame({'Date': dates, 'Steps': steps})
        fig = px.line(df, x='Date', y='Steps', title='Activity Over Time')
        st.plotly_chart(fig)
