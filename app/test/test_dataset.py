import unittest
import requests
import json
import random

import helper

class TestDataset(unittest.TestCase):

	def test(self):
		headers = helper.createUserAndLogin()

		# create dataset
		datasetName = helper.getRandomName('dataset-')
		createData = {
			'name': datasetName,
			'desc': 'description1'
		}
		response = requests.post(helper.BASE_URL + 'datasets/', headers=headers, data=json.dumps(createData))
		self.assertEqual(response.status_code, 200, response.text)
		dataset1 = response.json()
		self.assertEqual(dataset1['name'], datasetName)
		self.assertEqual(dataset1['desc'], createData['desc'])

		# get all datasets
		response = requests.get(helper.BASE_URL + 'datasets', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		datasets = response.json()
		self.assertEqual(len(datasets), 1)
		self.assertEqual(datasets[0]['name'], datasetName)

		# get dataset
		response = requests.get(helper.BASE_URL + 'datasets/' + datasetName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		dataset2 = response.json()
		self.assertEqual(dataset2['name'], datasetName)
		self.assertEqual(dataset2['desc'], createData['desc'])

		# update dataset
		newDatasetName = helper.getRandomName('dataset-')
		updatedData = {
			'name': newDatasetName,
			'desc': 'description2'
		}
		response = requests.put(helper.BASE_URL + 'datasets/' + datasetName, headers=headers, data=json.dumps(updatedData))
		self.assertEqual(response.status_code, 200, response.text)
		updatedDataset = response.json()
		self.assertEqual(updatedDataset['name'], newDatasetName)
		self.assertEqual(updatedDataset['desc'], updatedData['desc'])
		datasetName = newDatasetName

		# get dataset
		response = requests.get(helper.BASE_URL + 'datasets/' + datasetName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		updatedDataset = response.json()
		self.assertEqual(updatedDataset['name'], datasetName)
		self.assertEqual(updatedDataset['desc'], updatedData['desc'])

		# delete dataset
		response = requests.delete(helper.BASE_URL + 'datasets/' + datasetName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)

		# get dataset
		response = requests.get(helper.BASE_URL + 'datasets/' + datasetName, headers=headers)
		self.assertEqual(response.status_code, 404, response.text)

		# get all datasets
		response = requests.get(helper.BASE_URL + 'datasets', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		datasets = response.json()
		self.assertEqual(len(datasets), 0)

if __name__ == '__main__':
	unittest.main()
