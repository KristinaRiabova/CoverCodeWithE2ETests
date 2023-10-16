from datetime import datetime
from update_user import app
import requests
import unittest.mock as mock
import json
import unittest
from update_user import (
    fetch_user_data,
    process_user_data,
    calculate_total_user_online_time,
    calculate_user_average_time,
    forget_user_data,
    parse_date,
)

class FunctionalTests(unittest.TestCase):

    def test_parse_date(self):
        date_string = "2023-10-16T14:30"
        expected_date = datetime(2023, 10, 16, 14, 30)
        self.assertEqual(parse_date(date_string), expected_date)

    def test_calculate_total_user_online_time(self):
        user_data_storage = {
            "user1": [["2023-10-16T14:30", "2023-10-16T15:00"]],
            "user2": [["2023-10-16T13:00", "2023-10-16T14:00"]],
        }
        total_time = calculate_total_user_online_time("user1", user_data_storage)
        self.assertEqual(total_time, {"totalTime": 1800})

    def test_calculate_user_average_time(self):
        user_data_storage = {
            "user1": [["2023-10-16T14:30", "2023-10-16T15:00"]],
            "user2": [["2023-10-16T13:00", "2023-10-16T14:00"]],
        }
        average_time = calculate_user_average_time("user1", user_data_storage)
        self.assertEqual(average_time, {"weeklyAverage": 900, "dailyAverage": 1800})

    def test_forget_user_data(self):
        user_id = "user1"
        user_data_storage = {
            "user1": [["2023-10-16T14:30", "2023-10-16T15:00"]],
            "user2": [["2023-10-16T13:00", "2023-10-16T14:00"]],
        }
        forget_user_data(user_id, user_data_storage)
        self.assertNotIn(user_id, user_data_storage)

    def test_process_user_data(self):
        user_data_storage = {}
        data = {
            'data': [
                {'userId': 'user1', 'isOnline': True, 'lastSeenDate': '2023-10-16T14:30'},
                {'userId': 'user2', 'isOnline': False, 'lastSeenDate': '2023-10-16T13:00'},
            ]
        }
        process_user_data(data, user_data_storage)
        self.assertIn('user1', user_data_storage)
        self.assertIn('user2', user_data_storage)

    @unittest.mock.patch('requests.get')
    def test_fetch_user_data(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {
            'data': [{'userId': 'user1', 'isOnline': True, 'lastSeenDate': '2023-10-16T14:30'}],
        }
        mock_get.return_value = mock_response

        data = fetch_user_data(1)
        self.assertEqual(data, {
            'data': [{'userId': 'user1', 'isOnline': True, 'lastSeenDate': '2023-10-16T14:30'}]
        })

    @unittest.mock.patch('requests.get')
    def test_fetch_user_data_request_failed(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Simulated error")

        data = fetch_user_data(1)
        self.assertIsNone(data)

    @unittest.mock.patch('requests.get')
    def test_fetch_user_data_invalid_response(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        data = fetch_user_data(1)
        self.assertIsNone(data)

    def test_get_total_user_online_time(self):
        client = app.test_client()
        response = client.get('/api/stats/user/total?userId=05227367-07f0-b3a5-8345-2513e0c45cca')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(isinstance(data, dict) and 'totalTime' in data)

    def test_get_user_average_time(self):
        client = app.test_client()
        response = client.get('/api/stats/user/average?userId=2e164e3c-3abd-a835-8e00-a3fa4b1d636e')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(isinstance(data, dict) and 'weeklyAverage' in data and 'dailyAverage' in data)

    def test_forget_user(self):
        client = app.test_client()
        user_id = '02d4563d-5727-c811-b3b7-57a10f6be25a'
        response = client.post(f'/api/user/forget?userId={user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('userId', data)
        self.assertEqual(data['userId'], user_id)




if __name__ == '__main__':
    unittest.main()
