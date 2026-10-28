import unittest
import requests
import json

import helper

class TestNode(unittest.TestCase):

	def test(self):
		headers = helper.createUserAndLogin()
		dataset = helper.createDataset(headers)

		# create node
		nodeName = helper.getRandomName('node-')
		desc = 'desc2'
		node1 = helper.createNode(headers, dataset['name'], name=nodeName, desc=desc)
		self.assertEqual(node1['name'], nodeName)
		self.assertEqual(node1['desc'], desc)

		# get all nodes
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		nodes = response.json()
		self.assertEqual(len(nodes), 1)
		self.assertEqual(nodes[0]['name'], nodeName)
		self.assertEqual(nodes[0]['sensorCount'], 0)

		# the list counts the node's sensors, also in the dataset
		sensor1 = helper.createSensor(headers, dataset['name'], nodeName)
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(response.json()[0]['sensorCount'], 1)
		self.assertIsNone(response.json()[0]['lastTimestamp'])
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'], headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(response.json()['nodes'][0]['sensorCount'], 1)

		# the list has the newest reading of all the node's sensors
		sensor2 = helper.createSensor(headers, dataset['name'], nodeName)
		helper.createReadings(headers, dataset['name'], nodeName, sensor1['name'], [{'time': '2026-01-01T12:00:00Z'}])
		helper.createReadings(headers, dataset['name'], nodeName, sensor2['name'], [{'time': '2026-01-02T12:00:00Z'}])
		helper.createReadings(headers, dataset['name'], nodeName, sensor1['name'], [{'time': '2025-12-31T12:00:00Z'}])
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'], headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(response.json()['nodes'][0]['lastTimestamp'], '2026-01-02T12:00:00+00:00')

		# get node
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + nodeName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		node2 = response.json()
		self.assertEqual(node2['name'], nodeName)
		self.assertEqual(node2['desc'], desc)

		# update node
		newNodeName = helper.getRandomName('node-')
		updatedData = {
			'name': newNodeName,
			'desc': 'description2'
		}
		response = requests.put(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + nodeName, headers=headers, data=json.dumps(updatedData))
		self.assertEqual(response.status_code, 200, response.text)
		updatedNode = response.json()
		self.assertEqual(updatedNode['name'], newNodeName)
		self.assertEqual(updatedNode['desc'], updatedData['desc'])
		nodeName = newNodeName

		# get node
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + nodeName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		updatedNode = response.json()
		self.assertEqual(updatedNode['name'], nodeName)
		self.assertEqual(updatedNode['desc'], updatedData['desc'])

		# delete node
		response = requests.delete(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + nodeName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)

		# get node
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + nodeName, headers=headers)
		self.assertEqual(response.status_code, 404, response.text)

		# get all datasets
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		nodes = response.json()
		self.assertEqual(len(nodes), 0)

if __name__ == '__main__':
	unittest.main()
