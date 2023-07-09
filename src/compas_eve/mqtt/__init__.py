import json

import paho.mqtt.client as mqtt

from ..core import MessageEncoder
from ..core import Transport
from ..event_emitter import EventEmitterMixin

__all__ = ["MqttTransport"]


class MqttTransport(Transport, EventEmitterMixin):
    def __init__(self, host, port=1883, *args, **kwargs):
        super(MqttTransport, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self._is_connected = False
        self.client = mqtt.Client()  # todo: generate client_id
        self.client.on_connect = self._on_connect
        self.client.connect(self.host, self.port)
        self.client.loop_start()

    def close(self):
        print("Closing")
        self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        self._is_connected = True
        self.emit("ready")

    def on_ready(self, callback):
        if self._is_connected:
            callback()
        else:
            self.once("ready", callback)

    def publish(self, topic, message):
        # event_key = "event_{}".format(topic.name)

        def _callback(**kwargs):
            # TODO: can we avoid the additional cast to dict?
            json_message = json.dumps(dict(message), cls=MessageEncoder)
            self.client.publish(topic.name, json_message)
            # self.emit(event_key, message)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        event_key = "event_{}".format(topic.name)

        def _callback(**kwargs):
            self.on(event_key, callback)

        self.client.subscribe(topic.name)

        def on_message(client, userdata, msg):
            msg = topic.message_type.parse(json.loads(msg.payload.decode()))
            callback(msg)

        self.client.on_message = on_message

        self.on_ready(_callback)

    def advertise(self, topic):
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # mqtt does not need anything here
        return advertise_id

    def unadvertise(self, topic):
        pass

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic.name)
