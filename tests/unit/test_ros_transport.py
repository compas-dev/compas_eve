import importlib
import sys
import types

import pytest

from compas_eve import Message
from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic


class FakeRos:
    def __init__(self, host, port, **options):
        self.host = host
        self.port = port
        self.options = options
        self.run_timeout = None
        self.terminated = False

    def run(self, timeout):
        self.run_timeout = timeout

    def on_ready(self, callback):
        callback()

    def terminate(self):
        self.terminated = True


class FakeRosMessage(dict):
    pass


class FakeRosTopic:
    def __init__(self, client, name, message_type, **options):
        self.client = client
        self.name = name
        self.message_type = message_type
        self.options = options
        self.messages = []
        self.callback = None
        self.is_advertised = False
        self.unsubscribe_count = 0

    def advertise(self):
        self.is_advertised = True

    def unadvertise(self):
        self.is_advertised = False

    def publish(self, message):
        self.messages.append(message)

    def subscribe(self, callback):
        self.callback = callback

    def unsubscribe(self):
        self.unsubscribe_count += 1
        self.callback = None

    def receive(self, message):
        self.callback(message)


@pytest.fixture
def RosTransport(monkeypatch):
    fake_roslibpy = types.ModuleType("roslibpy")
    fake_roslibpy.Ros = FakeRos
    fake_roslibpy.Message = FakeRosMessage
    fake_roslibpy.Topic = FakeRosTopic
    monkeypatch.setitem(sys.modules, "roslibpy", fake_roslibpy)
    sys.modules.pop("compas_eve.ros", None)
    sys.modules.pop("compas_eve.ros.ros_transport", None)
    module = importlib.import_module("compas_eve.ros")
    yield module.RosTransport
    sys.modules.pop("compas_eve.ros", None)
    sys.modules.pop("compas_eve.ros.ros_transport", None)


def test_constructor_connects_to_rosbridge(RosTransport):
    transport = RosTransport("robot.local", 9091, connect_timeout=4, is_secure=True)

    assert transport.client.host == "robot.local"
    assert transport.client.port == 9091
    assert transport.client.options == {"is_secure": True}
    assert transport.client.run_timeout == 4


def test_publish_uses_native_ros_type_and_topic_options(RosTransport):
    transport = RosTransport()
    topic = Topic(
        "/chatter",
        "std_msgs/String",
        compression="none",
        latch=True,
        throttle_rate=20,
        queue_size=5,
        queue_length=2,
        reconnect_on_close=False,
    )

    Publisher(topic, transport=transport).publish(Message(data="hello"))

    ros_topic = transport._publishers[topic.name]
    assert ros_topic.message_type == "std_msgs/String"
    assert ros_topic.options == {
        "compression": "none",
        "latch": True,
        "throttle_rate": 20,
        "queue_size": 5,
        "queue_length": 2,
        "reconnect_on_close": False,
    }
    assert ros_topic.is_advertised
    assert ros_topic.messages == [{"data": "hello"}]


def test_multiple_local_subscribers_share_ros_subscription(RosTransport):
    transport = RosTransport()
    topic = Topic("/chatter", "std_msgs/String")
    received_a = []
    received_b = []
    subscriber_a = Subscriber(topic, received_a.append, transport=transport)
    subscriber_b = Subscriber(topic, received_b.append, transport=transport)

    subscriber_a.subscribe()
    subscriber_b.subscribe()
    ros_topic = transport._subscribers[topic.name]
    ros_topic.receive({"data": "first"})
    subscriber_a.unsubscribe()
    ros_topic.receive({"data": "second"})

    assert received_a == [{"data": "first"}]
    assert received_b == [{"data": "first"}, {"data": "second"}]
    assert ros_topic.unsubscribe_count == 0

    subscriber_b.unsubscribe()
    assert ros_topic.unsubscribe_count == 1


def test_ros_topic_requires_native_message_type(RosTransport):
    transport = RosTransport()

    with pytest.raises(TypeError, match="ROS message type string"):
        transport.advertise(Topic("/chatter"))


def test_ros_topic_rejects_unknown_options(RosTransport):
    transport = RosTransport()

    with pytest.raises(TypeError, match="unknown"):
        transport.advertise(Topic("/chatter", "std_msgs/String", unknown=True))


def test_close_cleans_up_topics_and_client(RosTransport):
    transport = RosTransport()
    topic = Topic("/chatter", "std_msgs/String")
    Publisher(topic, transport=transport).advertise()
    Subscriber(topic, lambda message: None, transport=transport).subscribe()

    transport.close()

    assert not transport._publishers[topic.name].is_advertised
    assert transport._subscribers[topic.name].unsubscribe_count == 1
    assert transport.client.terminated
