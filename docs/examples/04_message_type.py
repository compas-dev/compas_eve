import compas_eve as eve


# Create a custom message type
class CustomMessage(eve.Message):
    def __init__(self, value=None):
        super(CustomMessage, self).__init__()
        self["value"] = value


# Define a default transport using MQTT
from compas_eve.mqtt import MqttTransport

tx = MqttTransport("broker.hivemq.com")
eve.set_default_transport(tx)

# Create publisher and subscriber (using the EchoSubscriber for simplicity)
topic = eve.Topic("/hello_world/", message_type=CustomMessage)
pub = eve.Publisher(topic)
sub = eve.EchoSubscriber(topic)
sub.subscribe()

# Starting publishing messages
import time

for i in range(10):
    pub.publish(CustomMessage(i))
    time.sleep(1)
