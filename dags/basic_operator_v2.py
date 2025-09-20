from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

import random
from datetime import datetime, timedelta

def even_number_list(ti):
    num_range = ti.xcom_pull(task_ids='filter_even_odd', key='choose_arbitrary_number')
    lst = [i for i in range(num_range) if i % 2 == 0]
    print(f"Even Number task executed! list: {lst}")
    return lst
def odd_number_list(ti):
    num_range= ti.xcom_pull(task_ids='filter_even_odd', key='choose_arbitrary_number')
    lst = [i for i in range(num_range) if i % 2 != 0]
    print(f"Odd Number task executed! list: {lst}")
    return lst

def choose_arbitrary_number(ti):
    arbitrary_num = random.randint(0, 20)
    print(f"Arbitrary number generated: {arbitrary_num}")
    ti.xcom_push(key='choose_arbitrary_number', value=arbitrary_num)

    if arbitrary_num % 2 == 0:
        return 'even_number_task'
    else:
        return 'odd_number_task'

def find_max_number(numbers):
    if not numbers:
        return None
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    print(f"The maximum number is: {max_num}")
    return max_num

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failures' : False,
    'email_on_retry' : False,
    'retries' : 1,
    'retry_delay' : timedelta(minutes=1)
}

with DAG(
    dag_id='basic_operator_dag_v2',
    default_args=default_args,
    description='A simple DAG for demonstration purposes v2',
    start_date=datetime(2025, 9, 19),
    schedule='@daily',
    catchup=False,
) as dag:
    start = EmptyOperator(
        task_id='start'
    )
    bash_task = BashOperator(
        task_id='bash_task',
        bash_command='echo pwd is $(pwd) && echo ls is $(ls)'
    )
    task_01 = PythonOperator(
        task_id = 'find_max_number',
        python_callable =find_max_number,
        op_kwargs = {'numbers': [1, 3, 7, 2, 15]}
    )
    task_02 = BranchPythonOperator(
        task_id= 'filter_even_odd',
        python_callable= choose_arbitrary_number
    )
    task_03 = PythonOperator(
        task_id = 'even_number_task',
        python_callable = even_number_list
    )
    task_04 = PythonOperator(
        task_id = 'odd_number_task',
        python_callable= odd_number_list
    )
    task_05 = EmptyOperator(
        task_id='end',
        trigger_rule=TriggerRule.ONE_SUCCESS
    )

start >> bash_task >> task_01 >> task_02 >> [task_03, task_04] >> task_05