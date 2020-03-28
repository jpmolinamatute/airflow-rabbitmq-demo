#! /usr/bin/env python

from os import environ
import boto3
import pika
from shared.rabbitmq_conn import get_rabbitmq_conn

CONN = boto3.client('s3')

def check_env():
    if 'AWS_ACCESS_KEY_ID' not in environ:
        raise ValueError('Error: AWS_ACCESS_KEY_ID is not defined as enviroment variable')
    if 'AWS_SECRET_ACCESS_KEY' not in environ:
        raise ValueError('Error: AWS_SECRET_ACCESS_KEY is not defined as enviroment variable')
    if 'AWS_DEFAULT_REGION' not in environ:
        raise ValueError('Error: AWS_DEFAULT_REGION is not defined as enviroment variable')
    if 'PIPILE_NAME' not in environ:
        raise ValueError('Error: PIPILE_NAME is not defined as enviroment variable')
    # if 'AWS_SOURCE_BUCKET_NAME' not in environ:
    #     raise ValueError('Error: AWS_SOURCE_BUCKET_NAME is not defined as enviroment variable')
    # if 'AWS_SOURCE_BUCKET_PREFIX' not in environ:
    #     raise ValueError('Error: AWS_SOURCE_BUCKET_PREFIX is not defined as enviroment variable')

def get_files_list(continuation=None):
    result = None
    bucket = 'rein-ai-data-warehouse'
    prefix = 'juanpa'

    if isinstance(continuation, str):
        result = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix, ContinuationToken=continuation)
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
    objs = get_files_list()
    counter = 1
    while 'NextContinuationToken' in objs and isinstance(objs['NextContinuationToken'], str):
        for single_file in objs['Contents']:
            print(f'Sending: {single_file["Key"]}')
            channel.basic_publish(
                exchange=environ['PIPILE_NAME'],
                routing_key="init",
                body=single_file['Key'],
                properties=pika.BasicProperties(delivery_mode=2)
            )
            counter += 1
        objs = get_files_list(objs['NextContinuationToken'])
    print(f'Total files sent: {counter}')


if __name__ == "__main__":
    check_env()
    conn = create_channel()
    push_to_server(conn[1])
    conn[0].close()
