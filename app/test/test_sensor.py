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

	def test_units(self):
		# each unit once and sorted, without empty ones or those of other datasets
		headers = helper.createUserAndLogin()
		dataset = helper.createDataset(headers)
		node = helper.createNode(headers, dataset['name'])
		for unit in ['V', '°C', '%', 'V', '']:
			helper.createSensor(headers, dataset['name'], node['name'], unit=unit)
		otherDataset = helper.createDataset(headers)
		helper.createSensor(headers, otherDataset['name'], helper.createNode(headers, otherDataset['name'])['name'], unit='K')

		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/units', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(response.json(), ['%', 'V', '°C'])

	def test_guess_unit(self):
		# without a unit, a sensor gets the one most used by sensors with the same name in the dataset
		headers = helper.createUserAndLogin()
		dataset = helper.createDataset(headers)
		nodeNames = [helper.createNode(headers, dataset['name'])['name'] for _ in range(5)]
		for nodeName, unit in zip(nodeNames, ['°C', '°C', 'K']):
			helper.createSensor(headers, dataset['name'], nodeName, name='temperature', unit=unit)
		otherDataset = helper.createDataset(headers)
		for _ in range(3):
			helper.createSensor(headers, otherDataset['name'], helper.createNode(headers, otherDataset['name'])['name'], name='temperature', unit='F')

		sensor = helper.createSensor(headers, dataset['name'], nodeNames[3], name='temperature', unit='')
		self.assertEqual(sensor['unit'], '°C')

		# also when created by its first reading
		helper.createReading(headers, dataset['name'], nodeNames[4], 'temperature')
		response = requests.get(helper.BASE_URL + 'datasets/' + dataset['name'] + '/nodes/' + nodeNames[4] + '/sensors/temperature', headers=headers)
		self.assertEqual(response.status_code, 200, response.text)
		self.assertEqual(response.json()['unit'], '°C')

		# a given unit is kept, and without sensors of the same name there is nothing to guess from
		self.assertEqual(helper.createSensor(headers, dataset['name'], nodeNames[3], name='temperature2', unit='K')['unit'], 'K')
		self.assertEqual(helper.createSensor(headers, dataset['name'], nodeNames[3], name='humidity', unit='')['unit'], '')

if __name__ == '__main__':
	unittest.main()
