from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
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

def print_hello():
    print("Hello World!")

with DAG(dag_id='basic_operator_dag',
         default_args=default_args,
         description='A simple DAG with basic operators',
         schedule='@daily',
         catchup=False) as dag:
    start = EmptyOperator(task_id='start')
    bash_task1 = BashOperator(
        task_id='bash_task',
        bash_command='echo "Hello from Bash!"'
    )
    bash_task2 = BashOperator(
        task_id='bash_task2',
        bash_command='echo "pwd is $(pwd) && echo ls is $(ls)"'
    )
    python_task = PythonOperator(
        task_id='python_task',
        python_callable=print_hello
    )
    end = EmptyOperator(task_id='end')

    start >> bash_task1 >> bash_task2 >> python_task >> end



