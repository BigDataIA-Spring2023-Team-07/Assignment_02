import streamlit as st
import pandas as pd
import numpy as np
import sys
sys.path.append('../Assignment_02')
from backend import main_goes18
import requests

st.title('Generate GOES18 image URL')

FASTAPI_url='http://127.0.0.1:8000/goes_station'
response=requests.get(FASTAPI_url)

if response.status_code == 200:
    station=response.json()
    station_list=station['Stations']
    station_box = st.selectbox(
        'Station:',station_list)
    FASTAPI_url='http://127.0.0.1:8000/goes_years'
    data={'station':station_box}
    response=requests.get(FASTAPI_url,json=data)
    if response.status_code==200:
        year=response.json()
        year_list=year['Year']
        year_box = st.selectbox('Year:',year_list)
        FASTAPI_url='http://127.0.0.1:8000/goes_days'
        data={'station':station_box,'year':year_box}
        response=requests.get(FASTAPI_url,json=data)
        if response.status_code==200:
            day=response.json()
            day_list=day['Day']
            day_box = st.selectbox('Day:',day_list)
            FASTAPI_url='http://127.0.0.1:8000/goes_hours'
            data={'station':station_box,'year':year_box, 'day':day_box}
            response=requests.get(FASTAPI_url,json=data)
            if response.status_code==200:
                hour=response.json()
                hour_list=hour['Hour']
                hour_box = st.selectbox('Hour:',hour_list)
                FASTAPI_url='http://127.0.0.1:8000/goes_files'
                data={'station':station_box,'year':year_box, 'day':day_box,'hour':hour_box}
                response=requests.get(FASTAPI_url,json=data)
                if response.status_code==200:
                    file=response.json()
                    file_list=file['Files']
                    file_box = st.selectbox('Files:',file_list)

                if st.button('Submit'):

                    FASTAPI_url='http://127.0.0.1:8000/goes_fetch_url'
                    input={'station':station_box,'year':year_box,'day':day_box,'hour':hour_box,'file':file_box}
                    response=requests.post(FASTAPI_url,json=input)
                    if response.status_code==200:
                        goes_url=response.json()
                        goes_url=goes_url['NOAAURL']
                        st.markdown("**Generated URL**")
                        st.write(goes_url)
                        FASTAPI_url='http://127.0.0.1:8000/goes_AWS_url'
                        input={'station':station_box,'year':year_box,'day':day_box,'hour':hour_box,'file':file_box}
                        response=requests.post(FASTAPI_url,json=input)
                        if response.status_code==200:
                            aws_url=response.json()
                            aws_url=aws_url['S3URL']
                            st.markdown("**AWS S3 URL**")
                            st.write(aws_url)
                        else:
                            st.markdown("**Error generating AWS S3 URL**")
                    
                    else:
                            st.markdown("**Error generating NOAA GOES URL**")
    
