#!/usr/bin/env python3
import os
from aws_cdk import ( App, Environment, Stack )
from aws_cdk.aws_ec2 import ( Vpc )
from containers.container_management import (
    add_cluster,
    add_service,
    add_task_definition_with_container,
    ContainerConfig,
    TaskConfig
)


app = App()
stack = Stack(app, 'my-container-infrastructure', 
                  env=Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                      region=os.getenv('CDK_DEFAULT_REGION')))

vpc = Vpc.from_lookup(stack, 'vpc', is_default=True)

id = 'my-test-cluster'
cluster = add_cluster(stack, id, vpc)

task_config = TaskConfig(cpu=512, memory_limit_mb=1024, family='webserver');
container_config = ContainerConfig(dockerhub_image='httpd')
taskdef = add_task_definition_with_container(stack,
                                             f'taskdef-{task_config.family}',
                                             task_config=task_config,
                                             container_config=container_config)
add_service(stack, f'service-{task_config.family}', cluster, taskdef, 80, 0);
app.synth()
