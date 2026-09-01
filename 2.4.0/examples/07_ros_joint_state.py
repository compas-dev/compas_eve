import time
from threading import Event

from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic
from compas_eve.ros import RosTransport

transport = RosTransport("localhost", 9090)
topic = Topic("/compas_eve/joint_states", "sensor_msgs/JointState", queue_size=10)
message_received = Event()


def print_joint_state(message):
    print("Frame:", message["header"]["frame_id"])
    for name, position, velocity in zip(message["name"], message["position"], message["velocity"]):
        print("{}: position={}, velocity={}".format(name, position, velocity))
    message_received.set()


subscriber = Subscriber(topic, print_joint_state, transport=transport)
subscriber.subscribe()
time.sleep(0.5)  # Allow rosbridge to register the subscription.

publisher = Publisher(topic, transport=transport)
publisher.publish(
    {
        "header": {
            "stamp": {"sec": 0, "nanosec": 0},
            "frame_id": "robot_base",
        },
        "name": ["shoulder_joint", "elbow_joint", "wrist_joint"],
        "position": [0.25, -0.5, 1.2],
        "velocity": [0.1, 0.0, -0.1],
        "effort": [4.2, 2.8, 0.7],
    }
)

if not message_received.wait(timeout=5):
    raise RuntimeError("No joint state received")

subscriber.unsubscribe()
publisher.unadvertise()
transport.close()
