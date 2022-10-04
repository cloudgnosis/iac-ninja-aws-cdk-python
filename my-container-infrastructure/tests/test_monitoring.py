import pytest
from aws_cdk import Stack
from aws_cdk.assertions import Template
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_sns import Topic
from monitoring import (
    init_monitoring,
    MonitoringConfig
)


def test_init_monitoring_of_stack_with_defaults():
    stack = Stack()

    config = MonitoringConfig(dashboard_name='test-monitoring')
    monitoring = init_monitoring(stack, config)
    template = Template.from_stack(stack)
    print(template)
    template.resource_count_is('AWS::CloudWatch::Dashboard', 1)
    template.has_resource_properties('AWS::CloudWatch::Dashboard', {
        'DashboardName': config.dashboard_name
    })


def test_init_monitoring_of_stack_with_sns_alarm_topic():
    stack = Stack()
    vpc = Vpc(stack, 'vpc')
    alarm_topic = Topic(stack, 'alarm-topic')

    monitoring_config = MonitoringConfig(
        dashboard_name='test-monitoring',
        default_alarm_topic=alarm_topic  # type: ignore
    )

    monitoring = init_monitoring(stack, config=monitoring_config)
    assert(monitoring.default_alarm_topic == monitoring_config.default_alarm_topic)
    assert(monitoring.default_alarm_name_prefix == monitoring_config.dashboard_name)


def test_init_monitoring_of_stack_with_sns_alarm_topic_and_alarm_prefix():
    stack = Stack()
    vpc = Vpc(stack, 'vpc')
    alarm_topic = Topic(stack, 'alarm-topic')

    monitoring_config = MonitoringConfig(
        dashboard_name='test-monitoring',
        default_alarm_topic=alarm_topic,  # type: ignore
        default_alarm_name_prefix='my-prefix'
    )
    monitoring = init_monitoring(stack, config=monitoring_config)
    assert(monitoring.default_alarm_topic == monitoring_config.default_alarm_topic)
    assert(monitoring.default_alarm_name_prefix == monitoring_config.default_alarm_name_prefix)