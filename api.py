import ast
import json
import sqlite3
import os
from fastapi import FastAPI, Response, status
import requests
from backend import nexrad_main, main_goes18
from pydantic import BaseModel
import pandas as pd
import re


data_path = 'data/'
database_file_name = 'assignment_01.db'
database_path = os.path.join('data/', database_file_name)
data_files = os.listdir('data/')

goes_database_file_name = 'goes18.db'
goes_database_file_path = os.path.join('data/',goes_database_file_name)

app = FastAPI()

class Nexrad_S3_fetch_month(BaseModel):
    yearSelected: str

class Nexrad_S3_fetch_day(BaseModel):
    year: str
    month: str

class Nexrad_S3_fetch_station(BaseModel):
    year: str
    month: str
    day: str

class Nexrad_S3_fetch_file(BaseModel):
    year: str
    month: str
    day: str
    station: str

class Nexrad_S3_fetch_url(BaseModel):
    year: str
    month: str
    day: str
    station: str
    file:str



@app.get('/nexrad_s3_fetch_month')
async def nexrad_s3_fetch_month(nexrad_s3_fetch_month: Nexrad_S3_fetch_month):

    """Generates the list of months for the year chosen by the user
    
    Args:
        year (str): year chosen by the user
        
    Returns:
        list: Returns the list of months"""


    if not re.match(r"^[0-9]{4}$", nexrad_s3_fetch_month.yearSelected):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    if int(nexrad_s3_fetch_month.yearSelected) < 2022 or int(nexrad_s3_fetch_month.yearSelected) > 2023:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    else:
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()
        month = pd.read_sql_query("SELECT DISTINCT Month FROM nexrad_" + nexrad_s3_fetch_month.yearSelected, connection)
        month = month['Month'].tolist()
        month.insert(0, None)
        return {"Month": month}

@app.get('/nexrad_s3_fetch_day')
async def nexrad_s3_fetch_day(nexrad_s3_fetch_day: Nexrad_S3_fetch_day):
    
        """Generates the list of days for the month chosen by the user
        
        Args:
            year (str): year chosen by the user
            month (str): month chosen by the user
            
        Returns:
            list: Returns the list of days"""
        
        # In the database the month is stored as 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 but in the bucket its stored as 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12
    
        if not re.match(r"^(1[0-2]|[1-9])$", nexrad_s3_fetch_day.month):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        if int(nexrad_s3_fetch_day.month) < 1 or int(nexrad_s3_fetch_day.month) > 12 :
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
        
        else:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            day = pd.read_sql_query("SELECT DISTINCT Day FROM nexrad_" + nexrad_s3_fetch_day.year + " WHERE year = '" + nexrad_s3_fetch_day.year + "'" + " AND month = '" + nexrad_s3_fetch_day.month + "'", connection)
            day = day['Day'].tolist()
            day.insert(0, None)
            return {"Day": day}

@app.get('/nexrad_s3_fetch_station')
async def nexrad_s3_fetch_station(nexrad_s3_fetch_station: Nexrad_S3_fetch_station):
    
        """Generates the list of stations for the day chosen by the user
        
        Args:
            year (str): year chosen by the user
            month (str): month chosen by the user
            day (str): day chosen by the user
            
        Returns:
            list: Returns the list of stations"""

        # In the database the day is stored as 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.... but in the bucket its stored as 01, 02, 03, 04, 05, 06, 07, 08, 09, 10....
            
        if not re.match(r"^(3[01]|[12][0-9]|[1-9])$", nexrad_s3_fetch_station.day):
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
        
        if int(nexrad_s3_fetch_station.day) < 1 or int(nexrad_s3_fetch_station.day) > 31:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)

        else:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()
            station = pd.read_sql_query("SELECT DISTINCT Station FROM nexrad_" + nexrad_s3_fetch_station.year + " WHERE year = '" + nexrad_s3_fetch_station.year + "'" + " AND month = '" + nexrad_s3_fetch_station.month + "'" + " AND day = '" + nexrad_s3_fetch_station.day + "'", connection)
            station = station['Station'][0]
            station = ast.literal_eval(station)
            station.insert(0, None)
            return {"Station": station}

@app.get('/nexrad_s3_fetch_file')
async def nexrad_s3_fetch_file(nexrad_s3_fetch_file: Nexrad_S3_fetch_file):

    """Generates the list of files for the station chosen by the user
        
        Args:
            
            year (str): year chosen by the user
            month (str): month chosen by the user
            day (str): day chosen by the user
            station (str): station chosen by the user
            
            Returns:
                list: Returns the list of files"""


    if not re.match(r"^[A-Z0-9]{4}$", nexrad_s3_fetch_file.station):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    else:
        if len(nexrad_s3_fetch_file.month) == 1:
            nexrad_s3_fetch_file.month = '0' + nexrad_s3_fetch_file.month
        if len(nexrad_s3_fetch_file.day) == 1:
            nexrad_s3_fetch_file.day = '0' + nexrad_s3_fetch_file.day

        file_tup = nexrad_main.listFiles(nexrad_s3_fetch_file.year, nexrad_s3_fetch_file.month, nexrad_s3_fetch_file.day, nexrad_s3_fetch_file.station)
        file_list = list(file_tup)
        return {"File": file_list}




