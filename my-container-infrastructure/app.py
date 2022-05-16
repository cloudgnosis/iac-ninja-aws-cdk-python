#!/usr/bin/env python3
import os
from aws_cdk import ( App, Environment, Stack )
from aws_cdk.aws_ec2 import ( Vpc )
from containers.container_management import add_cluster


app = App()
stack = Stack(app, 'my-container-infrastructure', 
                  env=Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                      region=os.getenv('CDK_DEFAULT_REGION')))

vpc = Vpc.from_lookup(stack, 'vpc', is_default=True)

id = 'my-test-cluster'
add_cluster(stack, id, vpc)

app.synth()
