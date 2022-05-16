from dataclasses import dataclass
import string
from constructs import Construct
from aws_cdk.aws_ec2 import IVpc
from aws_cdk.aws_ecs import Cluster

def add_cluster(scope: Construct, id: str, vpc: IVpc) -> Cluster:
    return Cluster(scope, id, vpc=vpc)

