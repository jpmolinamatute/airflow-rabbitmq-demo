#! /usr/bin/env python

from os import environ
import psycopg2


def check_env():
    if "AIRFLOW_DB_USER" not in environ:
        raise ValueError("Error: AIRFLOW_DB_USER is not defined as enviroment variable")
    if "AIRFLOW_DB_PASS" not in environ:
        raise ValueError("Error: AIRFLOW_DB_PASS is not defined as enviroment variable")
    if "AIRFLOW_DB_HOST" not in environ:
        raise ValueError("Error: AIRFLOW_DB_HOST is not defined as enviroment variable")
    if "AIRFLOW_DB_NAME" not in environ:
        raise ValueError("Error: AIRFLOW_DB_NAME is not defined as enviroment variable")
    if "AIRFLOW_DB_PORT" not in environ:
        raise ValueError("Error: AIRFLOW_DB_PORT is not defined as enviroment variable")


def get_db_conn():
    check_env()
    connection = False
    try:
        connection = psycopg2.connect(
            user=environ["AIRFLOW_DB_USER"],
            password=environ["AIRFLOW_DB_PASS"],
            host=environ["AIRFLOW_DB_HOST"],
            port=environ["AIRFLOW_DB_PORT"],
            database=environ["AIRFLOW_DB_NAME"],
        )
    except (psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    return connection
