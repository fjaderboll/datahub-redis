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
