import unittest
import requests
import json
from concurrent.futures import ThreadPoolExecutor

import helper

class TestIntegrity(unittest.TestCase):

	def test_password_change(self):
		(username, password) = helper.createUser()
		headers = {'Content-Type': 'application/json'}
		response = requests.post(helper.BASE_URL + 'users/' + username + '/login', headers=headers, data=json.dumps({'password': password}))
		self.assertEqual(response.status_code, 200, response.text)
		headers['Authorization'] = 'Bearer ' + response.json()['token']

		response = requests.put(helper.BASE_URL + 'users/' + username, headers=headers, data=json.dumps({'password': 'new-password'}))
		self.assertEqual(response.status_code, 200, response.text)

		response = requests.post(helper.BASE_URL + 'users/' + username + '/login', headers=headers, data=json.dumps({'password': password}))
		self.assertEqual(response.status_code, 401, response.text)
		response = requests.post(helper.BASE_URL + 'users/' + username + '/login', headers=headers, data=json.dumps({'password': 'new-password'}))
		self.assertEqual(response.status_code, 200, response.text)

	def test_concurrent_auto_create(self):
		headers = helper.createUserAndLogin()
		dataset = helper.createDataset(headers)
		count = 20

		def post(i):
			return requests.post(helper.getReadingsUrl(dataset['name'], 'node1', 'sensor1'), headers=headers, data=json.dumps([{'value': i, 'time': str(-i)}]))

		with ThreadPoolExecutor(count) as executor:
			responses = list(executor.map(post, range(count)))
		for response in responses:
			self.assertEqual(response.status_code, 200, response.text)

		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes', headers=headers)
		self.assertEqual([node['name'] for node in response.json()], ['node1'])
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/node1/sensors', headers=headers)
		self.assertEqual([sensor['name'] for sensor in response.json()], ['sensor1'])
		self.assertEqual(len(helper.getReadings(headers, dataset['name'], 'node1', 'sensor1')), count)

	def test_deleted_dataset_leaves_no_readings(self):
		headers = helper.createUserAndLogin()
		dataset = helper.createDataset(headers)
		helper.createReadings(headers, dataset['name'], 'node1', 'sensor1', [{}, {}, {}])

		response = requests.delete(helper.BASE_URL + 'datasets/' + dataset['name'], headers=headers)
		self.assertEqual(response.status_code, 200, response.text)

		helper.createDataset(headers, name=dataset['name'])
		helper.createNode(headers, dataset['name'], name='node1')
		helper.createSensor(headers, dataset['name'], 'node1', name='sensor1')
		self.assertEqual(helper.getReadings(headers, dataset['name'], 'node1', 'sensor1'), [])

	def test_deleted_user_tokens_are_invalid(self):
		headers = helper.createUserAndLogin()
		response = requests.get(helper.BASE_URL + 'datasets', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)

		username = requests.get(helper.BASE_URL + 'tokens', headers=headers).json()[0]['username']
		response = requests.delete(helper.BASE_URL + 'users/' + username, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)

		response = requests.get(helper.BASE_URL + 'datasets', headers=headers)
		self.assertEqual(response.status_code, 401, response.text)

if __name__ == '__main__':
	unittest.main()
