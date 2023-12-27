import unittest
import requests
import json

import util

class TestDataset(unittest.TestCase):

	def test(self):
		headers = util.createUserAndLogin()

		# create dataset
		createData = {
			'name': 'dataset1',
			'desc': 'description1'
		}
		response = requests.post(util.BASE_URL + 'datasets/', headers=headers, data=json.dumps(createData))
		response.raise_for_status()
		dataset1 = response.json()
		self.assertEqual(dataset1['name'], createData['name'])
		self.assertEqual(dataset1['desc'], createData['desc'])

		# get
		response = requests.get(util.BASE_URL + 'datasets/' + dataset1['name'], headers=headers)
		response.raise_for_status()
		dataset2 = response.json()
		self.assertEqual(dataset2['name'], createData['name'])
		self.assertEqual(dataset2['desc'], createData['desc'])

if __name__ == '__main__':
	unittest.main()
