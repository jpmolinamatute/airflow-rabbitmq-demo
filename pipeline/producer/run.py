#! /usr/bin/env python

from os import environ
import boto3
import pika
from shared.rabbitmq_conn import get_rabbitmq_conn

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

def get_files_list(bucket, prefix):
    conn = boto3.client('s3')
    return conn.list_objects_v2(Bucket=bucket, Prefix=prefix)['Contents']

def push_to_server():
    connection = get_rabbitmq_conn()
    channel = connection.channel()
    channel.exchange_declare(
        exchange=environ['PIPILE_NAME'],
        exchange_type='direct'
    )
    channel.queue_declare(queue='init', durable=True)
    file_list = get_files_list('rein-ai-data-warehouse', 'juanpa/')
    for key in file_list:
        message = key['Key']
        print(message)
        channel.basic_publish(
            exchange=environ['PIPILE_NAME'],
            routing_key="init",
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
    print('fsdgdgiehtsgiuohfgdwe7rtw36rtwafgweufgru38457345872052456')
    channel.basic_publish(
        exchange=environ['PIPILE_NAME'],
        routing_key="init",
        body='fsdgdgiehtsgiuohfgdwe7rtw36rtwafgweufgru38457345872052456',
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f'{len(file_list) + 1} files were processed')
    connection.close()


if __name__ == "__main__":
    check_env()
    push_to_server()
