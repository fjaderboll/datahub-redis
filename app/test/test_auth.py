import unittest
import requests
import json

import helper

class TestAuth(unittest.TestCase):

	def login(self, username, password):
		return requests.post(helper.BASE_URL + 'users/' + username + '/login', headers={'Content-Type': 'application/json'}, data=json.dumps({'password': password}))

	def bearer(self, token):
		return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

	def mqttLogin(self, username, password):
		# what NanoMQ calls when a client connects
		data = {'clientid': 'test-client', 'username': username, 'password': password}
		return requests.post(helper.BASE_URL + 'mqtt/authenticate', headers={'Content-Type': 'application/json'}, data=json.dumps(data))

	def mqttAuthorize(self, username, topic):
		# what NanoMQ calls before letting a client publish
		data = {'username': username, 'access': '2', 'topic': topic}
		return requests.post(helper.BASE_URL + 'mqtt/authorize', headers={'Content-Type': 'application/json'}, data=json.dumps(data))

	def setAllowNonAdminLogin(self, adminToken, allow):
		response = requests.put(helper.BASE_URL + 'state/settings', headers=self.bearer(adminToken), data=json.dumps({'allowNonAdminLogin': allow}))
		self.assertEqual(response.status_code, 200, response.text)

	def createToken(self, loginToken, **data):
		response = requests.post(helper.BASE_URL + 'tokens/', headers=self.bearer(loginToken), data=json.dumps(data))
		self.assertEqual(response.status_code, 200, response.text)
		return response.json()

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

	def test_mqtt_login(self):
		(username, password) = helper.createUser()
		(otherUsername, _) = helper.createUser()
		loginToken = self.login(username, password).json()['token']
		token = self.createToken(loginToken, desc='device', ttl=0)

		# any of the user's tokens is the password, the user's password is not
		self.assertEqual(self.mqttLogin(username, token['token']).status_code, 200)
		self.assertEqual(self.mqttLogin(username, loginToken).status_code, 200)
		self.assertEqual(self.mqttLogin(username, password).status_code, 403)
		self.assertEqual(self.mqttLogin(username, '').status_code, 403)

		# topic permissions are checked by username, so it must be the token's own user
		self.assertEqual(self.mqttLogin(otherUsername, token['token']).status_code, 403)

		# a disabled token can't log in
		response = requests.put(helper.BASE_URL + 'tokens/' + token['id'], headers=self.bearer(loginToken), data=json.dumps({'enabled': False}))
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(self.mqttLogin(username, token['token']).status_code, 403)

	def test_mqtt_only_token(self):
		(username, password) = helper.createUser()
		loginToken = self.login(username, password).json()['token']

		self.assertEqual(self.createToken(loginToken, desc='api', ttl=0)['mqttOnly'], False)
		token = self.createToken(loginToken, desc='mqtt', ttl=0, mqttOnly=True)
		self.assertEqual(token['mqttOnly'], True)

		# logs in to MQTT, but can't be used for the REST API
		self.assertEqual(self.mqttLogin(username, token['token']).status_code, 200)
		self.assertEqual(requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(token['token'])).status_code, 401)

		response = requests.get(helper.BASE_URL + 'tokens/' + token['id'], headers=self.bearer(loginToken))
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(response.json()['mqttOnly'], True)

		# the flag can be changed
		response = requests.put(helper.BASE_URL + 'tokens/' + token['id'], headers=self.bearer(loginToken), data=json.dumps({'mqttOnly': False}))
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(response.json()['mqttOnly'], False)
		self.assertEqual(requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(token['token'])).status_code, 200)

	@unittest.skipUnless(helper.ADMIN_USERNAME and helper.ADMIN_PASSWORD, 'needs ADMIN_USERNAME and ADMIN_PASSWORD')
	def test_non_admin_lockout(self):
		adminToken = self.login(helper.ADMIN_USERNAME, helper.ADMIN_PASSWORD).json()['token']
		(username, password) = helper.createUser()
		loginToken = self.login(username, password).json()['token']
		mqttToken = self.createToken(loginToken, desc='mqtt', ttl=0, mqttOnly=True)['token']
		dataset = helper.createDataset(self.bearer(loginToken))
		topic = 'in/datasets/' + dataset['name'] + '/readings'
		self.assertEqual(self.mqttAuthorize(username, topic).status_code, 200)

		self.setAllowNonAdminLogin(adminToken, False)
		try:
			# the password, all tokens, and clients already connected to MQTT stop working
			self.assertEqual(self.login(username, password).status_code, 401)
			self.assertEqual(requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(loginToken)).status_code, 401)
			self.assertEqual(self.mqttLogin(username, mqttToken).status_code, 403)
			self.assertEqual(self.mqttLogin(username, loginToken).status_code, 403)
			self.assertEqual(self.mqttAuthorize(username, topic).status_code, 403)

			# but not for administrators, who can turn it back on
			self.assertEqual(requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(adminToken)).status_code, 200)
		finally:
			self.setAllowNonAdminLogin(adminToken, True)

		# and work again when it's turned back on
		self.assertEqual(requests.get(helper.BASE_URL + 'tokens/', headers=self.bearer(loginToken)).status_code, 200)
		self.assertEqual(self.mqttLogin(username, mqttToken).status_code, 200)

if __name__ == '__main__':
	unittest.main()
