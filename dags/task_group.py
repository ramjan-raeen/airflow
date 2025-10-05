#   Trigger the DAG using the command: time should be in UTC
# airflow dags trigger task_group_dag --logical-date 2025-09-21T10:37:00+00:00
# airflow dags trigger task_group_dag --logical-date "$(date -Iseconds)"

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    dag_id='task_group_dag',
    default_args=default_args,
    description='A DAG to demonstrate Task Groups',
    start_date=datetime(2025,9,20),
    schedule='@daily',
    catchup=False
) as dag:
    
    task_01 = EmptyOperator(
        task_id='start'
    )
    with TaskGroup('extract_data') as extract:

        task_02 = GCSToBigQueryOperator(
            task_id = 'gcs_to_bq_student',
            bucket = 'hands-dev2',
            source_objects = ['students/student_habits_performance.csv'],
            destination_project_dataset_table = 'hands-on-dev-202409.university_data.student_habits_performance',
            source_format = 'CSV',
            skip_leading_rows = 1,
            write_disposition = 'WRITE_TRUNCATE',
            create_disposition = 'CREATE_IF_NEEDED',
            field_delimiter = ',',
            autodetect = True
        )
        task_03 = GCSToBigQueryOperator(
            task_id='gcs_to_bq_employees',
            bucket = 'hands-dev2',
            source_objects = ["employees/employees_data"],
            destination_project_dataset_table = 'hands-on-dev-202409.employees.employees',
            source_format='CSV',
            skip_leading_rows=1,
            write_disposition = 'WRITE_TRUNCATE',
            create_disposition = 'CREATE_IF_NEEDED',
            field_delimiter = ',',
            autodetect = True
        )
    
    with TaskGroup('Transform_and_load') as transform_and_load:
        pass

        task_04 = BigQueryInsertJobOperator(
        task_id="matrix_of_students",
        configuration={
            "query": {
                "query": '''
                INSERT INTO `hands-on-dev-202409.university_data.student_avg_metrics`
                SELECT 
                    student_id,
                    AVG(study_hours_per_day) AS avg_study_hours_per_student,
                    AVG(attendance_percentage) AS avg_attendance_per_student,
                    AVG(sleep_hours) AS avg_sleep_hours_per_student
                FROM 
                    `hands-on-dev-202409.university_data.student_habits_performance`
                GROUP BY 
                    student_id
            ''',
                "useLegacySql": False,
            }
        },
        location="asia-south1",
    )

        task_05 = BigQueryInsertJobOperator(
            task_id = 'top_3_highest_salary',
            configuration = {
                "query":{
                    "query":'''
                    INSERT INTO `hands-on-dev-202409.employees.top_3_salary`
                    with top_3_salary as(
                        SELECT user_id, dept, salary, row_number() over(partition by dept order by salary desc) d_rnk  FROM `hands-on-dev-202409.employees.employees` 
                    ) select * except(d_rnk) from top_3_salary where d_rnk <=3 
                    ''',
                "useLegacySql": False
                }

            },
            location="asia-south1",
        )
        

    task_06 = EmptyOperator(
            task_id='end'
        )

task_01 >> extract >> transform_and_load >> task_06