import datetime
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator


def task_fail_slack_alert(context):
    ti = context.get("task_instance")
    task_id = ti.task_id
    dag_id = ti.dag_id
    exec_date = context.get("execution_date")
    log_url = ti.log_url
    slack_webhook_token = BaseHook.get_connection("slack").password
    slack_msg = f"""
        :red_circle: Task Failed.
        ----------------
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

    return failed_alert.execute(context=context)


def task_successed_slack_alert(context):
    ti = context.get("task_instance")
    task_id = ti.task_id
    dag_id = ti.dag_id
    exec_date = context.get("execution_date")
    log_url = ti.log_url
    slack_webhook_token = BaseHook.get_connection("slack").password
    slack_msg = f"""
        Task Successed.
        ---------------
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
        retries=2,
        retry_delay=datetime.timedelta(seconds=2),
    )

    return failed_alert.execute(context=context)


DEFAULT_VALUES = {
    "owner": "airflow",
    "depends_on_past": False,
    "on_failure_callback": task_fail_slack_alert,
    # "on_success_callback": task_successed_slack_alert,
}
