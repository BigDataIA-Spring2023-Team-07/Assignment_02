import streamlit as st
from backend import goes_file_retrieval_main

st.title("Generate NOAA-GOES18 URL BY FILE")

file_name = st.text_input('Enter File Name')
st.text("")
if st.button('Get URL'):
    with st.spinner('Processing...'):
        if file_name:
            validate_res = goes_file_retrieval_main.validate_file(file_name)
            st.text("")
            if validate_res == 'Valid filename':
                get_res = goes_file_retrieval_main.get_file_url(file_name)
                if get_res == 404:
                    st.error('File does not exist. Please check the file name and try again!', icon="🚨")
                else:
                    st.write('Download URL:  \n ', get_res)
            else:
                st.warning(validate_res, icon="⚠️")
        else:
            st.warning('Please enter a file name!', icon="⚠️")
          
