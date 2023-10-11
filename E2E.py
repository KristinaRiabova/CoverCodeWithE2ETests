import unittest
import threading
import time
import requests
from update_user import app

class TestE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_thread = threading.Thread(target=app.run, kwargs={'debug': False})
        cls.app_thread.daemon = True
        cls.app_thread.start()
        cls.wait_for_app_to_start()

    @classmethod
    def tearDownClass(cls):
        cls.app_thread.join(timeout=1)

    @classmethod
    def wait_for_app_to_start(cls):
        time.sleep(2)

    def test_get_total_user_online_time(self):
        user_id = '88885096-1825-640b-1dff-281b668b24e5'
        response = requests.get(f'http://localhost:5000/api/stats/user/total?userId={user_id}')
        self.assertEqual(response.status_code, 200)

    def test_get_user_average_time(self):
        user_id = '88885096-1825-640b-1dff-281b668b24e5'
        response = requests.get(f'http://localhost:5000/api/stats/user/average?userId={user_id}')
        self.assertEqual(response.status_code, 200)

    def test_forget_user(self):
        user_id = '8b0b5db6-19d6-d777-575e-915c2a77959a'
        response = requests.post(f'http://localhost:5000/api/user/forget?userId={user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('userId', data)
        self.assertEqual(data['userId'], user_id)


if __name__ == '__main__':
    unittest.main()
