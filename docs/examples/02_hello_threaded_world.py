import time
from threading import Thread

from compas_eve import Message
from compas_eve import Publisher
from compas_eve import Subscriber
from compas_eve import Topic

topic = Topic("/compas_eve/hello_world/", Message)


def start_publisher():
    publisher = Publisher(topic)

    for i in range(20):
        msg = Message(text=f"Hello world #{i}")
        print(f"Publishing message: {msg.text}")
        publisher.publish(msg)
        time.sleep(1)


def start_subscriber():
    subcriber = Subscriber(topic, callback=lambda msg: print(f"Received message: {msg.text}"))
    subcriber.subscribe()


# Define one thread for each
t1 = Thread(target=start_subscriber)
t2 = Thread(target=start_publisher)

# Start both threads
t1.start()
t2.start()

# Wait until both threads complete
t1.join()
t2.join()
