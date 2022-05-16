from dataclasses import dataclass
import string
from constructs import Construct
from aws_cdk.aws_ec2 import IVpc
from aws_cdk.aws_ecs import (
    Cluster,
    ContainerImage,
    FargateTaskDefinition,
    TaskDefinition
)

def add_cluster(scope: Construct, id: str, vpc: IVpc) -> Cluster:
    return Cluster(scope, id, vpc=vpc)

@dataclass
class TaskConfig:
    cpu: int
    memory_limit_mb: int
    family: str

@dataclass
class ContainerConfig:
    dockerhub_image: str


def add_task_definition_with_container(scope: Construct, 
                                       id: str,
                                       task_config: TaskConfig,
                                       container_config: ContainerConfig) -> TaskDefinition:
    taskdef = FargateTaskDefinition(scope, 
                                    id,
                                    cpu=task_config.cpu,
                                    memory_limit_mib=task_config.memory_limit_mb,
                                    family=task_config.family)
    image = ContainerImage.from_registry(container_config.dockerhub_image)
    taskdef.add_container(f'container-{container_config.dockerhub_image}', image=image)
    return taskdef

