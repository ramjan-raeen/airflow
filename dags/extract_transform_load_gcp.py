# To execute dags using airflow command to need to pass logical-date as param instead execution_date as default
# airflow dags trigger extract_transform_load_gcs_to_gbq --logical-date "$(date -Iseconds)"


from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from google.cloud import storage

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}


    
def get_latest_gcs_file(ti, bucket, prefix):
    client = storage.Client()
    blobs = client.list_blobs(bucket, prefix=prefix)
    latest_blob = max(blobs, key=lambda b: b.updated, default=None)
    print(f"latest blob: gs://{latest_blob.name if latest_blob else 'None'}")
    if latest_blob:
        ti.xcom_push(key='latest_file', value=latest_blob.name)
    else:
        raise ValueError("No files found in GCS bucket with the given prefix.")
    

with DAG(
    dag_id='extract_transform_load_gcs_to_gbq',
    default_args=default_args,
    description='A DAG to extract data from GCS, transform it, and load it into BigQuery',
    start_date=datetime(2025, 6, 20),
    schedule='@daily',
    catchup=False,
) as dag:
    start = EmptyOperator(
        task_id='start'
    )
    list_latest_file = PythonOperator(
        task_id='get_latest_gcs_file',
        python_callable=get_latest_gcs_file,
        op_kwargs={
            'bucket': 'hands-dev2',
            'prefix': 'students/'
        }
    )
    extract_file = GCSToBigQueryOperator(
        task_id='extract_data_from_gcs',
        bucket='hands-dev2',
        source_objects=["{{ ti.xcom_pull(task_ids='get_latest_gcs_file', key='latest_file') }}"],
        destination_project_dataset_table='hands-on-dev-202409.university_data.student_habits_performance',
        source_format='CSV',
        skip_leading_rows=1,
        write_disposition='WRITE_APPEND',
        create_disposition='CREATE_IF_NEEDED',
        field_delimiter=',',
        autodetect=True,
        gcp_conn_id='google_cloud_default',
    )
    
    end = EmptyOperator(
        task_id='end'
    )

    start >>list_latest_file >> extract_file >> end