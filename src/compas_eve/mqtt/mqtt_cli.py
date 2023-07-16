# fmt: off
from __future__ import print_function

from ..core import Transport
from ..event_emitter import EventEmitterMixin

from compas.data import json_dumps
from compas.data import json_loads

import clr
import json
import os
import sys

lib_dir = os.path.join(os.path.dirname(__file__), "netlib")
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

clr.AddReference("MQTTnet")

from System import Action
from System.Text import Encoding
from System.Threading import CancellationToken, CancellationTokenSource
from System.Threading.Tasks import Task

from MQTTnet import MqttFactory
from MQTTnet import MqttApplicationMessageBuilder
from MQTTnet.Client import MqttClientConnectResult
from MQTTnet.Client import MqttClientConnectResultCode
from MQTTnet.Client import MqttClientOptionsBuilder
from MQTTnet.Client import MqttClientDisconnectOptionsBuilder


class MqttTransport(Transport, EventEmitterMixin):
    def __init__(self, host, port=1883, *args, **kwargs):
        super(MqttTransport, self).__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self._is_connected = False
        self._local_callbacks = {}

        self.cancellation_token_source = CancellationTokenSource()
        self.cancellation_token = self.cancellation_token_source.Token

        self.factory = MqttFactory()
        options = MqttClientOptionsBuilder().WithTcpServer(host, port).Build()

        self.client = self.factory.CreateMqttClient()
        self.client.ConnectAsync(options, self.cancellation_token).ContinueWith.Overloads[Action[Task[MqttClientConnectResult]]](self._on_connect)


    def _on_connect(self, event_args):
        if event_args.Result.ResultCode == MqttClientConnectResultCode.Success:
            self._is_connected = event_args.Result.ResultCode == MqttClientConnectResultCode.Success
            self.emit("ready")

    def close(self):
        options = MqttClientDisconnectOptionsBuilder().WithReasonString("Normal").Build()
        self.client.DisconnectAsync(options, CancellationToken.None) # noqa: E999 (disable flake8 error, which incorrectly parses None as the python keyword)

    def on_ready(self, callback):
        if self._is_connected:
            callback()
        else:
            self.once("ready", callback)

    def publish(self, topic, message):
        # TODO: can we avoid the additional cast to dict?
        application_message = (
            MqttApplicationMessageBuilder()
            .WithTopic(topic.name)
            .WithPayload(json_dumps(dict(message)))
            .Build()
        )

        def _callback(**kwargs):
            self.client.PublishAsync(application_message, CancellationToken.None)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        event_key = "event:{}".format(topic.name)
        subscribe_id = "{}:{}".format(event_key, id(callback))

        def _local_callback(application_message):
            payload = Encoding.UTF8.GetString(application_message.Payload)
            msg = topic.message_type.parse(json_loads(payload))
            callback(msg)

        def _subscribe_callback(**kwargs):
            subscribe_opts = self.factory.CreateSubscribeOptionsBuilder().WithTopicFilter(lambda f: f.WithTopic(topic.name)).Build()
            self.client.ApplicationMessageReceivedAsync += self._on_message
            self.client.SubscribeAsync(subscribe_opts, self.cancellation_token)
            self.on(event_key, _local_callback)

        self._local_callbacks[subscribe_id] = _local_callback

        self.on_ready(_subscribe_callback)

        return subscribe_id

    def _on_message(self, event_args):
        event_key = "event:{}".format(event_args.ApplicationMessage.Topic)
        self.emit(event_key, event_args.ApplicationMessage)

    def advertise(self, topic):
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # mqtt does not need anything here
        return advertise_id

    def unadvertise(self, topic):
        pass

    def unsubscribe_by_id(self, subscribe_id):
        ev_type, topic_name, _callback_id = subscribe_id.split(":")
        event_key = "{}:{}".format(ev_type, topic_name)

        callback = self._local_callbacks[subscribe_id]
        self.off(event_key, callback)
        del self._local_callbacks[subscribe_id]

        unsubscribe_opts = self.factory.CreateUnsubscribeOptionsBuilder().WithTopicFilter(topic_name).Build()
        self.client.UnsubscribeAsync(unsubscribe_opts, self.cancellation_token)
        self.client.ApplicationMessageReceivedAsync -= self._on_message

    def unsubscribe(self, topic):
        unsubscribe_opts = self.factory.CreateUnsubscribeOptionsBuilder().WithTopicFilter(topic.name).Build()
        self.client.UnsubscribeAsync(unsubscribe_opts, self.cancellation_token)
        self.client.ApplicationMessageReceivedAsync -= self._on_message
