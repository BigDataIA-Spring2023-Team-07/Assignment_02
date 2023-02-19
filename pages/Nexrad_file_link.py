import streamlit as st
from backend import nexrad_file_retrieval_main

st.title("Generate NOAA-NEXRAD URL BY FILE")

file_name = st.text_input('Enter File Name')
st.text("")
if st.button('Get URL'):
    with st.spinner('Processing...'):
        if file_name:
            res = nexrad_file_retrieval_main.get_nexrad_file_url(file_name)
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
            st.warning('Please enter a file name!', icon="⚠️")
          
