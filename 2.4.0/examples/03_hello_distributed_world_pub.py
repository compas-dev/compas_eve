import time

from compas_eve import Publisher
from compas_eve import Topic
from compas_eve.mqtt import MqttTransport

topic = Topic("/compas_eve/hello_world/")
tx = MqttTransport("broker.hivemq.com")

publisher = Publisher(topic, transport=tx)

for i in range(20):
    msg = dict(text=f"Hello world #{i}")
    print(f"Publishing message: {msg}")
    publisher.publish(msg)
    time.sleep(1)
