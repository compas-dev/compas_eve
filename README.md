# COMPAS EVE

[![Made with COMPAS](https://compas.dev/badge.svg)](https://compas.dev)
[![Github Actions Build Status](https://github.com/gramaziokohler/compas_eve/workflows/build/badge.svg)](https://github.com/gramaziokohler/compas_eve/actions)
[![License](https://img.shields.io/github/license/gramaziokohler/compas_eve.svg)](https://pypi.python.org/pypi/compas_eve)
[![pip downloads](https://img.shields.io/pypi/dm/compas_eve)](https://pypi.python.org/project/compas_eve)
[![PyPI Package latest release](https://img.shields.io/pypi/v/compas_eve.svg)](https://pypi.python.org/pypi/compas_eve)
[![Supported implementations](https://img.shields.io/pypi/implementation/compas_eve.svg)](https://pypi.python.org/pypi/compas_eve)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17955773.svg)](https://doi.org/10.5281/zenodo.17955773)
[![Twitter Follow](https://img.shields.io/twitter/follow/compas_dev?style=social)](https://twitter.com/compas_dev)

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
* Zenoh support
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

### Zenoh

Apache Zenoh is a pub/sub/query protocol. In many ways, it is similar to MQTT but with some additional features and optimizations. COMPAS EVE also supports Zenoh as a transport protocol with an identical API to MQTT:

```python
import compas_eve as eve
from compas_eve.zenoh import ZenohTransport

tx = ZenohTransport()
eve.set_default_transport(tx)

pub = eve.Publisher("/hello_world")
sub = eve.EchoSubscriber("/hello_world")
sub.subscribe()

for i in range(10):
    pub.publish(dict(text=f"Hello World {i}"))
```

### Using different codecs

By default, COMPAS EVE uses JSON for message serialization. However, you can use different codecs for more efficient serialization:

```python
import compas_eve as eve
from compas_eve import JsonMessageCodec
from compas_eve.codecs import ProtobufMessageCodec
from compas_eve.mqtt import MqttTransport

# Use JSON codec (default)
json_codec = JsonMessageCodec()
tx = MqttTransport("broker.hivemq.com", codec=json_codec)

# Or use Protocol Buffers for binary serialization (requires compas_pb)
pb_codec = ProtobufMessageCodec()
tx = MqttTransport("broker.hivemq.com", codec=pb_codec)
```


### Usage from Rhinoceros 3D

It is possible to use the same code from within Rhino/Grasshopper.

To install `compas_eve`, use the the syntax `# r: compas_eve` at the top of any Python 3.x script in Rhino/Grasshopper.
