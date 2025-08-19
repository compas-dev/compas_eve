from threading import Event

from compas_eve import Message
from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve import set_default_transport

try:
    from compas_eve import ZeroMQTransport
    ZEROMQ_AVAILABLE = True
except ImportError:
    ZEROMQ_AVAILABLE = False

import pytest


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_zeromq_import():
    """Test that ZeroMQ transport can be imported."""
    assert ZeroMQTransport is not None


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_default_transport_publishing():
    set_default_transport(ZeroMQTransport("inproc://test1"))
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_default_transport_publishing/", Message)

    Subscriber(topic, lambda m: event.set()).subscribe()
    Publisher(topic).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_pubsub():
    tx = ZeroMQTransport("inproc://test2")
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_pubsub/", Message)

    Subscriber(topic, lambda m: event.set(), transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"
    
    tx.close()


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_two_subs():
    tx = ZeroMQTransport("inproc://test3")
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
    
    tx.close()


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_unsub():
    tx = ZeroMQTransport("inproc://test4")
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

    received = result["event"].wait(timeout=1)
    assert received is False, "Second message received but it should have been unsubscribed"
    assert result["count"] == 1, "Did not unsubscribe properly"
    assert len(list(tx._local_callbacks.keys())) == 0, "Internal callback reference should have been released"
    
    tx.close()


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_message_type_parsing():
    tx = ZeroMQTransport("inproc://test5")
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_message_type_parsing/", Message)

    result = {}

    def callback(msg):
        result["message"] = msg
        event.set()

    Subscriber(topic, callback, transport=tx).subscribe()
    Publisher(topic, transport=tx).publish(Message(name="Compas Eve", done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"
    assert result["message"].name == "Compas Eve"
    assert result["message"].done is True
    
    tx.close()


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_dict_as_message():
    tx = ZeroMQTransport("inproc://test6")
    event = Event()
    topic = Topic("/messages_compas_eve_test/test_dict_as_message/", Message)

    result = {}

    def callback(msg):
        result["message"] = msg
        event.set()

    Subscriber(topic, callback, transport=tx).subscribe()
    Publisher(topic, transport=tx).publish({"name": "Compas Eve", "done": True})

    received = event.wait(timeout=3)
    assert received, "Message not received"
    assert result["message"].name == "Compas Eve"
    assert result["message"].done is True
    
    tx.close()