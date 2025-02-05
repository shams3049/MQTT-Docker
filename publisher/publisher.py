import time
import json
import psutil
import datetime
import paho.mqtt.client as mqtt

# Define the MQTT broker address
broker_address = "mosquitto"

# Create an MQTT client instance with a unique client ID and protocol version
client = mqtt.Client(client_id="MemoryPublisher", protocol=mqtt.MQTTv5)

# Define the callback function for when the client connects to the broker
def on_connect(client, userdata, flags, reasonCode, properties):
    if reasonCode == 0:
        print("Connected to MQTT broker!")
    else:
        print(f"Connection failed with code: {reasonCode}")

# Set the on_connect callback function
client.on_connect = on_connect

# Attempt to connect to the MQTT broker and start the network loop
while True:
    try:
        client.connect(broker_address, 1883, 60)
        client.loop_start()  # Start the network loop in a background thread
        break
    except Exception as e:
        print(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
        time.sleep(5)

# Main publishing loop to send memory usage data to the MQTT broker
while True:
    # Get the current memory usage
    mem = psutil.virtual_memory()
    # Create a message payload with the current timestamp, memory usage, and status
    message = {
        "timestamp": datetime.datetime.now().isoformat(),
        "memory_usage": mem.percent,
        "status": "up"
    }
    # Print the message to the console
    print(f"Publishing: {message}")
    # Publish the message to the "system/memory" topic
    client.publish("system/memory", json.dumps(message))
    # Wait for 5 seconds before publishing the next message
    time.sleep(5)
