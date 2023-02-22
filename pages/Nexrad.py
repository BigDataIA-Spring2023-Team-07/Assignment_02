import requests
import streamlit as st
import json
from backend import nexrad_main, nexrad_main_sqlite
from pages import Nexrad
import os
import sqlite3
import warnings
import ast

import pandas as pd
warnings.filterwarnings("ignore")


data_path = 'data/'
database_file_name = 'assignment_01.db'
database_path = os.path.join('data/', database_file_name)
data_files = os.listdir('data/')


st.title("Generate Link Nexrad")



# User selects the year
yearSelected = st.selectbox(
    'Select the year',
    (None, '2022', '2023'), key = 'year')



# User selects the month
if yearSelected != None:
    FASTAPI_URL = "http://localhost:8000/nexrad_s3_fetch_month"
    response = requests.get(FASTAPI_URL, json={"yearSelected": yearSelected})
    monthSelected = None
    if response.status_code == 200:
        month = response.json()
        month = month['Month']
        monthSelected = st.selectbox(
            'Select the month',
            tuple(month), key = 'month')

    # User selects the day
    if monthSelected != None:
        FASTAPI_URL = "http://localhost:8000/nexrad_s3_fetch_day"
        response = requests.get(FASTAPI_URL, json={"year": yearSelected, "month": monthSelected})
        daySelected = None
        if response.status_code == 200:
            day = response.json()
            day = day['Day']
            daySelected = st.selectbox(
                'Select the day',
                tuple(day), key = 'day')

        # User selects the station
        if daySelected != None:
            FASTAPI_URL = "http://localhost:8000/nexrad_s3_fetch_station"
            response = requests.get(FASTAPI_URL, json={"year": yearSelected, "month": monthSelected, "day": daySelected})
            stationSelected = None
            if response.status_code == 200:
                station = response.json()
                station = station['Station']
                stationSelected = st.selectbox(
                    'Select the station',
                    tuple(station), key = 'station')

        
        # User selects the file
            with st.spinner('Fetching Files...'):
                if stationSelected != None:
                    FASTAPI_URL = "http://localhost:8000/nexrad_s3_fetch_file"
                    response = requests.get(FASTAPI_URL, json={"year": yearSelected, "month": monthSelected, "day": daySelected, "station": stationSelected})
                    fileSelected = None
                    if response.status_code == 200:
                        file = response.json()
                        file = file['File']
                        fileSelected = st.selectbox(
                            'Select the file',
                            tuple(file), key = 'file')


            if st.button("Submit"):
                with st.spinner('Generating Public S3 Link...'):
                    FASTAPI_URL = "http://localhost:8000/nexrad_s3_fetchurl"

                    response = requests.post(FASTAPI_URL, json={"year": yearSelected, "month": monthSelected, "day": daySelected, "station": stationSelected, "file": fileSelected})
                    if response.status_code == 200:
                        generated_url = response.json()
                        st.success("Successfully generated Public S3 link")
                        st.markdown("**Public URL**")

                        st.write(generated_url['Public S3 URL'])
                    else:
                        st.error("Error in generating Public S3 link")
                        st.write(response.json())

                with st.spinner('Generating Custom Link...'):

                    if len(monthSelected) == 1:
                        monthSelected = '0' + monthSelected
                    if len(daySelected) == 1:
                        daySelected = '0' + daySelected
                    
                    FASTAPI_URL = "http://localhost:8000/nexrad_s3_fetch_key"
                    response = requests.get(FASTAPI_URL, json={"year": yearSelected, "month": monthSelected, "day": daySelected, "station": stationSelected, "file": fileSelected})
                    if response.status_code == 200:
                        obj_key = response.json()['Key']

                        FASTAPI_URL = "http://localhost:8000/nexrad_s3_upload"
                        response = requests.post(FASTAPI_URL, json={"key": obj_key, "source_bucket": 'noaa-nexrad-level2', "target_bucket": 'damg7245-team7'})
                        if response.status_code == 200:
                            user_key = response.json()['Uploaded_Key']
                            FASTAPI_URL = "http://localhost:8000/nexrad_s3_generate_user_link"

                            response = requests.post(FASTAPI_URL, json={"target_bucket": 'damg7245-team7', "user_key": user_key})
                            if response.status_code == 200:
                                user_url = response.json()['User S3 URL']
                                st.success("Successfully uploaded to User S3 Bucket")
                                st.markdown("**AWS S3 URL**")
                                st.write(user_url)





