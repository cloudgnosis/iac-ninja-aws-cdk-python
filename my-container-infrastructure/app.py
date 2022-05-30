#!/usr/bin/env python3
import os
from aws_cdk import ( App, Environment, Stack )
from aws_cdk.aws_ec2 import ( Vpc )
from containers.container_management import (
    add_cluster,
    add_loadbalanced_service,
    add_task_definition_with_container,
    ContainerConfig,
    TaskConfig
)


app = App()
stack = Stack(app, 'my-container-infrastructure', 
                  env=Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                      region=os.getenv('CDK_DEFAULT_REGION')))

vpcname = app.node.try_get_context('vpcname')
if (vpcname):
    vpc = Vpc.from_lookup(stack, 'vpc', vpc_name=vpcname)
else:
    vpc = Vpc(stack, 'vpc', vpc_name='my-vpc', nat_gateways=1, max_azs=2)

id = 'my-test-cluster'
cluster = add_cluster(stack, id, vpc)

task_config = TaskConfig(cpu=512, memory_limit_mb=1024, family='webserver');
container_config = ContainerConfig(dockerhub_image='httpd', tcp_ports=[80])
taskdef = add_task_definition_with_container(stack,
                                             f'taskdef-{task_config.family}',
                                             task_config=task_config,
                                             container_config=container_config)
add_loadbalanced_service(stack, f'service-{task_config.family}', cluster, taskdef, 80, 2, True);
app.synth()
