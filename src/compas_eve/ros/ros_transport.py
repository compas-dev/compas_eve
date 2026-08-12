from typing import Any
from typing import Callable
from typing import Dict
from typing import Tuple
from typing import Union

import roslibpy

from ..core import Message
from ..core import Topic
from ..core import Transport


class RosTransport(Transport):
    """ROS transport backed by a rosbridge WebSocket connection.

    Messages use native ROS message types and are represented as JSON-compatible
    dictionaries, matching the behavior of [roslibpy](https://roslibpy.readthedocs.io/).

    Parameters
    ----------
    host
        Host name of the rosbridge server.
    port
        WebSocket port of the rosbridge server. Defaults to ``9090``.
    connect_timeout
        Maximum number of seconds to wait for the initial connection.
    **client_options
        Additional options passed to ``roslibpy.Ros``.

    Notes
    -----
    The topic's ``message_type`` must be a ROS message type string, such as
    ``"std_msgs/String"``. ROS topic options can be passed to [Topic][]:
    ``compression``, ``latch``, ``throttle_rate``, ``queue_size``,
    ``queue_length``, and ``reconnect_on_close``.
    """

    _TOPIC_OPTION_DEFAULTS = {
        "compression": None,
        "latch": False,
        "throttle_rate": 0,
        "queue_size": 100,
        "queue_length": 0,
        "reconnect_on_close": True,
    }

    def __init__(self, host: str = "localhost", port: int = 9090, connect_timeout: float = 10, **client_options: Any) -> None:
        super(RosTransport, self).__init__()
        self.host = host
        self.port = port
        self.client = roslibpy.Ros(host=host, port=port, **client_options)
        self._publishers: Dict[str, roslibpy.Topic] = {}
        self._subscribers: Dict[str, roslibpy.Topic] = {}
        self._topic_configs: Dict[str, Tuple[Any, ...]] = {}
        self._subscriptions: Dict[str, Dict[str, Callable]] = {}
        self._subscription_handlers: Dict[str, Callable] = {}
        self._local_callbacks: Dict[str, Tuple[str, Callable]] = {}
        self._advertised_topics = set()
        self.client.run(timeout=connect_timeout)

    def _topic_config(self, topic: Topic) -> Tuple[str, Dict[str, Any], Tuple[Any, ...]]:
        if not isinstance(topic.message_type, str):
            raise TypeError("RosTransport topics require a ROS message type string, e.g. Topic('/chatter', 'std_msgs/String')")

        unknown_options = set(topic.options) - set(self._TOPIC_OPTION_DEFAULTS)
        if unknown_options:
            raise TypeError("Unsupported ROS topic options: {}".format(", ".join(sorted(unknown_options))))

        options = dict(self._TOPIC_OPTION_DEFAULTS)
        options.update(topic.options)
        config_key = (topic.message_type,) + tuple(options[name] for name in self._TOPIC_OPTION_DEFAULTS)
        return topic.message_type, options, config_key

    def _get_topic(self, topic: Topic, topics: Dict[str, roslibpy.Topic]) -> roslibpy.Topic:
        message_type, options, config_key = self._topic_config(topic)
        existing_config = self._topic_configs.get(topic.name)
        if existing_config is not None and existing_config != config_key:
            raise ValueError("ROS topic {!r} is already configured with different message type or options".format(topic.name))

        existing = topics.get(topic.name)
        if existing is not None:
            return existing

        ros_topic = roslibpy.Topic(self.client, topic.name, message_type, **options)
        topics[topic.name] = ros_topic
        self._topic_configs[topic.name] = config_key
        return ros_topic

    def on_ready(self, callback: Callable) -> None:
        """Invoke a callback when the rosbridge connection is ready."""
        self.client.on_ready(callback)

    def publish(self, topic: Topic, message: Union[Message, dict], **options: Any) -> None:
        """Publish a native ROS message dictionary to a topic."""
        if options:
            raise TypeError("publish() got unexpected options for RosTransport: {}".format(", ".join(options)))

        if isinstance(message, Message):
            values = message.data
        elif isinstance(message, dict):
            values = message
        else:
            raise TypeError("RosTransport messages must be dictionaries or compas_eve.Message instances")

        self._get_topic(topic, self._publishers).publish(roslibpy.Message(values))

    def subscribe(self, topic: Topic, callback: Callable) -> str:
        """Subscribe to a native ROS topic."""
        ros_topic = self._get_topic(topic, self._subscribers)
        subscribe_id = "subscribe:{}:{}".format(topic.name, self.id_counter)
        callbacks = self._subscriptions.get(topic.name)

        if callbacks is None:
            callbacks = {subscribe_id: callback}

            def _ros_callback(message: Dict[str, Any]) -> None:
                for local_callback in list(callbacks.values()):
                    local_callback(message)

            self._subscriptions[topic.name] = callbacks
            self._subscription_handlers[topic.name] = _ros_callback
            self._local_callbacks[subscribe_id] = (topic.name, callback)
            try:
                ros_topic.subscribe(_ros_callback)
            except Exception:
                del self._subscriptions[topic.name]
                del self._subscription_handlers[topic.name]
                del self._local_callbacks[subscribe_id]
                raise
        else:
            callbacks[subscribe_id] = callback
            self._local_callbacks[subscribe_id] = (topic.name, callback)
        return subscribe_id

    def unsubscribe_by_id(self, subscribe_id: str) -> None:
        """Unsubscribe one callback using its subscription identifier."""
        if subscribe_id not in self._local_callbacks:
            return

        topic_name, _callback = self._local_callbacks.pop(subscribe_id)
        callbacks = self._subscriptions[topic_name]
        del callbacks[subscribe_id]

        if not callbacks:
            self._subscribers[topic_name].unsubscribe()
            del self._subscriptions[topic_name]
            del self._subscription_handlers[topic_name]

    def unsubscribe(self, topic: Topic) -> None:
        """Unsubscribe all local callbacks from a topic."""
        callbacks = self._subscriptions.pop(topic.name, None)
        if callbacks is None:
            return

        self._subscribers[topic.name].unsubscribe()
        self._subscription_handlers.pop(topic.name, None)
        for subscribe_id in list(callbacks):
            self._local_callbacks.pop(subscribe_id, None)

    def advertise(self, topic: Topic) -> str:
        """Advertise a native ROS topic."""
        self._get_topic(topic, self._publishers).advertise()
        self._advertised_topics.add(topic.name)
        return "advertise:{}:{}".format(topic.name, self.id_counter)

    def unadvertise(self, topic: Topic) -> None:
        """Stop advertising a native ROS topic."""
        if topic.name not in self._advertised_topics:
            return
        self._publishers[topic.name].unadvertise()
        self._advertised_topics.remove(topic.name)

    def close(self) -> None:
        """Close all topics and terminate the rosbridge client."""
        for topic_name in list(self._subscriptions):
            self._subscribers[topic_name].unsubscribe()
        for topic_name in list(self._advertised_topics):
            self._publishers[topic_name].unadvertise()
        self._subscriptions.clear()
        self._subscription_handlers.clear()
        self._local_callbacks.clear()
        self._advertised_topics.clear()
        self.client.terminate()
