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
    PortMapping,
    Protocol,
    TaskDefinition
)
from aws_cdk.aws_ecs_patterns import ApplicationLoadBalancedFargateService
from aws_cdk.aws_logs import RetentionDays


@dataclass
class ClusterConfig:
    vpc: IVpc
    enable_container_insights: bool = False


def add_cluster(scope: Construct, id: str, config: ClusterConfig) -> Cluster:
    return Cluster(scope, id, vpc=config.vpc, container_insights=config.enable_container_insights)

@dataclass
class TaskConfig:
    cpu: int
    memory_limit_mb: int
    family: str

@dataclass
class ContainerConfig:
    dockerhub_image: str
    tcp_ports: list[int]

def add_task_definition_with_container(scope: Construct, 
                                       id: str,
                                       task_config: TaskConfig,
                                       container_config: ContainerConfig) -> FargateTaskDefinition:
    taskdef = FargateTaskDefinition(scope, 
                                    id,
                                    cpu=task_config.cpu,
                                    memory_limit_mib=task_config.memory_limit_mb,
                                    family=task_config.family)
    image = ContainerImage.from_registry(container_config.dockerhub_image)
    logdriver = LogDriver.aws_logs(stream_prefix=task_config.family, log_retention=RetentionDays.ONE_DAY)
    containerdef = taskdef.add_container(f'container-{container_config.dockerhub_image}',
                                         image=image,
                                         logging=logdriver)
    for port in container_config.tcp_ports:
        containerdef.add_port_mappings(PortMapping(container_port=port, protocol=Protocol.TCP))
    return taskdef

def add_loadbalanced_service(scope: Construct, 
                             id: str,
                             cluster: Cluster,
                             taskdef: FargateTaskDefinition,
                             port: int,
                             desired_count: int,
                             public_endpoint = True,
                             service_name: str = None) -> ApplicationLoadBalancedFargateService:  # type: ignore
    service = ApplicationLoadBalancedFargateService(
        scope, id,
        cluster=cluster,
        task_definition=taskdef,
        desired_count=desired_count,
        service_name=service_name,
        circuit_breaker=DeploymentCircuitBreaker(rollback=True),
        public_load_balancer=public_endpoint,
        listener_port=port)
    return service

@dataclass
class ScalingThreshold:
    percent: float

@dataclass
class ServiceScalingConfig:
    min_count: int
    max_count: int
    scale_cpu_target: ScalingThreshold
    scale_memory_target: ScalingThreshold

def set_service_scaling(service: FargateService, config: ServiceScalingConfig):
    scaling = service.auto_scale_task_count(max_capacity=config.max_count, min_capacity=config.min_count)
    scaling.scale_on_cpu_utilization('CpuScaling', target_utilization_percent=config.scale_cpu_target.percent)
    scaling.scale_on_memory_utilization('MemoryScaling', target_utilization_percent=config.scale_memory_target.percent)
    