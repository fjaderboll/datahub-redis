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

if __name__ == '__main__':
	unittest.main()
