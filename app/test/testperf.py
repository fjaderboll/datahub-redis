import unittest
import os
import requests
import json
import random

class TestPerf(unittest.TestCase):
	BASE_URL = os.environ.get('BASE_URL', 'http://localhost:2070/')

	def test_perf(self):
		testId = str(random.randint(0, 1000))
		for i in range(1, 1000):
			self.create_user(testId + '.' + str(i))

	def create_user(self, suffix):
		user = {
			'username': 'perf-' + suffix,
			'password': 'abc123'
		}
		headers = {
			'Content-Type': 'application/json'
		}
		response = requests.post(self.BASE_URL + 'users/', headers=headers, data=json.dumps(user))
		self.assertEqual(response.status_code, 200, response.text)

if __name__ == '__main__':
	unittest.main()
