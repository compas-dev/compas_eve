"""
Example demonstrating custom codec usage with COMPAS EVE.

This example shows how to:
1. Use the default JsonMessageCodec
2. Create a custom codec
3. Use ProtobufMessageCodec (if compas_pb is installed)
"""

import json

import compas_eve as eve
from compas_eve import JsonMessageCodec, MessageCodec


# Example 1: Using the default JSON codec (implicit)
print("=" * 60)
print("Example 1: Default JSON Codec (implicit)")
print("=" * 60)

pub = eve.Publisher("/example/default")
sub = eve.EchoSubscriber("/example/default")
sub.subscribe()

pub.publish(eve.Message(text="Hello with default JSON codec", count=1))
print()


# Example 2: Explicitly using JSON codec
print("=" * 60)
print("Example 2: Explicit JSON Codec")
print("=" * 60)

json_codec = JsonMessageCodec()
transport = eve.InMemoryTransport(codec=json_codec)

pub = eve.Publisher("/example/json", transport=transport)
sub = eve.EchoSubscriber("/example/json", transport=transport)
sub.subscribe()

pub.publish(eve.Message(text="Hello with explicit JSON codec", count=2))
print()


# Example 3: Custom codec
print("=" * 60)
print("Example 3: Custom Codec")
print("=" * 60)


class UpperCaseCodec(MessageCodec):
    """A simple custom codec that converts all string values to uppercase."""

    def encode(self, message):
        """Encode message by converting all string values to uppercase."""
        # Assume message is a Message instance
        data = message.data

        # Convert string values to uppercase
        encoded_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                encoded_data[key] = value.upper()
            else:
                encoded_data[key] = value
        return json.dumps(encoded_data)

    def decode(self, encoded_data, message_type):
        """Decode data (strings remain uppercase)."""
        data = json.loads(encoded_data)
        return message_type.parse(data)


custom_codec = UpperCaseCodec()
custom_transport = eve.InMemoryTransport(codec=custom_codec)

pub = eve.Publisher("/example/custom", transport=custom_transport)

# Create a custom subscriber that prints the message
class PrintSubscriber(eve.Subscriber):
    def message_received(self, message):
        print(f"Received: {message}")

sub = PrintSubscriber("/example/custom", transport=custom_transport)
sub.subscribe()

pub.publish(eve.Message(text="hello world", count=3))
print()


# Example 4: Protocol Buffers codec (if available)
print("=" * 60)
print("Example 4: Protocol Buffers Codec (if available)")
print("=" * 60)

try:
    from compas_eve.codecs import ProtobufMessageCodec
    
    pb_codec = ProtobufMessageCodec()
    pb_transport = eve.InMemoryTransport(codec=pb_codec)
    
    pub = eve.Publisher("/example/protobuf", transport=pb_transport)
    sub = eve.EchoSubscriber("/example/protobuf", transport=pb_transport)
    sub.subscribe()
    
    pub.publish(eve.Message(text="Hello with Protocol Buffers", count=4))
    print("✓ Protocol Buffers codec is working!")
    
except ImportError as e:
    print(f"Protocol Buffers codec not available: {e}")
    print("Install with: pip install compas_pb")

print()
print("=" * 60)
print("All examples completed!")
print("=" * 60)
