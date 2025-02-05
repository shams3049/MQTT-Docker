import unittest
from unittest.mock import patch, MagicMock
import simulated_service

class TestSimulatedService(unittest.TestCase):

    @patch('simulated_service.mqtt.Client')
    def test_mqtt_connection(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect.return_value = 0

        simulated_service.simulated_service_client = mock_client_instance
        simulated_service.simulated_service_client.connect("mosquitto", 1883, 60)

        mock_client_instance.connect.assert_called_with("mosquitto", 1883, 60)
        self.assertEqual(mock_client_instance.connect.call_count, 1)

    @patch('simulated_service.mqtt.Client')
    @patch('simulated_service.time.sleep', return_value=None)
    def test_publish_heartbeat(self, mock_sleep, MockClient):
        mock_client_instance = MockClient.return_value
        mock_client_instance.connect.return_value = 0

        simulated_service.simulated_service_client = mock_client_instance
        simulated_service.simulated_service_client.connect("mosquitto", 1883, 60)
        simulated_service.simulated_service_client.loop_start()

        with patch('simulated_service.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            simulated_service.heartbeat_message = {
                "timestamp": mock_datetime.now.return_value.isoformat.return_value,
                "status": "up"
            }
            simulated_service.simulated_service_client.publish("service/heartbeat", simulated_service.json.dumps(simulated_service.heartbeat_message))

        mock_client_instance.publish.assert_called_with("service/heartbeat", simulated_service.json.dumps(simulated_service.heartbeat_message))
        self.assertEqual(mock_client_instance.publish.call_count, 1)

if __name__ == '__main__':
    unittest.main()
