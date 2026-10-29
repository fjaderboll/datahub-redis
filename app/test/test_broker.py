import unittest
import requests
import json

import helper

class TestBroker(unittest.TestCase):

	def login(self, username, password):
		response = requests.post(helper.BASE_URL + 'users/' + username + '/login', headers={'Content-Type': 'application/json'}, data=json.dumps({'password': password}))
		response.raise_for_status()
		return {'Authorization': 'Bearer ' + response.json()['token']}

	def test_admin_only(self):
		(username, password) = helper.createUser()
		headers = self.login(username, password)
		isAdmin = requests.get(helper.BASE_URL + 'users/' + username, headers=headers).json()['isAdmin']

		response = requests.get(helper.BASE_URL + 'state/broker', headers=headers)
		self.assertEqual(response.status_code, 200 if isAdmin else 403, response.text)

	@unittest.skipUnless(helper.ADMIN_USERNAME and helper.ADMIN_PASSWORD, 'needs ADMIN_USERNAME and ADMIN_PASSWORD')
	def test_state(self):
		headers = self.login(helper.ADMIN_USERNAME, helper.ADMIN_PASSWORD)
		response = requests.get(helper.BASE_URL + 'state/broker', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		broker = response.json()
		self.assertTrue(broker['version'])
		self.assertGreaterEqual(broker['connections'], 1)

		# the app's own clients are always connected, subscribed to the readings sent to datahub
		appClients = [client for client in broker['clients'] if client['isApp']]
		self.assertTrue(appClients)
		for client in appClients:
			self.assertTrue(client['connected'])
			self.assertTrue(client['connectedAt'], 'the login is recorded')
			self.assertTrue(all(s['topic'].startswith('$share/datahub/in/') for s in client['subscriptions']))

if __name__ == '__main__':
	unittest.main()
