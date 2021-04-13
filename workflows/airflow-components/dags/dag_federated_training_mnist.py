from datetime import timedelta

from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.log.logging_mixin import LoggingMixin

from kaapana.operators.LocalUnzipFileOperator import LocalUnzipFileOperator
from kaapana.operators.LocalWorkflowCleanerOperator import LocalWorkflowCleanerOperator

#from kaapana.operators.LocalMinioOperator import LocalMinioOperator # needs option to overwrite it#s name, so two minio-action-get can be applied
#from federated_training.federated_training.LocalMinioOperator import LocalMinioOperator

from federated_training.federated_training.TrainingOperatorMNIST import TrainingOperatorMNIST
from federated_training.federated_training.TriggerDagOperator import TriggerDagOperator


log = LoggingMixin().log

args = {
    'ui_visible': False,
    'owner': 'kaapana',
    'start_date': days_ago(0),
    'retries': 2,
    'retry_delay': timedelta(seconds=30),
}

dag = DAG(
    dag_id='federated-training-mnist',
    default_args=args,
    schedule_interval=None,
    concurrency=10,
    max_active_runs=5
    )

get_model_from_minio = LocalMinioOperator(
    dag=dag,
    name='minio-action-get-model',
    action='get',
    bucket_name='federated-exp-mnist',
    action_operator_dirs=['model']
    )

get_data_from_minio = LocalMinioOperator(
    dag=dag,
    name='minio-action-get-data',
    action='get',
    bucket_name='federated-exp-mnist',
    action_operator_dirs=['data'],
    operator_out_dir='data'
    )

unzip_data = LocalUnzipFileOperator(
    dag=dag,
    operator_in_dir='data'
    )

train_model = TrainingOperatorMNIST(
    dag=dag,
    input_operator=unzip_data
    )

pass_on_model = LocalMinioOperator(
    dag=dag,action='put',
    bucket_name='federated-exp-mnist',
    action_operator_dirs=['cache'],
    operator_out_dir='',
    zip_files=False
    )

cleanup = LocalWorkflowCleanerOperator(dag=dag, clean_workflow_dir=True)

[get_model_from_minio, get_data_from_minio >> unzip_data] >> train_model >> pass_on_model >> cleanup