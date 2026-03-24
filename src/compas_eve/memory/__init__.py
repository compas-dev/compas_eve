from typing import Callable
from typing import Optional
from compas_eve.codecs import MessageCodec
from compas_eve.event_emitter import EventEmitterMixin
from compas_eve.core import Transport
from compas_eve.core import Topic
from compas_eve.core import Message

__all__ = ["InMemoryTransport"]


class InMemoryTransport(Transport, EventEmitterMixin):
    """In-Memory transport is ideal for simple single-process apps and testing.

    It will only distribute messages within the same process, not across different processes.

    Parameters
    ----------
    codec
        The codec to use for encoding and decoding messages.
        If not provided, defaults to [JsonMessageCodec][compas_eve.codecs.JsonMessageCodec].
    """

    def __init__(self, codec: Optional[MessageCodec] = None, *args, **kwargs):
        super(InMemoryTransport, self).__init__(codec=codec, *args, **kwargs)
        self._local_callbacks = {}

    def on_ready(self, callback: Callable):
        """In-memory transport is always ready, it will immediately trigger the callback."""
        callback()

    def publish(self, topic: Topic, message: Message):
        """Publish a message to a topic.

        Parameters
        ----------
        topic
            Instance of the topic to publish to.
        message
            Instance of the message to publish.
        """
        event_key = "event:{}".format(topic.name)

        def _callback(**kwargs):
            encoded_message = self.codec.encode(message)
            encoded_message_bytes = encoded_message if isinstance(encoded_message, bytes) else encoded_message.encode("utf-8")
            self.emit(event_key, encoded_message_bytes)

        self.on_ready(_callback)

    def subscribe(self, topic: Topic, callback: Callable) -> str:
        """Subscribe to a topic.

        Every time a new message is received on the topic, the callback will be invoked.

        Parameters
        ----------
        topic
            Instance of the topic to subscribe to.
        callback
            Callback to invoke whenever a new message arrives. The callback should
            receive only one `msg` argument, e.g. `lambda msg: print(msg)`.

        Returns
        -------
        str
            Returns an identifier of the subscription.
        """
        event_key = "event:{}".format(topic.name)
        subscribe_id = "{}:{}".format(event_key, id(callback))

        def _local_callback(msg):
            message_obj = self.codec.decode(msg, topic.message_type)
            callback(message_obj)

        def _callback(**kwargs):
            self.on(event_key, _local_callback)

        self._local_callbacks[subscribe_id] = _local_callback

        self.on_ready(_callback)

        return subscribe_id

    def unsubscribe_by_id(self, subscribe_id: str):
        """Unsubscribe from the specified topic based on the subscription id."""
        ev_type, topic_name, _callback_id = subscribe_id.split(":")
        event_key = "{}:{}".format(ev_type, topic_name)

        callback = self._local_callbacks[subscribe_id]
        self.off(event_key, callback)
        del self._local_callbacks[subscribe_id]

    def unsubscribe(self, topic: Topic):
        """Unsubscribe from the specified topic.


        Parameters
        ----------
        topic
            Instance of the topic to unsubscribe from.
        """
        event_key = "event:{}".format(topic.name)
        self.remove_all_listeners(event_key)

    def advertise(self, topic: Topic):
        """Announce this code will publish messages to the specified topic.

        This call has no effect on the in-memory transport."""
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # in-memory does not need anything here
        return advertise_id

    def unadvertise(self, topic: Topic):
        """Announce that this code will stop publishing messages to the specified topic.

        This call has no effect on the in-memory transport."""
        pass
