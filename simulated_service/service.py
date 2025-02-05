import time
import json
import random
import datetime
import paho.mqtt.client as mqtt

# Define the MQTT broker address
mqtt_broker_address = "mosquitto"

# Create an MQTT client instance with a unique client ID and protocol version
simulated_service_client = mqtt.Client(client_id="SimulatedService", protocol=mqtt.MQTTv5)

# Define the callback function for when the client connects to the broker
def on_connect(simulated_service_client, userdata, flags, reasonCode, properties):
    if reasonCode == 0:
        print("Simulated Service connected to MQTT broker!")
    else:
        print("Simulated Service connection failed, code:", reasonCode)

# Set the on_connect callback function
simulated_service_client.on_connect = on_connect

# Attempt to connect to the MQTT broker and start the network loop
while True:
    try:
        simulated_service_client.connect(mqtt_broker_address, 1883, 60)
        simulated_service_client.loop_start()  # Start the network loop in a background thread
        break
    except Exception as e:
        print("Simulated Service connection error:", e)
        time.sleep(5)

# Simulate a service that stays "up" for a random period then toggles "down" (and vice versa)
service_state = True  # True means "up", False means "down"
state_duration = random.randint(2, 6)  # number of iterations (each ~5 seconds) before toggling

# Main publishing loop to send heartbeat messages to the MQTT broker
while True:
    # Create a message payload with the current timestamp and status
    heartbeat_message = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "up" if service_state else "down"
    }
    # Print the message to the console
    print("Publishing simulated service heartbeat:", heartbeat_message)
    # Publish the message to the "service/heartbeat" topic
    simulated_service_client.publish("service/heartbeat", json.dumps(heartbeat_message))
    # Wait for 5 seconds before publishing the next message
    time.sleep(5)
    state_duration -= 1
    if state_duration <= 0:
        service_state = not service_state  # toggle state
        state_duration = random.randint(2, 6)
