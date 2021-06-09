import os
from datetime import timedelta

from kaapana.kubetools.resources import Resources as PodResources
from kaapana.blueprints.kaapana_global_variables import BATCH_NAME, WORKFLOW_DIR

#from kaapana.operators.KaapanaBaseOperator import KaapanaBaseOperator, default_registry, default_project
# --> TODO: on_success_back back owerwrite must be possible


class TrainingBraTSOperator(KaapanaBaseOperator):

    @staticmethod
    def on_success(info_dict):
        print("##################################################### on_success!")
        pod_id = info_dict["ti"].task.kube_name
        print("--> training ended, now delete pod {} !".format(pod_id))
        KaapanaBaseOperator.pod_stopper.stop_pod_by_name(pod_id=pod_id)
    
    def __init__(self,
                 dag,
                 host_ip=None,
                 fed_round=None,
                 n_epochs=None,
                 batch_size=None,
                 validation=None,
                 val_interval=None,
                 return_best_model=None,
                 verbose=None,
                 seed=None,
                 env_vars=None,
                 execution_timeout=timedelta(hours=6),
                 *args, **kwargs
                 ):

        if env_vars is None:
            env_vars = {}
        
        envs = {
            "HOST_IP": str(host_ip),
            "FED_ROUND": str(fed_round),
            "N_EPOCHS": str(n_epochs),
            "BATCH_SIZE": str(batch_size),
            "VALIDATION": str(validation),
            "VAL_INTERVAL": str(val_interval),
            "RETURN_BEST_MODEL": str(return_best_model),
            "VERBOSE": str(verbose),
            "SEED": str(seed),
        }

        env_vars.update(envs)

        pod_resources = PodResources(
            request_memory=None,
            request_cpu=None,
            limit_memory=None,
            limit_cpu=None,
            limit_gpu=None
        )

        super().__init__(
            dag=dag,
            name="model-training",
            image="{}{}/federated-exp-brats-train:0.1.0-vdev".format(default_registry, default_project),
            image_pull_secrets=["registry-secret"],
            env_vars=env_vars,
            on_success_callback=TrainingBraTSOperator.on_success,
            execution_timeout=execution_timeout,
            training_operator=True,
            #ram_mem_mb=6000,
            ram_mem_mb=None,
            ram_mem_mb_lmt=None,
            pod_resources=pod_resources,
            gpu_mem_mb=4000,
            *args, **kwargs
            )