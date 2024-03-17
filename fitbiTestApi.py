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
@st.experimental_memo
def load_tokens(file_path):
    tokens = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Ensure the line is not empty
                label, token = line.strip().split(' = ')
                tokens[label] = token
    return tokens

# UI
st.title('Fitbit Data Explorer')

# Load and select access token
token_file_path = 'access_tokens.txt'  # Ensure this file exists
tokens = load_tokens(token_file_path)
selected_label = st.selectbox('Select a Watch:', list(tokens.keys()))
selected_token = tokens[selected_label]

# Select data type
data_type = st.radio("Select Data Type:", ['Sleep', 'Activity'])

# Date range picker
date_range = st.date_input("Select Date Range:")
if len(date_range) == 2:
    start_date, end_date = date_range
    fetched_data = fetch_data(selected_token, data_type, start_date.isoformat(), end_date.isoformat())
    # Assuming the rest of the data handling and plotting logic remains the same...
else:
    st.write("Please select a start and end date.")


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