@app.post('/nexrad_s3_fetchurl')
async def nexrad_s3_fetchurl(nexrad_s3_fetch: Nexrad_S3_fetch_url):

    """Generates the link for the file in the nexrad S3 bucket
    
    Args:
        year (str): year chosen by the user
        month (str): month chosen by the user
        day (str): day chosen by the user
        station (str): station chosen by the user
        file (str): file chosen by the user
        
    Returns:
        str: Returns the url of the file"""

    
    if not re.match(r"^[A-Z0-9]{4}\d{8}_\d{6}_V06$", nexrad_s3_fetch.file) or re.match(r"^[A-Z0-9]{4}\d{8}_\d{6}_V06_MDM$", nexrad_s3_fetch.file) :
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


    else:
        if len(nexrad_s3_fetch.month) == 1:
            nexrad_s3_fetch.month = '0' + nexrad_s3_fetch.month
        if len(nexrad_s3_fetch.day) == 1:
            nexrad_s3_fetch.day = '0' + nexrad_s3_fetch.day

        url = "https://noaa-nexrad-level2.s3.amazonaws.com/" + nexrad_s3_fetch.year + "/" + nexrad_s3_fetch.month + "/" + nexrad_s3_fetch.day + "/" \
        +  nexrad_s3_fetch.station + "/" + nexrad_s3_fetch.file

        response = requests.get(url)
        if response.status_code == 200:
            nexrad_main.write_logs("link generated for the User bucket")
            nexrad_main.write_logs(url)
            return {"Public S3 URL": url}
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)



### GOES Code

class goes_year(BaseModel):
    
    station: str
    
class goes_day(BaseModel):
    station: str
    year: str
    
class goes_hour(BaseModel):
    station: str
    year: str
    day: str     
    
class goes_file(BaseModel):
    station: str
    year: str
    day: str
    hour: str

class goes_url(BaseModel):
    station: str
    year: str
    day: str
    hour: str
    file: str

@app.get('/goes_station')
async def grab_station():
    """for pulling all the stations in the file from database

    Returns:
        stations_list: list of stations
    """
    stations=main_goes18.grab_station()
    
    return {'Stations':stations}


@app.get('/goes_years')
async def grab_years(user_station: goes_year ):
    """for pulling all the years in the station from database

    Args:
        station (string): station name

    Returns:
        year_list: list of all the years for a particular station
    """
    # 
    
    if not re.match(r"[A-Za-z0-9\.,;:!?()\"'%\-]+",user_station.station):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    else:
        
        year_list=main_goes18.grab_years(user_station.station)    
        
        return {'Year':year_list}

@app.get('/goes_days')
async def grab_months(user_day: goes_day):
    """for pulling all the days in the particular station,year from database

    Args:
        station (str): station
        years (str): year

    Returns:
        day_list: list of days for a particular station,year
    """
    
    if not re.match(r"[A-Za-z0-9\.,;:!?()\"'%\-]+",user_day.station):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_day.year)<2022 or int(user_day.year)>2023:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    else:
        
        day_list=main_goes18.grab_days(user_day.station,user_day.year)
        return {'Day':day_list}

@app.get('/goes_hours')
async def grab_hours(user_hour: goes_hour):
    
    """for pulling all the hours in the file for a particular station,year,day

    Args:
        station (str): station name
        years (str): year
        days (str): day

    Returns:
        hour_list: list of all hours in the file for a particular station,year,day
    """
    
    if not re.match(r"[A-Za-z0-9\.,;:!?()\"'%\-]+",user_hour.station):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_hour.year)<2022 or int(user_hour.year)>2023:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_hour.day)<1 or int(user_hour.day)>365:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    else:
        hour_list=main_goes18.grab_hours(user_hour.station,user_hour.year,user_hour.day)
        return {'Hour':hour_list}

@app.get('/goes_files')
async def grab_files(user_files: goes_file):
    """pulls files from noaa18 aws bucket for a set of station, year,day,hour

    Args:
        station (str): station name
        years (str): year
        days (str): day
        hours (str): hour

    Returns:
        file_names: list of files present in noaa18 aws bucket for a set of station, year,day,hour
    """
    
    # client_id=create_connection()
    
    # write_logs("fetching Files in list from NOAA bucket")
    if not re.match(r"[A-Za-z0-9\.,;:!?()\"'%\-]+",user_files.station):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_files.year)<2022 or int(user_files.year)>2023:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_files.day)<1 or int(user_files.day)>365:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_files.hour)<0 or int(user_files.hour)>24:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
        
    else:
        files_list=main_goes18.grab_files(user_files.station,user_files.year,user_files.day,user_files.hour)
        return {"Files":files_list}


@app.post('/goes_fetch_url')
async def create_url(user_url: goes_url):
    
    if not re.match(r"[A-Za-z0-9\.,;:!?()\"'%\-]+",user_url.station):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_url.year)<2022 or int(user_url.year)>2023:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_url.day)<1 or int(user_url.day)>365:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_url.hour)<0 or int(user_url.hour)>24:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not re.match(r"OR_ABI-L1b-RadC-M6C01_G18_s\d{14}_e\d{14}_c\d{14}\.nc",user_url.file):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    else:
        
        url=main_goes18.create_url(user_url.station,user_url.year,user_url.day,user_url.hour,user_url.file)
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return {'NOAAURL': url}
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        
@app.post('/goes_AWS_url')
async def s3_url(user_purl: goes_url):
     
    if not re.match(r"[A-Za-z0-9\.,;:!?()\"'%\-]+",user_purl.station):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_purl.year)<2022 or int(user_purl.year)>2023:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_purl.day)<1 or int(user_purl.day)>365:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if int(user_purl.hour)<0 or int(user_purl.hour)>24:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    if not re.match(r"OR_ABI-L1b-RadC-M6C01_G18_s\d{14}_e\d{14}_c\d{14}\.nc",user_purl.file):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    else:
        
        key = main_goes18.generate_key(user_purl.station,user_purl.year,user_purl.day,user_purl.hour,user_purl.file)
        url=main_goes18.copy_files_s3(key,user_purl.file)
        
        response = requests.get(url)
        
        if response.status_code == 200:
            return {'S3URL': url}
        else:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
     
            
    
    
    
    


