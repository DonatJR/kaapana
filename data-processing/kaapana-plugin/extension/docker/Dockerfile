FROM local-only/base-installer:latest

LABEL IMAGE="kaapana-plugin"
LABEL VERSION="0.1.1"
LABEL CI_IGNORE="False"

COPY files/dags/dag_delete_series_from_platform.py /kaapana/tmp/dags/
COPY files/dags/dag_download_selected_files.py /kaapana/tmp/dags/
COPY files/dags/dag_service_extract_metadata.py /kaapana/tmp/dags/
COPY files/dags/dag_collect_metadata.py /kaapana/tmp/dags/
COPY files/dags/dag_convert_itk2dcm.py /kaapana/tmp/dags/
COPY files/dags/dag_send_dicom.py /kaapana/tmp/dags/
COPY files/dags/dag_service_process_incoming_dcm.py /kaapana/tmp/dags/
COPY files/dags/dag_dicom_upload.py /kaapana/tmp/dags/
COPY files/dags/dag_service_reindex_dicom_data.py /kaapana/tmp/dags/
COPY files/dags/dag_tag_dataset.py /kaapana/tmp/dags/
COPY files/dags/dag_tag_seg_ct_tuples.py /kaapana/tmp/dags/
COPY files/dags/dag_tag_train_test_split_dataset.py /kaapana/tmp/dags/
COPY files/dags/dag_service_extract_metadata_trigger_rule.json /kaapana/tmp/dags/
COPY files/dags/dag_service_daily_cleanup_jobs.py /kaapana/tmp/dags/
COPY files/dags/dag_service_segmentation_thumbnail_trigger_rule.json /kaapana/tmp/dags/
COPY files/dags/dag_service_segmentation_thumbnail.py /kaapana/tmp/dags/

COPY files/mounted_scripts/ /kaapana/tmp/mounted_scripts

COPY files/plugin/ /kaapana/tmp/plugins