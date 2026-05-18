from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import pytest

from compas_eve.mqtt import MqttTransport
from compas_eve.mqtt.mqtt_paho import PAHO_MQTT_V2_AVAILABLE


def test_paho_mqtt_v1_compatibility():
    with patch("compas_eve.mqtt.mqtt_paho.PAHO_MQTT_V2_AVAILABLE", False), patch("paho.mqtt.client.Client") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # This should work as if paho-mqtt 1.x is installed
        transport = MqttTransport("localhost")

        # Should have called mqtt.Client() without callback_api_version
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert "client_id" in call_args.kwargs
        assert call_args.kwargs["client_id"].startswith("compas_eve_")
        assert call_args.kwargs["transport"] == "tcp"
        assert "callback_api_version" not in call_args.kwargs
        assert transport.client == mock_client


def test_paho_mqtt_v2_compatibility():
    if not PAHO_MQTT_V2_AVAILABLE:
        pytest.skip("paho-mqtt 2.x not available in this environment")

    with patch("paho.mqtt.client.Client") as mock_client_class:
        from paho.mqtt.enums import CallbackAPIVersion

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # This should work as if paho-mqtt 2.x is installed
        transport = MqttTransport("localhost")

        # Should have called mqtt.Client() with both client_id and callback_api_version parameters
        mock_client_class.assert_called_once()
        call_args = mock_client_class.call_args
        assert "client_id" in call_args.kwargs
        assert call_args.kwargs["client_id"].startswith("compas_eve_")
        assert call_args.kwargs["transport"] == "tcp"
        assert "callback_api_version" in call_args.kwargs
        assert call_args.kwargs["callback_api_version"] == CallbackAPIVersion.VERSION1
        assert transport.client == mock_client


def test_mqtt_websockets_transport():
    with patch("compas_eve.mqtt.mqtt_paho.PAHO_MQTT_V2_AVAILABLE", False), patch("paho.mqtt.client.Client") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        MqttTransport("localhost", port=443, transport="websockets")

        call_args = mock_client_class.call_args
        assert call_args.kwargs["transport"] == "websockets"
        mock_client.tls_set.assert_not_called()
        mock_client.connect.assert_called_once_with("localhost", 443)


def test_mqtt_tls_enabled_before_connect():
    with patch("compas_eve.mqtt.mqtt_paho.PAHO_MQTT_V2_AVAILABLE", False), patch("paho.mqtt.client.Client") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        MqttTransport("localhost", port=443, transport="websockets", tls=True)

        mock_client.tls_set.assert_called_once_with()
        assert mock_client.method_calls[:2] == [call.tls_set(), call.connect("localhost", 443)]


def test_mqtt_tls_options_enable_tls():
    with patch("compas_eve.mqtt.mqtt_paho.PAHO_MQTT_V2_AVAILABLE", False), patch("paho.mqtt.client.Client") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        MqttTransport("localhost", tls_options={"ca_certs": "/tmp/ca.pem"})

        mock_client.tls_set.assert_called_once_with(ca_certs="/tmp/ca.pem")
