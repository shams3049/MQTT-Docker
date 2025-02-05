import time
import json
import random
import datetime
import paho.mqtt.client as mqtt

broker_address = "mosquitto"
client = mqtt.Client(client_id="SimulatedService", protocol=mqtt.MQTTv5)

def on_connect(client, userdata, flags, reasonCode, properties):
    if reasonCode == 0:
        print("Simulated Service connected to MQTT broker!")
    else:
        print("Simulated Service connection failed, code:", reasonCode)

client.on_connect = on_connect

# Connect and start network loop
while True:
    try:
        client.connect(broker_address, 1883, 60)
        client.loop_start()
        break
    except Exception as e:
        print("Simulated Service connection error:", e)
        time.sleep(5)

# Simulate a service that stays "up" for a random period then toggles "down" (and vice versa)
state = True  # True means "up", False means "down"
state_duration = random.randint(2, 6)  # number of iterations (each ~5 seconds) before toggling

while True:
    message = {
        "timestamp": datetime.datetime.now().isoformat(),
        "status": "up" if state else "down"
    }
    print("Publishing simulated service heartbeat:", message)
    client.publish("service/heartbeat", json.dumps(message))
    time.sleep(5)
    state_duration -= 1
    if state_duration <= 0:
        state = not state  # toggle state
        state_duration = random.randint(2, 6)
