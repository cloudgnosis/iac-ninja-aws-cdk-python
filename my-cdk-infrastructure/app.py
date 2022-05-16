#!/usr/bin/env python3
import os
import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2


app = cdk.App()
stack = cdk.Stack(app, 'my-stack', 
                  env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                                      region=os.getenv('CDK_DEFAULT_REGION')))
vpc = ec2.Vpc.from_lookup(stack, 'my-vpc', is_default=True)
ec2.Instance(stack, 'my-ec2', 
             instance_type=ec2.InstanceType.of(instance_class=ec2.InstanceClass.BURSTABLE2,
                                               instance_size=ec2.InstanceSize.MICRO),
             machine_image=ec2.MachineImage.latest_amazon_linux(),
             vpc=vpc)

app.synth()
