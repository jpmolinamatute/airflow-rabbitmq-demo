#!/usr/bin/env python

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from dronelogs.run import init

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "description": 'Insert UUID row into db'
}

# todaysdate = datetime.now()

with DAG(
        "dronelogbook",
        default_args=DEFAULT_ARGS,
        schedule_interval='@once',
        start_date=datetime(2019, 6, 4)
        # start_date=datetime(
        #     todaysdate.year,
        #     todaysdate.month,
        #     todaysdate.day,
        #     todaysdate.hour - 1,
        #     todaysdate.minute
        # )
    ) as dag:

    run_this = PythonOperator(
        task_id='print_the_context',
        python_callable=init,
        dag=dag
    )
