import unittest
import time

import helper

standalone = False

class TestPerf(unittest.TestCase):

	def log(self, text, startTime):
		if standalone:
			message = text
			if startTime:
				message += ' in {0:.3f} seconds'.format(time.time() - startTime)
			print(message)

	def test(self):
		st = time.time()
		username = helper.getRandomName('perfuser-')
		headers = helper.createUserAndLogin(username)
		self.log('Logged in', st)

		datasetCount = 2
		nodeCount = 10
		sensorCount = 3
		readingCount = 100

		st = time.time()
		datasets = []
		for i in range(0, datasetCount):
			dataset = helper.createDataset(headers)
			dataset['nodes'] = []

			for j in range(0, nodeCount):
				node = helper.createNode(headers, dataset['name'])
				node['sensors'] = []

				for k in range(0, sensorCount):
					sensor = helper.createSensor(headers, dataset['name'], node['name'])
					node['sensors'].append(sensor)
				dataset['nodes'].append(node)
			datasets.append(dataset)

		self.log('Created {} datasets, {} nodes and {} sensors'.format(datasetCount, datasetCount*nodeCount, datasetCount*nodeCount*sensorCount), st)

		st1 = time.time()
		for dataset in datasets:
			for node in dataset['nodes']:
				for sensor in node['sensors']:
					st2 = time.time()
					for i in range(0, readingCount):
						helper.createReading(headers, dataset['name'], node['name'], sensor['name'])
					self.log('Created {} readings'.format(readingCount), st2)

		self.log('Created {} readings'.format(datasetCount*nodeCount*sensorCount*readingCount), st1)

		st1 = time.time()
		for dataset in datasets:
			for node in dataset['nodes']:
				for sensor in node['sensors']:
					st2 = time.time()
					readings = helper.getReadings(headers, dataset['name'], node['name'], sensor['name'])
					self.log('Loaded {} readings'.format(len(readings)), st2)

		self.log('Loaded {} readings'.format(datasetCount*nodeCount*sensorCount*readingCount), st1)

if __name__ == '__main__':
	standalone = True
	unittest.main()
