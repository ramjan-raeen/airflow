import random
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

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
def even_number():
    lst = [i for i in range(10) if i % 2 == 0]
    print("Even number task executed!")
    return lst
def odd_number():
    lst = [i for i in range(10) if i % 2 != 0]
    print("Odd number task executed!")
    return lst
def branch_logic(**kwargs):
    arbitrary_num = random.randint(0, 10)
    print(f"Arbitrary number generated: {arbitrary_num}")
    if arbitrary_num % 2 == 0:
        return 'python_branch_task1'
    else:
        return 'python_branch_task2'

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
    python_branch_task1 = PythonOperator(
        task_id='python_branch_task1',
        python_callable=even_number
    )
    python_branch_task2 = PythonOperator(
        task_id='python_branch_task2',
        python_callable=odd_number
    )
    branch_task = BranchPythonOperator(
        task_id='branch_task',
        python_callable=branch_logic,
    )
    end = EmptyOperator(
        task_id='end',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        )

    start >> bash_task1 >> bash_task2 >> python_task >> branch_task 
    branch_task >> [python_branch_task1, python_branch_task2] >> end



