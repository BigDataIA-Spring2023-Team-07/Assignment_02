import streamlit as st
from PIL import Image
import pandas as pd

from passlib.context import CryptContext
from pages import Nexrad
from pages import Nexrad_plot
import sqlite3
import os
import requests

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
#st.set_page_config(page_title="streamlit_app.py", initial_sidebar_state="collapsed")
#st.markdown(no_sidebar_style, unsafe_allow_html=True)

def create_plot_table():
    """creates data base leveraging the dataframe created
    """
    # with open(ddl_file_path, 'r') as sql_file:
        # sql_script = sql_file.read()
    database_file_name = "assignment_01.db"
    database_file_path = os.path.join('data/',database_file_name)
    db = sqlite3.connect(database_file_path)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE if not exists NEXRAD_PLOT (Id,State,City,ICAO_Location_Identifier,Coordinates,Lat,Lon)''')
    df = pd.read_csv("data/Nexrad.csv")
    df["Lon"] = -1 * df["Lon"]
    df.to_sql('nexrad_plot', db, if_exists='append', index = False)
    db.commit()
    db.close()

def create_default_user():
    """creates data base leveraging the dataframe created
    """
    # with open(ddl_file_path, 'r') as sql_file:
        # sql_script = sql_file.read()
    database_file_name = "assignment_01.db"
    database_file_path = os.path.join('data/',database_file_name)
    db = sqlite3.connect(database_file_path)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE if not exists Users (id,username,hashed_password)''')
    user= pd.read_sql_query("SELECT * FROM Users", db)
    if len(user) == 0:
        pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_cxt.hash(("spring2023"))
        cursor.execute("Insert into Users values (?,?,?)", (1,"damg7245",hashed_password))
        db.commit()
        db.close()

if __name__ == "__main__":
    #create_plot_table()
    create_default_user()
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
                    st.success('Login Successful')
                    st.markdown('http://localhost:8501/Home', unsafe_allow_html=True)
                elif int(response.json()['status_code']) == 404:
                    st.error('Username not found in the database')
                else:
                    st.error('Password is incorrect')