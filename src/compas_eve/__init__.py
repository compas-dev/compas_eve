__author__ = ["Gonzalo Casas"]
__copyright__ = "COMPAS Association"
__license__ = "MIT License"
__email__ = "casas@arch.ethz.ch"
__version__ = "2.1.1"

from .event_emitter import EventEmitterMixin  # noqa: F401 needed here to avoid circular import on py2.7
from .core import (
    Message,
    Publisher,
    Subscriber,
    EchoSubscriber,
    Transport,
    Topic,
    get_default_transport,
    set_default_transport,
)
from .codecs import MessageCodec
from .memory import InMemoryTransport

set_default_transport(InMemoryTransport())

__all__ = [
    "Message",
    "Publisher",
    "Subscriber",
    "EchoSubscriber",
    "Topic",
    "Transport",
    "MessageCodec",
    "get_default_transport",
    "set_default_transport",
    "InMemoryTransport",
]
