import requests
import streamlit as st
from backend import nexrad_file_retrieval_main

st.title("Generate NOAA-NEXRAD URL By Filename")

file_name = st.text_input('Enter File Name')
st.text("")
if st.button('Get URL'):
    with st.spinner('Processing...'):
        if file_name:
            FASTAPI_URL = "http://localhost:8000/nexrad_get_download_link"
            response = requests.post(FASTAPI_URL, json={"filename": file_name})
            if response.status_code == 200:              
               res = response.json()['Response']
               # res = nexrad_file_retrieval_main.get_nexrad_file_url(file_name)
               st.text("")
               if res == 'invalid filename':                
                 st.warning('Entered file name is invalid!', icon="⚠️")
               elif res == 'invalid datetime':
                 st.warning('Entered file name is invalid. Please check the date/time format!', icon="⚠️")
               elif res == 404:
                 st.error('File does not exist. Please check the file name and try again!', icon="🚨")
               else:
                 st.write('Download URL:  \n ', res)
            else:
               st.error('API Response Status Code Error', icon="🚨")
        else:
            st.warning('Please enter a file name!', icon="⚠️")
          
