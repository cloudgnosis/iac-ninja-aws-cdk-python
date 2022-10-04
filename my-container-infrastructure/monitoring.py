from dataclasses import dataclass
import string
from cdk_monitoring_constructs import MonitoringFacade
from constructs import Construct

@dataclass
class MonitoringConfig:
    dashboard_name: str

@dataclass
class MonitoringContext:
    handler: MonitoringFacade


def init_monitoring(scope: Construct, config: MonitoringConfig) -> MonitoringContext:
    return MonitoringContext(handler=MonitoringFacade(scope, config.dashboard_name))
