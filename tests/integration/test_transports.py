import time
from threading import Event

import pytest
from compas.datastructures import Graph
from compas.geometry import Frame

from compas_eve import Message
from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve import set_default_transport
from compas_eve.mqtt import MqttTransport

try:
    from compas_eve.zenoh import ZenohTransport
except ImportError:
    ZenohTransport = None

HOST = "localhost"


@pytest.fixture(params=["mqtt", "zenoh"])
def tx(request):
    if request.param == "mqtt":
        tx = MqttTransport(HOST)
    elif request.param == "zenoh":
        if ZenohTransport is None:
            pytest.skip("zenoh not installed")
        tx = ZenohTransport()
    yield tx
    if hasattr(tx, "close"):
        tx.close()


def test_client_id():
    custom_client_id = "my_custom_client_id"
    transport = MqttTransport(HOST, client_id=custom_client_id)
    assert transport.client._client_id == custom_client_id.encode("utf-8")
    transport.close()

    transport = MqttTransport(HOST, client_id=None)
    assert transport.client._client_id.startswith("compas_eve_".encode("utf-8"))
    transport.close()


def test_default_transport_publishing(tx):
    set_default_transport(tx)
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_default_transport_publishing/", Message)

    Subscriber(topic, lambda m: event.set()).subscribe()
    time.sleep(0.1)
    Publisher(topic).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"


def test_pubsub(tx):
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_pubsub/", Message)

    Subscriber(topic, lambda m: event.set(), transport=tx).subscribe()
    time.sleep(0.1)
    Publisher(topic, transport=tx).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"


def test_two_subs(tx):
    event1 = Event()
    event2 = Event()
    topic = Topic("/messages_compas_eve_test/test_two_subs/", Message)

    Subscriber(topic, lambda m: event1.set(), transport=tx).subscribe()
    Subscriber(topic, lambda m: event2.set(), transport=tx).subscribe()
    time.sleep(0.1)
    Publisher(topic, transport=tx).publish(Message(done=True))

    received1 = event1.wait(timeout=3)
    received2 = event2.wait(timeout=3)
    assert received1, "Message 1 not received"
    assert received2, "Message 2 not received"


def test_unsub(tx):
    topic = Topic("/messages_compas_eve_test/test_unsub/", Message)

    result = dict(count=0, event=Event())

    def callback(msg):
        result["count"] += 1
        result["event"].set()

    pub = Publisher(topic, transport=tx)
    sub = Subscriber(topic, callback, transport=tx)

    sub.subscribe()
    time.sleep(0.1)
    pub.publish(Message(done=True))
    received = result["event"].wait(timeout=3)
    assert received, "First message not received"
    assert len(list(tx._local_callbacks.keys())) == 1, "Internal callback reference should have been kept"

    result["event"].clear()
    sub.unsubscribe()
    time.sleep(0.1)
    pub.publish(Message(done=True))

    received = result["event"].wait(timeout=1)
    assert received is False, "Second message received but it should have been unsubscribed"
    assert result["count"] == 1, "Did not unsubscribe properly"
    assert len(list(tx._local_callbacks.keys())) == 0, "Internal callback reference should have been released"


def test_message_type_parsing(tx):
    class TestMessage(Message):
        @property
        def hello_name(self):
            return "Hello {}".format(self.name)

    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg
        result["event"].set()

    topic = Topic("/messages_compas_eve_test/test_message_type_parsing/", TestMessage)

    Subscriber(topic, callback, transport=tx).subscribe()
    time.sleep(0.1)
    Publisher(topic, transport=tx).publish(TestMessage(name="Jazz"))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"]["name"] == "Jazz", "Messages should be accessible as dict"
    assert result["value"].hello_name == "Hello Jazz"


def test_compas_data_as_message(tx):
    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg
        result["event"].set()

    topic = Topic("/messages_compas_eve_test/test_compas_data_as_message/")

    Subscriber(topic, callback, transport=tx).subscribe()
    time.sleep(0.1)
    Publisher(topic, transport=tx).publish(dict(frame=Frame.worldXY(), graph=Graph()))

    assert result is not None, "No result?"
    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"]["frame"] == Frame.worldXY()
    assert isinstance(result["value"]["graph"], Graph)


def test_nested_message_types(tx):
    class Header(Message):
        def __init__(self, sequence_id=None):
            super(Header, self).__init__()
            self["sequence_id"] = sequence_id

    class DataTestMessage(Message):
        def __init__(self, name=None, location=None, header=None):
            super(DataTestMessage, self).__init__()
            self["name"] = name
            self["location"] = location
            self["header"] = header or Header(1)

        @classmethod
        def parse(cls, value):
            return cls(
                name=value["name"],
                location=value["location"],
                header=Header(**value["header"]),
            )

    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg
        result["event"].set()

    topic = Topic("/messages_compas_eve_test/test_nested_message_types/", DataTestMessage)

    Subscriber(topic, callback, transport=tx).subscribe()
    time.sleep(0.1)
    Publisher(topic, transport=tx).publish(DataTestMessage(name="Jazz", location=1.334))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"].location == 1.334
    assert result["value"].header.sequence_id == 1


def test_dict_as_message(tx):
    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg
        result["event"].set()

    topic = Topic("/messages_compas_eve_test/test_dict_as_message/", Message)

    Subscriber(topic, callback, transport=tx).subscribe()
    time.sleep(0.1)
    Publisher(topic, transport=tx).publish(dict(name="Jazz"))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"]["name"] == "Jazz", "Messages should be accessible as dict"
