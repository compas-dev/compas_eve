import time

from compas_eve import Publisher
from compas_eve import Topic
from compas_eve.zenoh import ZenohTransport

topic = Topic("/hello/zenoh")
tx = ZenohTransport()

publisher = Publisher(topic, transport=tx)

for i in range(20):
    msg = dict(text=f"Hello world #{i} over Zenoh")
    print(f"Publishing message: {msg}")
    publisher.publish(msg)
    time.sleep(1)
