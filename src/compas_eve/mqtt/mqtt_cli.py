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
        # event_key = "event_{}".format(topic.name)

        # TODO: can we avoid the additional cast to dict?
        application_message = (
            MqttApplicationMessageBuilder()
            .WithTopic(topic.name)
            .WithPayload(json_dumps(dict(message)))
            .Build()
        )

        def _callback(**kwargs):
            self.client.PublishAsync(application_message, CancellationToken.None)
            # self.emit(event_key, message)

        self.on_ready(_callback)

    def subscribe(self, topic, callback):
        event_key = "event_{}".format(topic.name)

        def on_message(event_args):
            payload = Encoding.UTF8.GetString(event_args.ApplicationMessage.Payload)
            msg = topic.message_type.parse(json_loads(payload))
            callback(msg)

        def _subscribe_callback(**kwargs):
            self.on(event_key, callback)

            subscribe_opts = self.factory.CreateSubscribeOptionsBuilder().WithTopicFilter(lambda f: f.WithTopic(topic.name)).Build()
            self.client.ApplicationMessageReceivedAsync += on_message
            self.client.SubscribeAsync(subscribe_opts, self.cancellation_token)

        self.on_ready(_subscribe_callback)

    def advertise(self, topic):
        advertise_id = "advertise:{}:{}".format(topic.name, self.id_counter)
        # mqtt does not need anything here
        return advertise_id

    def unadvertise(self, topic):
        pass

    def unsubscribe(self, topic):
        # self.client.unsubscribe(topic.name)
        pass
