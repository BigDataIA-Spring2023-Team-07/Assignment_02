import requests
import streamlit as st
from backend import nexrad_file_retrieval_main
import os
from dotenv import load_dotenv
import requests

load_dotenv()

ACCESS_TOKEN = os.environ["access_token"]
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

st.title("Generate NOAA-NEXRAD URL By Filename")

response = requests.get('http://127.0.0.1:8000/is_logged_in',headers=headers)

if response.status_code == 200:
    file_name = st.text_input('Enter File Name')
    st.text("")
    if st.button('Get URL'):
        with st.spinner('Processing...'):
            if file_name:
                FASTAPI_URL = "http://localhost:8000/nexrad_get_download_link"
                response = requests.post(FASTAPI_URL, json={"filename": file_name})
                if response .status_code == 200:
                    res = response.json()['Response']
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
                    st.error('Either you have not logged in or else your session has expired.', icon="🚨")
            else:
                st.warning('Please enter a file name!', icon="⚠️")
else:
    st.error('Either you have not logged in or else your session has expired.', icon="🚨")
