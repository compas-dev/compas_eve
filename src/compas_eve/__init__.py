"""
********************************************************************************
compas_eve
********************************************************************************

.. currentmodule:: compas_eve


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Message
    Topic
    Publisher
    Subscriber
    Transport
    InMemoryTransport
    get_default_transport
    set_default_transport

"""

from __future__ import print_function

import os


__author__ = ["Gonzalo Casas"]
__copyright__ = "Gramazio Kohler Research"
__license__ = "MIT License"
__email__ = "casas@arch.ethz.ch"
__version__ = "0.3.4"

from .event_emitter import EventEmitterMixin  # noqa: F401 needed here to avoid circular import on py2.7
from .core import Message, Publisher, Subscriber, Transport, Topic, get_default_transport, set_default_transport
from .memory import InMemoryTransport

HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, "../../"))

set_default_transport(InMemoryTransport())

__all__ = [
    "HOME",
    "Message",
    "Publisher",
    "Subscriber",
    "Topic",
    "Transport",
    "get_default_transport",
    "set_default_transport",
    "InMemoryTransport",
]
__all_plugins__ = ["compas_eve.rhino.install"]
