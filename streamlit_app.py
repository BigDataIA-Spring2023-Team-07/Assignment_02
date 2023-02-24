import streamlit as st
from PIL import Image
import pandas as pd

from passlib.context import CryptContext
from pages import Nexrad
from pages import Nexrad_plot
import sqlite3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
#st.set_page_config(page_title="streamlit_app.py", initial_sidebar_state="collapsed")
#st.markdown(no_sidebar_style, unsafe_allow_html=True)

def create_plot_table():
    response = requests.post('http://127.0.0.1:8000/create_plot_table')
    return response   

def create_default_user():
    response = requests.post('http://127.0.0.1:8000/create_default_user')
    return response

if __name__ == "__main__":
    create_default_user()
    create_plot_table()
    with st.container():
        Username = st.text_input('Username')
        Password = st.text_input('Password')
        if st.button('Verify'):
            if Username == "" or Password == "":
                st.error('Username or Password value is empty')
            else:
                data = {
                "grant_type": "password",
                "username": Username,
                "password": Password
                }
                response = requests.post('http://127.0.0.1:8000/login',data=data)
                if int(response.json()['status_code']) == 200:
                    os.environ["access_token"] = response.json()['access_token']
                    with open(".env", "w") as f:
                        f.write(f"access_token={response.json()['access_token']}\n")
                    st.success('Login Successful')
                    st.markdown('http://localhost:8501/Home', unsafe_allow_html=True)
                elif int(response.json()['status_code']) == 404:
                    st.error('Username not found in the database')
                else:
                    st.error('Password is incorrect')