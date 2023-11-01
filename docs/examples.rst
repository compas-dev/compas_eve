********************************************************************************
Examples
********************************************************************************

.. currentmodule:: compas_eve

.. note::

    This tutorial assumes that you have already installed ``compas_eve``.
    If you haven't, please follow the instructions in the :ref:`installation` section.

The main feature of ``compas_eve`` is to allow communication between different
parts of a program using messages. These messages are sent around using a
publisher/subscriber model, or pub/sub for short. In pub/sub communication,
messages are not sent directly from a sender to a receiver, instead, they are
sent to a :class:`Topic`. A topic is like a mailbox, the :class:`Publisher`
sends messages to the topic without the need for a subcriber to be
actively listening for messages, and also the :class:`Subscriber` can start
listening for messages on a topic without the need for any publisher to be
currently sending anything.

This creates a highly decoupled communication model that facilitates the creation
of complex software with simple code.

An additional benefit of pub/sub is that it is not limited to 1-to-1 communication:
on a single topic, there can be multiple publishers and multiple subscribers all
communicating at the same time without additional coordination.

Hello World
-----------

Let's see a **Hello World** example of this type of communication using ``compas_eve``.
This example is very contrived because both the publisher and the subscriber are defined
in the same script and the same thread.

.. literalinclude :: examples/01_hello_world.py
   :language: python

This example is the simplest possible, and it only shows the main concepts needed
to communicate. In particular, ``compas_eve`` uses by default an **in-memory transport**
for the messages, this means that messages are can only be received within the same program.

Hello Threaded World
--------------------

Let's try to extend this first example and add multiple threads to illustrate
multi-threaded communication:

.. literalinclude :: examples/02_hello_threaded_world.py
   :language: python

This get more interesting! Now the publisher and subscriber are in separate threads. However,
the in-memory transport is limited to *same-process*. This means that if we launch this
script twice, the messages will not jump from one process to the other.
In other words, if we want to communicate with a subscriber on a different process on the machine,
or even on a completely separate machine, we need to take an extra step.

Hello Distributed World
-----------------------

Fortunately, it is very easy to extend our example and enable communication across processes, machines,
networks, continents, anything that is connected to the Internet!

The only difference is that we are going to configure a different :class:`Transport` implementation for
our messages. In this case, we will use the MQTT transport method. `MQTT <https://en.wikipedia.org/wiki/MQTT>`_
is a network protocol very popular for IoT applications because of its lightweight.

We are going to split the code and create one script for sending messages with a publisher and a different
one for receiving. This will enable us to start the two examples at the same time from different windows, or
potentially from different machines!

First the publisher example:

.. literalinclude :: examples/03_hello_distributed_world_pub.py
   :language: python

And now the subscriber example:

.. literalinclude :: examples/03_hello_distributed_world_sub.py
   :language: python

You can start both programs in two completely different terminal windows,
or even completely different computers and they will be able to communicate!

And since pub/sub allows any number of publishers and any number of
subscriber per topic, you can start the same scripts more than once and the
messages will be received and send multiple times!
