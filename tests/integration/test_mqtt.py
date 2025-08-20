from threading import Event

from compas.data import Data

from compas_eve import Message
from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve import set_default_transport
from compas_eve.mqtt import MqttTransport

HOST = "localhost"


def test_client_id():
    custom_client_id = "my_custom_client_id"
    transport = MqttTransport(HOST, client_id=custom_client_id)
    assert transport.client._client_id == custom_client_id.encode("utf-8")

    transport = MqttTransport(HOST, client_id=None)
    assert transport.client._client_id.startswith("compas_eve_".encode("utf-8"))


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
    assert result["value"]["name"] == "Jazz", "Messages should be accessible as dict"
    assert result["value"].hello_name == "Hello Jazz"


def test_compas_data_as_message():

    class Header(Data):
        def __init__(self, sequence_id=None):
            super(Header, self).__init__()
            self.sequence_id = sequence_id

        @property
        def __data__(self):
            return {"sequence_id": self.sequence_id}

    class DataTestMessage(Data):
        def __init__(self, name=None, location=None, header=None):
            super(DataTestMessage, self).__init__()
            self.name = name
            self.location = location
            self.header = header or Header(1)

        @property
        def __data__(self):
            return {"name": self.name, "location": self.location, "header": self.header.__data__}

        @classmethod
        def __from_data__(cls, data):
            return cls(
                name=data["name"],
                location=data["location"],
                header=Header.__from_data__(data["header"]),
            )

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
    Publisher(topic, transport=tx).publish(DataTestMessage(name="Jazz", location=1.334))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"].location == 1.334
    assert result["value"].header.sequence_id == 1


def test_nested_message_types():

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

    tx = MqttTransport(HOST)
    topic = Topic("/messages_compas_eve_test/test_nested_message_types/", DataTestMessage)

    Subscriber(topic, callback, transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(DataTestMessage(name="Jazz", location=1.334))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"].location == 1.334
    assert result["value"].header.sequence_id == 1


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
    assert result["value"]["name"] == "Jazz", "Messages should be accessible as dict"
