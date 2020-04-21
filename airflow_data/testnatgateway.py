#!/usr/bin/env python
from os import environ
import json
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.secret import Secret
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain
from testnatgateway.default_values import DEFAULT_VALUES

SECRET_ENV = Secret(deploy_type="env", deploy_target=None, secret="airflow-secret")
PIPILE_NAME = "testnatgateway"
WORKLOAD = int(environ["DAG_WORKLOAD"])

DRONE_LOG_DAG = DAG(
    PIPILE_NAME,
    default_args=DEFAULT_VALUES,
    schedule_interval=None,  # '@once',
    description="Insert UUID row into db",
    start_date=days_ago(1),
)

INDEX_FILE = "index.txt"
INDEX_PREFIX = f"airflow/{PIPILE_NAME}/indexes"
INDEX2 = KubernetesPodOperator(
    dag=DRONE_LOG_DAG,
    image=f"{environ['DOCKER_REGISTRY']}/pipeline/{PIPILE_NAME}:index",
    namespace="airflow",
    image_pull_policy="Always",
    name="index",
    arguments=[INDEX_PREFIX, INDEX_FILE],
    secrets=[SECRET_ENV],
    configmaps=["airflow-config"],
    in_cluster=True,
    config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
    is_delete_operator_pod=True,
    hostnetwork=False,
    task_id=f"{PIPILE_NAME}-task-0",
)

for i in range(1, WORKLOAD + 1):
    ARGUMENTS = json.dumps(
        {
            "index_file": INDEX_FILE,
            "index_prefix": INDEX_PREFIX,
            "batch_number": i,
            "worklaod": WORKLOAD,
        }
    )

    DECRYPT_FILES2 = KubernetesPodOperator(
        dag=DRONE_LOG_DAG,
        image=f"{environ['DOCKER_REGISTRY']}/pipeline/{PIPILE_NAME}:decrypt",
        namespace="airflow",
        image_pull_policy="Always",
        name="decrypt",
        do_xcom_push=False,
        arguments=[ARGUMENTS],
        secrets=[SECRET_ENV],
        configmaps=["airflow-config"],
        in_cluster=True,
        config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
        is_delete_operator_pod=True,
        hostnetwork=False,
        task_id=f"{PIPILE_NAME}-task-1-{i}",
    )

    chain(INDEX2, DECRYPT_FILES2)
