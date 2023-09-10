from compas.data import json_dumps
from compas.data import json_loads

from ..core import Transport
from ..event_emitter import EventEmitterMixin

import paho.mqtt.client as mqtt


class MqttTransport(Transport, EventEmitterMixin):
    """MQTT transport allows sending and receiving messages using an MQTT broker.

    Parameters
    ----------
    host : str
        Host name for the MQTT broker, e.g. ``broker.hivemq.com`` or ``localhost`` if
        you are running a local broker on your machine.
    port : int
        MQTT broker port, defaults to ``1883``.
    """

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
        """Close the connection to the MQTT broker."""
        self.client.loop_stop()

    def _on_connect(self, client, userdata, flags, rc):
        self._is_connected = True
        self.emit("ready")

    def on_ready(self, callback):
        """Allows to hook-up to the event triggered when the connection to MQTT broker is ready.

        Parameters
        ----------
        callback : function
            Function to invoke when the connection is established.
        """
        if self._is_connected:
            callback()
        else:
            self.once("ready", callback)

    def publish(self, topic, message):
        """Publish a message to a topic.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to publish to.
        message : :class:`Message`
            Instance of the message to publish.
        """

        def _callback(**kwargs):
            # TODO: can we avoid the additional cast to dict?
            json_message = json_dumps(dict(message))
            self.client.publish(topic.name, json_message)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        """Subscribe to a topic.

        Every time a new message is received on the topic, the callback will be invoked.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to subscribe to.
        callback : function
            Callback to invoke whenever a new message arrives. The callback should
            receive only one `msg` argument, e.g. ``lambda msg: print(msg)``.

        Returns
        -------
        str
            Returns an identifier of the subscription.
        """
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
        """Announce this code will publish messages to the specified topic.

        This call has no effect on this transport implementation."""
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # mqtt does not need anything here
        return advertise_id

    def unadvertise(self, topic):
        """Announce that this code will stop publishing messages to the specified topic.

        This call has no effect on this transport implementation."""
        pass

    def unsubscribe_by_id(self, subscribe_id):
        """Unsubscribe from the specified topic based on the subscription id."""
        ev_type, topic_name, _callback_id = subscribe_id.split(":")
        event_key = "{}:{}".format(ev_type, topic_name)

        callback = self._local_callbacks[subscribe_id]
        self.off(event_key, callback)
        self.client.unsubscribe(topic_name)

        del self._local_callbacks[subscribe_id]

    def unsubscribe(self, topic):
        """Unsubscribe from the specified topic."""
        self.client.unsubscribe(topic.name)
