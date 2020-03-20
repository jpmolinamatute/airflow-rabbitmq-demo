#!/usr/bin/env python
from os import environ
from datetime import datetime
import boto3
from dronelogs.db_conn import get_db_conn
from dronelogs.get_uuid_from_string import get_uuid

STEP_NAME = 'init'

def check_env():
    if 'AWS_ACCESS_KEY_ID' not in environ:
        raise ValueError('Error: AWS_ACCESS_KEY_ID is not defined as enviroment variable')
    if 'AWS_SECRET_ACCESS_KEY' not in environ:
        raise ValueError('Error: AWS_SECRET_ACCESS_KEY is not defined as enviroment variable')
    if 'AWS_DEFAULT_REGION' not in environ:
        raise ValueError('Error: AWS_DEFAULT_REGION is not defined as enviroment variable')
    if 'PIPILE_NAME' not in environ:
        raise ValueError('Error: PIPILE_NAME is not defined as enviroment variable')

def get_files_list(bucket, prefix):
    conn = boto3.client('s3')
    return conn.list_objects_v2(Bucket=bucket, Prefix=prefix)['Contents']

def process(body):
    uuid = get_uuid(body)
    if isinstance(uuid, str):
        print(f"Valid {uuid}!")
        connection = get_db_conn()
        if connection:
            tablename = environ['PIPILE_NAME']
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {tablename} WHERE uuid = '{uuid}' LIMIT 1;")
            if cursor.rowcount == 0:
                values = (uuid, '{}', datetime.now())
                print(f"Inserting {uuid} into {tablename}")
                cursor.execute(f"INSERT INTO {tablename} (uuid, progress, startedat) VALUES (%s, %s, %s)", values)
                connection.commit()
            else:
                print(f"{uuid} alredy exists in {tablename}")
            cursor.close()
            connection.close()
        else:
            raise TypeError("Error: Connection to DB failed, most likely wrong credentials")
    else:
        print(f"Error: wrong UUID {body}")

def init():
    check_env()
    for key in get_files_list('rein-ai-data-warehouse', 'juanpa/'):
        uuid = key['Key']
        print(f"Initializin: {uuid}")
        process(uuid)

if __name__ == "__main__":
    init()
