"""
********************************************************************************
compas_eve
********************************************************************************

.. currentmodule:: compas_eve


.. toctree::
    :maxdepth: 1


"""

from __future__ import print_function

import os


__author__ = ["Gonzalo Casas"]
__copyright__ = "Gramazio Kohler Research"
__license__ = "MIT License"
__email__ = "casas@arch.ethz.ch"
__version__ = "0.1.0"


HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, "../../"))

from .core import Message, Publisher, Subscriber, Transport, Topic, get_default_transport, set_default_transport
from .memory import InMemoryTransport

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
