import fitbit
import gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import hashlib
import random
from pymongo import MongoClient
import requests
from datetime import timedelta

# YOU NEED TO PUT IN YOUR OWN CLIENT_ID AND CLIENT_SECRET
CLIENT_ID='23RSQ9'
CLIENT_SECRET='02cfa1fab17c92b884943da2b97eef4d'

server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
server.browser_authorize()
ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])
auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)


def getActivityData():

    # List of activity types to retrieve from Fitbit API
    activityList = ['activities/minutesSedentary', 'activities/minutesLightlyActive','activities/minutesFairlyActive',
                    'activities/minutesVeryActive', 'activities/heart']
    
    # Retrieve activity data from Fitbit API for specified date range and activity types
    minutesSedentary = df_fitbit(activityList[0], base_date, end_date, token)['activities-minutesSedentary']
    minutesLightlyActive = df_fitbit(activityList[1], base_date, end_date, token)['activities-minutesLightlyActive']
    minutesFairlyActive = df_fitbit(activityList[2], base_date, end_date, token)['activities-minutesFairlyActive']
    minutesVeryActive = df_fitbit(activityList[3], base_date, end_date, token)['activities-minutesVeryActive']
    heartRate = df_fitbit(activityList[4], base_date, end_date, token)['activities-heart']
    
    # Loop through sedentary minutes data and create new data entries for each type of activity
    for sedentary in minutesSedentary:
        datetimeSed = sedentary['dateTime']
        totalTime = int(sedentary['value'])
        
        # Find matching heart rate data for the sedentary minute and add to the total time
        for heart in heartRate:
            if heart['dateTime'] == datetimeSed:
                if totalTime == 1440:
                    totalTime = 0
                minutesSedentaryDict = {
                    "dateTime": datetimeSed, 
                    "value": totalTime, 
                    } 
                create_data(minutesSedentaryDict,"minutesSedentary")

                # Find matching lightly active minutes data for the sedentary minute and add to the total time
                for lightlyActive in minutesLightlyActive:
                    if datetimeSed == lightlyActive['dateTime']:
                        minutesLightlyActiveDict = {
                            "dateTime": datetimeSed, 
                            "value": int(lightlyActive['value']), 
                            } 
                        create_data(minutesLightlyActiveDict,"minutesLightlyActive")
                        totalTime += int(lightlyActive['value'])
                
                # Find matching fairly active minutes data for the sedentary minute and add to the total time
                for fairlyActive in minutesFairlyActive:
                    if datetimeSed == fairlyActive['dateTime']:
                        minutesFairlyActiveDict = {
                            "dateTime": datetimeSed, 
                            "value": int(fairlyActive['value']), 
                            } 
                        create_data(minutesFairlyActiveDict,"minutesFairlyActive")

                        totalTime += int(fairlyActive['value'])

                # Find matching very active minutes data for the sedentary minute and add to the total time
                for veryActive in minutesVeryActive:
                    if datetimeSed == veryActive['dateTime']:
                        minutesVeryActiveDict = {
                            "dateTime": datetimeSed, 
                            "value": int(veryActive['value']), 
                            } 
                        create_data(minutesVeryActiveDict,"minutesVeryActive")
                    
                        totalTime += int(veryActive['value'])

        # Create a new data entry for total wear time for the day
        activityDict = {
            "dateTime": datetimeSed, 
            "value": totalTime, 
            }    
    
        create_data(activityDict,"totalWearTime")

def getStepsData():
    # Get steps count data from the Fitbit API for the specified date range
    steps_count = df_fitbit('activities/steps', base_date, end_date, token)['activities-steps']

    # Initialize an empty list to store the dates with over 10,000 steps
    highly_active_days = []

    # Loop through each item in the steps count data
    for i in range(0, len(steps_count)):
        # Get the number of steps and the date for the current item
        steps = steps_count[i].get('value')
        date = steps_count[i].get('dateTime')
        
        # Create a dictionary for the steps count data for the current date
        stepsDict = {
            "dateTime": date, 
            "value": steps, 
        }
        
        create_data(stepsDict,"steps")

def getSleepData():

    sleepList = df_fitbit('sleep', base_date, end_date, token)['sleep']

    for sleepItem in sleepList:
        mainSleep = sleepItem['isMainSleep']
        if mainSleep == True:
            
            startTimeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['startTime']
            }
            create_data(startTimeDict,"sleep_startTime")

            endTimeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['endTime']
            }
            create_data(endTimeDict,"sleep_endTime")

            timeInBedDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['timeInBed']
            }
            create_data(timeInBedDict,"timeInBed")

            minutesAsleepDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['minutesAsleep']
            }
            create_data(minutesAsleepDict,"minutesAsleep")

            minutesAwakeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['minutesAwake']
            }
            create_data(minutesAwakeDict,"minutesAwake")

            efficiencyDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['efficiency']
            }
            create_data(efficiencyDict,"sleep_efficiency")

            summaryDeepDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['levels']['summary']['deep']['minutes']
            }
            create_data(summaryDeepDict,"sleep_Deep")

            summaryLightDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['levels']['summary']['light']['minutes']
            }
            create_data(summaryLightDict,"sleep_Light")

            summaryRemDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['levels']['summary']['rem']['minutes']
            }
            create_data(summaryRemDict,"sleep_Rem")

            summaryWakeDict = {
                "dateTime": sleepItem['dateOfSleep'],
                "value": sleepItem['levels']['summary']['wake']['minutes']
            }
            create_data(summaryWakeDict,"sleep_Wake")

def df_fitbit(activity, base_date, end_date, token):
    url = 'https://api.fitbit.com/1.2/user/-/' + activity + '/date/' + base_date + '/' + end_date + '.json'
    response = requests.get(url=url, headers={'Authorization':'Bearer ' + token}).json()

    return response

def create_data(dictItem,typeItem):
    data_list = []
    # create a random hash ID
    hash_object = hashlib.sha256(str(random.getrandbits(256)).encode())
    id = hash_object.hexdigest()  
    # create a new dictionary with the id, type, and data fields
    new_dict = {
        'id': id,
        'type': typeItem,
        'data': dictItem
      }           
        # append the new dictionary to the output list
    collection.insert_one(new_dict)
    return data_list 


token = ACCESS_TOKEN
base_date = '2024-03-17'
end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# establing connection
try:
    connect = MongoClient()
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

# connecting or switching to the database
db = connect.fitbitDB

# creating or switching to fitbitCollection
collection = db.fitbitCollection
