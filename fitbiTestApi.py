import streamlit as st
import requests

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

# Streamlit UI
st.title('Fitbit Data Summary')

access_token = st.text_input('Enter your Fitbit Access Token:', '')

if access_token:
    sleep_data = get_sleep_data(access_token)
    activity_data = get_activity_data(access_token)

    st.subheader('Sleep Data')
    st.write(sleep_data)

    st.subheader('Activity Data')
    st.write(activity_data)
