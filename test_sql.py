
import os
from backend import nexrad_main
import boto3








s3 = nexrad_main.createConnection()

bucket_name = 'damg7245-team7'
key = 'database.db' # name of the file in the bucket

# Download the file from S3 and save it locally
s3.download_file(bucket_name, key, os.path.join('data' , 'database.db'))
