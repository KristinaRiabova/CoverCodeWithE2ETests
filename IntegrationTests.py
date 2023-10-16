import unittest
import json
from update_user import app

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_user_intervals_endpoint(self):
        response = self.app.get('/user_intervals')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertTrue(all(isinstance(k, str) and isinstance(v, list) for k, v in data.items()))

    def test_get_total_user_online_time_endpoint(self):
        user_id = '5ed4eae5-d93c-6b18-be47-93a787c73bcb'
        response = self.app.get(f'/api/stats/user/total?userId={user_id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        if "error" not in data:
            self.assertIsInstance(data, dict)
            self.assertIn("totalTime", data)

    def test_get_user_average_time_endpoint(self):
        user_id = '88885096-1825-640b-1dff-281b668b24e5'
        response = self.app.get(f'/api/stats/user/average?userId={user_id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        if "error" not in data:
            self.assertIsInstance(data, dict)
            self.assertIn("weeklyAverage", data)
            self.assertIn("dailyAverage", data)

    def test_forget_user(self):
        response = self.app.post('/api/user/forget?userId=02d4563d-5727-c811-b3b7-57a10f6be25a')
        self.assertEqual(response.status_code, 200)


        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('userId', data)

    def test_forget_user_missing_user_id(self):
        response = self.app.post('/api/user/forget')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('error', data)

    def test_user_average_time_no_intervals(self):
        user_id = 'no_intervals_user'
        response = self.app.get(f'/api/stats/user/average?userId={user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertEqual(data['weeklyAverage'], 0)
        self.assertEqual(data['dailyAverage'], 0)

    def test_invalid_user_id_average_time(self):
        invalid_user_id = 'invalid_user_id'
        response = self.app.get(f'/api/stats/user/average?userId={invalid_user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('error', data)

    def test_forget_user_invalid_user_id(self):
        invalid_user_id = 'invalid_user_id'
        response = self.app.post(f'/api/user/forget?userId={invalid_user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('error', data)

    def test_forget_user_already_forgotten(self):

        response = self.app.post('/api/user/forget?userId=02d4563d-5727-c811-b3b7-57a10f6be25a')
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/api/user/forget?userId=02d4563d-5727-c811-b3b7-57a10f6be25a')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('error', data)
    def test_invalid_user_id(self):
        invalid_user_id = 'invalid_user_id'
        response = self.app.get(f'/api/stats/user/total?userId={invalid_user_id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(data, dict)
        self.assertIn('error', data)

    def test_get_user_average1_time_endpoint(self):
        user_id = '88885096-1825-640b-1dff-281b668b24e5'
        response = self.app.get(f'/api/stats/user/average?userId={user_id}')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        if "error" not in data:
            self.assertIsInstance(data, dict)
            self.assertIn("weeklyAverage", data)
            self.assertIn("dailyAverage", data)
            self.assertGreater(data["weeklyAverage"], 0)
            self.assertGreater(data["dailyAverage"], 0)


if __name__ == '__main__':
    unittest.main()

