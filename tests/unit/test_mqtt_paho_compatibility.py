"""Test MQTT paho version compatibility."""

from unittest.mock import Mock, patch

import pytest

from compas_eve.mqtt.mqtt_paho import MqttTransport, PAHO_MQTT_V2_AVAILABLE


def test_paho_mqtt_v1_compatibility():
    """Test that the MqttTransport works with paho-mqtt 1.x style client creation."""
    with patch("compas_eve.mqtt.mqtt_paho.PAHO_MQTT_V2_AVAILABLE", False), patch(
        "paho.mqtt.client.Client"
    ) as mock_client_class:

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # This should work as if paho-mqtt 1.x is installed
        transport = MqttTransport("localhost")

        # Should have called mqtt.Client() without parameters
        mock_client_class.assert_called_once_with()
        assert transport.client == mock_client


def test_paho_mqtt_v2_compatibility():
    """Test that the MqttTransport works with paho-mqtt 2.x style client creation."""
    if not PAHO_MQTT_V2_AVAILABLE:
        pytest.skip("paho-mqtt 2.x not available in this environment")

    with patch("paho.mqtt.client.Client") as mock_client_class:
        from paho.mqtt.enums import CallbackAPIVersion

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # This should work as if paho-mqtt 2.x is installed
        transport = MqttTransport("localhost")

        # Should have called mqtt.Client() with callback_api_version parameter
        mock_client_class.assert_called_once_with(callback_api_version=CallbackAPIVersion.VERSION1)
        assert transport.client == mock_client


def test_version_detection():
    """Test that version detection works correctly."""
    # Test that the import detection works correctly
    if PAHO_MQTT_V2_AVAILABLE:
        # If v2 is available, we should be able to import CallbackAPIVersion
        from paho.mqtt.enums import CallbackAPIVersion

        assert CallbackAPIVersion.VERSION1 is not None
    else:
        # If v2 is not available, import should fail
        with pytest.raises(ImportError):
            from paho.mqtt.enums import CallbackAPIVersion
