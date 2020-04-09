#!/usr/bin/env python
from os import environ
import json
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.secret import Secret
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain

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

WORKLOAD = int(environ['DAG_WORKLOAD']) + 1

dag = DAG(
    environ['PIPILE_NAME'],
    default_args=DEFAULT_ARGS,
    schedule_interval=None, # '@once',
    start_date=days_ago(1)
)

index_file = "index.txt"
index_prefix = f"airflow/{environ['PIPILE_NAME']}/indexes"


INDEX = KubernetesPodOperator(
    dag=dag,
    image=f"{environ['DOCKER_REGISTRY']}/{environ['PIPILE_NAME']}:index",
    namespace='airflow',
    image_pull_policy='Always',
    name="index",
    arguments=[index_prefix, index_file],
    secrets=[
        SECRET_ENV
    ],
    configmaps=["airflow-config"],
    in_cluster=True,
    config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
    is_delete_operator_pod=True,
    hostnetwork=False,
    task_id="task-0"
)

for i in range(1, WORKLOAD):
    ARGUMENTS = json.dumps({
        "index_file": index_file,
        "index_prefix": index_prefix,
        "batch_number": i,
        "worklaod": WORKLOAD
    })
    init_id = f"task-1-{i}"
    INIT_FLOW = KubernetesPodOperator(
        dag=dag,
        image=f"{environ['DOCKER_REGISTRY']}/{environ['PIPILE_NAME']}:init",
        namespace='airflow',
        image_pull_policy='Always',
        name="init",
        secrets=[
            SECRET_ENV
        ],
        do_xcom_push=True,
        configmaps=["airflow-config"],
        arguments=[ARGUMENTS],
        in_cluster=True,
        config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
        is_delete_operator_pod=True,
        hostnetwork=False,
        task_id=init_id
    )
    DECRYPT_FILES = KubernetesPodOperator(
        dag=dag,
        image=f"{environ['DOCKER_REGISTRY']}/{environ['PIPILE_NAME']}:decrypt",
        namespace='airflow',
        image_pull_policy='Always',
        name="decrypt",
        do_xcom_push=False,
        arguments=[ARGUMENTS],
        secrets=[
            SECRET_ENV
        ],
        env_vars={
            "BATCH_FILE": "{{ ti.xcom_pull(task_ids=init_id, key='sub_index_path') }}"
        },
        configmaps=["airflow-config"],
        in_cluster=True,
        config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
        is_delete_operator_pod=True,
        hostnetwork=False,
        task_id=f"task-2-{i}"
    )

    chain(INIT_FLOW, DECRYPT_FILES)
