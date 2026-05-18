from threading import Event

import pytest

from compas_eve import InMemoryTransport
from compas_eve import Message
from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve import set_default_transport


def test_default_transport_publishing():
    set_default_transport(InMemoryTransport())
    event = Event()
    topic = Topic("/messages_compas_eve_test/", Message)

    Subscriber(topic, lambda m: event.set()).subscribe()
    Publisher(topic).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"


def test_pubsub():
    tx = InMemoryTransport()
    event = Event()
    topic = Topic("/messages_compas_eve_test/", Message)

    Subscriber(topic, lambda m: event.set(), transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"


def test_two_subs():
    tx = InMemoryTransport()
    event1 = Event()
    event2 = Event()
    topic = Topic("/messages_compas_eve_test/", Message)

    Subscriber(topic, lambda m: event1.set(), transport=tx).subscribe()
    Subscriber(topic, lambda m: event2.set(), transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(Message(done=True))

    received1 = event1.wait(timeout=1)
    received2 = event2.wait(timeout=1)
    assert received1, "Message 1 not received"
    assert received2, "Message 2 not received"


def test_unsub():
    tx = InMemoryTransport()
    topic = Topic("/messages_compas_eve_test/", Message)

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

    received = result["event"].wait(timeout=0.1)
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

    tx = InMemoryTransport()
    topic = Topic("/messages_compas_eve_test/", TestMessage)

    Subscriber(topic, callback, transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(TestMessage(name="Jazz"))

    received = result["event"].wait(timeout=3)
    assert received, "Message not received"
    assert result["value"].name == "Jazz"
    assert result["value"].hello_name == "Hello Jazz"


def test_message_str():
    msg = Message(a=3)
    assert str(msg) == "{'a': 3}"


def test_retain_delivers_to_late_subscriber():
    tx = InMemoryTransport()
    topic = Topic("/messages_compas_eve_test/retain/", Message)

    Publisher(topic, transport=tx).publish(Message(value=42), retain=True)

    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg.value
        result["event"].set()

    Subscriber(topic, callback, transport=tx).subscribe()

    received = result["event"].wait(timeout=1)
    assert received, "Retained message not delivered to late subscriber"
    assert result["value"] == 42


def test_retain_last_message_wins():
    tx = InMemoryTransport()
    topic = Topic("/messages_compas_eve_test/retain_last/", Message)
    pub = Publisher(topic, transport=tx)

    pub.publish(Message(value=1), retain=True)
    pub.publish(Message(value=2), retain=True)

    result = dict(value=None, event=Event())

    def callback(msg):
        result["value"] = msg.value
        result["event"].set()

    Subscriber(topic, callback, transport=tx).subscribe()

    received = result["event"].wait(timeout=1)
    assert received, "Retained message not delivered"
    assert result["value"] == 2


def test_no_retain_does_not_deliver_to_late_subscriber():
    tx = InMemoryTransport()
    topic = Topic("/messages_compas_eve_test/no_retain/", Message)

    Publisher(topic, transport=tx).publish(Message(value=42))

    event = Event()
    Subscriber(topic, lambda m: event.set(), transport=tx).subscribe()

    received = event.wait(timeout=0.2)
    assert not received, "Non-retained message should not be delivered to late subscriber"


def test_unknown_option_raises():
    tx = InMemoryTransport()
    topic = Topic("/messages_compas_eve_test/bad_option/", Message)

    with pytest.raises(TypeError):
        Publisher(topic, transport=tx).publish(Message(value=1), unknown_flag=True)
