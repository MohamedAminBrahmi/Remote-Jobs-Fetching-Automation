from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag
from pendulum import datetime


@dag(
    dag_id="remote_jobs_fetching_notebook",
    start_date=datetime(2026, 1, 1, tz="UTC"),
    schedule="0 10 * * *",
    catchup=False,
    tags=["notebook", "jobs"],
)
def remote_jobs_fetching_notebook():
    BashOperator(
        task_id="execute_notebook",
        bash_command=(
            'cd /opt/airflow/project && '
            'papermill "remote jobs fetching.ipynb" '
            '"/opt/airflow/logs/remote_jobs_fetching_{{ ds_nodash }}.ipynb"'
        ),
    )


remote_jobs_fetching_notebook()