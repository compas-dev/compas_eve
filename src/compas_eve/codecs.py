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

    ProtobufMessageCodec

"""

from .core import MessageCodec

__all__ = ["ProtobufMessageCodec"]


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

    def encode(self, data):
        """Encode data to Protocol Buffers binary format.
        
        Parameters
        ----------
        data : dict
            Data dictionary to encode.
            
        Returns
        -------
        bytes
            Protocol Buffers binary representation of the data.
        """
        if not COMPAS_PB_AVAILABLE:
            raise ImportError(
                "The ProtobufMessageCodec requires 'compas_pb' to be installed. "
                "Please install it with: pip install compas_pb"
            )
        return compas_pb.encode(data)

    def decode(self, encoded_data):
        """Decode Protocol Buffers binary data to data dictionary.
        
        Parameters
        ----------
        encoded_data : bytes
            Protocol Buffers binary data to decode.
            
        Returns
        -------
        dict
            Decoded data dictionary.
        """
        if not COMPAS_PB_AVAILABLE:
            raise ImportError(
                "The ProtobufMessageCodec requires 'compas_pb' to be installed. "
                "Please install it with: pip install compas_pb"
            )
        return compas_pb.decode(encoded_data)
