from compas_pb.core import _deserialize_any
from compas_pb.core import _serializer_any
from compas_pb.registry import pb_deserializer
from compas_pb.registry import pb_serializer

from compas_eve import Message
from compas_eve.proto import message_pb2


@pb_serializer(Message)
def message_to_pb(message: Message) -> message_pb2.Message:
    pb = message_pb2.Message()
    for k, v in message.data.items():
        pb.data[k].CopyFrom(_serializer_any(v))
    return pb


@pb_deserializer(message_pb2.Message)
def message_from_pb(pb: message_pb2.Message) -> Message:
    message = Message()
    for k, v in pb.data.items():
        message[k] = _deserialize_any(v)
    return message
