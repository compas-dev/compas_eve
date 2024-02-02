"""
********************************************************************************
compas_eve.mqtt
********************************************************************************

.. currentmodule:: compas_eve.mqtt


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    MqttTransport

"""

import sys

if sys.platform == "cli":
    from .mqtt_cli import MqttTransport
else:
    from .mqtt_paho import MqttTransport

__all__ = ["MqttTransport"]
