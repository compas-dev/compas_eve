import sys

if sys.platform == "cli":
    from .mqtt_cli import MqttTransport
else:
    from .mqtt_paho import MqttTransport

__all__ = ["MqttTransport"]
