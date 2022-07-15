import os
import sys
import glob
import zipfile
from subprocess import PIPE, run
import re
import yaml

from kaapana.operators.KaapanaPythonBaseOperator import KaapanaPythonBaseOperator
from kaapana.blueprints.kaapana_global_variables import BATCH_NAME, WORKFLOW_DIR


class LocalCreateIsoInstanceOperator(KaapanaPythonBaseOperator):
    def start(self, ds, ti, **kwargs):
        print("Starting an isolated environment...")

        operator_dir = os.path.dirname(os.path.abspath(__file__))
        playbooks_dir = os.path.join(operator_dir, "ansible_playbooks")
        playbook_path = os.path.join(playbooks_dir, "00_start_"+self.platformType+"_instance.yaml")
        if not os.path.isfile(playbook_path):
            print("Playbook yaml not found!! Exiting now...")
            exit(1)
        
        config_filepath = os.path.join(operator_dir, "platform_specific_configs", "cloud_platform_config.yaml")
        with open(config_filepath, "r") as stream:
            platform_config = yaml.safe_load(stream)
        
        extra_vars = ""
        if self.platformType == "openstack":
            os_username = platform_config["configurations"][self.platformType]["username"]
            os_password = platform_config["configurations"][self.platformType]["password"]
            for key, value in platform_config["configurations"][self.platformType]["openstack"]["extra_vars"].items():
                extra_vars += f"{key}={value} "
            extra_vars = extra_vars.rstrip() # to remove blank space in the end 
        else:
            print(f"Sorry!! {self.platformType} is not yet supported. Exiting now...")
            exit(1)

        command = ["ansible-playbook", playbook_path, "--extra-vars", extra_vars]
        output = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, timeout=6000)
        print(f'STD OUTPUT LOG is {output.stdout}')
        if output.returncode == 0:
            print(f'Iso Instance created successfully!')
            ip_addr_string = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', output.stdout)
            print(f'IP address of new TFDA isolated instance is: {ip_addr_string[-1]}')
            ti.xcom_push(key="iso_env_ip", value=ip_addr_string[-1])
        else:
            print(f"Failed to create isolated environment! ERROR LOGS:\n{output.stderr}")
        

    def __init__(self,
                 dag,
                 platformType = "openstack",
                 **kwargs):

        super().__init__(
            dag=dag,
            name="create-iso-inst",
            python_callable=self.start,
            **kwargs
        )
        self.platformType = platformType