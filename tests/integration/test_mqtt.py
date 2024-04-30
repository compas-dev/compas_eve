from threading import Event

from compas.data import Data

from compas_eve import Message
from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve import set_default_transport
from compas_eve.mqtt import MqttTransport

HOST = "broker.hivemq.com"


def test_default_transport_publishing():
    set_default_transport(MqttTransport(HOST))
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_default_transport_publishing/", Message)

    Subscriber(topic, lambda m: event.set()).subscribe()
    Publisher(topic).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"


def test_pubsub():
    tx = MqttTransport(HOST)
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_pubsub/", Message)

    Subscriber(topic, lambda m: event.set(), transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"


def test_two_subs():
    tx = MqttTransport(HOST)
    event1 = Event()
    event2 = Event()
    topic = Topic("/messages_compas_eve_test/test_two_subs/", Message)

    Subscriber(topic, lambda m: event1.set(), transport=tx).subscribe()
    Subscriber(topic, lambda m: event2.set(), transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(Message(done=True))

    received1 = event1.wait(timeout=2)
    received2 = event2.wait(timeout=2)
    assert received1, "Message 1 not received"
    assert received2, "Message 2 not received"


def test_unsub():
    tx = MqttTransport(HOST)
    topic = Topic("/messages_compas_eve_test/test_unsub/", Message)

    result = dict(count=0, event=Event())

    def callback(msg):
        result["count"] += 1
        result["event"].set()

    pub = Publisher(topic, transport=tx)
    sub = Subscriber(topic, callback, transport=tx)

    sub.subscribe()
    pub.publish(Message(done=True))
    received = result["event"].wait(timeout=3)
    assert received, "First message not received"
    assert len(list(tx._local_callbacks.keys())) == 1, "Internal callback reference should have been kept"

    result["event"].clear()
    sub.unsubscribe()
    pub.publish(Message(done=True))

    received = result["event"].wait(timeout=3)
    assert received is False, "Second message received but it should have been unsubscribed"
    assert result["count"] == 1, "Did not unsubscribe properly"
    assert len(list(tx._local_callbacks.keys())) == 0, "Internal callback reference should have been released"


def test_message_type_parsing():
    class TestMessage(Message):
        @property
        def hello_name(self):
            return "Hello {}".format(self.name)

    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg
        result["event"].set()

    tx = MqttTransport(HOST)
    topic = Topic("/messages_compas_eve_test/test_message_type_parsing/", TestMessage)

    Subscriber(topic, callback, transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(TestMessage(name="Jazz"))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"].hello_name == "Hello Jazz"


def test_compas_data_as_message():

    class DataTestMessage(Data):
        def __init__(self, name=None, eclipse=None):
            self.name = name
            self.eclipse = eclipse

        def __to_data__(self):
            return {"name": self.name, "eclipse": self.eclipse}

        @classmethod
        def parse(cls, value):
            return cls.__from_data__(value)

    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg
        result["event"].set()

    tx = MqttTransport(HOST)
    topic = Topic("/messages_compas_eve_test/test_compas_data_as_message/", DataTestMessage)

    Subscriber(topic, callback, transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(DataTestMessage(name="Jazz", eclipse=1.334))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"].eclipse == 1.334


def test_dict_as_message():
    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg
        result["event"].set()

    tx = MqttTransport(HOST)
    topic = Topic("/messages_compas_eve_test/test_dict_as_message/", Message)

    Subscriber(topic, callback, transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(dict(name="Jazz"))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
