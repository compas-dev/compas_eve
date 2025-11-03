# env: C:\Users\ckasirer\Documents\repos\compas_eve\src
"""
Publish messages to a topic.

COMPAS EVE v2.0.0
"""

import time

import Grasshopper
import System
from compas_ghpython import create_id
from scriptcontext import sticky as st

from compas_eve import Publisher
from compas_eve import Topic
from compas_eve.ghpython import warning


class PublishComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, transport, topic_name: str, message, on: bool):
        if not topic_name:
            warning(ghenv.Component, "Please specify the name of the topic")
            return

        if on is None:
            on = True

        key = create_id(ghenv.Component, "publisher_{}".format(id(transport)))
        key_count = create_id(ghenv.Component, "publisher_count_{}".format(id(transport)))
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
