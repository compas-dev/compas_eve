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
def test_zeromq_tcp_pubsub():
    """Test ZeroMQ transport with TCP endpoints."""
    tx = ZeroMQTransport("tcp://localhost:25555")
    event = Event()
    topic = Topic("/messages_compas_eve_test/tcp_pubsub/", Message)

    Subscriber(topic, lambda m: event.set(), transport=tx).subscribe()
    
    # Small delay to ensure subscriber is ready
    import time
    time.sleep(0.1)
    
    Publisher(topic, transport=tx).publish(Message(done=True))

    received = event.wait(timeout=3)
    assert received, "Message not received"
    
    tx.close()


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_zeromq_tcp_message_content():
    """Test that message content is preserved correctly with TCP transport."""
    tx = ZeroMQTransport("tcp://localhost:25556")
    event = Event()
    topic = Topic("/messages_compas_eve_test/tcp_content/", Message)

    result = {}

    def callback(msg):
        result["message"] = msg
        event.set()

    Subscriber(topic, callback, transport=tx).subscribe()
    
    # Small delay to ensure subscriber is ready
    import time
    time.sleep(0.1)
    
    test_message = Message(
        name="ZeroMQ Test", 
        value=42, 
        nested={"key": "value", "list": [1, 2, 3]}
    )
    Publisher(topic, transport=tx).publish(test_message)

    received = event.wait(timeout=3)
    assert received, "Message not received"
    assert result["message"].name == "ZeroMQ Test"
    assert result["message"].value == 42
    assert result["message"].nested["key"] == "value"
    assert result["message"].nested["list"] == [1, 2, 3]
    
    tx.close()


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available") 
def test_zeromq_tcp_multiple_topics():
    """Test that multiple topics work correctly with TCP transport."""
    tx = ZeroMQTransport("tcp://localhost:25557")
    
    topic1 = Topic("/test/topic1", Message)
    topic2 = Topic("/test/topic2", Message)
    
    event1 = Event()
    event2 = Event()
    
    result = {}
    
    def callback1(msg):
        result["topic1"] = msg
        event1.set()
        
    def callback2(msg):
        result["topic2"] = msg 
        event2.set()

    # Subscribe to both topics
    Subscriber(topic1, callback1, transport=tx).subscribe()
    Subscriber(topic2, callback2, transport=tx).subscribe()
    
    # Small delay to ensure subscribers are ready
    import time
    time.sleep(0.1)
    
    # Publish to topic1
    Publisher(topic1, transport=tx).publish(Message(source="topic1"))
    
    # Publish to topic2  
    Publisher(topic2, transport=tx).publish(Message(source="topic2"))

    received1 = event1.wait(timeout=3)
    received2 = event2.wait(timeout=3)
    
    assert received1, "Message 1 not received"
    assert received2, "Message 2 not received"
    assert result["topic1"].source == "topic1"
    assert result["topic2"].source == "topic2"
    
    tx.close()


@pytest.mark.skipif(not ZEROMQ_AVAILABLE, reason="ZeroMQ transport not available")
def test_zeromq_tcp_unsubscribe():
    """Test unsubscribe functionality with TCP transport."""
    tx = ZeroMQTransport("tcp://localhost:25558") 
    topic = Topic("/test/unsub", Message)

    result = dict(count=0, event=Event())

    def callback(msg):
        result["count"] += 1
        result["event"].set()

    sub = Subscriber(topic, callback, transport=tx)
    pub = Publisher(topic, transport=tx)

    # Subscribe and receive first message
    sub.subscribe()
    
    # Small delay to ensure subscriber is ready
    import time
    time.sleep(0.1)
    
    pub.publish(Message(seq=1))
    
    received = result["event"].wait(timeout=3)
    assert received, "First message not received"
    assert result["count"] == 1

    # Unsubscribe
    result["event"].clear()
    sub.unsubscribe()
    
    # Publish second message - should not be received
    pub.publish(Message(seq=2))
    
    received = result["event"].wait(timeout=1)
    assert received is False, "Second message received but it should have been unsubscribed"
    assert result["count"] == 1, "Message count should still be 1"
    
    tx.close()