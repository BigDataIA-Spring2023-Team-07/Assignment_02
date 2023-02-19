import streamlit as st
import json
from backend import nexrad_main, nexrad_main_sqlite
from pages import Nexrad
import os
import sqlite3
import warnings
warnings.filterwarnings("ignore")


data_path = 'data/'
database_file_name = 'assignment_01.db'
database_path = os.path.join('data/', database_file_name)
data_files = os.listdir('data/')



def generateData():

    """Generates csv file for nexrad 2022 and nexrad 2023 data

    """

    # Grabs the Json if its not available
    nexrad_main.grabData()


    # Creates csv file based on the Json file
    if 'nexrad_data_2022.csv' not in data_files:
        nexrad_main.generateCsv('2022')

    if 'nexrad_data_2023.csv' not in data_files:
        nexrad_main.generateCsv('2023')

def insertData_to_db():
    """
    Inserts the contents from csv file to db
    """

    # Inserts the contents from csv file to db
    year = ['2022','2023']
    for y in year:
        nexrad_main_sqlite.insert_data(y)


def retrieveData_from_db(yearSelected):
    """Retrieves the contents from db

    Args:
        yearSelected (str): the year for which the data is to be retrieved

    Returns:
        Json: returns the retrived data in Json format
    """

    # Retrieves the contents from db

    if yearSelected == '2022':

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        cursor.execute("Select * from nexrad_2022_json")

        rows = cursor.fetchall()
        data = json.loads(rows[0][0])
        connection.close()

    if yearSelected == '2023':

        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        cursor.execute("Select * from nexrad_2023_json")

        rows = cursor.fetchall()
        data = json.loads(rows[0][0])
        connection.close()

    return data


Nexrad.generateData()

st.title("Generate Link Nexrad")


# User selects the year
yearSelected = st.selectbox(
    'Select the year',
    ('2022', '2023'), key = 'year1')

insertData_to_db()
data = retrieveData_from_db(yearSelected)
nexrad_main.appendCsv()


# User selects the month
monthSelected = st.selectbox(
    'Select the month',
    tuple(data.keys()), key = 'month')

# User selects the day
daySelected = st.selectbox(
    'Select the day',
    tuple(data[monthSelected].keys()), key = 'day')


# User selects the station
stationSelected = st.selectbox(
    'Select the station',
    tuple(data[monthSelected][daySelected]), key = 'station')


# User selects the file
file_tup = nexrad_main.listFiles(yearSelected, monthSelected, daySelected, stationSelected)
fileSelected = st.selectbox(
        'Select the file',
        file_tup, key = 'file')


if st.button("Submit"):
    if fileSelected == None:
        st.warning('Please click on the submit button and then select the file before clicking on generate link', icon="⚠️")
    else:
        generated_url = nexrad_main.generateLink(yearSelected, monthSelected, daySelected, stationSelected, fileSelected)
        st.markdown("**Public URL**")
        st.write(generated_url)


        st.markdown("**AWS S3 URL**")
        obj_key = nexrad_main.getKey(yearSelected, monthSelected, daySelected, stationSelected, fileSelected)
        user_key = nexrad_main.uploadFiletoS3(obj_key, 'noaa-nexrad-level2', 'damg7245-team7')
        user_url = nexrad_main.generateUserLink('damg7245-team7' ,user_key)
        st.write(user_url)





