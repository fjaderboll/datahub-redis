import unittest
import requests
import json
import random

class TestUser(unittest.TestCase):
	USERNAME = 'laban-' + str(random.randint(0, 1000))
	PASSWORD = 'abc123'

	def test_create(self):
		user = {
			'username': self.USERNAME,
			'password': self.PASSWORD
		}
		headers = {
			'Content-Type': 'application/json'
		}
		response = requests.post('http://localhost:2070/users/', headers=headers, data=json.dumps(user))
		self.assertEqual(response.status_code, 200, response.text)

	def test_login(self):
		data = {
			'password': self.PASSWORD
		}
		headers = {
			'Content-Type': 'application/json'
		}
		response = requests.post('http://localhost:2070/users/' + self.USERNAME + '/login', headers=headers, data=json.dumps(data))
		self.assertEqual(response.status_code, 200, response.text)

	def test_impersonate(self):
		response = requests.get('http://localhost:2070/users/' + self.USERNAME + '/impersonate')
		self.assertEqual(response.status_code, 200, response.text)

	def test_get(self):
		response = requests.get('http://localhost:2070/users/' + self.USERNAME)
		self.assertEqual(response.status_code, 200, response.text)

	def test_list(self):
		response = requests.get('http://localhost:2070/users/')
		self.assertEqual(response.status_code, 200, response.text)

if __name__ == '__main__':
	unittest.main()
