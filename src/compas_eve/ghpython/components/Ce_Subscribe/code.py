"""
Subscribe to a topic to receive messages.

COMPAS EVE v0.5.0
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_eve import Topic
from compas_eve import Subscriber
from compas_eve.ghpython import BackgroundWorker


class SubscribeComponent(component):
    def RunScript(self, transport, topic_name, start, on):
        if not topic_name:
            raise ValueError("Please specify the name of the topic")

        if on is None:
            on = True

        if not on:
            BackgroundWorker.stop_instance_by_component(ghenv)  # noqa: F821
            return None

        args = (
            transport,
            topic_name,
        )

        self.worker = BackgroundWorker.instance_by_component(
            ghenv,  # noqa: F821
            self.start_subscriber,
            dispose_function=self.stop_subscriber,
            force_new=start,
            auto_set_done=False,
            args=args,
        )

        if not self.worker.is_working() and not self.worker.is_done() and start:
            self.worker.start_work()

        if hasattr(self.worker, "result"):
            return self.worker.result
        else:
            return None

    def start_subscriber(self, worker, transport, topic_name):
        worker.count = 0

        def received_message(message):
            worker.count += 1
            worker.display_message("Received {} messages".format(worker.count))
            worker.update_result(message, 10)

        topic = Topic(topic_name)
        worker.subscriber = Subscriber(topic, callback=received_message, transport=transport)
        worker.subscriber.subscribe()
        worker.display_message("Subscribed")

    def stop_subscriber(self, worker):
        if hasattr(worker, "subscriber"):
            worker.subscriber.unsubscribe()
        worker.display_message("Stopped")
