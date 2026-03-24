from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Type
from typing import Union


DEFAULT_TRANSPORT = None


def get_default_transport() -> Optional["Transport"]:
    """Retrieve the default transport implementation to be used system-wide.

    Returns
    -------
    Transport
        Instance of a transport class. By default, `compas_eve` uses
        [InMemoryTransport][compas_eve.memory.InMemoryTransport].
    """
    return DEFAULT_TRANSPORT


def set_default_transport(transport: Optional["Transport"]) -> None:
    """Assign a default transport implementation to be used system-wide.

    Parameters
    ----------
    transport
        Instance of a transport class. By default, `compas_eve` uses
        [InMemoryTransport][compas_eve.memory.InMemoryTransport].
    """
    global DEFAULT_TRANSPORT
    DEFAULT_TRANSPORT = transport


class Transport(object):
    """Defines the base interface for different transport implementations.

    Parameters
    ----------
    codec
        The codec to use for encoding and decoding messages.
        If not provided, defaults to [JsonMessageCodec][compas_eve.codecs.JsonMessageCodec].
    """

    def __init__(self, codec: Optional[Any] = None, *args: Any, **kwargs: Any) -> None:
        super(Transport, self).__init__(*args, **kwargs)
        from compas_eve.codecs import JsonMessageCodec

        self._id_counter = 0
        if codec is None:
            codec = JsonMessageCodec()
        self.codec = codec

    @property
    def id_counter(self) -> int:
        """Generate an auto-incremental ID starting from 1."""
        self._id_counter += 1
        return self._id_counter

    def publish(self, topic: "Topic", message: Union["Message", dict]) -> None:
        pass

    def subscribe(self, topic: "Topic", callback: Callable) -> Optional[str]:
        pass

    def unsubscribe(self, topic: "Topic") -> None:
        pass

    def advertise(self, topic: "Topic") -> Optional[str]:
        pass

    def unadvertise(self, topic: "Topic") -> None:
        pass


class Message(object):
    """Message objects used for publishing and subscribing to/from topics.

    A message is fundamentally a dictionary and behaves as one."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Message, self).__init__()
        self.data = {}
        self.data.update(*args, **kwargs)

    def ToString(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.data)

    def __getattr__(self, name: str) -> Any:
        return self.data[name]

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "data" or key in self.__dict__:
            super(Message, self).__setattr__(key, value)
        else:
            self.data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    def __jsondump__(self, minimal: bool = False) -> Dict[str, Any]:
        return self.data

    @classmethod
    def parse(cls, value: Dict[str, Any]) -> "Message":
        instance = cls(**value)
        return instance


class Topic(object):
    """A topic is like a mailbox where messages can be sent and received.

    Topics are described by a name, a type of message they accept, and a
    set of options.

    Attributes
    ----------
    name
        Name of the topic.
    message_type
        Class defining the message structure. Use [Message][] for
        a generic, non-typed checked message implementation.
        Defaults to [Message][].
    options
        A dictionary of options.
    """

    # TODO: Add documentation/examples of possible options

    def __init__(self, name: str, message_type: Optional[Type[Message]] = None, **options: Any) -> None:
        self.name = name
        self.message_type = message_type or Message
        self.options = options


class Publisher(object):
    """Publisher for a specific topic.

    Parameters
    ----------
    topic
        The topic to publish messages to. If a string is provided, a new topic instance
        will be created using the string as topic name.
    transport
        The transport to use for publishing. If not provided, the default transport will be used.
    """

    def __init__(self, topic: Union[Topic, str], transport: Optional[Transport] = None) -> None:
        self.topic = topic if isinstance(topic, Topic) else Topic(topic)
        self.transport = transport or get_default_transport()
        self._advertise_id = None

    @property
    def is_advertised(self) -> bool:
        """Indicate if the publisher has announced its topic as advertised or not.

        Returns
        -------
        bool
            True if advertised as publisher of this topic, False otherwise.
        """
        return self._advertise_id is not None

    def message_published(self, message: Union[Message, dict]) -> None:
        """Handler called when a message has been published."""
        pass

    def publish(self, message: Union[Message, dict]) -> None:
        """Publish a message to the topic.

        Parameters
        ----------
        message
            The message to publish.
        """
        # TODO: check if message type matches self.topic.message_type declared
        if not self.is_advertised:
            self.advertise()

        self.transport.publish(self.topic, message)
        self.message_published(message)

    def advertise(self) -> None:
        """Advertise the publisher for the topic."""
        if self.is_advertised:
            return

        self._advertise_id = self.transport.advertise(self.topic)

    def unadvertise(self) -> None:
        """Unadvertise the publisher for the topic."""
        if not self.is_advertised:
            return

        self.transport.unadvertise(self.topic)
        self._advertise_id = None


class Subscriber(object):
    """Subscriber for a specific topic.

    Parameters
    ----------
    topic
        The topic to subscribe to. If a string is provided, a new topic instance
        will be created using the string as topic name.
    transport
        The transport to use for subscribing. If not provided, the default transport will be used.
    """

    def __init__(self, topic: Union[Topic, str], callback: Optional[Callable] = None, transport: Optional[Transport] = None) -> None:
        self.transport = transport or get_default_transport()
        self.topic = topic if isinstance(topic, Topic) else Topic(topic)
        self._subscribe_id = None
        self._callback = callback

    def message_received(self, message: Union[Message, dict]) -> None:
        """Handler called whenever a new message is received.

        By default, this implementation will simply invoke the callback
        used on init (if any), but sub-classes can override this behavior."""
        if self._callback:
            self._callback(message)

    @property
    def is_subscribed(self) -> bool:
        """Indicate if the instace is currently subscribed to its topic or not."""
        return self._subscribe_id is not None

    def subscribe(self) -> None:
        if self._subscribe_id:
            return

        self._subscribe_id = self.transport.subscribe(self.topic, self.message_received)

    def unsubscribe(self) -> None:
        """Unregister the subscriber from its topic."""
        if not self._subscribe_id:
            return

        self.transport.unsubscribe_by_id(self._subscribe_id)
        self._subscribe_id = None


class EchoSubscriber(Subscriber):
    """Simple subscriber that prints received messages on the console (ie. `stdout`).

    Parameters
    ----------
    topic
        The topic to subscribe to. If a string is provided, a new topic instance
        will be created using the string as topic name.
    """

    def __init__(self, topic: Union[Topic, str], transport: Optional[Transport] = None) -> None:
        super(EchoSubscriber, self).__init__(topic, callback=self.echo, transport=transport)

    def echo(self, message: Union[Message, dict]) -> None:
        """Print received messages to the console."""
        print(str(message))
