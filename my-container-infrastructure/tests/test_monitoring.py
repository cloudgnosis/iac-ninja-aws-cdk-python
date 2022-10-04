import pytest
from aws_cdk import Stack
from aws_cdk.assertions import (
    Capture,
    Match,
    Template
)
from aws_cdk.aws_ec2 import Vpc
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