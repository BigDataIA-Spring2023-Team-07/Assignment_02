import streamlit as st
from PIL import Image
import pandas as pd

from pages import Nexrad
from pages import Nexrad_plot
import sqlite3
import os

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


if __name__ == "__main__":
    create_plot_table()
    st.title("Are you looking for SEVIR data?")
    st.text("Team07-Assignment1")
    st.text("Let us fetch that for you!")
    image = Image.open('image.png')
    st.image(image, caption='four humans working to fetch satelite data')
