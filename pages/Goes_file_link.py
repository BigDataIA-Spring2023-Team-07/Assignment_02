import requests
import streamlit as st
from backend import goes_file_retrieval_main

st.title("Generate NOAA-GOES18 URL BY FILE")

file_name = st.text_input('Enter File Name')
st.text("")
if st.button('Get URL'):
    with st.spinner('Processing...'):
        if file_name:
            response = requests.post('http://127.0.0.1:8000/validatefileUrl',json={'file_name': file_name})
            validate_res = response.json()['message']
            st.text("")
            if validate_res == 'Valid filename':
                response1 = requests.post('http://127.0.0.1:8000/getfileUrl',json={'file_name': file_name})
                get_res = response1.json()
                if get_res['status_code'] == '404':
                    st.error('File does not exist. Please check the file name and try again!', icon="🚨")
                else:
                    st.write('Download URL:  \n ', get_res['message'])
            elif validate_res == 'Authentication Error':
                st.write('You are not authorized to access this file.')
            else:
                st.warning(validate_res, icon="⚠️")
        else:
            st.warning('Please enter a file name!', icon="⚠️")
          
