# Welcome to Airflow

🧩 1️⃣ Apache Airflow Architecture

Apache Airflow is designed around a modular, distributed architecture — meaning its components can scale independently.

## 🔧Core Components
| Component                         | Description                                                                                                                                       |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scheduler**                     | Responsible for scheduling jobs (DAGs). It looks at the DAG definitions, determines which tasks are ready to run, and sends them to the executor. |
| **Executor**                      | Actually runs the tasks — either locally (LocalExecutor), in parallel on multiple machines (CeleryExecutor, KubernetesExecutor, etc.).            |
| **Worker(s)**                     | Execute the task instances assigned by the executor. Each worker runs tasks in isolation (like a Docker container, process, or pod).              |
| **Web Server (UI)**               | Provides a web interface for users to visualize DAGs, monitor progress, retry failed tasks, etc. Usually runs via a Flask web app.                |
| **Metadata Database**             | A relational database (e.g., PostgreSQL/MySQL) used to store metadata — DAGs, task states, logs, variables, connections, etc.                     |
| **DAGs Folder (Code Repository)** | A file system or bucket containing all the DAG Python scripts. The scheduler reads them periodically to detect new or updated workflows.          |

## 🏗️ How They Interact

You write a DAG (Directed Acyclic Graph) — a Python file defining the workflow and task dependencies.

The Scheduler scans the DAG folder and decides which tasks are ready.

It uses the Executor to queue those tasks.

The Executor assigns them to Workers.

Each Worker executes the task (for example, running a Spark job or a Python script).

The task’s state (success/failure/etc.) is recorded in the Metadata Database.

The Web UI continuously reads from the database and shows the DAG and task statuses.


## ☁️ 2️⃣ Cloud Composer Architecture (Google Managed Airflow)

Cloud Composer is a fully managed Airflow service by Google Cloud, meaning Google handles much of the infrastructure for you — scaling, monitoring, and integration with other GCP services.

## 🌐 Key Components in Cloud Composer
| Component                             | Managed by | Description                                                                                                                 |
| ------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Airflow Environment (GKE cluster)** | Google     | Composer runs Airflow on **Google Kubernetes Engine (GKE)**. The Scheduler, Web Server, and Workers run as Kubernetes pods. |
| **Airflow Metadata DB**               | Google     | Managed **Cloud SQL** (PostgreSQL) instance.                                                                                |
| **DAGs and Plugins Storage**          | Google     | Stored in a **Cloud Storage bucket (GCS)** under `/dags/`, `/plugins/`, and `/data/`.                                       |
| **Logs**                              | Google     | Task logs are stored in **Cloud Logging** (and optionally GCS).                                                             |
| **Networking**                        | You        | Composer integrates with your **VPC**, **Service Accounts**, and **IAM** for access control.                                |
| **Monitoring**                        | Google     | Uses **Cloud Monitoring** and **Cloud Logging** dashboards.                                                                 |

## Cloud Composer Commands
| **Service Name** | **gcloud command**|
|------------------|-------------------|
|Create Composer Environement | `gcloud composer environments create hands-on-comp-env --location asia-south1  --image-version composer-2.15.1-airflow-2.9.3 --service-account composer-sa@$PROJECT_ID.gserviceaccount.com`|
| Create Service Account | `gcloud iam service-account create composer-sa` |
| Get Project Number | `PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")`|
| Add policy for Agent | `gcloud projects add-iam-policy-binding $PROJECT_ID --member "serviceAccount:service-$PROJECT_NUMBER@cloudcomposer-accounts.iam.gserviceaccount.com" --role "roles/composer.ServiceAgentV2Ext"`|
| **Trigger DAG** | `gcloud composer environments run hands-on-comp-env --location asia-south1 dags trigger -- test_composer_env`|
|**Composer Worker**| `gcloud projects add-iam-policy-binding $PROJECT_ID --member "serviceAccount:composer-sa@$PROJECT_ID.iam.gserviceaccount.com" --role "roles/composer.worker"`|
| **Storage Admin** | `gcloud projects add-iam-policy-binding $PROJECT_ID --member "serviceAccount:composer-sa@$PROJECT_ID.iam.gserviceaccount.com" --role "roles/storage.admin"`|
| **Given access BigQuery Admin to Composer's service account** | `gcloud projects add-iam-policy-binding $PROJECT_ID --member "serviceAccount:composer-sa@$PROJECT_ID.iam.gserviceaccount.com" --role "roles/bigquery.admin"`|


## 🔄 Cloud Composer Data Flow

