# import pandas as pd
# import plotly.express as px
# import sqlite3
# import os
# import streamlit as st

# database_file_name = "assignment_01.db"
# database_file_path = os.path.join('data/',database_file_name)
# db = sqlite3.connect(database_file_path)

# df = pd.read_sql_query("SELECT * FROM nexrad_plot", db)
# #sql_query = pd.read_sql('SELECT * FROM NEXRAD_PLOT', con)
# #df = pd.DataFrame(sql_query, columns = ['Id', 'State', 'City','ICAO_Location_Identifier','Coordinates','Lat','Lon'])
# st.title("NEXRAD Station Locations")
# fig = px.scatter_geo(df,lat='Lat',lon='Lon')
# fig.update_layout(title = 'Nexrad Locations', title_x=0.5)
# st.plotly_chart(fig, use_container_width=True)
