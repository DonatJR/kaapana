from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.models import DAG
from datetime import datetime
from nnunet.LocalDiceOperator import LocalDiceOperator
from nnunet.LocalDataorganizerOperator import LocalDataorganizerOperator
from nnunet.LocalSegCheckOperator import LocalSegCheckOperator

from nnunet.NnUnetOperator import NnUnetOperator
from kaapana.operators.ResampleOperator import ResampleOperator
from kaapana.operators.DcmConverterOperator import DcmConverterOperator
from kaapana.operators.DcmSendOperator import DcmSendOperator
from kaapana.operators.Itk2DcmSegOperator import Itk2DcmSegOperator
from kaapana.operators.DcmSeg2ItkOperator import DcmSeg2ItkOperator

from kaapana.operators.LocalGetInputDataOperator import LocalGetInputDataOperator
from kaapana.operators.LocalWorkflowCleanerOperator import LocalWorkflowCleanerOperator
from nnunet.GetEnsembleOperator import GetEnsembleOperator
from kaapana.operators.Bin2DcmOperator import Bin2DcmOperator
from kaapana.operators.LocalGetRefSeriesOperator import LocalGetRefSeriesOperator

seg_filter = ""

ui_forms = {
    "workflow_form": {
        "type": "object",
        "properties": {
            "input": {
                "title": "Input Modality",
                "default": "CT",
                "description": "Expected input modality.",
                "type": "string",
                "readOnly": True,
            }
        }
    }
}

args = {
    'ui_visible': True,
    'ui_forms': ui_forms,
    'owner': 'kaapana',
    'start_date': days_ago(0),
    'retries': 0,
    'retry_delay': timedelta(seconds=60)
}

dag = DAG(
    dag_id='nnunet-racoon-ensemble',
    default_args=args,
    concurrency=3,
    max_active_runs=1,
    schedule_interval=None
)

get_input = LocalGetInputDataOperator(
    dag=dag,
    check_modality=True,
    parallel_downloads=5
)

dcm2nifti_seg = DcmSeg2ItkOperator(
    dag=dag,
    input_operator=get_input,
    output_format="nii.gz",
    seg_filter=seg_filter,
    delete_input_on_success=True
)

get_ref_ct_series_from_seg = LocalGetRefSeriesOperator(
    dag=dag,
    input_operator=get_input,
    search_policy="reference_uid",
    parallel_downloads=5,
    modality=None,
    delete_input_on_success=True
)

dcm2nifti_ct = DcmConverterOperator(
    dag=dag,
    input_operator=get_ref_ct_series_from_seg,
    output_format='nii.gz',
    delete_input_on_success=True
)

resample_seg = ResampleOperator(
    dag=dag,
    input_operator=dcm2nifti_seg,
    original_img_operator=dcm2nifti_ct,
    operator_out_dir=dcm2nifti_seg.operator_out_dir,
    delete_input_on_success=False
)

check_seg = LocalSegCheckOperator(
    dag=dag,
    abort_on_error=False,
    move_data=True,
    input_operators=[dcm2nifti_seg, dcm2nifti_ct],
    delete_input_on_success=False
)

extract_ensemble = GetEnsembleOperator(dag=dag)

nnunet_predict = NnUnetOperator(
    dag=dag,
    mode="inference",
    input_modality_operators=[dcm2nifti_ct],
    inf_softmax=True,
    inf_threads_prep=1,
    inf_threads_nifti=1,
    models_dir=extract_ensemble.operator_out_dir,
)

nnunet_ensemble = NnUnetOperator(
    dag=dag,
    input_operator=nnunet_predict,
    mode="ensemble",
    inf_threads_nifti=4,
)

data_organizer = LocalDataorganizerOperator(
    dag=dag,
    keep_parallel_id=False,
    gt_operator=dcm2nifti_gt,
    ensemble_operator=nnunet_ensemble,
    input_operator=nnunet_predict,
)

resample_gt = ResampleOperator(
    dag=dag,
    input_operator=dcm2nifti_gt,
    original_img_operator=dcm2nifti_ct,
    operator_out_dir=dcm2nifti_gt.operator_out_dir,
    parallel_id="gt",
    batch_name=str(get_test_images.operator_out_dir),
    delete_input_on_success=False,
)
resample_single = ResampleOperator(
    dag=dag,
    operator_in_dir="single-model-prediction",
    operator_out_dir="single-model-prediction",
    original_img_operator=dcm2nifti_ct,
    parallel_id="single",
    batch_name=str(get_test_images.operator_out_dir),
    delete_input_on_success=False,
)
resample_ensemble = ResampleOperator(
    dag=dag,
    operator_in_dir="ensemble-prediction",
    operator_out_dir="ensemble-prediction",
    original_img_operator=dcm2nifti_ct,
    parallel_id="ensemble",
    batch_name=str(get_test_images.operator_out_dir),
    delete_input_on_success=False,
)

evaluation = LocalDiceOperator(
    dag=dag,
    gt_operator=dcm2nifti_gt,
    ensemble_operator=nnunet_ensemble,
    input_operator=nnunet_predict,
)

clean = LocalWorkflowCleanerOperator(dag=dag, clean_workflow_dir=False)

get_input >> dcm2bin >> extract_model >> nnunet_predict >> nnunet_ensemble >> data_organizer
data_organizer >> resample_single >> evaluation
data_organizer >> resample_ensemble >> evaluation
get_test_images >> dcm2nifti_gt >> resample_gt >> evaluation >> clean
get_test_images >> get_ref_ct_series_from_gt >> dcm2nifti_ct
dcm2nifti_ct >> nnunet_predict
dcm2nifti_ct >> resample_gt
