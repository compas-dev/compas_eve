from ..event_emitter import EventEmitterMixin
from ..core import Transport


class InMemoryTransport(Transport, EventEmitterMixin):
    """In-Memory transport is ideal for simple single-process apps and testing.

    It will only distribute messages within the same process, not across different processes."""

    def __init__(self, *args, **kwargs):
        super(InMemoryTransport, self).__init__(*args, **kwargs)

    def on_ready(self, callback):
        """In-memory transport is always ready, it will immediately trigger the callback."""
        callback()

    def publish(self, topic, message):
        """Publish a message to a topic."""
        event_key = "event_{}".format(topic.name)

        def _callback(**kwargs):
            self.emit(event_key, message)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        """Subscribe to be notified of messages on a given topic."""
        event_key = "event_{}".format(topic.name)

        def _callback(**kwargs):
            self.on(event_key, callback)

        self.on_ready(_callback)

    def unsubscribe(self, topic):
        """Unsubscribe from the specified topic."""
        event_key = "event_{}".format(topic.name)
        self.remove_all_listeners(event_key)

    def advertise(self, topic):
        """Announce this code will publish messages to the specified topic.

        This call has no effect on the in-memory transport."""
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # in-memory does not need anything here
        return advertise_id

    def unadvertise(self, topic):
        """Announce this code will stop publishing messages to the specified topic.

        This call has no effect on the in-memory transport."""
        pass
