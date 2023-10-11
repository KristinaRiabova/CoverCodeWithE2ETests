import unittest
from update_user import app
import json

class FunctionalTests(unittest.TestCase):

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
