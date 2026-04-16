# r: compas_eve>=2.2.0
"""
Initialize a Zenoh transport.
"""

from threading import Event

import Grasshopper
from compas_ghpython import create_id
from scriptcontext import sticky as st

from compas_eve.zenoh import ZenohTransport


class ZenohConnectComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, connect: bool):
        zenoh_transport = None

        key = create_id(ghenv.Component, "zenoh_transport")  # noqa: F821
        zenoh_transport = st.get(key, None)

        if zenoh_transport:
            st[key].close()

        if connect:
            event = Event()
            transport = ZenohTransport()
            transport.on_ready(event.set)

            if not event.wait(5):
                raise Exception("Failed to initialize Zenoh router transport.")

            st[key] = transport

        zenoh_transport = st.get(key, None)
        is_connected = zenoh_transport._is_connected if zenoh_transport else False
        return (zenoh_transport, is_connected)
