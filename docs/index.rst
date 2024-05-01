********************************************************************************
Event Extensions for COMPAS
********************************************************************************

.. rst-class:: lead

``compas_eve`` adds event-based communication infrastructure to the COMPAS framework.

Using events is a way to decouple the components of a system, making it easier to develop, test, and maintain.

.. figure:: /_images/pubsub.png
  :figclass: figure
  :class: figure-img img-fluid


.. code-block:: python

    >>> import compas_eve as eve
    >>> pub = eve.Publisher("/hello_world")
    >>> sub = eve.EchoSubscriber("/hello_world")
    >>> sub.subscribe()
    >>> for i in range(10):
    ...    pub.publish(dict(text=f"Hello World {i}"))

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :titlesonly:

   Introduction <self>
   installation
   examples
   grasshopper
   api
   license


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
