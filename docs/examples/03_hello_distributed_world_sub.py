import time

from compas_eve import Message
from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve.mqtt import MqttTransport

topic = Topic("/compas_eve/hello_world/", Message)
tx = MqttTransport("broker.hivemq.com")

subcriber = Subscriber(topic, callback=lambda msg: print(f"Received message: {msg.text}"), transport=tx)
subcriber.subscribe()

print("Waiting for messages, press CTRL+C to cancel")
while True:
    time.sleep(1)
