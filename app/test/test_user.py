import unittest
import os
import requests
import json
import random

class TestUser(unittest.TestCase):
	BASE_URL = os.environ.get('BASE_URL', 'http://localhost:2070/')
	USERNAME = 'laban-' + str(random.randint(0, 1000))
	PASSWORD = 'abc123'
	HEADERS = {
		'Content-Type': 'application/json'
	}

	def test(self):
		# create
		createUser = {
			'username': self.USERNAME,
			'password': self.PASSWORD
		}
		response = requests.post(self.BASE_URL + 'users/', headers=self.HEADERS, data=json.dumps(createUser))
		self.assertEqual(response.status_code, 200, response.text)
		user = response.json()
		self.assertEqual(user['username'], self.USERNAME)
		isAdmin = user['isAdmin']

		# login
		data = {
			'password': self.PASSWORD
		}
		response = requests.post(self.BASE_URL + 'users/' + self.USERNAME + '/login', headers=self.HEADERS, data=json.dumps(data))
		self.assertEqual(response.status_code, 200, response.text)
		tokenInfo = response.json()
		self.assertEqual(tokenInfo['username'], self.USERNAME)
		self.assertEqual(tokenInfo['enabled'], True)
		self.HEADERS['Authorization'] = 'Bearer ' + tokenInfo['token']

		# get
		response = requests.get(self.BASE_URL + 'users/' + self.USERNAME, headers=self.HEADERS)
		self.assertEqual(response.status_code, 200, response.text)
		user = response.json()
		self.assertEqual(user['username'], self.USERNAME)
		self.assertEqual(user['isAdmin'], False)

		# impersonate
		response = requests.post(self.BASE_URL + 'users/' + self.USERNAME + '/impersonate', headers=self.HEADERS)
		self.assertEqual(response.status_code, 200 if isAdmin else 403, response.text)

		# list users
		response = requests.get(self.BASE_URL + 'users/', headers=self.HEADERS)
		self.assertEqual(response.status_code, 200 if isAdmin else 403, response.text)

if __name__ == '__main__':
	unittest.main()
