#!/usr/bin/env python3
import os
from typing import Sequence
from aws_cdk import ( App, Duration, Environment, Stack )
from aws_cdk.aws_cloudwatch import ComparisonOperator
from aws_cdk.aws_cloudwatch_actions import (
    OpsItemCategory,
    OpsItemSeverity
)
from aws_cdk.aws_ec2 import ( IVpc, Vpc )
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_sns_subscriptions import EmailSubscription
from cdk_monitoring_constructs import (
    IAlarmActionStrategy,
    MultipleAlarmActionStrategy,
    OpsItemAlarmActionStrategy,
    RunningTaskCountThreshold,
    SnsAlarmActionStrategy
)
from monitoring import (
    init_monitoring,
    MonitoringConfig
)
from containers.container_management import (
    add_cluster,
    add_loadbalanced_service,
    add_task_definition_with_container,
    set_service_scaling,
    ScalingThreshold,
    ServiceScalingConfig,
    ClusterConfig,
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
cluster_config = ClusterConfig(vpc=vpc, enable_container_insights=True)
cluster = add_cluster(stack, id, cluster_config)

task_config = TaskConfig(cpu=512, memory_limit_mb=1024, family='webserver');
container_config = ContainerConfig(dockerhub_image='httpd', tcp_ports=[80])
taskdef = add_task_definition_with_container(stack,
                                             f'taskdef-{task_config.family}',
                                             task_config=task_config,
                                             container_config=container_config)
service = add_loadbalanced_service(stack, f'service-{task_config.family}', cluster, taskdef, 80, 2, True);
set_service_scaling(
    service=service.service,
    config=ServiceScalingConfig(
        min_count=1,
        max_count=4,
        scale_cpu_target=ScalingThreshold(percent=50),
        scale_memory_target=ScalingThreshold(percent=70))
)

alarm_topic = Topic(stack, 'alarm-topic', display_name='Alarm topic')

monitoring_config = MonitoringConfig(dashboard_name='monitoring', default_alarm_topic=alarm_topic) # type: ignore
monitoring = init_monitoring(stack, monitoring_config)  

alarm_actions = []
alarm_actions.append(OpsItemAlarmActionStrategy(OpsItemSeverity.MEDIUM, OpsItemCategory.PERFORMANCE))
if monitoring_config.default_alarm_topic:
    alarm_actions.append(SnsAlarmActionStrategy(
        on_alarm_topic=monitoring_config.default_alarm_topic,
        on_ok_topic=monitoring_config.default_alarm_topic))

monitoring.handler.add_medium_header('Test App monitoring')
monitoring.handler.monitor_fargate_service(
    fargate_service=service,
    human_readable_name='My test service',
    add_running_task_count_alarm={
        'alarm1': RunningTaskCountThreshold(
            max_running_tasks=2,
            comparison_operator_override=ComparisonOperator.LESS_THAN_THRESHOLD,
            evaluation_periods=2,
            datapoints_to_alarm=2,
            period=Duration.minutes(5),
            action_override=MultipleAlarmActionStrategy(alarm_actions)
        )
    })

alarm_email = 'hello@example.com'
alarm_topic.add_subscription(EmailSubscription(alarm_email))

app.synth()
