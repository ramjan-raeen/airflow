from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025,6,20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


def get_context_vars(*args, **kwargs):
    print(f"args[1]: {args[0]} and args[2]: {args[1]}")
    print(f"primary_skill: {kwargs['primary_skill']} and secondary_skill: {kwargs['secondary_skill']}")
    print(f"task id is: {kwargs['task'].task_id}")
    print(f"dag id is: {kwargs['dag'].dag_id}")
    print(f"run id is: {kwargs['run_id']}")
    print(f"task instance: {kwargs['ti']}")
    print(f"task id:{kwargs['ti'].task_id}")
    print(f"state: {kwargs['ti'].state}")
    print(f"task start time: {kwargs['ti'].start_date}")

    print(f"dag run is: {kwargs['dag_run']}")
    print(f"dag run id is: {kwargs['dag_run'].run_id}")
    print(f"dag run type is : {kwargs['dag_run'].run_type}")

    print(f"dag start_date/schedule time: {kwargs['dag_run'].start_date}")
    print(f"dag end_date/job finished time is: {kwargs['dag_run'].end_date}")
    print(f"dag logical_date/exactly that time job has started: {kwargs['dag_run'].logical_date}")
    print(f"data_interval_start/the time when the job started to process data: {kwargs['dag_run'].data_interval_start}")
    print(f"data_interval_end/the time when the job finished processing data: {kwargs['dag_run'].data_interval_end}")

with DAG(
    dag_id='get_context_vars_dag',
    default_args=default_args,
    description='A DAG to fetch context variables',
    schedule='@daily',
    catchup=False,
) as dag:
    task1 = EmptyOperator(
        task_id='start'
    )
    task2 = PythonOperator(
        task_id='get_context_vars',
        python_callable=get_context_vars,
        op_args=[101, 100],
        op_kwargs={'primary_skill':'GCP', 'secondary_skill':'Python'},
        
        
    )
    task3 = EmptyOperator(
        task_id='end'
    )
  

    task1 >> task2 >> task3