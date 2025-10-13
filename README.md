# COMPAS EVE

Event-based communication for the COMPAS framework.

```python
>>> import compas_eve as eve
>>> pub = eve.Publisher("/hello_world")
>>> sub = eve.EchoSubscriber("/hello_world")
>>> sub.subscribe()
>>> for i in range(10):
...    pub.publish(dict(text=f"Hello World {i}"))
```

It is extremely easy to send messages around. COMPAS EVE supports
different transport mechanisms to send messages between different threads, processes, computers, etc.

## Installation

Install using `pip`:

```bash

    pip install compas_eve
```

Or using `conda`:

```bash

    conda install compas_eve
```

## Supported features

* Publisher/subscriber communication model (N-to-N communication)
* In-process events
* MQTT support
* Extensible codec system for message serialization (JSON, Protocol Buffers)

## Examples

### In-process events

The simplest option is to use in-process events. This works for
simple applications and allows to communicate between threads.

```python
import compas_eve as eve

pub = eve.Publisher("/hello_world")
sub = eve.EchoSubscriber("/hello_world")
sub.subscribe()

for i in range(10):
    pub.publish(dict(text=f"Hello World {i}"))
```

### MQTT

MQTT is a protocol that allows to send messages between different
systems/computers. Using MQTT is very simple as well:

```python
import compas_eve as eve
from compas_eve.mqtt import MqttTransport

tx = MqttTransport("broker.hivemq.com")
eve.set_default_transport(tx)

pub = eve.Publisher("/hello_world")
sub = eve.EchoSubscriber("/hello_world")
sub.subscribe()

for i in range(10):
    pub.publish(dict(text=f"Hello World {i}"))
```

This example shows how to send and receive from a single script, but
running publishers and subscribers on different scripts, different processes, or even different computers will work the exact same way.

### Using different codecs

By default, COMPAS EVE uses JSON for message serialization. However, you can use different codecs for more efficient serialization:

```python
import compas_eve as eve
from compas_eve import JsonMessageCodec
from compas_eve.mqtt import MqttTransport

# Use JSON codec (default)
json_codec = JsonMessageCodec()
tx = MqttTransport("broker.hivemq.com", codec=json_codec)

# Or use Protocol Buffers for binary serialization (requires compas_pb)
try:
    from compas_eve.codecs import ProtobufMessageCodec
    pb_codec = ProtobufMessageCodec()
    tx = MqttTransport("broker.hivemq.com", codec=pb_codec)
except ImportError:
    print("Install compas_pb for Protocol Buffers support: pip install compas_pb")
```


### Usage from Rhinoceros 3D

It is possible to use the same code from within Rhino/Grasshopper.

Make sure you have installed it to Rhino using the COMPAS installation mechanism:

```bash
    python -m compas_rhino.install
```

Note: Rhino 7 (IronPython) is no longer supported. Please use Rhino 8 or later.
