import unittest
import requests
import json

import helper

class TestAuth(unittest.TestCase):

	def login(self, username, password):
		return requests.post(helper.BASE_URL + 'users/' + username + '/login', headers={'Content-Type': 'application/json'}, data=json.dumps({'password': password}))

	def bearer(self, token):
		return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

	def test_password(self):
		(username, password) = helper.createUser()
		self.assertEqual(self.login(username, password).status_code, 200)
		self.assertEqual(self.login(username, password + 'x').status_code, 401)

		# change password
		token = self.login(username, password).json()['token']
		response = requests.put(helper.BASE_URL + 'users/' + username, headers=self.bearer(token), data=json.dumps({'password': 'new-password'}))
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(self.login(username, password).status_code, 401)
		self.assertEqual(self.login(username, 'new-password').status_code, 200)

	def test_tokens(self):
		(username, password) = helper.createUser()
		loginToken = self.login(username, password).json()['token']

		# the full token is only given when created, after that only its label
		response = requests.post(helper.BASE_URL + 'tokens/', headers=self.bearer(loginToken), data=json.dumps({'desc': 'device', 'ttl': 0}))
		self.assertEqual(response.status_code, 200, response.text)
		created = response.json()
		token = created['token']
		self.assertEqual(len(token), 32)

		response = requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(token))
		self.assertEqual(response.status_code, 200, response.text)
		listed = next(t for t in response.json() if t['id'] == created['id'])
		self.assertEqual(listed['token'], token[0:2] + '...' + token[-2:])

		# revoke
		response = requests.delete(helper.BASE_URL + 'tokens/' + created['id'], headers=self.bearer(loginToken))
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(token)).status_code, 401)

		# logout invalidates the token used
		response = requests.post(helper.BASE_URL + 'users/' + username + '/logout', headers=self.bearer(loginToken))
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(loginToken)).status_code, 401)

if __name__ == '__main__':
	unittest.main()
