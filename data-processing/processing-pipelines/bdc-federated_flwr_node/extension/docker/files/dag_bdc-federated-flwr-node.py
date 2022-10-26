from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models import DAG
from bdc_federated_flwr_node.BDCFederatedFlwrNodeOperator import BDCFederatedFlwrNodeOperator
# from bdc_federated_flwr_node.TrainValDataSplitOperator import TrainValDataSplitOperator
from kaapana.operators.TrainValDataSplitOperator import TrainValDataSplitOperator
# from kaapana.operators.BreastDensityClassifierOperator import BreastDensityClassifierOperator
from kaapana.operators.LocalGetInputDataOperator import LocalGetInputDataOperator
from kaapana.operators.LocalWorkflowCleanerOperator import LocalWorkflowCleanerOperator
from kaapana.operators.LocalMinioOperator import LocalMinioOperator

from airflow.utils.trigger_rule import TriggerRule


log = LoggingMixin().log

ui_forms = {
    "elasticsearch_form": {
        "type": "object",
        "properties": {
            "dataset": "$default",
            "index": "$default",
            "cohort_limit": "$default",
            "input_modality": {
                "title": "Input Modality",
                "default": "MG",
                "description": "Expected input modality.",
                "type": "string",
                "required": True
            },
            "single_execution": {
                "type": "boolean",
                "title": "Single execution",
                "description": "Whether your report is execute in single mode or not",
                "default": False,
                "readOnly": True,
                "required": True
            }
        }
    },
    "workflow_form": {
        "type": "object",
        "properties": {
            "single_execution": {
                "title": "single execution",
                "description": "Should each series be processed separately?",
                "type": "boolean",
                "default": False,
                "readOnly": False,
            },
            "train_split": {
                "title": "relative train data split",
                "default": '0.7',
                "description": "Relative amount of data used for training, rest is using for validation split.",
                "type": "string",
                "required": True,
                "readOnly": False
            },
            "batch_size": {
                "title": "batch size",
                "default": 4,
                "description": "Batch size used to forward data through network.",
                "type": "integer",
                "required": True,
                "readOnly": False
            },
            "num_epochs": {
                "title": "number of training epochs",
                "default": 10,
                "description": "Number of epochs executed during training.",
                "type": "integer",
                "required": True,
                "readOnly": False
            },
            "val_frequency": {
                "title": "validation ferquency",
                "default": 3,
                "description": "Validation frequency in ratio to executed training epochs.",
                "type": "integer",
                "required": True,
                "readOnly": False
            },
            "crop_size": {
                "title": "cropping size",
                "default": 1000,
                "description": "Image size to which train images are randomly cropped and val images are center cropped.",
                "type": "integer",
                "required": True,
                "readOnly": False
            }
        }
    }
}

args = {
    'ui_forms': ui_forms,
    'ui_visible': True,
    'ui_federated': True,
    'owner': 'kaapana',
    'start_date': days_ago(0),
    'retries': 0,
    'retry_delay': timedelta(seconds=30)
}

dag = DAG(
    dag_id='bdc-federated-flwr-node',
    default_args=args,
    schedule_interval=None
    )


get_input = LocalGetInputDataOperator(dag=dag)

get_from_minio_init = LocalMinioOperator(dag=dag,
                                    name='get_from_minio_init',
                                    action='get',
                                    # run_dir='/data/get_from_minio_init/',
                                    bucket_name='simpleclassification',
                                    file_white_tuples=('.csv'))

# train_val_split = LocalTrainValDataSplitOperator(dag=dag,
#                                                  input_operator=get_input,
#                                                  # minio_operator=get_from_minio_init,
#                                                  )

train_val_split = TrainValDataSplitOperator(dag=dag,
                                            input_operator=get_input,
                                            minio_operator=get_from_minio_init,
                                            # dev_server='code-server'
                                            )

# dcm images from 'get_input' are mounted in Pod/Container at data/batch/<long char string>/*.dcm
# minio data from 'get_from_minio' is mounted in Pod/Container at minio/simpleclassification/*.csv
bdc_fl_flwr_node = BDCFederatedFlwrNodeOperator(dag=dag,
                                                # input_operator=get_input,
                                                input_operator=train_val_split,
                                                # second_input_operator=train_val_split,
                                                # minio_operator=get_from_minio_split,
                                                allow_federated_learning=True,
                                                trigger_rule=TriggerRule.ALL_DONE,  # if marked as skip_operator still skipped, but if not helps to enforce execution
                                                # whitelist_federated_learning=
                                                # dev_server='code-server'   # argument which enables debugging via code_server in "Pending Applications"
                                                # cmds=["tail"], arguments=["-f", "/dev/null"],
                                                )                                                            

clean = LocalWorkflowCleanerOperator(dag=dag,clean_workflow_dir=True)


# Flow

# w/o minio
get_from_minio_init >> train_val_split >> bdc_fl_flwr_node >> clean
get_input >> train_val_split
