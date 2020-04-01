#! /usr/bin/env python

from os import environ
import psycopg2

def check_env():
    if 'DB_USER' not in environ:
        raise ValueError('Error: DB_USER is not defined as enviroment variable')
    if 'DB_PASS' not in environ:
        raise ValueError('Error: DB_PASS is not defined as enviroment variable')
    if 'DB_HOST' not in environ:
        raise ValueError('Error: DB_HOST is not defined as enviroment variable')
    if 'DB_NAME' not in environ:
        raise ValueError('Error: DB_NAME is not defined as enviroment variable')
    if 'DB_PORT' not in environ:
        raise ValueError('Error: DB_PORT is not defined as enviroment variable')

def get_db_conn():
    check_env()
    connection = False
    try:
        connection = psycopg2.connect(
            user=environ['DB_USER'],
            password=environ['DB_PASS'],
            host=environ['DB_HOST'],
            port=environ['DB_PORT'],
            database=environ['DB_NAME']
        )
    except (psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    return connection
