from compas.geometry import Frame
from compas_eve import Message
from compas_eve.codecs import JsonMessageCodec
from compas_eve.codecs import ProtobufMessageCodec


def test_json_codec_encode_decode():
    codec = JsonMessageCodec()

    original_message = Message(name="test", value=42, active=True)
    encoded = codec.encode(original_message)
    wire_encoding = encoded.encode("utf-8")  # simulate wire encoding
    decoded = codec.decode(wire_encoding, Message)

    assert isinstance(encoded, str)
    assert isinstance(decoded, Message)
    assert decoded.name == "test"
    assert decoded.value == 42
    assert decoded.active is True


def test_json_codec_nested_data():
    codec = JsonMessageCodec()

    nested_data = {"coordinates": [1.0, 2.0, 3.0], "metadata": {"author": "test", "version": 1}, "tags": ["geometry", "point"]}

    original_message = Message(**nested_data)
    encoded = codec.encode(original_message).encode("utf-8")
    decoded = codec.decode(encoded, Message)

    assert decoded.coordinates == [1.0, 2.0, 3.0]
    assert decoded.metadata["author"] == "test"
    assert decoded.metadata["version"] == 1
    assert decoded.tags == ["geometry", "point"]


def test_json_codec_empty_message():
    codec = JsonMessageCodec()

    original_message = Message()
    encoded = codec.encode(original_message).encode("utf-8")
    decoded = codec.decode(encoded, Message)

    assert isinstance(decoded, Message)
    assert str(decoded) == "{}"


def test_json_codec_roundtrip():
    """Test JSON codec maintains data integrity through multiple encode/decode cycles."""
    codec = JsonMessageCodec()

    original_message = Message(string_val="hello world", int_val=123, float_val=3.14159, bool_val=True, null_val=None, list_val=[1, 2, 3], dict_val={"key": "value"})

    # Multiple roundtrips
    current = original_message
    for _ in range(3):
        encoded = codec.encode(current).encode("utf-8")
        current = codec.decode(encoded, Message)

    assert current.string_val == "hello world"
    assert current.int_val == 123
    assert current.float_val == 3.14159
    assert current.bool_val is True
    assert current.null_val is None
    assert current.list_val == [1, 2, 3]
    assert current.dict_val == {"key": "value"}


def test_protobuf_codec_encode_decode():
    codec = ProtobufMessageCodec()

    # Test with simple message
    original_message = Message(name="test", value=42, active=True, frame=Frame.worldXY())
    encoded = codec.encode(original_message.data)
    decoded = codec.decode(encoded, dict)

    assert isinstance(encoded, bytes)
    assert isinstance(decoded, dict)
    assert decoded["name"] == "test"
    assert decoded["value"] == 42
    assert decoded["active"] is True
    assert decoded["frame"].point == [0.0, 0.0, 0.0]
    assert decoded["frame"].xaxis == [1.0, 0.0, 0.0]
    assert decoded["frame"].yaxis == [0.0, 1.0, 0.0]


def test_protobuf_codec_nested_data():
    """Test Protobuf codec handles nested data structures."""
    codec = ProtobufMessageCodec()

    nested_data = {"coordinates": [1.0, 2.0, 3.0], "metadata": {"author": "test", "version": 1}, "tags": ["geometry", "point"]}

    original_message = Message(**nested_data)
    encoded = codec.encode(original_message.data)
    decoded = codec.decode(encoded)

    assert decoded["coordinates"] == [1.0, 2.0, 3.0]
    assert decoded["metadata"]["author"] == "test"
    assert decoded["metadata"]["version"] == 1
    assert decoded["tags"] == ["geometry", "point"]


def test_protobuf_codec_roundtrip():
    """Test Protobuf codec maintains data integrity through multiple encode/decode cycles."""
    codec = ProtobufMessageCodec()

    original_message = Message(string_val="hello world", int_val=123, float_val=3.14159, bool_val=True, list_val=[1, 2, 3], dict_val={"key": "value"})
    original_message = original_message.data

    # Multiple roundtrips
    current = original_message
    for _ in range(3):
        encoded = codec.encode(current)
        current = codec.decode(encoded)

    assert current["string_val"] == "hello world"
    assert current["int_val"] == 123
    assert current["float_val"] == 3.14159
    assert current["bool_val"] is True
    assert current["list_val"] == [1, 2, 3]
    assert current["dict_val"] == {"key": "value"}


def test_codec_compatibility():
    """Test that both codecs produce equivalent results for the same message."""
    json_codec = JsonMessageCodec()
    protobuf_codec = ProtobufMessageCodec()

    original_message = Message(name="compatibility_test", count=100, enabled=False, data=[1, 2, 3, 4, 5])

    # Encode with both codecs
    json_encoded = json_codec.encode(original_message).encode("utf-8")
    protobuf_encoded = protobuf_codec.encode(original_message.data)

    # Decode with respective codecs
    json_decoded = json_codec.decode(json_encoded, Message)
    protobuf_decoded = protobuf_codec.decode(protobuf_encoded, Message)

    # Both should produce equivalent messages
    assert json_decoded["name"] == protobuf_decoded["name"] == "compatibility_test"
    assert json_decoded["count"] == protobuf_decoded["count"] == 100
    assert json_decoded["enabled"] == protobuf_decoded["enabled"] is False
    assert json_decoded["data"] == protobuf_decoded["data"] == [1, 2, 3, 4, 5]
