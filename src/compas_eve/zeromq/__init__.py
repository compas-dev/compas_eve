"""
********************************************************************************
compas_eve.zeromq
********************************************************************************

.. currentmodule:: compas_eve.zeromq


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    ZeroMQTransport

"""

from ..core import Transport
from ..event_emitter import EventEmitterMixin

try:
    import zmq
except ImportError:
    zmq = None

__all__ = ["ZeroMQTransport"]


class ZeroMQTransport(Transport, EventEmitterMixin):
    """ZeroMQ transport allows sending and receiving messages using ZeroMQ pub/sub sockets.

    Parameters
    ----------
    endpoint : str
        Endpoint for the pub/sub communication, e.g. ``tcp://localhost:5555`` or ``inproc://test``.
    bind_subscriber : bool, optional
        If True, the subscriber socket will bind to the endpoint and publisher will connect.
        If False, the publisher will bind to the endpoint and subscriber will connect.
        Defaults to True for most use cases.
    """

    def __init__(self, endpoint, bind_subscriber=True, *args, **kwargs):
        if zmq is None:
            raise ImportError("pyzmq is required for ZeroMQ transport. Please install it with: pip install pyzmq")
        
        super(ZeroMQTransport, self).__init__(*args, **kwargs)
        
        self.endpoint = endpoint
        self.bind_subscriber = bind_subscriber
        self._is_connected = False
        self._local_callbacks = {}
        
        # Create ZeroMQ context and sockets
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)
        
        # Configure sockets based on bind_subscriber setting
        if self.bind_subscriber:
            # Subscriber binds, publisher connects - good for many publishers, few subscribers
            self.sub_socket.bind(self.endpoint)
            self.pub_socket.connect(self.endpoint)
        else:
            # Publisher binds, subscriber connects - good for one publisher, many subscribers  
            self.pub_socket.bind(self.endpoint)
            self.sub_socket.connect(self.endpoint)
        
        # Set up polling for subscriber
        self.poller = zmq.Poller()
        self.poller.register(self.sub_socket, zmq.POLLIN)
        
        # Mark as connected (ZeroMQ doesn't have explicit connection state)
        self._is_connected = True
        
        # Start polling thread for incoming messages
        import threading
        self._polling = True
        self._poll_thread = threading.Thread(target=self._poll_messages)
        self._poll_thread.daemon = True
        self._poll_thread.start()
        
        # Emit ready event
        self.emit("ready")

    def close(self):
        """Close the ZeroMQ sockets and context."""
        self._polling = False
        if hasattr(self, '_poll_thread'):
            self._poll_thread.join(timeout=1)
        
        self.pub_socket.close()
        self.sub_socket.close()
        self.context.term()

    def _poll_messages(self):
        """Poll for incoming messages in a separate thread."""
        while self._polling:
            try:
                # Poll with timeout to allow thread termination
                socks = dict(self.poller.poll(100))  # 100ms timeout
                if self.sub_socket in socks:
                    # Receive topic and message
                    topic_bytes = self.sub_socket.recv(zmq.NOBLOCK)
                    message_bytes = self.sub_socket.recv(zmq.NOBLOCK)
                    
                    topic_name = topic_bytes.decode('utf-8')
                    message_str = message_bytes.decode('utf-8')
                    
                    # Emit the message event
                    event_key = "event:{}".format(topic_name)
                    self.emit(event_key, message_str)
                    
            except zmq.Again:
                # No message available, continue polling
                continue
            except Exception as e:
                # Emit error but continue polling
                self.emit("error", e)

    def on_ready(self, callback):
        """Allows to hook-up to the event triggered when the transport is ready.

        Parameters
        ----------
        callback : function
            Function to invoke when the connection is established.
        """
        if self._is_connected:
            callback()
        else:
            self.once("ready", callback)

    def publish(self, topic, message):
        """Publish a message to a topic.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to publish to.
        message : :class:`Message`
            Instance of the message to publish.
        """
        def _callback(**kwargs):
            json_message = topic._message_to_json(message)
            
            # Send topic and message as separate frames
            self.pub_socket.send_string(topic.name, zmq.SNDMORE)
            self.pub_socket.send_string(json_message)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        """Subscribe to a topic.

        Every time a new message is received on the topic, the callback will be invoked.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to subscribe to.
        callback : function
            Callback to invoke whenever a new message arrives. The callback should
            receive only one `msg` argument, e.g. ``lambda msg: print(msg)``.

        Returns
        -------
        str
            Returns an identifier of the subscription.
        """
        event_key = "event:{}".format(topic.name)
        subscribe_id = "{}:{}".format(event_key, id(callback))

        def _local_callback(message_str):
            msg = topic._message_from_json(message_str)
            callback(msg)

        def _subscribe_callback(**kwargs):
            # Subscribe to the topic on ZeroMQ socket
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic.name)
            
            # Register local callback for this topic
            self.on(event_key, _local_callback)

        self._local_callbacks[subscribe_id] = _local_callback

        self.on_ready(_subscribe_callback)

        return subscribe_id

    def advertise(self, topic):
        """Announce this code will publish messages to the specified topic.

        This call has no effect on this transport implementation.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to advertise.

        Returns
        -------
        str
            Advertising identifier.
        """
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # ZeroMQ does not need explicit advertising
        return advertise_id

    def unadvertise(self, topic):
        """Announce that this code will stop publishing messages to the specified topic.

        This call has no effect on this transport implementation.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to stop publishing messages to.
        """
        pass

    def unsubscribe_by_id(self, subscribe_id):
        """Unsubscribe from the specified topic based on the subscription id.

        Parameters
        ----------
        subscribe_id : str
            Identifier of the subscription.
        """
        ev_type, topic_name, _callback_id = subscribe_id.split(":")
        event_key = "{}:{}".format(ev_type, topic_name)

        callback = self._local_callbacks[subscribe_id]
        self.off(event_key, callback)
        
        # Unsubscribe from ZeroMQ socket
        self.sub_socket.setsockopt_string(zmq.UNSUBSCRIBE, topic_name)

        del self._local_callbacks[subscribe_id]

    def unsubscribe(self, topic):
        """Unsubscribe from the specified topic.

        Parameters
        ----------
        topic : :class:`Topic`
            Instance of the topic to unsubscribe from.
        """
        # Unsubscribe from ZeroMQ socket
        self.sub_socket.setsockopt_string(zmq.UNSUBSCRIBE, topic.name)
        
        # Remove all local listeners for this topic
        event_key = "event:{}".format(topic.name)
        self.remove_all_listeners(event_key)