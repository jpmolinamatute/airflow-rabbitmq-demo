#! /usr/bin/env python

from os import environ
import boto3
import pika
from pipeline.shared.rabbitmq_conn import get_rabbitmq_conn

CONN = boto3.client('s3')

DEV = 15

def check_env():
    if 'AWS_ACCESS_KEY_ID' not in environ:
        raise ValueError('Error: AWS_ACCESS_KEY_ID is not defined as enviroment variable')
    if 'AWS_SECRET_ACCESS_KEY' not in environ:
        raise ValueError('Error: AWS_SECRET_ACCESS_KEY is not defined as enviroment variable')
    if 'AWS_DEFAULT_REGION' not in environ:
        raise ValueError('Error: AWS_DEFAULT_REGION is not defined as enviroment variable')
    if 'PIPILE_NAME' not in environ:
        raise ValueError('Error: PIPILE_NAME is not defined as enviroment variable')
    if 'AWS_RAW_S3_BUCKET' not in environ:
        raise ValueError('Error: AWS_RAW_S3_BUCKET is not defined as enviroment variable')
    # if 'AWS_SOURCE_BUCKET_PREFIX' not in environ:
    #     raise ValueError('Error: AWS_SOURCE_BUCKET_PREFIX is not defined as enviroment variable')

def get_files_list(continuation=None):
    result = None
    bucket = environ['AWS_RAW_S3_BUCKET']
    prefix = 'juanpa'

    if isinstance(continuation, str):
        result = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix, ContinuationToken=continuation)
    elif isinstance(continuation, int):
        result = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=continuation)
    else:
        result = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return result

def create_channel():
    connection = get_rabbitmq_conn()
    channel = connection.channel()
    channel.exchange_declare(
        exchange=environ['PIPILE_NAME'],
        exchange_type='direct'
    )
    channel.queue_declare(queue='init', durable=True)
    return (connection, channel)

def push_to_server(channel):
    objs = get_files_list(DEV)
    files_counter = 0
    keep_going = True
    while keep_going:
        for name in objs['Contents']:
            print(f'Sending: {name["Key"]}')
            channel.basic_publish(
                exchange=environ['PIPILE_NAME'],
                routing_key="init",
                body=name['Key'],
                properties=pika.BasicProperties(delivery_mode=2)
            )
            files_counter += 1
        if DEV is None:
            if 'NextContinuationToken' in objs:
                objs = get_files_list(objs['NextContinuationToken'])
            else:
                keep_going = False
        else:
            keep_going = False

    print(f'Total files sent: {files_counter}')

def init():
    check_env()
    conn = create_channel()
    push_to_server(conn[1])
    conn[0].close()

if __name__ == "__main__":
    init()
