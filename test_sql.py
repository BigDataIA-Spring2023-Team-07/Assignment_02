
import pandas as pd
import sqlite3

# read the CSV file into a DataFrame
df = pd.read_csv('data/nexrad_2023.csv')

# create a connection to the SQLite database
conn = sqlite3.connect('assignment_01.db')

# write the DataFrame to the database
table_name = 'nexrad_2023'
df.to_sql(table_name, conn, if_exists='replace', index=False)

# close the database connection
conn.close()
