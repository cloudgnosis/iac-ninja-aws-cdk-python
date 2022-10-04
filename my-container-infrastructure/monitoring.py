from dataclasses import dataclass
from aws_cdk.aws_sns import ITopic
from cdk_monitoring_constructs import AlarmFactoryDefaults, MonitoringFacade, NoopAlarmActionStrategy, SnsAlarmActionStrategy
from constructs import Construct

@dataclass
class MonitoringConfig:
    dashboard_name: str
    default_alarm_topic: ITopic = None # type: ignore
    default_alarm_name_prefix: str = None  # type: ignore

@dataclass
class MonitoringContext:
    handler: MonitoringFacade
    default_alarm_topic: ITopic = None # type: ignore
    default_alarm_name_prefix: str = None  # type: ignore


def init_monitoring(scope: Construct, config: MonitoringConfig) -> MonitoringContext:
    sns_alarm_strategy = NoopAlarmActionStrategy()
    if config.default_alarm_topic:
        sns_alarm_strategy = SnsAlarmActionStrategy(on_alarm_topic=config.default_alarm_topic)
    default_alarm_name_prefix = config.default_alarm_name_prefix
    if default_alarm_name_prefix == None:
        default_alarm_name_prefix = config.dashboard_name
    return MonitoringContext(
        handler=MonitoringFacade(
            scope,
            config.dashboard_name,
            alarm_factory_defaults=AlarmFactoryDefaults(
                actions_enabled=True,
                action=sns_alarm_strategy,
                alarm_name_prefix=default_alarm_name_prefix
            )),
            default_alarm_topic=config.default_alarm_topic,
            default_alarm_name_prefix=default_alarm_name_prefix)