You upload your DAG files to the GCS bucket (gs://<composer-environment-name>/dags/).

The Scheduler (running in GKE) automatically detects new DAGs.

Tasks are scheduled and executed by Airflow Workers (pods on GKE).

Task logs and metadata are stored in:

Cloud SQL → task states, DAG runs

Cloud Logging → execution logs

GCS → optional log storage

You monitor everything via:

Airflow Web UI (accessible from GCP Console)

Cloud Monitoring dashboards



## 🔍 Summary Comparison

| Feature                  | Apache Airflow (Self-managed)   | Cloud Composer (Managed)          |
| ------------------------ | ------------------------------- | --------------------------------- |
| **Deployment**           | Manual setup (VMs, Docker, K8s) | Managed on GKE                    |
| **Database**             | Self-managed PostgreSQL/MySQL   | Cloud SQL                         |
| **Storage for DAGs**     | Local filesystem                | GCS bucket                        |
| **Logging**              | Local or S3/Elasticsearch       | Cloud Logging / GCS               |
| **Monitoring**           | Manual                          | Cloud Monitoring                  |
| **Scaling**              | Manual                          | Auto-scaled pods on GKE           |
| **Integration with GCP** | Manual                          | Native (BigQuery, Dataflow, etc.) |





# Airflow Operators

| Service                        | Description                                           | Operator Class Names                                                                                                                                                                                                            |
| ------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Python Programming** | To write python functions | `PythonOperator` |
| **MySQL** | To connect through MySQL database | `MySQLConnector` |
| **EmptyOperator** | Empty as ealier known as DummyOperator, it does not anything, just asign | `EmptyOperator` |
| **ShortCircuitOperator** | ShortCircuitOperator operator used for stop the downstream task with condition satisfied | `ShortCircuitOperator` |
| **BigQuery**                   | Run queries, load/extract tables, copy datasets, jobs | `BigQueryInsertJobOperator`, `BigQueryGetDataOperator`, `BigQueryCheckOperator`, `BigQueryIntervalCheckOperator`, `BigQueryValueCheckOperator`, `BigQueryTableExistenceSensor`, `BigQueryExecuteQueryOperator`                                                  |
| **BigQuery Data Transfer**     | Trigger transfer configs                              | `BigQueryCreateDataTransferOperator`, `BigQueryDeleteDataTransferOperator`, `BigQueryUpdateDataTransferOperator`, `BigQueryRunDataTransferOperator`                                                                             |
| **Bigtable**                   | Table / instance ops                                  | `BigtableCreateInstanceOperator`, `BigtableDeleteInstanceOperator`, `BigtableUpdateClusterOperator`, `BigtableGetDataOperator`                                                                                                  |
| **AlloyDB**                    | AlloyDB cluster / backup ops                          | `AlloyDBCreateClusterOperator`, `AlloyDBDeleteClusterOperator`, `AlloyDBCreateBackupOperator`                                                                                                                                   |
| **AutoML**                     | Train / deploy models                                 | `AutoMLTrainModelOperator`, `AutoMLDeployModelOperator`, `AutoMLPredictOperator`                                                                                                                                                |
| **Batch**                      | Submit GCP Batch jobs                                 | `CloudBatchSubmitJobOperator`, `CloudBatchDeleteJobOperator`                                                                                                                                                                    |
| **Build (Cloud Build)**        | Build containers, run steps                           | `CloudBuildCreateBuildOperator`, `CloudBuildCancelBuildOperator`                                                                                                                                                                |
| **Composer**                   | Manage Composer envs                                  | `CloudComposerCreateEnvironmentOperator`, `CloudComposerUpdateEnvironmentOperator`, `CloudComposerDeleteEnvironmentOperator`                                                                                                    |
| **Compute Engine**             | Manage VMs, disks                                     | `ComputeEngineStartInstanceOperator`, `ComputeEngineStopInstanceOperator`, `ComputeEngineInsertInstanceOperator`, `ComputeEngineDeleteInstanceOperator`                                                                         |
| **Cloud SQL**                  | Instance / DB / user mgmt                             | `CloudSQLCreateInstanceOperator`, `CloudSQLDeleteInstanceOperator`, `CloudSQLImportInstanceOperator`, `CloudSQLExportInstanceOperator`, `CloudSQLExecuteQueryOperator`                                                          |
| **Cloud Storage (GCS)**        | Buckets, objects                                      | `GCSCreateBucketOperator`, `GCSDeleteBucketOperator`, `GCSListObjectsOperator`, `GCSDeleteObjectsOperator`, `GCSToBigQueryOperator`, `GCSToGCSOperator`                                                                         |
| **Cloud Run**                  | Deploy services, jobs                                 | `CloudRunDeployServiceOperator`, `CloudRunDeleteServiceOperator`, `CloudRunJobCreateOperator`, `CloudRunJobDeleteOperator`                                                                                                      |
| **Cloud Functions**            | Deploy / invoke functions                             | `CloudFunctionDeployFunctionOperator`, `CloudFunctionDeleteFunctionOperator`, `CloudFunctionInvokeFunctionOperator`                                                                                                             |
| **Data Catalog**               | Tag templates, entries                                | `DatacatalogCreateEntryGroupOperator`, `DatacatalogDeleteEntryOperator`, `DatacatalogCreateTagTemplateOperator`, `DatacatalogUpdateTagOperator`                                                                                 |
| **Data Fusion**                | Pipelines, instances                                  | `CloudDataFusionCreatePipelineOperator`, `CloudDataFusionStartPipelineOperator`, `CloudDataFusionStopPipelineOperator`, `CloudDataFusionDeletePipelineOperator`                                                                 |
| **Data Loss Prevention (DLP)** | Inspection, de-identify                               | `CloudDLPCreateInspectTemplateOperator`, `CloudDLPCreateDeidentifyTemplateOperator`, `CloudDLPInspectContentOperator`, `CloudDLPDeidentifyContentOperator`                                                                      |
| **Dataflow**                   | Launch pipelines                                      | `DataflowCreatePythonJobOperator`, `DataflowCreateJavaJobOperator`, `DataflowTemplatedJobStartOperator`, `DataflowStopJobOperator`                                                                                              |
| **Dataplex**                   | Manage lakes / assets                                 | `DataplexCreateLakeOperator`, `DataplexDeleteLakeOperator`, `DataplexCreateAssetOperator`                                                                                                                                       |
| **Dataprep**                   | Run jobs                                              | `DataprepGetJobsForJobGroupOperator`, `DataprepRunJobGroupOperator`                                                                                                                                                             |
| **Dataproc**                   | Cluster / job ops                                     | `DataprocCreateClusterOperator`, `DataprocDeleteClusterOperator`, `DataprocSubmitJobOperator`, `DataprocSubmitPigJobOperator`, `DataprocSubmitHiveJobOperator`, `DataprocSubmitSparkJobOperator`, `DataprocStopClusterOperator` |
| **Dataproc Metastore**         | Service mgmt                                          | `DataprocMetastoreCreateServiceOperator`, `DataprocMetastoreDeleteServiceOperator`, `DataprocMetastoreUpdateServiceOperator`                                                                                                    |
| **Datastore / Firestore**      | CRUD ops                                              | `DatastoreExportEntitiesOperator`, `DatastoreImportEntitiesOperator`, `FirestoreExportDocumentsOperator`, `FirestoreImportDocumentsOperator`                                                                                    |
| **GKE (Kubernetes Engine)**    | Cluster mgmt                                          | `GKECreateClusterOperator`, `GKEDeleteClusterOperator`, `GKEStartPodOperator`                                                                                                                                                   |
| **Life Sciences**              | Submit pipelines                                      | `LifeSciencesRunPipelineOperator`                                                                                                                                                                                               |
| **Logging**                    | Create sinks, log exports                             | `GcsBucketCreateSinkOperator`, `LoggingExportToGCSOperator`                                                                                                                                                                     |
| **Memorystore**                | Redis / memcache                                      | `MemcacheCreateInstanceOperator`, `MemcacheUpdateInstanceOperator`, `MemcacheDeleteInstanceOperator`                                                                                                                            |
| **Pub/Sub**                    | Topics, subs, publish                                 | `PubSubCreateTopicOperator`, `PubSubDeleteTopicOperator`, `PubSubCreateSubscriptionOperator`, `PubSubPublishMessageOperator`, `PubSubPullOperator`                                                                              |
| **Spanner**                    | Manage DBs                                            | `SpannerInstanceDatabaseCreateOperator`, `SpannerInstanceDatabaseDeleteOperator`, `SpannerQueryDatabaseInstanceOperator`                                                                                                        |
| **Translate API**              | Translate text                                        | `CloudTranslateTextOperator`, `CloudTranslateDocumentOperator`                                                                                                                                                                  |
| **Speech-to-Text / TTS**       | Speech services                                       | `CloudSpeechToTextRecognizeSpeechOperator`, `CloudTextToSpeechSynthesizeOperator`                                                                                                                                               |
| **Vision**                     | Image / OCR                                           | `CloudVisionAnnotateImageOperator`, `CloudVisionDetectTextOperator`                                                                                                                                                             |
| **Video Intelligence**         | Video analysis                                        | `CloudVideoIntelligenceDetectVideoOperator`                                                                                                                                                                                     |
| **Vertex AI (ML Engine)**      | Models, training, endpoints                           | `CreateCustomTrainingJobOperator`, `CreateAutoMLTrainingJobOperator`, `RunBatchPredictionJobOperator`, `DeleteModelOperator`, `DeployModelOperator`                                                                             |
| **Workflows**                  | Execute workflows                                     | `WorkflowsExecuteWorkflowOperator`, `WorkflowsDeleteWorkflowOperator`                                                                                                                                                           |




