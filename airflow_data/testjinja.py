from os import environ
import json
from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from pipeline.dronelogs.default_values import DEFAULT_VALUES


PIPILE_NAME = "testjimja"

DRONE_LOG_DAG = DAG(
    PIPILE_NAME,
    default_args=DEFAULT_VALUES,
    schedule_interval=None,  # '@once',
    description="Insert UUID row into db",
    start_date=days_ago(1),
)

INDEX = KubernetesPodOperator(
    dag=DRONE_LOG_DAG,
    image=f"{environ['DOCKER_REGISTRY']}/pipeline/dronelogs:jinja1",
    namespace="airflow",
    image_pull_policy="Always",
    name="jinja1",
    do_xcom_push=True,
    in_cluster=True,
    config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
    is_delete_operator_pod=True,
    hostnetwork=False,
    task_id=f"{PIPILE_NAME}-task-0",
)

templated_command = "{{"
templated_command += "ti.xcom_pull("
templated_command += f"dag_id='{PIPILE_NAME}', task_ids='{PIPILE_NAME}-task-0'"
templated_command += ")"
templated_command += "}}"

DECRYPT_FILES = KubernetesPodOperator(
    dag=DRONE_LOG_DAG,
    image=f"{environ['DOCKER_REGISTRY']}/pipeline/dronelogs:jinja2",
    namespace="airflow",
    image_pull_policy="Always",
    name="decrypt",
    do_xcom_push=False,
    arguments=[templated_command],
    env_vars={"BATCH_FILE": templated_command, "PIPILE_NAME": PIPILE_NAME},
    in_cluster=True,
    config_file=f"{environ['AIRFLOW_HOME']}/.kube/config",
    is_delete_operator_pod=True,
    hostnetwork=False,
    task_id=f"{PIPILE_NAME}-task-1",
)


INDEX >> DECRYPT_FILES
