import time
import pandas as pd
import os
import boto3
from dotenv import load_dotenv
import json
import random, string
import logging
import sqlite3
import sys
cwd = os.getcwd()


logging.basicConfig(filename = 'assignment_01.log',level=logging.INFO, force= True, format='%(asctime)s:%(levelname)s:%(message)s')


load_dotenv()

# Navigate to the project directory
project_dir = os.path.abspath(os.path.join(cwd, '..'))
sys.path.insert(0, project_dir)
os.environ['PYTHONPATH'] = project_dir + ':' + os.environ.get('PYTHONPATH', '')

database_path = os.path.join(project_dir, 'data', 'assignment_01.db')


clientlogs = boto3.client('logs',
region_name= "us-east-1",
aws_access_key_id=os.environ.get('AWS_LOG_ACCESS_KEY'),
aws_secret_access_key=os.environ.get('AWS_LOG_SECRET_KEY'))



def createConnection():
    
    """ This function creates a connection to the AWS S3 bucket for fetching data
    Args:
        None
    Returns:
        s3client (boto3.client): The boto3 client object
    """


    s3client = boto3.client('s3',
    region_name= "us-east-1",
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY1'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY1'))

    write_logs("Connection to S3 bucket created")

    return s3client

    

def listFiles(year, month, day, station):

    """Lists the files in the S3 bucket baswed on the given year, month, day and station
    Args:
        year (str): year chosen by the user
        month (str): month chosen by the user
        day (str): day chosen by the user
        station (str): station chosen by the user
    Returns:
        tuple: Returns the tuple list of all the files available for the given year, month, day and station
    """

    s3 = createConnection()
    lst = []
    bucket = 'noaa-nexrad-level2'
    result = s3.list_objects(Bucket=bucket, Prefix= year + "/" + month + "/" + day + "/" + station + "/", Delimiter='/')
    for o in result.get('Contents'):
        lst.append(o.get('Key').split('/')[4])

    write_logs("files retrieved for the given year, month, day and station from the S3 bucket")
    return tuple(lst) 


def get_distinct_month(yearSelected):

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    month = pd.read_sql_query("SELECT DISTINCT Month FROM nexrad_" + yearSelected, connection)
    month = month['Month'].tolist()
    month.insert(0, None)

    return month
    





def write_logs(message):

    """Writes the logs to the cloudwatch logs

    Args:
        message (str): The message to be written to the logs
    """

    clientlogs.put_log_events (
    logGroupName="assignment_01",
    logStreamName="app_logs",
    logEvents=[
        {
    'timestamp' : int(time.time()* 1e3),
    'message': message,
    }
    ]
    )










# def createJson(year):
#     """Creates a json file with the nexrad data

#     Args:
#         year (string): The year to be used to create the json file

#     Returns:
#         generatedJson (Json): Generated Json based on the fiven year
#     """
    
#     generatedJson = {}
#     s3 = createConnection()

#     bucket = 'noaa-nexrad-level2'
#     paginator = s3.get_paginator('list_objects')
#     config = {"PageSize":100}
#     operation_parameters = {'Bucket': bucket,
#                         'Prefix': year + "/",
#                         'Delimiter':'/',
#                         'PaginationConfig': config}
                        

#     result = paginator.paginate(**operation_parameters)

#     for page in result:
#         for o in page.get('CommonPrefixes'):
#             generatedJson[o.get('Prefix').split('/')[1]] = {}
    
#     for m in list(generatedJson.keys()):
#         result = s3.list_objects(Bucket=bucket, Prefix= year + "/" + m + '/' , Delimiter='/')
#         for o in result.get('CommonPrefixes'):
#             generatedJson[m][o.get('Prefix').split('/')[2]] = []

#     for m in list(generatedJson.keys()):
#         for d in list(generatedJson[m].keys()):
#             result = s3.list_objects(Bucket=bucket, Prefix= year + '/' +m+'/'+d+'/', Delimiter='/')
#             for o in result.get('CommonPrefixes'):
#                 generatedJson[m][d].append(o.get('Prefix').split('/')[3])


#     return generatedJson




# def grabData():

#     """Grabs the data from the S3 bucket and creates a json file for each year"""

#     # Call grab data function to create Json for year 2022 and 2023

#     year = ['2022', '2023']

#     for y in year:

#         data_files = os.listdir('data/')
#         if 'nexrad_data_'+str(y)+'.json' not in data_files:
#             with open(os.path.join('data/', 'nexrad_data_'+str(y)+'.json'), 'w') as outfile:
#                 json.dump(createJson(y), outfile)
#                 logging.info("Json file created for the year " + str(y))




# def generateCsv(year):

#     """Generates the csv file for the given year
    
#     Args:
#         year (str): year for which the CSV file is to be generated
#     """

#     month_lst = []
#     day_lst = []
#     station_lst = []


#     with open('data/nexrad_data_' + year + '.json') as user_file:
#         file_contents = user_file.read()
#     data = json.loads(file_contents)


#     for month in data:
#         for day in data[month]:
#             month_lst.append(month)
#             day_lst.append(day)
#             station_lst.append(data[month][day])

#     df = pd.DataFrame({'Year': year, 'Month': month_lst, 'Day': day_lst, 'Station': station_lst})
#     df.to_csv(os.path.join(data_path, 'nexrad_data_' + year + '.csv'), index=False)












