import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime
from datetime import time
from datetime import datetime, timedelta

# Consolidated Function to Fetch Data
def fetch_data(access_token, data_type, start_date, end_date, start_time, end_time):
    base_url = "https://api.fitbit.com/1.2/user/-/"
    base_urll = "https://api.fitbit.com/1/user/-/"
    headers = {"Authorization": f"Bearer {access_token}"}
    url_dict = {
        'Sleep': f"{base_url}sleep/date/{start_date}/{end_date}.json",
        'Steps': f"{base_url}activities/steps/date/{start_date}/{end_date}.json",
        'Steps Intraday': f"{base_url}activities/steps/date/{start_date}/1d/1min/time/{start_time}/{end_time}.json",
        'Sleep Levels': f"{base_url}sleep/date/{start_date}/{end_date}.json",
        'Heart Rate': f"{base_url}activities/heart/date/{start_date}/1d/1sec/time/{start_time}/{end_time}.json",
        'HRV Intraday by Interval': f"{base_urll}hrv/date/{start_date}/{end_date}/all.json",
        'Daily RMSSD': f"{base_urll}hrv/date/{start_date}/all.json",
        'ECG': f'{base_urll}ecg/list.json?afterDate=2022-09-28&sort=asc&limit=1&offset=0'
    }
    
    
    response = requests.get(url_dict[data_type], headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}, {response.text}")
        return None


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
token_file_path = 'access_tokens.txt'  
tokens = load_tokens(token_file_path)
selected_label = st.selectbox('Select a Watch:', list(tokens.keys()))
selected_token = tokens[selected_label]

# Select data type
data_type = st.radio("Select Data Type:", ['Sleep', 'Steps', 'Steps Intraday', 'Sleep Levels', 'Heart Rate','Daily RMSSD', 'HRV Intraday by Interval', 'ECG'])

# Initialize default start and end dates as today's date, or choose your own defaults
default_start_date = datetime.today() - timedelta(days=7)
default_end_date = datetime.today()

start_time = st.time_input('Select Start Time', value=time(9, 00))
end_time = st.time_input('Select End Time', value=time(18, 00))

st.write(f'Selected Start Time: {start_time.strftime("%H:%M")}')
st.write(f'Selected End Time: {end_time.strftime("%H:%M")}')

# Existing code to select the date range
selected_date_range = st.date_input("Select Date Range:", [default_start_date, default_end_date])
df = pd.DataFrame()

# Validate selected date range
if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    if start_date <= end_date:
        fetched_data = fetch_data(selected_token, data_type, start_date.isoformat(), end_date.isoformat(),start_time, end_time)
        if not fetched_data:
            st.write("Failed to fetch data or no data available for the selected range.")
        else:
            if data_type == 'Sleep':
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
    
            elif data_type == 'Steps':
                steps_summary = fetched_data.get("activities-steps", [])
                dates = [entry["dateTime"] for entry in steps_summary]
                steps = [int(entry["value"]) for entry in steps_summary]

                df = pd.DataFrame({"Date": dates, "Steps": steps})
                if not df.empty:
                    fig = px.bar(df, x="Date", y="Steps", title="Daily Steps Summary")
                    st.plotly_chart(fig)
                else:
                    st.write("No daily steps data available for the selected date range.")

            elif data_type == 'Steps Intraday':
                steps_intraday = fetched_data.get("activities-steps-intraday", {}).get("dataset", [])
                times = [datetime.strptime(entry["time"], "%H:%M:%S").time() for entry in steps_intraday]
                steps = [entry["value"] for entry in steps_intraday]

                df = pd.DataFrame({"Time": times, "Steps": steps})
                if not df.empty:
                    fig = px.line(df, x="Time", y="Steps", title="Intraday Steps (1-minute interval)")
                    st.plotly_chart(fig)
                else:
                    st.write("No intraday steps data available for the selected time range.")

            elif data_type == 'Heart Rate':
                # Access the 'activities-heart-intraday' section directly
                intraday_data = fetched_data.get('activities-heart-intraday', {}).get('dataset', [])
                times = []
                heart_rates = []

                # Iterate through the 'dataset' list
                for data_point in intraday_data:
                    if 'time' in data_point and 'value' in data_point:
                        time = data_point['time']
                        heart_rate = data_point['value']
                        times.append(time)
                        heart_rates.append(heart_rate)

                if times and heart_rates:
                    # Assuming 'dates' contains the date(s) for these intraday data points
                    # You might need to adjust how 'Date' is determined based on your requirements
                    df = pd.DataFrame({
                        'Time': times,
                        'Heart Rate': heart_rates
                    })

                    # Check and correct DataFrame typo
                    if not df.empty:
                        # Adjust the plotting to reflect that it's intraday data (time vs. heart rate)
                        fig = px.line(df, x='Time', y='Heart Rate', title='Intraday Heart Rate')
                        st.plotly_chart(fig)
                    else:
                        st.write("No intraday heart rate data available for the selected date range.")
                else:
                    st.write("No heart rate data found.") 

            elif data_type == 'HRV Intraday by Interval':
                hrv_intraday_data = fetched_data.get('hrv', [])[0].get('minutes', [])  # Assuming we're interested in the first entry
                times = [entry['minute'] for entry in hrv_intraday_data]
                rmssd_values = [entry['value']['rmssd'] for entry in hrv_intraday_data]

                if times and rmssd_values:  # Ensure both lists have data
                    df_hrv = pd.DataFrame({
                        'Time': times,
                        'RMSSD': rmssd_values
                    })
                    fig = px.line(df_hrv, x='Time', y='RMSSD', title='HRV RMSSD Intraday Variation')
                    st.plotly_chart(fig)
                else:
                    st.write("No HRV intraday data available for the selected date range.")
            elif data_type == 'daily RMSSD':
                hrv_daily_summary = fetched_data.get('hrv', [])
                dates = []
                average_rmssd_values = []

                for daily_data in hrv_daily_summary:
                    date = daily_data['dateTime']
                    rmssd_values = [measure['value']['dailyRmssd'] for measure in daily_data.get('value', [])]
                    
                    if rmssd_values:  # Ensure there are RMSSD values to calculate an average
                        average_rmssd = sum(rmssd_values) / len(rmssd_values)
                        dates.append(date)
                        average_rmssd_values.append(average_rmssd)

                if dates and average_rmssd_values:
                    df = pd.DataFrame({"Date": dates, "Average RMSSD": average_rmssd_values})
                    fig = px.bar(df, x="Date", y="Average RMSSD", title="Daily Average RMSSD Summary")
                    st.plotly_chart(fig)
                else:
                    st.write("No daily RMSSD data available for the selected date range.")        
            # Processing and visualizing ECG data
            elif data_type == 'ECG':
                ecg_readings = fetched_data.get('ecgReadings', [])
                if ecg_readings:
                    # Example: Focus on the first reading for simplicity
                    reading = ecg_readings[0]
                    average_hr = reading['averageHeartRate']
                    waveform_samples = reading['waveformSamples']
                    sampling_frequency = reading['samplingFrequencyHz']

                    # Display average heart rate
                    st.write(f"Average Heart Rate: {average_hr} bpm")

                    # Visualizing a subset of the ECG waveform
                    # Note: Adjust the visualization based on your needs and the number of samples
                    waveform_df = pd.DataFrame({
                        'Sample Number': range(len(waveform_samples)),
                        'Amplitude': waveform_samples
                    })
                    fig = px.line(waveform_df, x='Sample Number', y='Amplitude', title='ECG Waveform')
                    st.plotly_chart(fig)
                else:
                    st.write("No ECG data available for the selected range.")
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
