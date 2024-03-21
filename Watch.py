import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
import datetime
from datetime import time, datetime, timedelta
import json
import jwt 



from datetime import datetime, timedelta

class Watch:
    def __init__(self, base_url_12, base_url_1, token):
        self.base_url_12 = base_url_12
        self.base_url_1 = base_url_1
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}'
        }
        

class subject(Watch):
    def __init__(self,
                 url,
                 token,
                 start_date,
                 end_date,
                 start_time,
                 end_time,
                 subject
                 ):
        super().__init__(url, token)
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.start_datetime = datetime.strptime(f'{self.start_date} {self.start_time}', '%Y-%m-%d %H:%M:%S')
        self.end_datetime = datetime.strptime(f'{self.end_date} {self.end_time}', '%Y-%m-%d %H:%M:%S')
        self.start_timestamp = int(self.start_datetime.timestamp())
        self.end_timestamp = int(self.end_datetime.timestamp())
        self.data = self.get_data()
        self.activity_time_series = None
        self.breathing_rate = None
        self.plot = self.get_plot()
        
    def fetch_data(self, type_url):
        
        response = requests.get(type_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Failed to fetch data: {response.status_code}, {response.text}"
        
    
    def get_Activity_Time_Series(self, resource, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_1}activities/{resource}/date/{start_date}/{end_date}.json')
        
        if resource == 'tracker/calories':
            data = url['activities-tracker-calories']
            df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'calories': [x['value'] for x in data]})
            return df

        elif resource == 'tracker/steps':
            data = url['activities-tracker-steps']
            df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'steps': [x['value'] for x in data]})
            return df
            
        elif resource == 'tracker/distance':
            data = url['activities-tracker-distance']
            df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'distance': [x['value'] for x in data]})
            return df
            
        elif resource == 'tracker/minutesSedentary':
            data = url['activities-tracker-minutesSedentary']
            df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'minutes_sedentary': [x['value'] for x in data]})
            return df
        
        elif resource == 'tracker/minutesLightlyActive':
            
            data = url['activities-tracker-minutesLightlyActive']
            df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'minutesLightlyActive': [x['value'] for x in data]})

            return df
        
        elif resource == 'tracker/minutesFairlyActive':
            
            data = url['activities-tracker-minutesFairlyActive']
            df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'minutesFairlyActive': [x['value'] for x in data]})
            
            return df
        
        elif resource == 'tracker/minutesVeryActive':
            
            data = url['activities-tracker-minutesVeryActive']
            df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'minutesVeryActive': [x['value'] for x in data]})

            return df
        
        elif resource == 'tracker/activityCalories':
            data = url['activities-tracker-activityCalories']
            df = pd.DataFrame(
                {'date': [x['dateTime'] for x in data], 'activityCalories': [x['value'] for x in data]})
            return df
        else:
            return df
        
    def get_Breathing_Rate(self, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_1}br/date/{start_date}/{end_date}.json')
        data = url['br']
        df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'breathing_rate': [x['value']['breathingRate'] for x in data]})
        return df            
    

    def get_Device(self):
        url = self.fetch_data(f'{self.base_url_1}devices.json')
        data = url[0]

        df = pd.DataFrame()
        df['battery'] = [data['batteryLevel']]
        df['lastSyncTime'] = [data['lastSyncTime']]
        df['device Version'] = [data['deviceVersion']]
        df['id'] = [data['id']]
        
        return df
    
    def get_Heart_Rate_Date_Range(self, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_1}activities/heart/date/{start_date}/{end_date}.json')
        data = url['activities-heart']
        df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'resting_heart_rate': [x['value']['restingHeartRate'] for x in data]})
        
        return df
    
    def get_HRV_Summary(self, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_1}hrv/date/{start_date}/{end_date}.json')
        data = url['hrv']
        df = pd.DataFrame({'date': [x['dateTime'] for x in data], 'dailyRmssd': [x['value']['dailyRmssd'] for x in data], 'deepRmssd': [x['value']['deepRmssd'] for x in data]})

        return df
    
    def get_Activity_Intraday(self, resource, start_date, end_date, detail_level, start_time, end_time):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        all_dates = pd.date_range(start_date, end_date)
        all_data_frames = []

        # Convert the date to string
        all_dates = [date.strftime('%Y-%m-%d') for date in all_dates]

        for date in all_dates:
            url = self.fetch_data(f'{self.base_url_1}activities/{resource}/date/{date}/1d/{detail_level}/time/{start_time}/{end_time}.json')
        
            if resource == 'calories':
                data = url['activities-calories-intraday']['dataset']
                df = pd.DataFrame({'time': [x['time'] for x in data], 'calories': [x['value'] for x in data]})
                df['date'] = date
                
                all_data_frames.append(df)
                
                
            elif resource == 'steps':
                data = url['activities-steps-intraday']['dataset']
                df = pd.DataFrame({'time': [x['time'] for x in data], 'steps': [x['value'] for x in data]})
                df['date'] = date
                
                all_data_frames.append(df)

            elif resource == 'distance':
                data = url['activities-distance-intraday']['dataset']
                df = pd.DataFrame({'time': [x['time'] for x in data], 'distance': [x['value'] for x in data]})
                df['date'] = date
                
                all_data_frames.append(df)
                
        final_df = pd.concat(all_data_frames)
        return final_df
    
    def get_Breath_Rate_Intraday(self, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_1}br/date/{start_date}/{end_date}/all.json')
        data = url['br']


        df = pd.DataFrame({
            'date': [x['dateTime'] for x in data], 
            'breath rate deep sleep': [x['value']['deepSleepSummary']['breathingRate'] for x in data],
            'breath rate rem sleep': [x['value']['remSleepSummary']['breathingRate'] for x in data],
            'breath rate light sleep': [x['value']['lightSleepSummary']['breathingRate'] for x in data],
            'breath rate full sleep': [x['value']['fullSleepSummary']['breathingRate'] for x in data]
        })
        
        return df
    
    def get_Heart_Rate_Intraday_(self, start_date, end_date, detail_level, start_time, end_time):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_dates = pd.date_range(start_date, end_date)
        all_data_frames = []
        
        all_dates = [date.strftime('%Y-%m-%d') for date in all_dates]
        
        for date in all_dates:
            url = self.fetch_data(f'{self.base_url_1}activities/heart/date/{date}/1d/{detail_level}/time/{start_time}/{end_time}.json')
            data = url['activities-heart-intraday']['dataset']
            df = pd.DataFrame({'time': [x['time'] for x in data], 'heart_rate': [x['value'] for x in data]})
            df['date'] = date
            all_data_frames.append(df)
            
        final_df = pd.concat(all_data_frames)
        return final_df
    
    def get_HRV_Intraday(self, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_dates = pd.date_range(start_date, end_date)
        all_data_frames = []
        
        all_dates = [date.strftime('%Y-%m-%d') for date in all_dates]
        
        for date in all_dates:    
            url = self.fetch_data(f'{self.base_url_1}hrv/date/{date}/all.json')
            
            # Initialize an empty list to hold the extracted data
            extracted_data = []

            # Iterate through each entry in the "hrv" list
            for entry in url["hrv"]:
                date = entry["dateTime"]
                for minute_entry in entry["minutes"]:
                    # Parsing the 'minute' string to separate the date and time
                    datetime_str = minute_entry["minute"]
                    date_part, time_part = datetime_str.split('T')
                    time_part = time_part.split('.')[0]  # Removing milliseconds
                    
                    # Extracting values
                    rmssd = minute_entry["value"]["rmssd"]
                    coverage = minute_entry["value"]["coverage"]
                    hf = minute_entry["value"]["hf"]
                    lf = minute_entry["value"]["lf"]
                    
                    # Append the extracted information as a tuple to our list
                    extracted_data.append((date_part, time_part, rmssd, coverage, hf, lf))

            # Convert the list of tuples into a DataFrame
            df = pd.DataFrame(extracted_data, columns=["Date", "Time", "RMSSD", "Coverage", "HF", "LF"])
            df['date'] = date
            all_data_frames.append(df)
            
        final_df = pd.concat(all_data_frames)
        return df
    
    def get_SpO2_Intraday(self, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_1}spo2/date/{start_date}/{end_date}/all.json')
        data = url
        df = pd.DataFrame()
        for i in range(len(data)):
            df['date'] = df.append(data[i]['dateTime'])
            for j in range(len(data[i]['minutes'])):
                df['minute'] = df.append(data[i]['minutes'][j]['minute'])
                df['value'] = df.append(data[i]['minutes'][j]['value'])
        return df
    
    def get_Temperature(self, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_1}body/temperature/date/{start_date}/{end_date}.json')
                
        data = url['tempSkin']
        df = pd.DataFrame({
            'date': [x['dateTime'] for x in data], 
            'tempSkin': [x['value']['nightlyRelative'] for x in data]
        })
        return df
        
    def get_Sleep(self, start_date, end_date):
        url = self.fetch_data(f'{self.base_url_12}sleep/date/{start_date}/{end_date}.json')
        data = url['sleep']
        df = pd.DataFrame({
            'date': [x['dateOfSleep'] for x in data], 
            'duration': [x['duration'] for x in data],
            'efficiency': [x['efficiency'] for x in data],
            'minutesAsleep': [x['minutesAsleep'] for x in data],
            'minutesAwake': [x['minutesAwake'] for x in data],
            'minutesToFallAsleep': [x['minutesToFallAsleep'] for x in data],
            'timeInBed': [x['timeInBed'] for x in data]
        })    
        return df  
    
    # Merge dataframes
    def Merge(self, df1, df2, on):
        return pd.merge(df1, df2, on=on)
        
    
    
        
            
            
        

        
        