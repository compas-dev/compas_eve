import time

from compas_eve import EchoSubscriber
from compas_eve import Publisher
from compas_eve import Topic
from compas_eve.ros import RosTransport

transport = RosTransport("localhost", 9090)
topic = Topic("/chatter", "std_msgs/String", queue_size=10)

subscriber = EchoSubscriber(topic, transport=transport)
subscriber.subscribe()

publisher = Publisher(topic, transport=transport)
publisher.publish({"data": "Hello ROS"})

time.sleep(1)
transport.close()
