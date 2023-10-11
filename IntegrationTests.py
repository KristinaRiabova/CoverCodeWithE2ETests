import unittest
import json
from update_user import app

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_user_intervals_endpoint(self):
        response = self.app.get('/user_intervals')
        self.assertEqual(response.status_code, 200)


    def test_get_total_user_online_time_endpoint(self):
        user_id = '5ed4eae5-d93c-6b18-be47-93a787c73bcb'
        response = self.app.get(f'/api/stats/user/total?userId={user_id}')
        self.assertEqual(response.status_code, 200)


    def test_get_user_average_time_endpoint(self):
        user_id = '88885096-1825-640b-1dff-281b668b24e5'
        response = self.app.get(f'/api/stats/user/average?userId={user_id}')
        self.assertEqual(response.status_code, 200)

    def test_forget_user(self):

        response = self.app.post('/api/user/forget?userId=02d4563d-5727-c811-b3b7-57a10f6be25a')


        self.assertEqual(response.status_code, 200)


        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('userId', data)

    def test_forget_user_missing_user_id(self):
        response = self.app.post('/api/user/forget')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
