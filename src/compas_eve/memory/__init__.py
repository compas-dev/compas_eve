"""
********************************************************************************
compas_eve.memory
********************************************************************************

.. currentmodule:: compas_eve.memory


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    InMemoryTransport

"""

from compas_eve.event_emitter import EventEmitterMixin
from compas_eve.core import Transport

__all__ = ["InMemoryTransport"]


class InMemoryTransport(Transport, EventEmitterMixin):
    """In-Memory transport is ideal for simple single-process apps and testing.

    It will only distribute messages within the same process, not across different processes.

    Parameters
    ----------
    codec : :class:`MessageCodec`, optional
        The codec to use for encoding and decoding messages.
        If not provided, defaults to :class:`JsonMessageCodec`.
    """

    def __init__(self, codec=None, *args, **kwargs):
        super(InMemoryTransport, self).__init__(codec=codec, *args, **kwargs)
        self._local_callbacks = {}

    def on_ready(self, callback):
        """In-memory transport is always ready, it will immediately trigger the callback."""
        callback()

    def publish(self, topic, message):
        """Publish a message to a topic.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to publish to.
        message : :class:`Message`
            Instance of the message to publish.
        """
        event_key = "event:{}".format(topic.name)

        def _callback(**kwargs):
            self.emit(event_key, message)

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

        def _callback(**kwargs):
            self.on(event_key, callback)

        self._local_callbacks[subscribe_id] = callback

        self.on_ready(_callback)

        return subscribe_id

    def unsubscribe_by_id(self, subscribe_id):
        """Unsubscribe from the specified topic based on the subscription id."""
        ev_type, topic_name, _callback_id = subscribe_id.split(":")
        event_key = "{}:{}".format(ev_type, topic_name)

        callback = self._local_callbacks[subscribe_id]
        self.off(event_key, callback)
        del self._local_callbacks[subscribe_id]

    def unsubscribe(self, topic):
        """Unsubscribe from the specified topic."""
        event_key = "event:{}".format(topic.name)
        self.remove_all_listeners(event_key)

    def advertise(self, topic):
        """Announce this code will publish messages to the specified topic.

        This call has no effect on the in-memory transport."""
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # in-memory does not need anything here
        return advertise_id

    def unadvertise(self, topic):
        """Announce that this code will stop publishing messages to the specified topic.

        This call has no effect on the in-memory transport."""
        pass
