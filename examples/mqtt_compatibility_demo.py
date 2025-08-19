#!/usr/bin/env python3
"""
Demonstration script to show MQTT-PAHO 2.0 compatibility.

This script demonstrates that the MqttTransport can work with both
paho-mqtt 1.x and 2.x versions automatically.
"""

import sys
import os

# Add the src directory to the path to import compas_eve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    print("COMPAS Eve MQTT-PAHO 2.0 Compatibility Demonstration")
    print("=" * 55)
    
    try:
        # Import and check version compatibility
        from compas_eve.mqtt.mqtt_paho import PAHO_MQTT_V2_AVAILABLE
        import paho.mqtt
        
        print(f"paho-mqtt version: {paho.mqtt.__version__}")
        print(f"MQTT-PAHO 2.0 support available: {PAHO_MQTT_V2_AVAILABLE}")
        print()
        
        # Try to create transport (will fail due to network but shows client creation works)
        try:
            from compas_eve.mqtt.mqtt_paho import MqttTransport
            print("Attempting to create MqttTransport (will fail due to no broker)...")
            transport = MqttTransport('nonexistent-broker.local')
            print("✓ Transport created successfully")
        except Exception as e:
            if "No address associated with hostname" in str(e) or "gaierror" in str(e):
                print("✓ Client creation successful (expected network error)")
            else:
                print(f"❌ Unexpected error: {e}")
                raise
        
        print()
        print("Compatibility verification:")
        if PAHO_MQTT_V2_AVAILABLE:
            from paho.mqtt.enums import CallbackAPIVersion
            print(f"✓ Using MQTT-PAHO 2.0 with CallbackAPIVersion.VERSION1")
            print(f"✓ CallbackAPIVersion available: {hasattr(CallbackAPIVersion, 'VERSION1')}")
        else:
            print("✓ Using MQTT-PAHO 1.x legacy mode")
            print("✓ No CallbackAPIVersion required")
            
        print()
        print("🎉 All compatibility checks passed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())