from compas.data import json_dumps
from compas.data import json_loads

DEFAULT_TRANSPORT = None


class MessageCodec(object):
    """Abstract base class for message codecs.
    
    A codec is responsible for encoding and decoding message data
    to/from a specific representation format (e.g., JSON, Protocol Buffers).
    """

    def encode(self, data):
        """Encode data to the codec's representation format.
        
        Parameters
        ----------
        data : dict
            Data dictionary to encode.
            
        Returns
        -------
        bytes or str
            Encoded representation of the data.
        """
        raise NotImplementedError("Subclasses must implement encode()")

    def decode(self, encoded_data):
        """Decode data from the codec's representation format.
        
        Parameters
        ----------
        encoded_data : bytes or str
            Encoded data to decode.
            
        Returns
        -------
        dict
            Decoded data dictionary.
        """
        raise NotImplementedError("Subclasses must implement decode()")


class JsonMessageCodec(MessageCodec):
    """JSON codec for message serialization.
    
    This codec uses the COMPAS framework's JSON serialization functions
    to encode and decode message data.
    """

    def encode(self, data):
        """Encode data to JSON string.
        
        Parameters
        ----------
        data : dict
            Data dictionary to encode.
            
        Returns
        -------
        str
            JSON string representation of the data.
        """
        return json_dumps(data)

    def decode(self, encoded_data):
        """Decode JSON string to data dictionary.
        
        Parameters
        ----------
        encoded_data : str
            JSON string to decode.
            
        Returns
        -------
        dict
            Decoded data dictionary.
        """
        return json_loads(encoded_data)


def get_default_transport():
    """Retrieve the default transport implementation to be used system-wide.

    Returns
    -------
    :class:`~compas_eve.Transport`
        Instance of a transport class. By default, ``compas_eve`` uses
        :class:`~compas_eve.memory.InMemoryTransport`.
    """
    return DEFAULT_TRANSPORT


def set_default_transport(transport):
    """Assign a default transport implementation to be used system-wide.

    Parameters
    ----------
    transport : :class:`~compas_eve.Transport`
        Instance of a transport class. By default, ``compas_eve`` uses
        :class:`~compas_eve.memory.InMemoryTransport`.
    """
    global DEFAULT_TRANSPORT
    DEFAULT_TRANSPORT = transport


class Transport(object):
    """Defines the base interface for different transport implementations.
    
    Parameters
    ----------
    codec : :class:`MessageCodec`, optional
        The codec to use for encoding and decoding messages. 
        If not provided, defaults to :class:`JsonMessageCodec`.
    """

    def __init__(self, codec=None, *args, **kwargs):
        super(Transport, self).__init__(*args, **kwargs)
        self._id_counter = 0
        self.codec = codec if codec is not None else JsonMessageCodec()

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


class Message(object):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__()
        self.data = {}
        self.data.update(*args, **kwargs)

    def ToString(self):
        return str(self)

    def __str__(self):
        return str(self.data)

    def __getattr__(self, name):
        return self.data[name]

    def __setattr__(self, key, value):
        if key == "data" or key in self.__dict__:
            super(Message, self).__setattr__(key, value)
        else:
            self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __jsondump__(self, minimal=False):
        return self.data

    @classmethod
    def parse(cls, value):
        instance = cls(**value)
        return instance


class Topic(object):
    """A topic is like a mailbox where messages can be sent and received.

    Topics are described by a name, a type of message they accept, and a
    set of options.

    Attributes
    ----------
    name : str
        Name of the topic.
    message_type : type
        Class defining the message structure. Use :class:`Message` for
        a generic, non-typed checked message implementation.
        Defaults to :class:`Message`.
    options : dict
        A dictionary of options.
    """

    # TODO: Add documentation/examples of possible options

    def __init__(self, name, message_type=None, **options):
        self.name = name
        self.message_type = message_type or Message
        self.options = options

    def _message_to_data(self, message):
        """Convert a message to a data representation ready to be encoded.

        Normally, this method expects sub-classes of Message as input.
        However, it can deal with regular dictionaries as well as classes
        implementing the COMPAS data framework.
        
        Parameters
        ----------
        message : :class:`Message` or dict or object
            Message to convert. Can be a Message instance, a dict, or 
            an object implementing __data__.
            
        Returns
        -------
        dict
            Data dictionary representation of the message.
        """
        try:
            data = message.data
        except (KeyError, AttributeError):
            try:
                data = message.__data__
            except (KeyError, AttributeError):
                data = dict(message)
        return data


class Publisher(object):
    """Publisher for a specific topic.

    Parameters
    ----------
    topic : :class:`Topic` or str
        The topic to publish messages to. If a string is provided, a new topic instance
        will be created using the string as topic name.
    transport : :class:`Transport`, optional
        The transport to use for publishing. If not provided, the default transport will be used.
    """

    def __init__(self, topic, transport=None):
        self.topic = topic if isinstance(topic, Topic) else Topic(topic)
        self.transport = transport or get_default_transport()
        self._advertise_id = None

    @property
    def is_advertised(self):
        """Indicate if the publisher has announced its topic as advertised or not.

        Returns
        -------
        bool
            True if advertised as publisher of this topic, False otherwise.
        """
        return self._advertise_id is not None

    def message_published(self, message):
        """Handler called when a message has been published."""
        pass

    def publish(self, message):
        """Publish a message to the topic.

        Parameters
        ----------
        message : :class:`Message` or dict
            The message to publish.
        """
        # TODO: check if message type matches self.topic.message_type declared
        if not self.is_advertised:
            self.advertise()

        self.transport.publish(self.topic, message)
        self.message_published(message)

    def advertise(self):
        """Advertise the publisher for the topic."""
        if self.is_advertised:
            return

        self._advertise_id = self.transport.advertise(self.topic)

    def unadvertise(self):
        """Unadvertise the publisher for the topic."""
        if not self.is_advertised:
            return

        self.transport.unadvertise(self.topic)
        self._advertise_id = None


class Subscriber(object):
    """Subscriber for a specific topic.

    Parameters
    ----------
    topic : :class:`Topic` or str
        The topic to subscribe to. If a string is provided, a new topic instance
        will be created using the string as topic name.
    transport : :class:`Transport`, optional
        The transport to use for subscribing. If not provided, the default transport will be used.
    """

    def __init__(self, topic, callback=None, transport=None):
        self.transport = transport or get_default_transport()
        self.topic = topic if isinstance(topic, Topic) else Topic(topic)
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


class EchoSubscriber(Subscriber):
    """Simple subscriber that prints received messages on the console (ie. `stdout`).

    Parameters
    ----------
    topic : :class:`Topic` or str
        The topic to subscribe to. If a string is provided, a new topic instance
        will be created using the string as topic name.
    """

    def __init__(self, topic, transport=None):
        super(EchoSubscriber, self).__init__(topic, callback=self.echo, transport=transport)

    def echo(self, message):
        """Print received messages to the console."""
        print(str(message))
