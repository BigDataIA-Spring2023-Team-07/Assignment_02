import io
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import timedelta
import pandas as pd
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import boto3
import sqlite3



dag = DAG(
    dag_id="fetch_from_s3",
    schedule="0 5 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["labs", "damg7245"]
)


def create_s3_client():
    """Creates a s3 client
    
    Returns:
        s3_client (S3 Client): S3 Client
        
    """
    s3_hook = S3Hook(aws_conn_id='My AWS Connection', region_name='us-east-1')
    s3_client = s3_hook.get_conn()

    return s3_client

def createJson(year):
    """Creates a json file with the nexrad data

    Args:
        year (string): The year to be used to create the json file

    Returns:
        generatedJson (Json): Generated Json based on the fiven year
    """
    
    generatedJson = {}
    s3 = create_s3_client()

    bucket = 'noaa-nexrad-level2'
    paginator = s3.get_paginator('list_objects')
    config = {"PageSize":100}
    operation_parameters = {'Bucket': bucket,
                        'Prefix': year + "/",
                        'Delimiter':'/',
                        'PaginationConfig': config}
                        

    result = paginator.paginate(**operation_parameters)

    for page in result:
        for o in page.get('CommonPrefixes'):
            generatedJson[o.get('Prefix').split('/')[1]] = {}
    
    for m in list(generatedJson.keys()):
        result = s3.list_objects(Bucket=bucket, Prefix= year + "/" + m + '/' , Delimiter='/')
        for o in result.get('CommonPrefixes'):
            generatedJson[m][o.get('Prefix').split('/')[2]] = []

    for m in list(generatedJson.keys()):
        for d in list(generatedJson[m].keys()):
            result = s3.list_objects(Bucket=bucket, Prefix= year + '/' +m+'/'+d+'/', Delimiter='/')
            for o in result.get('CommonPrefixes'):
                generatedJson[m][d].append(o.get('Prefix').split('/')[3])


    return generatedJson


def upload_csv_to_S3(df, year):
    """Uploads the given dataframe to S3

    Args:
        df (Dataframe): Dataframe to be uploaded to S3
    """
    s3 = S3Hook(aws_conn_id='My AWS Connection', region_name='us-east-1')
    aws_credentials = s3.get_credentials()
    s3_resource = boto3.resource('s3', aws_access_key_id=aws_credentials.access_key, aws_secret_access_key=aws_credentials.secret_key, region_name='us-east-1')



    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    bucket_name = 'damg7245-team7'
    s3_key = 'data/' + year + '.csv'
    s3_resource.Object(bucket_name, s3_key).put(Body=csv_buffer.getvalue())


def upload_database_to_S3():

    s3 = S3Hook(aws_conn_id='My AWS Connection', region_name='us-east-1')
    aws_credentials = s3.get_credentials()
    s3_resource = boto3.resource('s3', aws_access_key_id=aws_credentials.access_key, aws_secret_access_key=aws_credentials.secret_key, region_name='us-east-1')


    s3_resource.meta.client.upload_file('assignment_02.db', 'damg7245-team7' , 'database.db')




def generateCsv(year):

    """Generates the csv file for the given year
    
    Args:
        year (str): year for which the CSV file is to be generated
    """

    month_lst = []
    day_lst = []
    station_lst = []



    data = createJson(year)

    # convert json to csv

    for month in data:
        for day in data[month]:
            for station in data[month][day]:
                month_lst.append(month)
                day_lst.append(day)
                station_lst.append(station)

    month_lst = [str(x) for x in month_lst]
    day_lst = [str(x) for x in day_lst]
    station_lst = [str(x) for x in station_lst]

    month_lst = [s[1:] if s.startswith('0') else s for s in month_lst if s != '0']
    day_lst =   [s[1:] if s.startswith('0') else s for s in day_lst if s != '0']

    
    df = pd.DataFrame({'Year': year, 'Month': month_lst, 'Day': day_lst, 'Station': station_lst})
    upload_csv_to_S3(df, year)



    # create a connection to the SQLite database
    conn = sqlite3.connect('assignment_02.db')

    # write the DataFrame to the database
    table_name = 'nexrad_' + year 
    df.to_sql(table_name, conn, if_exists='replace', index=False)

    # close the database connection
    conn.close()

##GOES18 workflow
def uploadcsv_goes_s3(df):
    """Uploads the given dataframe to S3

    Args:
        df (Dataframe): Dataframe to be uploaded to S3
    """
    s3 = S3Hook(aws_conn_id='My AWS Connection', region_name='us-east-1')
    aws_credentials = s3.get_credentials()
    s3_resource = boto3.resource('s3', aws_access_key_id=aws_credentials.access_key, aws_secret_access_key=aws_credentials.secret_key, region_name='us-east-1')
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    bucket_name = 'damg7245-team7'
    s3_key = 'data/df_goes18.csv'
    s3_resource.Object(bucket_name, s3_key).put(Body=csv_buffer.getvalue())

def create_goes_df():
    """for creatign dataframe of all the files in a particular station

    Args:
        client_id (boto3.client): aws client id
    """
    client_id=create_s3_client()
    # write_logs("fetching objects in NOAA s3 bucket")
    paginator = client_id.get_paginator('list_objects_v2')
    noaa_bucket = paginator.paginate(Bucket='noaa-goes18', PaginationConfig={"PageSize": 50})
    # write_logs("Writing Files in list from NOAA bucket")
    station=[]
    year=[]
    day=[]
    hour=[]
    
    for count, page in enumerate(noaa_bucket):
        files = page.get("Contents")
        for file in files:
            
            if 'ABI-L1b-RadC' not in file['Key'].split("/")[0]:
                break
            
            # if ((file['Key'].split("/")[0] not in station) or (file['Key'].split("/")[1] not in year) or (file['Key'].split("/")[2] not in day) or (file['Key'].split("/")[3] not in hour)):
            station.append(file['Key'].split("/")[0])
            year.append(file['Key'].split("/")[1])
            day.append(file['Key'].split("/")[2])
            hour.append(file['Key'].split("/")[3])
            print(file['Key'])
        else:
            continue
        break
        
    df_goes18=pd.DataFrame({'Station': station,
     'Year': year,
     'Day': day,
     'Hour': hour
    })
    df_goes18.drop_duplicates(inplace=True)
    
    uploadcsv_goes_s3(df_goes18)
    # df_goes18.to_csv('data/df_goes18.csv',index=False)
    # write_logs("File created in data folder")
    
    # create a connection to the SQLite database
    conn = sqlite3.connect('assignment_02.db')
    
    # goes18_dat = pd.read_csv('data/df_goes18.csv') # load to DataFrame

    df_goes18.to_sql('goes18_metadata', conn, if_exists='replace', index = False) # write to sqlite table
    
    # close the database connection
    conn.close()


with dag:

    generate_csv_2022 = PythonOperator(
        task_id="generate_csv_2022",
        python_callable=generateCsv,
        op_kwargs={'year': '2022'}
    )

    generate_csv_2023 = PythonOperator(
        task_id="generate_csv_2023",
        python_callable=generateCsv,
        op_kwargs={'year': '2023'}
    )
    
    generate_csv_goes = PythonOperator(
        task_id="generate_csv_goes",
        python_callable=create_goes_df
    )
    
    upload_database_to_S3 = PythonOperator(
        task_id="upload_database_to_S3",
        python_callable=upload_database_to_S3

    )

    generate_csv_2022 >> generate_csv_2023>> generate_csv_goes >> upload_database_to_S3






