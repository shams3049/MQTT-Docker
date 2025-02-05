from flask import Flask, render_template, jsonify
import threading
import json
import datetime
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Separate in-memory stores for memory and service heartbeat data
memory_data = []
service_data = []
data_lock = threading.Lock()

def on_connect(client, userdata, flags, reasonCode, properties):
    if reasonCode == 0:
        print("Subscriber connected to MQTT broker!")
        client.subscribe("system/memory")
        client.subscribe("service/heartbeat")
    else:
        print("Subscriber connection failed with code:", reasonCode)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        timestamp = datetime.datetime.fromisoformat(payload['timestamp'])
        with data_lock:
            if msg.topic == "system/memory":
                memory_data.append({
                    "timestamp": timestamp,
                    "memory_usage": payload['memory_usage'],
                    "status": payload.get("status", "up")
                })
                # Prune memory data older than 30 minutes
                cutoff = datetime.datetime.now() - datetime.timedelta(minutes=30)
                memory_data[:] = [d for d in memory_data if d["timestamp"] >= cutoff]
            elif msg.topic == "service/heartbeat":
                service_data.append({
                    "timestamp": timestamp,
                    "status": payload.get("status", "up")
                })
                # Prune service data older than 30 minutes
                cutoff = datetime.datetime.now() - datetime.timedelta(minutes=30)
                service_data[:] = [d for d in service_data if d["timestamp"] >= cutoff]
    except Exception as e:
        print("Error processing message:", e)

def mqtt_thread():
    client = mqtt.Client(client_id="MemorySubscriber", protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect("mosquitto", 1883, 60)
            break
        except Exception as e:
            print(f"MQTT connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    client.loop_forever()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    with data_lock:
        return jsonify({
            "memory": [{
                "timestamp": d["timestamp"].isoformat(),
                "memory_usage": d["memory_usage"],
                "status": d["status"]
            } for d in memory_data],
            "service": [{
                "timestamp": d["timestamp"].isoformat(),
                "status": d["status"]
            } for d in service_data]
        })

if __name__ == "__main__":
    thread = threading.Thread(target=mqtt_thread)
    thread.daemon = True
    thread.start()
    app.run(host="0.0.0.0", port=5000)
