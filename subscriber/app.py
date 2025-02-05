from flask import Flask, render_template, jsonify
import threading
import json
import datetime
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Separate in-memory stores for memory and service heartbeat data
memory_data_store = []
service_heartbeat_data_store = []
data_store_lock = threading.Lock()

# Callback function for when the client connects to the MQTT broker
def on_connect(mqtt_client, userdata, flags, reasonCode, properties):
    if reasonCode == 0:
        print("Subscriber connected to MQTT broker!")
        mqtt_client.subscribe("system/memory")
        mqtt_client.subscribe("service/heartbeat")
    else:
        print("Subscriber connection failed with code:", reasonCode)

# Callback function for when a message is received from the MQTT broker
def on_message(mqtt_client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        timestamp = datetime.datetime.fromisoformat(payload['timestamp'])
        with data_store_lock:
            if msg.topic == "system/memory":
                memory_data_store.append({
                    "timestamp": timestamp,
                    "memory_usage": payload['memory_usage'],
                    "status": payload.get("status", "up")
                })
                # Prune memory data older than 30 minutes
                cutoff = datetime.datetime.now() - datetime.timedelta(minutes=30)
                memory_data_store[:] = [d for d in memory_data_store if d["timestamp"] >= cutoff]
            elif msg.topic == "service/heartbeat":
                service_heartbeat_data_store.append({
                    "timestamp": timestamp,
                    "status": payload.get("status", "up")
                })
                # Prune service data older than 30 minutes
                cutoff = datetime.datetime.now() - datetime.timedelta(minutes=30)
                service_heartbeat_data_store[:] = [d for d in service_heartbeat_data_store if d["timestamp"] >= cutoff]
    except Exception as e:
        print("Error processing message:", e)

# Function to run the MQTT client in a separate thread
def mqtt_thread():
    mqtt_client = mqtt.Client(client_id="MemorySubscriber", protocol=mqtt.MQTTv5)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    while True:
        try:
            mqtt_client.connect("mosquitto", 1883, 60)
            break
        except Exception as e:
            print(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    mqtt_client.loop_forever()

# Route to render the main dashboard page
@app.route("/")
def index():
    return render_template("index.html")

# Route to provide memory and service data as JSON
@app.route("/data")
def data():
    with data_store_lock:
        return jsonify({
            "memory": [{
                "timestamp": d["timestamp"].isoformat(),
                "memory_usage": d["memory_usage"],
                "status": d["status"]
            } for d in memory_data_store],
            "service": [{
                "timestamp": d["timestamp"].isoformat(),
                "status": d["status"]
            } for d in service_heartbeat_data_store]
        })

if __name__ == "__main__":
    # Start the MQTT client thread
    thread = threading.Thread(target=mqtt_thread)
    thread.daemon = True
    thread.start()
    # Start the Flask web server
    app.run(host="0.0.0.0", port=5000)
