import os
import glob
from datetime import timedelta

from kaapana.operators.KaapanaBaseOperator import KaapanaBaseOperator, default_registry, default_platform_abbr, default_platform_version

class BreastDensityClassifierFederatedOperator(KaapanaBaseOperator):

    def __init__(self,
                 dag,
                 name='breast_density_classification-federated',
                 execution_timeout=timedelta(days=5),
                 *args, **kwargs
                 ):

        super().__init__(
            dag=dag,
            name=name,
            image=f"{default_registry}/bdc-federated:{default_platform_abbr}_{default_platform_version}__0.1.0",
            image_pull_secrets=["registry-secret"],
            execution_timeout=execution_timeout,
            ram_mem_mb=1000,
            ram_mem_mb_lmt=None,
            image_pull_policy="Always",
            *args, **kwargs
        )