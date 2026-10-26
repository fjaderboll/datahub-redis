import unittest
import requests
import json
import threading
import time

import helper

class TestReading(unittest.TestCase):

	def setUp(self):
		self.headers = helper.createUserAndLogin()
		dataset = helper.createDataset(self.headers)
		node = helper.createNode(self.headers, dataset['name'])
		sensor = helper.createSensor(self.headers, dataset['name'], node['name'])
		self.names = (dataset['name'], node['name'], sensor['name'])
		self.url = helper.getReadingsUrl(*self.names)

	def postReadings(self, readings):
		return requests.post(self.url, headers=self.headers, data=json.dumps(readings))

	def test_without_time(self):
		# readings without a time get the current one, also when many arrive within the same millisecond
		values = list(range(200))
		response = self.postReadings([{'value': v} for v in values])
		self.assertEqual(response.status_code, 200, response.text)
		created = response.json()
		self.assertEqual([r['value'] for r in created], values)
		self.assertEqual(len({r['timestamp'] for r in created}), len(values))

		readings = helper.getReadings(self.headers, *self.names)
		self.assertEqual(sorted(r['value'] for r in readings), values)

	def test_duplicate_time(self):
		reading = helper.createReading(self.headers, *self.names)[0]

		response = self.postReadings([{'value': 1, 'time': reading['timestamp']}])
		self.assertEqual(response.status_code, 400, response.text)
		self.assertIn('already has a reading', response.json()['message'])

	def test_stream(self):
		# every reading of a burst is streamed, the stream only has readings of the user's own datasets
		count = 100
		received = []
		def listen():
			with requests.get(helper.BASE_URL + 'state/readings', headers=self.headers, stream=True, timeout=10) as response:
				for line in response.iter_lines():
					received.append(json.loads(line)['value'])
					if len(received) == count:
						break
		listener = threading.Thread(target=listen, daemon=True)
		listener.start()
		time.sleep(1) # until subscribed

		response = self.postReadings([{'value': v} for v in range(count)])
		self.assertEqual(response.status_code, 200, response.text)

		listener.join(10)
		self.assertEqual(received, list(range(count)))

	def test_overview(self):
		# a sensor is silent when it has been quiet for much longer than it usually is
		(datasetName, nodeName, quietSensorName) = self.names
		newSensorName = helper.createSensor(self.headers, datasetName, nodeName)['name']
		hourlyNodeName = helper.createNode(self.headers, datasetName)['name']
		hourlySensorName = helper.createSensor(self.headers, datasetName, hourlyNodeName)['name']
		helper.createNode(self.headers, datasetName) # without sensors

		helper.createReadings(self.headers, datasetName, nodeName, quietSensorName, [{'time': str(-3600 - 60 * i)} for i in range(10)])
		helper.createReadings(self.headers, datasetName, nodeName, newSensorName, [{'time': '-60'}, {'time': '-120'}])
		helper.createReadings(self.headers, datasetName, hourlyNodeName, hourlySensorName, [{'time': str(-600 - 3600 * i)} for i in range(4)])

		response = requests.get(helper.BASE_URL + 'state/overview', headers=self.headers)
		self.assertEqual(response.status_code, 200, response.text)
		overview = response.json()

		self.assertEqual((overview['datasets'], overview['nodes'], overview['sensors']), (1, 3, 3))
		self.assertEqual(overview['readings24h'], 16)
		self.assertEqual(overview['silentSensors'], 1)
		self.assertEqual([node['nodeName'] for node in overview['recentNodes']], [nodeName, hourlyNodeName])

		sensors = {sensor['name']: sensor for node in overview['recentNodes'] for sensor in node['sensors']}
		# relative times are resolved one reading at a time, so they can be a millisecond apart
		self.assertAlmostEqual(sensors[quietSensorName]['interval'], 60, delta=0.01)
		self.assertIsNone(sensors[newSensorName]['interval'])
		self.assertAlmostEqual(sensors[hourlySensorName]['interval'], 3600, delta=0.01)
		self.assertEqual([name for name, sensor in sensors.items() if sensor['silent']], [quietSensorName])

		self.assertEqual([node['nodeName'] for node in overview['silentNodes']], [nodeName])

if __name__ == '__main__':
	unittest.main()
