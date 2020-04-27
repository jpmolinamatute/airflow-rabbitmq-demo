#!/usr/bin/env python

import time
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from pipeline.dronelogs.default_values import DEFAULT_VALUES


def my_fail_task():
    time.sleep(30)
    raise Exception("It's OK this is a fail task")


with DAG(
    "fail-task",
    description="This task will fail on purpose",
    default_args=DEFAULT_VALUES,
    schedule_interval=None,  # '@once',
    start_date=days_ago(1),
) as dag:

    UPDATE_LOCATION = PythonOperator(task_id="updateLocation", python_callable=my_fail_task,)
