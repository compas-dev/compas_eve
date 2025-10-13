import pytest
from unittest.mock import Mock, patch
from compas_eve.mqtt.mqtt_paho import MqttTransport, PAHO_MQTT_V2_AVAILABLE


def test_paho_mqtt_v1_compatibility():
        with patch("compas_eve.mqtt.mqtt_paho.PAHO_MQTT_V2_AVAILABLE", False), patch(
            "paho.mqtt.client.Client"
        ) as mock_client_class:

            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # This should work as if paho-mqtt 1.x is installed
            transport = MqttTransport("localhost")

            # Should have called mqtt.Client() with client_id parameter only (no callback_api_version)
            mock_client_class.assert_called_once()
            call_args = mock_client_class.call_args
            assert "client_id" in call_args.kwargs
            assert call_args.kwargs["client_id"].startswith("compas_eve_")
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
        assert "callback_api_version" in call_args.kwargs
        assert call_args.kwargs["callback_api_version"] == CallbackAPIVersion.VERSION1
        assert transport.client == mock_client
