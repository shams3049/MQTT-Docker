import time
import json
import psutil
import datetime
import paho.mqtt.client as mqtt

broker_address = "mosquitto"
# Use MQTTv5 to take advantage of the new callback API
client = mqtt.Client(client_id="MemoryPublisher", protocol=mqtt.MQTTv5)

def on_connect(client, userdata, flags, reasonCode, properties):
    if reasonCode == 0:
        print("Connected to MQTT broker!")
    else:
        print(f"Connection failed with code: {reasonCode}")

client.on_connect = on_connect

# Attempt connection and start the network loop
while True:
    try:
        client.connect(broker_address, 1883, 60)
        client.loop_start()  # Start network loop in background thread
        break
    except Exception as e:
        print(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
        time.sleep(5)

# Main publishing loop
while True:
    mem = psutil.virtual_memory()
    message = {
        "timestamp": datetime.datetime.now().isoformat(),
        "memory_usage": mem.percent,
        "status": "up"
    }
    print(f"Publishing: {message}")
    client.publish("system/memory", json.dumps(message))
    time.sleep(5)
