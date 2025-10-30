"""
********************************************************************************
compas_eve.codecs
********************************************************************************

.. currentmodule:: compas_eve.codecs


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    MessageCodec
    JsonMessageCodec
    ProtobufMessageCodec

"""

from compas.data import json_dumps
from compas.data import json_loads

__all__ = ["MessageCodec", "JsonMessageCodec", "ProtobufMessageCodec"]


class MessageCodec(object):
    """Abstract base class for message codecs.

    A codec is responsible for encoding and decoding messages
    to/from a specific representation format (e.g., JSON, Protocol Buffers).
    """

    def encode(self, message):
        """Encode a message to the codec's representation format.

        Parameters
        ----------
        message : :class:`Message` or dict or object
            Message to encode. Can be a Message instance, a dict, or
            an object implementing the COMPAS data framework.

        Returns
        -------
        bytes or str
            Encoded representation of the message.
        """
        raise NotImplementedError("Subclasses must implement encode()")

    def decode(self, encoded_data):
        """Decode data from the codec's representation format.

        Parameters
        ----------
        encoded_data : bytes
            Encoded data to decode.

        Returns
        -------
        :class:`Message` or dict or object
            Decoded message after reconstruction from the encoded data.
        """
        raise NotImplementedError("Subclasses must implement decode()")


class JsonMessageCodec(MessageCodec):
    """JSON codec for message serialization.

    This codec uses the COMPAS framework's JSON serialization functions
    to encode and decode message data. It can handle Message objects,
    COMPAS Data objects, and regular dictionaries.
    """

    def encode(self, message):
        """Encode a message to JSON string.

        Parameters
        ----------
        message : :class:`Message` or dict or object
            Message to encode. Can be a Message instance, a dict, or
            an object implementing the COMPAS data framework.

        Returns
        -------
        str
            JSON string representation of the message.
        """
        # Extract data from the message
        try:
            return json_dumps(message.data)
        except (KeyError, AttributeError):
            try:
                return json_dumps(message)
            except (KeyError, AttributeError):
                return json_dumps(dict(message))

    def decode(self, encoded_data, message_type):
        """Decode JSON message payloads to message object.

        Parameters
        ----------
        encoded_data : bytes
            Message bytes to decode into a JSON string.
        message_type : type
            The message type class to use for parsing.

        Returns
        -------
        :class:`Message`
            Decoded message object.
        """
        data = json_loads(encoded_data.decode())
        if hasattr(data, "__data__"):
            return data
        else:
            return message_type.parse(data)


try:
    import compas_pb

    COMPAS_PB_AVAILABLE = True
except ImportError:
    COMPAS_PB_AVAILABLE = False


class ProtobufMessageCodec(MessageCodec):
    """Protocol Buffers codec for message serialization.

    This codec uses the compas_pb package to encode and decode message data
    using Protocol Buffers binary format.

    Note
    ----
    This codec requires the ``compas_pb`` package to be installed.
    If ``compas_pb`` is not available, attempting to encode or decode
    will raise an ImportError.
    """

    def __init__(self):
        super(ProtobufMessageCodec, self).__init__()
        if not COMPAS_PB_AVAILABLE:
            raise ImportError(
                "The ProtobufMessageCodec requires 'compas_pb' to be installed. "
                "Please install it with: pip install compas_pb"
            )

    def encode(self, message):
        """Encode a message to Protocol Buffers binary format.

        Parameters
        ----------
        message : :class:`Message` or dict or object
            Message to encode. Can be a Message instance, a dict, or
            an object implementing the COMPAS data framework.

        Returns
        -------
        bytes
            Protocol Buffers binary representation of the message.
        """
        if not COMPAS_PB_AVAILABLE:
            raise ImportError(
                "The ProtobufMessageCodec requires 'compas_pb' to be installed. "
                "Please install it with: pip install compas_pb"
            )
        return compas_pb.pb_dump_bts(message)

    def decode(self, encoded_data, message_type=None):
        """Decode Protocol Buffers binary data to message object.

        Parameters
        ----------
        encoded_data : bytes
            Protocol Buffers binary data to decode.
        message_type : type, optional
            The message type class (not used for protobuf as it's encoded in the data).

        Returns
        -------
        object
            Decoded message object.
        """
        if not COMPAS_PB_AVAILABLE:
            raise ImportError(
                "The ProtobufMessageCodec requires 'compas_pb' to be installed. "
                "Please install it with: pip install compas_pb"
            )
        return compas_pb.pb_load_bts(encoded_data)
