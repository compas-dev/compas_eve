from compas.data import json_dumps
from compas.data import json_loads

from ..core import Transport
from ..event_emitter import EventEmitterMixin

import paho.mqtt.client as mqtt


class MqttTransport(Transport, EventEmitterMixin):
    def __init__(self, host, port=1883, *args, **kwargs):
        super(MqttTransport, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self._is_connected = False
        self._local_callbacks = {}
        self.client = mqtt.Client()  # todo: generate client_id
        self.client.on_connect = self._on_connect
        self.client.connect(self.host, self.port)
        self.client.loop_start()

    def close(self):
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
        def _callback(**kwargs):
            # TODO: can we avoid the additional cast to dict?
            json_message = json_dumps(dict(message))
            self.client.publish(topic.name, json_message)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        event_key = "event:{}".format(topic.name)
        subscribe_id = "{}:{}".format(event_key, id(callback))

        def _local_callback(msg):
            msg = topic.message_type.parse(json_loads(msg.payload.decode()))
            callback(msg)

        def _subscribe_callback(**kwargs):
            self.client.subscribe(topic.name)

            # We only really need to hook up once per client
            if not self.client.on_message:
                self.client.on_message = self._on_message

            self.on(event_key, _local_callback)

        self._local_callbacks[subscribe_id] = _local_callback

        self.on_ready(_subscribe_callback)

        return subscribe_id

    def _on_message(self, client, userdata, msg):
        event_key = "event:{}".format(msg.topic)
        self.emit(event_key, msg)

    def advertise(self, topic):
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # mqtt does not need anything here
        return advertise_id

    def unadvertise(self, topic):
        pass

    def unsubscribe_by_id(self, subscribe_id):
        ev_type, topic_name, _callback_id = subscribe_id.split(":")
        event_key = "{}:{}".format(ev_type, topic_name)

        callback = self._local_callbacks[subscribe_id]
        self.off(event_key, callback)
        self.client.unsubscribe(topic_name)

        del self._local_callbacks[subscribe_id]

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic.name)
