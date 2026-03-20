import threading

import zenoh

from ..core import Transport
from ..event_emitter import EventEmitterMixin


class ZenohTransport(Transport, EventEmitterMixin):
    """Zenoh transport allows sending and receiving messages using an Apache Zenoh router.

    Parameters
    ----------
    config : :class:`zenoh.Config`, optional
        The Zenoh configuration to use. If not provided, a default `zenoh.Config()` will be used.
    codec : :class:`MessageCodec`, optional
        The codec to use for encoding and decoding messages.
        If not provided, defaults to :class:`JsonMessageCodec`.
    """

    def __init__(self, config=None, codec=None, *args, **kwargs):
        super(ZenohTransport, self).__init__(codec=codec, *args, **kwargs)
        if config is None:
            self.config = zenoh.Config()
        else:
            self.config = config

        self._is_connected = False
        self._local_callbacks = {}
        self._publishers = {}
        self._subscribers = {}

        self.session = zenoh.open(self.config)
        self._is_connected = True

        def emit_ready():
            self.emit("ready")

        threading.Thread(target=emit_ready).start()

    def close(self):
        """Close the Zenoh session."""
        self.session.close()

    def _get_topic_name(self, topic):
        return topic.name.strip("/")

    def on_ready(self, callback):
        """Allows to hook-up to the event triggered when the connection is established.

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
            if self._get_topic_name(topic) not in self._publishers:
                self._publishers[self._get_topic_name(topic)] = self.session.declare_publisher(self._get_topic_name(topic))

            encoded_message = self.codec.encode(message)
            self._publishers[self._get_topic_name(topic)].put(encoded_message)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        """Subscribe to a topic.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to subscribe to.
        callback : function
            Callback to invoke whenever a new message arrives.

        Returns
        -------
        str
            Returns an identifier of the subscription.
        """
        event_key = "event:{}".format(self._get_topic_name(topic))
        subscribe_id = "{}:{}".format(event_key, id(callback))

        def _local_callback(msg):
            callback(msg)

        def _zenoh_handler(sample):
            payload = sample.payload.to_bytes() if hasattr(sample.payload, "to_bytes") else bytes(sample.payload)
            message_obj = self.codec.decode(payload, topic.message_type)
            self.emit(event_key, message_obj)

        def _subscribe_callback(**kwargs):
            if self._get_topic_name(topic) not in self._subscribers:
                self._subscribers[self._get_topic_name(topic)] = self.session.declare_subscriber(self._get_topic_name(topic), _zenoh_handler)

            self.on(event_key, _local_callback)

        self._local_callbacks[subscribe_id] = _local_callback

        self.on_ready(_subscribe_callback)

        return subscribe_id

    def unsubscribe(self, topic):
        """Unsubscribe from a topic.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to unsubscribe from.
        """
        event_key = "event:{}".format(self._get_topic_name(topic))

        if self._get_topic_name(topic) in self._subscribers:
            self._subscribers[self._get_topic_name(topic)].undeclare()
            del self._subscribers[self._get_topic_name(topic)]

        keys_to_remove = [k for k in self._local_callbacks.keys() if k.startswith(event_key + ":")]
        for k in keys_to_remove:
            self.remove_listener(event_key, self._local_callbacks[k])
            del self._local_callbacks[k]

    def advertise(self, topic):
        """Announce this code will publish messages to the specified topic.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to advertise.

        Returns
        -------
        str
            Advertising identifier.
        """
        advertise_id = "advertise:{}:{}".format(self._get_topic_name(topic), self.id_counter)
        return advertise_id

    def unsubscribe_by_id(self, subscribe_id):
        """Unsubscribe from the specified topic based on the subscription id.

        Parameters
        ----------
        subscribe_id : str
            The subscription identifier.
        """
        # subscribe_id format: "event:topic_name:id(callback)"
        parts = subscribe_id.split(":", 2)
        if len(parts) >= 2:
            topic_name = parts[1]
            if topic_name in self._subscribers:
                self._subscribers[topic_name].undeclare()
                del self._subscribers[topic_name]

        if subscribe_id in self._local_callbacks:
            # We don't have event_key directly but it is parts[0]:parts[1]
            event_key = "{}:{}".format(parts[0], parts[1])
            self.remove_listener(event_key, self._local_callbacks[subscribe_id])
            del self._local_callbacks[subscribe_id]
