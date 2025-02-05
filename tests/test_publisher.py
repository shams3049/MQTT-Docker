import unittest
from unittest.mock import patch, MagicMock
import publisher

class TestPublisher(unittest.TestCase):

    @patch('publisher.mqtt.Client')
    def test_mqtt_connection(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect.return_value = 0

        publisher.mqtt_client = mock_client_instance
        publisher.mqtt_client.connect("mosquitto", 1883, 60)

        mock_client_instance.connect.assert_called_with("mosquitto", 1883, 60)
        self.assertEqual(mock_client_instance.connect.call_count, 1)

    @patch('publisher.mqtt.Client')
    @patch('publisher.psutil.virtual_memory')
    @patch('publisher.time.sleep', return_value=None)
    def test_publish_memory_usage(self, mock_sleep, mock_virtual_memory, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect.return_value = 0
        mock_virtual_memory.return_value.percent = 50.0

        publisher.mqtt_client = mock_client_instance
        publisher.mqtt_client.connect("mosquitto", 1883, 60)
        publisher.mqtt_client.loop_start()

        with patch('publisher.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            publisher.memory_usage = mock_virtual_memory.return_value
            publisher.message_payload = {
                "timestamp": mock_datetime.now.return_value.isoformat.return_value,
                "memory_usage": publisher.memory_usage.percent,
                "status": "up"
            }
            publisher.mqtt_client.publish("system/memory", publisher.json.dumps(publisher.message_payload))

        mock_client_instance.publish.assert_called_with("system/memory", publisher.json.dumps(publisher.message_payload))
        self.assertEqual(mock_client_instance.publish.call_count, 1)

if __name__ == '__main__':
    unittest.main()
