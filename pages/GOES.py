import streamlit as st
import pandas as pd
import numpy as np
import sys
sys.path.append('../Assignment_01')
from backend import main_goes18

st.title('Generate GOES18 image URL')

station_box = st.selectbox(
    'Station:',
    main_goes18.grab_station())

year_box = st.selectbox(
    'Year:',
    main_goes18.grab_years(station_box))

day_box = st.selectbox(
    'Day:',
    main_goes18.grab_days(station_box,year_box))

hour_box = st.selectbox(
    'Hour:',
    main_goes18.grab_hours(station_box,year_box,day_box))

files_box = st.selectbox(
    'Files:',
    main_goes18.grab_files(station_box,year_box,day_box,hour_box))

if st.button('Submit'):
    if files_box==None:
        st.warning("Please select a file then click on submit",icon="⚠️")
    else:
        generated_url= main_goes18.create_url(station_box,year_box,day_box,hour_box,files_box)
        st.markdown("**Generated URL**")
        st.write(generated_url)
        
        
        
        st.markdown("**AWS S3 URL**")
        key = main_goes18.generate_key(station_box,year_box,day_box,hour_box,files_box)
        aws_url=main_goes18.copy_files_s3(key,files_box)
        st.write(aws_url)
    
