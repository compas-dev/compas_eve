"""
Publish messages to a topic.

COMPAS EVE v1.0.0
"""

import time

from ghpythonlib.componentbase import executingcomponent as component
from scriptcontext import sticky as st

from compas_eve import Topic
from compas_eve import Publisher
from compas_ghpython import create_id


class PublishComponent(component):
    def RunScript(self, transport, topic_name, message, on):
        if not topic_name:
            raise ValueError("Please specify the name of the topic")

        if on is None:
            on = True

        key = create_id(self, "publisher_{}".format(id(transport)))
        key_count = create_id(self, "publisher_count_{}".format(id(transport)))
        publisher = st.get(key, None)

        if not publisher:
            topic = Topic(topic_name)
            publisher = Publisher(topic, transport=transport)
            publisher.advertise()
            time.sleep(0.2)

            st[key] = publisher
            st[key_count] = 0

        if on and message:
            st[key_count] += 1
            publisher.publish(message)
            self.Message = "Published {} messages".format(st[key_count])

        return st[key_count]
