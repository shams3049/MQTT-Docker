import unittest
from unittest.mock import patch, MagicMock
import subscriber

class TestSubscriber(unittest.TestCase):

    @patch('subscriber.mqtt.Client')
    def test_mqtt_connection(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect.return_value = 0

        subscriber.mqtt_client = mock_client_instance
        subscriber.mqtt_client.connect("mosquitto", 1883, 60)

        mock_client_instance.connect.assert_called_with("mosquitto", 1883, 60)
        self.assertEqual(mock_client_instance.connect.call_count, 1)

    @patch('subscriber.mqtt.Client')
    def test_subscription_to_topics(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect.return_value = 0

        subscriber.mqtt_client = mock_client_instance
        subscriber.mqtt_client.connect("mosquitto", 1883, 60)
        subscriber.mqtt_client.subscribe("system/memory")
        subscriber.mqtt_client.subscribe("service/heartbeat")

        mock_client_instance.subscribe.assert_any_call("system/memory")
        mock_client_instance.subscribe.assert_any_call("service/heartbeat")
        self.assertEqual(mock_client_instance.subscribe.call_count, 2)

    @patch('subscriber.mqtt.Client')
    @patch('subscriber.json.loads')
    @patch('subscriber.datetime.datetime')
    def test_processing_received_messages(self, mock_datetime, mock_json_loads, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect.return_value = 0
        mock_json_loads.return_value = {
            "timestamp": "2023-01-01T00:00:00",
            "memory_usage": 50.0,
            "status": "up"
        }
        mock_datetime.fromisoformat.return_value = mock_datetime.now.return_value

        subscriber.mqtt_client = mock_client_instance
        subscriber.mqtt_client.connect("mosquitto", 1883, 60)
        subscriber.mqtt_client.on_message(mock_client_instance, None, MagicMock(topic="system/memory", payload=b'{"timestamp": "2023-01-01T00:00:00", "memory_usage": 50.0, "status": "up"}'))

        self.assertEqual(len(subscriber.memory_data_store), 1)
        self.assertEqual(subscriber.memory_data_store[0]["memory_usage"], 50.0)
        self.assertEqual(subscriber.memory_data_store[0]["status"], "up")

if __name__ == '__main__':
    unittest.main()
