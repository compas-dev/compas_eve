import time

from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic


topic = Topic("/compas_eve/hello_world/")

publisher = Publisher(topic)
subcriber = Subscriber(topic, callback=lambda msg: print(f"Received message: {msg}"))
subcriber.subscribe()

for i in range(20):
    msg = dict(text=f"Hello world #{i}")
    print(f"Publishing message: {msg}")
    publisher.publish(msg)
    time.sleep(1)
