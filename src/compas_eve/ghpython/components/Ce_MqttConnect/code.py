"""
Connect or disconnect to an MQTT broker.

COMPAS EVE v0.5.0
"""

from threading import Event

from compas_ghpython import create_id
from ghpythonlib.componentbase import executingcomponent as component
from scriptcontext import sticky as st

from compas_eve.mqtt import MqttTransport


class MqttConnectComponent(component):
    def RunScript(self, host, port, connect):
        mqtt_transport = None

        host = host or "127.0.0.1"
        port = port or 1883

        key = create_id(self, "mqtt_transport")
        mqtt_transport = st.get(key, None)

        if mqtt_transport:
            st[key].close()

        if connect:
            event = Event()
            transport = MqttTransport(host, port)
            transport.on_ready(event.set)
            if not event.wait(5):
                raise Exception("Failed to connect to MQTT broker.")

            st[key] = transport

        mqtt_transport = st.get(key, None)
        is_connected = mqtt_transport._is_connected if mqtt_transport else False
        return (mqtt_transport, is_connected)
