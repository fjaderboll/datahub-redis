import unittest
import requests
import json

import helper

class TestSensor(unittest.TestCase):

	def test(self):
		headers = helper.createUserAndLogin()
		dataset = helper.createDataset(headers)
		node = helper.createNode(headers, dataset['name'])

		# create sensor
		sensorName = helper.getRandomName('sensor-')
		desc = 'desc3'
		sensor1 = helper.createSensor(headers, dataset['name'], node['name'], name=sensorName, desc=desc)
		self.assertEqual(sensor1['name'], sensorName)
		self.assertEqual(sensor1['desc'], desc)

		# get all sensors
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + node['name'] + '/sensors', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		sensors = response.json()
		self.assertEqual(len(sensors), 1)
		self.assertEqual(sensors[0]['name'], sensorName)

		# get sensor
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + node['name'] + '/sensors/' + sensorName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		sensor2 = response.json()
		self.assertEqual(sensor2['name'], sensorName)
		self.assertEqual(sensor2['desc'], desc)

		# update sensor
		newSensorName = helper.getRandomName('sensor-')
		updatedData = {
			'name': newSensorName,
			'desc': 'description4',
			'unit': 'unit4'
		}
		response = requests.put(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + node['name'] + '/sensors/' + sensorName, headers=headers, data=json.dumps(updatedData))
		self.assertEqual(response.status_code, 200, response.text)
		updatedSensor = response.json()
		self.assertEqual(updatedSensor['name'], newSensorName)
		self.assertEqual(updatedSensor['desc'], updatedData['desc'])
		self.assertEqual(updatedSensor['unit'], updatedData['unit'])
		sensorName = newSensorName

		# get sensor
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + node['name'] + '/sensors/' + sensorName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		updatedSensor = response.json()
		self.assertEqual(updatedSensor['name'], sensorName)
		self.assertEqual(updatedSensor['desc'], updatedData['desc'])

		# delete sensor
		response = requests.delete(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + node['name'] + '/sensors/' + sensorName, headers=headers)
		self.assertEqual(response.status_code, 200, response.text)

		# get sensor
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + node['name'] + '/sensors/' + sensorName, headers=headers)
		self.assertEqual(response.status_code, 404, response.text)

		# get all sensors
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + node['name'] + '/sensors', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		sensors = response.json()
		self.assertEqual(len(sensors), 0)

if __name__ == '__main__':
	unittest.main()
