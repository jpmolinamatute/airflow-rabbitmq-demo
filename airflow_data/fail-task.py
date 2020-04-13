#!/usr/bin/env python

import time
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.operators.python_operator import PythonOperator


def task_fail_slack_alert(context):
    ti = context.get("task_instance")
    task_id = ti.task_id
    dag_id = ti.dag_id
    exec_date = context.get("execution_date")
    log_url = ti.log_url
    slack_webhook_token = BaseHook.get_connection("slack").password
    slack_msg = f"""
            :red_circle: Task Failed.
            *Task*: {task_id}
            *Dag*: {dag_id}
            *Execution Time*: {exec_date}
            *Log Url*: {log_url}
            """
    failed_alert = SlackWebhookOperator(
        task_id="slack_test",
        http_conn_id="slack",
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username="airflow",
    )
    print(failed_alert)
    return failed_alert.execute(context=context)


def my_fail_task():
    time.sleep(30)
    raise Exception("It's OK this is a fail task")


with DAG(
    "fail-task",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "description": "This task will fail on purpose",
        "on_failure_callback": task_fail_slack_alert,
    },
    schedule_interval=None,  # '@once',
    start_date=days_ago(1),
) as dag:

    UPDATE_LOCATION = PythonOperator(task_id="updateLocation", python_callable=my_fail_task,)
