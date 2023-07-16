# Python 2/3 compatibility import list
try:
    from collections import UserDict
except ImportError:
    from UserDict import UserDict

DEFAULT_TRANSPORT = None


def get_default_transport():
    return DEFAULT_TRANSPORT


def set_default_transport(transport):
    global DEFAULT_TRANSPORT
    DEFAULT_TRANSPORT = transport


class Transport(object):
    """Defines the base interface for different transport implementations."""

    def __init__(self, *args, **kwargs):
        super(Transport, self).__init__(*args, **kwargs)
        self._id_counter = 0

    @property
    def id_counter(self):
        """Generate an auto-incremental ID starting from 1."""
        self._id_counter += 1
        return self._id_counter

    def publish(self, topic, message):
        pass

    def subscribe(self, topic, callback):
        pass

    def unsubscribe(self, topic):
        pass

    def advertise(self, topic):
        pass

    def unadvertise(self, topic):
        pass


class Message(UserDict):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __getattr__(self, name):
        return self.data[name]

    @classmethod
    def parse(cls, value):
        instance = cls()
        instance.update(value)
        return instance


class Topic(object):
    """Describes a topic"""

    def __init__(self, name, message_type, **options):
        self.name = name
        self.message_type = message_type
        self.options = options


class Publisher(object):
    """Publisher interface."""

    def __init__(self, topic, transport=None):
        self.topic = topic
        self.transport = transport or get_default_transport()
        self._advertise_id = None

    @property
    def is_advertised(self):
        """Indicate if the publisher has announce its topic as advertised or not.

        Returns:
            bool: True if advertised as publisher of this topic, False otherwise.
        """
        return self._advertise_id is not None

    def message_published(self, message):
        """Handler called when a message has been published."""
        pass

    def publish(self, message):
        """Publish a message to a topic."""
        # TODO: check if message type matches self.topic.message_type declared
        if not self.is_advertised:
            self.advertise()

        self.transport.publish(self.topic, message)
        self.message_published(message)

    def advertise(self):
        if self.is_advertised:
            return

        self._advertise_id = self.transport.advertise(self.topic)

    def unadvertise(self):
        if not self.is_advertised:
            return

        self.transport.unadvertise(self.topic)
        self._advertise_id = None


class Subscriber(object):
    """Subscriber interface."""

    def __init__(self, topic, callback=None, transport=None):
        self.transport = transport or get_default_transport()
        self.topic = topic
        self._subscribe_id = None
        self._callback = callback

    def message_received(self, message):
        """Handler called whenever a new message is received.

        By default, this implementation will simply invoke the callback
        used on init (if any), but sub-classes can override this behavior."""
        if self._callback:
            self._callback(message)

    @property
    def is_subscribed(self):
        """Indicate if the instace is currently subscribed to its topic or not."""
        return self._subscribe_id is not None

    def subscribe(self):
        if self._subscribe_id:
            return

        self._subscribe_id = self.transport.subscribe(self.topic, self.message_received)

    def unsubscribe(self):
        """Unregister the subscriber from its topic."""
        if not self._subscribe_id:
            return

        self.transport.unsubscribe_by_id(self._subscribe_id)
        self._subscribe_id = None
