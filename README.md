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
* CPython & IronPython support

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


### Usage from Rhinoceros 3D

It is possible to use the same code from within Rhino/Grasshopper.

Make sure you have installed it to Rhino using the COMPAS installation mechanism:

```bash
    python -m compas_rhino.install -v 7.0
```
