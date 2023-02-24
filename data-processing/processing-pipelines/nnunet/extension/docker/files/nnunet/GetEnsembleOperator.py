from kaapana.operators.KaapanaBaseOperator import KaapanaBaseOperator, default_registry, kaapana_build_version
from datetime import timedelta
from datetime import timedelta

from kaapana.operators.KaapanaBaseOperator import KaapanaBaseOperator, \
    default_registry, kaapana_build_version


class GetEnsembleOperator(KaapanaBaseOperator):
    execution_timeout = timedelta(minutes=240)

    def __init__(
        self, dag, name="get-ensemble", env_vars={}, enable_proxy=True, execution_timeout=execution_timeout, **kwargs
    ):
        # envs = {
        #     "MODE": str(mode),
        #     "TARGET_LEVEL": str(target_level),
        #     "ZIP_FILE": str(zip_file)
        # }
        # env_vars.update(envs)

        super().__init__(
            dag=dag,
            image=f"{default_registry}/nnunet-get-models:{kaapana_build_version}",
            name=name,
            operator_out_dir="ensembel-model",
            image_pull_secrets=["registry-secret"],
            execution_timeout=execution_timeout,
            env_vars=env_vars,
            enable_proxy=enable_proxy,
            ram_mem_mb=1000,
            **kwargs,
        )
