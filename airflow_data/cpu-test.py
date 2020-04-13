#!/usr/bin/env python

from os import environ
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from dronelogs.default_values import DEFAULT_VALUES

DRONE_LOG_DAG = DAG(
    "airflow-test",
    default_args=DEFAULT_VALUES,
    schedule_interval=None,  # '@once',
    description="CPU Tests",
    start_date=days_ago(1),
)

for i in range(1, 30):
    CPU_TEST = KubernetesPodOperator(
        dag=DRONE_LOG_DAG,
        image=f"{environ['DOCKER_REGISTRY']}/{environ['PIPILE_NAME']}:cputest",
        namespace="load-testing",
        image_pull_policy="Always",
        name="cpu",
        do_xcom_push=False,
        in_cluster=True,
        config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
        is_delete_operator_pod=True,
        hostnetwork=False,
        task_id=f"task-{i}",
    )

    CPU_TEST
