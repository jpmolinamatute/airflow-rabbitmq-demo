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

bucket = environ['AWS_BUCKET_NAME']
prefix = 'juanpa'

dag = DAG(
        "dronelogbook",
        default_args=DEFAULT_ARGS,
        schedule_interval=None, # '@once',
        start_date=days_ago(1)
    )

objs = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix)
i = 1
files_counter = 0
while 'NextContinuationToken' in objs and isinstance(objs['NextContinuationToken'], str):
    file_list = []
    for name in objs['Contents']:
        files_counter += 1
        file_list.append(name["Key"])
    INIT_FLOW = KubernetesPodOperator(
        dag=dag,
        image=f"{environ['DOCKER_REGISTRY']}/{environ['PIPILE_NAME']}:init",
        namespace='airflow',
        image_pull_policy='Always',
        name="init",
        secrets=[
            SECRET_ENV
        ],
        configmaps=["airflow-config"],
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
        image=f"{environ['DOCKER_REGISTRY']}/{environ['PIPILE_NAME']}:decrypt",
        namespace='airflow',
        image_pull_policy='Always',
        name="decrypt",
        arguments=[" ".join(file_list)],
        secrets=[
            SECRET_ENV
        ],
        configmaps=["airflow-config"],
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
        ContinuationToken=objs['NextContinuationToken']
    )
    i += 1


print(f"Number of files LISTED: {files_counter}")
