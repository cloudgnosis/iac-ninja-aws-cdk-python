import pytest
from aws_cdk import Stack
from aws_cdk.assertions import (
    Capture,
    Match,
    Template
)
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ecs import ContainerDefinition
from containers.container_management import (
    add_cluster,
    add_service,
    add_task_definition_with_container,
    ContainerConfig,
    TaskConfig
)


def test_ECS_cluster_defined_with_existing_vpc():
    stack = Stack()
    vpc = Vpc(stack, 'vpc')
    cluster = add_cluster(stack, 'test-cluster', vpc=vpc)

    template = Template.from_stack(stack)

    template.resource_count_is('AWS::ECS::Cluster', 1)

    assert(cluster.vpc == vpc)


def test_ECS_fargate_task_definition_defined():
    stack = Stack()
    cpuval = 512
    memval = 1024
    familyval = 'test'
    task_cfg = TaskConfig(cpu=cpuval, memory_limit_mb=memval, family=familyval)
    image_name = 'httpd';
    container_cfg = ContainerConfig(dockerhub_image=image_name)

    taskdef = add_task_definition_with_container(stack, 'test-taskdef', task_cfg, container_cfg)

    template = Template.from_stack(stack)
    assert(taskdef.is_fargate_compatible)
    assert(taskdef in stack.node.children)

    template.resource_count_is('AWS::ECS::TaskDefinition', 1)
    template.has_resource_properties('AWS::ECS::TaskDefinition', {
        'RequiresCompatibilities': [ 'FARGATE' ],
        'Cpu': str(cpuval),
        'Memory': str(memval),
        'Family': familyval,
    })


def test_container_definition_added_to_task_definition():
    stack = Stack()
    cpuval = 512
    memval = 1024
    familyval = 'test'
    task_cfg = TaskConfig(cpu=cpuval, memory_limit_mb=memval, family=familyval)
    image_name = 'httpd';
    container_cfg = ContainerConfig(dockerhub_image=image_name)

    taskdef = add_task_definition_with_container(stack, 'test-taskdef', task_cfg, container_cfg)

    template = Template.from_stack(stack)
    containerdef : ContainerDefinition = taskdef.default_container

    assert(containerdef != None)
    assert(containerdef.image_name == image_name)

    template.has_resource_properties('AWS::ECS::TaskDefinition', {
        'ContainerDefinitions': Match.array_with([
            Match.object_like({
                'Image': image_name
            })
        ])
    })


@pytest.fixture
def service_test_input_data():
    stack = Stack()
    vpc = Vpc(stack, 'vpc')
    cluster = add_cluster(stack, 'test-cluster', vpc=vpc)
    cpuval = 512
    memval = 1024
    familyval = 'test'
    task_cfg = TaskConfig(cpu=cpuval, memory_limit_mb=memval, family=familyval)
    image_name = 'httpd';
    container_cfg = ContainerConfig(dockerhub_image=image_name)
    taskdef = add_task_definition_with_container(stack, 'test-taskdef', task_cfg, container_cfg)
    return { 'stack': stack, 'cluster': cluster, 'task_definition': taskdef}


def test_fargate_service_created_with_only_mandatory_properties(service_test_input_data):
    stack = service_test_input_data['stack']
    cluster = service_test_input_data['cluster']
    taskdef = service_test_input_data['task_definition']

    port = 80
    desired_count = 1

    service = add_service(stack, 'test-service', cluster, taskdef, port, desired_count)

    sg_capture = Capture()
    template = Template.from_stack(stack)

    assert(service.cluster == cluster)
    assert(service.task_definition == taskdef)

    template.resource_count_is('AWS::ECS::Service', 1)
    template.has_resource_properties('AWS::ECS::Service', {
        'DesiredCount': desired_count,
        'LaunchType': 'FARGATE',
        'NetworkConfiguration': Match.object_like({
            'AwsvpcConfiguration': Match.object_like({
                'AssignPublicIp': 'DISABLED',
                'SecurityGroups': Match.array_with([sg_capture])
            })
        })
    })

    template.resource_count_is('AWS::EC2::SecurityGroup', 1)
    template.has_resource_properties('AWS::EC2::SecurityGroup', {
        'SecurityGroupIngress': Match.array_with([
            Match.object_like({
                'CidrIp': '0.0.0.0/0',
                'FromPort': port,
                'IpProtocol': 'tcp'
            })
        ])
    })

