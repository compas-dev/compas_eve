import time

from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve.zenoh import ZenohTransport

topic = Topic("/hello/zenoh")
tx = ZenohTransport()

subcriber = Subscriber(topic, callback=lambda msg: print(f"Received message: {msg}"), transport=tx)
subcriber.subscribe()

print("Waiting for messages, press CTRL+C to cancel")
try:
    while True:
        time.sleep(1)
finally:
    subcriber.unsubscribe()
