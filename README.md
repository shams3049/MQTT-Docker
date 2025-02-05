# MQTT Docker Setup

This project demonstrates a simple MQTT setup using Docker. It includes a Mosquitto MQTT broker, a publisher that sends memory usage data, a subscriber that displays the data on a web dashboard, and a simulated service that sends heartbeat messages.

## Running the Project

1. Clone the repository:
   ```sh
   git clone https://github.com/shams3049/mqtt-docker-setup.git
   cd mqtt-docker-setup
   ```

2. Build and start the Docker containers:
   ```sh
   docker-compose up --build
   ```

3. Open your web browser and navigate to `http://localhost:5001` to view the dashboard.

## Process Diagram

Below is a process diagram illustrating the workflow of the MQTT Docker demo:

```mermaid
graph TD
    A[Publisher] -->|Publishes memory usage| B[MQTT Broker]
    C[Simulated Service] -->|Publishes heartbeat| B[MQTT Broker]
    B[MQTT Broker] -->|Forwards messages| D[Subscriber]
    D[Subscriber] -->|Displays data| E[Web Dashboard]
```

## Components

### Mosquitto MQTT Broker
- An open-source MQTT broker used to handle the communication between the publisher, subscriber, and simulated service.

### Publisher
- A Python script that publishes memory usage data to the MQTT broker every 5 seconds.

### Subscriber
- A Flask web application that subscribes to the MQTT broker and displays the received data on a web dashboard.

### Simulated Service
- A Python script that simulates a service by publishing heartbeat messages to the MQTT broker.
