from dataclasses import dataclass
import string
from constructs import Construct
from aws_cdk.aws_ec2 import (
    IVpc,
    Peer,
    Port,
    SecurityGroup
)
from aws_cdk.aws_ecs import (
    Cluster,
    ContainerImage,
    DeploymentCircuitBreaker,
    FargateService,
    FargateTaskDefinition,
    LogDriver,
    TaskDefinition
)
from aws_cdk.aws_logs import RetentionDays

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
    logdriver = LogDriver.aws_logs(stream_prefix=task_config.family, log_retention=RetentionDays.ONE_DAY)
    taskdef.add_container(f'container-{container_config.dockerhub_image}', image=image, logging=logdriver)
    return taskdef

def add_service(scope: Construct, 
                id: str,
                cluster: Cluster,
                taskdef: FargateTaskDefinition,
                port: int,
                desired_count: int,
                assign_public_ip = False,
                service_name: str = None) -> TaskDefinition:
    sg = SecurityGroup(scope, f'{id}-security-group',
                       description=f'Security group for service {service_name or ""}',
                       vpc=cluster.vpc)
    sg.add_ingress_rule(peer=Peer.any_ipv4(), connection=Port.tcp(port))

    service = FargateService(scope, id,
                             cluster=cluster,
                             task_definition=taskdef,
                             desired_count=desired_count,
                             service_name=service_name,
                             security_groups=[sg],
                             circuit_breaker=DeploymentCircuitBreaker(rollback=True),
                             assign_public_ip=assign_public_ip)
    return service
