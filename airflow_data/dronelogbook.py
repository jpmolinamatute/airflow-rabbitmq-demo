#!/usr/bin/env python
from os import environ
import boto3
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.secret import Secret
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain
from dronelogs.shared.check_env import check_env


check_env()

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "description": 'Insert UUID row into db'
}

SECRET_ENV = Secret(
    deploy_type='env',
    deploy_target=None,
    secret='airflow-secret'
)
CONN = boto3.client('s3')

bucket = 'rein-ai-data-warehouse'
prefix = 'juanpa'

dag = DAG(
        "dronelogbook",
        default_args=DEFAULT_ARGS,
        schedule_interval=None, # '@once',
        start_date=days_ago(1)
    )

objs = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=750)
i = 1
while 'NextContinuationToken' in objs and isinstance(objs['NextContinuationToken'], str):
    file_list = []
    for name in objs['Contents']:
        file_list.append(name["Key"])
    INIT_FLOW = KubernetesPodOperator(
        dag=dag,
        image="344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelogs:init",
        namespace='airflow',
        image_pull_policy='Always',
        name="init",
        env_vars={
            'AWS_DEFAULT_REGION': 'us-east-2',
            'PIPILE_NAME': 'dronelogsbook'
        },
        secrets=[
            SECRET_ENV
        ],
        arguments=[" ".join(file_list)],
        in_cluster=True,
        config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
        is_delete_operator_pod=True,
        hostnetwork=False,
        task_id=f"task-1-{i}",
        xcom_push=True
    )
    DECRYPT_FILES = KubernetesPodOperator(
        dag=dag,
        image="344286188962.dkr.ecr.us-east-2.amazonaws.com/dronelogs:decrypt",
        namespace='airflow',
        image_pull_policy='Always',
        name="decrypt",
        arguments=[" ".join(file_list)],
        env_vars={
            'AWS_DEFAULT_REGION': 'us-east-2',
            'PIPILE_NAME': 'dronelogsbook'
        },
        secrets=[
            SECRET_ENV
        ],
        in_cluster=True,
        config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
        is_delete_operator_pod=True,
        hostnetwork=False,
        task_id=f"task-2-{i}"
    )
    #pylint: disable=pointless-statement
    chain(INIT_FLOW, DECRYPT_FILES)
    objs = CONN.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
        ContinuationToken=objs['NextContinuationToken'],
        MaxKeys=750
    )
    i += 1
