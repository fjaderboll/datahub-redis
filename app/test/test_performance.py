import unittest
import time

import helper

standalone = False
threads = 1

class TestPerf(unittest.TestCase):

	def test(self):
		st = time.time()
		username = helper.getRandomName('perfuser-')
		headers = helper.createUserAndLogin(username)
		log('Logged in as ' + username, st)

		datasetCount = 2
		nodeCount = 10
		sensorCount = 3
		readingCount = 50

		st = time.time()
		datasets = []
		for i in range(datasetCount):
			dataset = helper.createDataset(headers)
			dataset['nodes'] = []

			for j in range(nodeCount):
				node = helper.createNode(headers, dataset['name'])
				node['sensors'] = []

				for k in range(sensorCount):
					sensor = helper.createSensor(headers, dataset['name'], node['name'])
					node['sensors'].append(sensor)
				dataset['nodes'].append(node)
			datasets.append(dataset)
		log('Created {} datasets, {} nodes and {} sensors'.format(datasetCount, datasetCount*nodeCount, datasetCount*nodeCount*sensorCount), st)

		self.createReadings(headers, datasets, 3, readingCount)
		self.createReadings(headers, datasets, 2, readingCount)
		self.createReadings(headers, datasets, 1, readingCount)
		self.createReadings(headers, datasets, 0, readingCount)

		self.loadReadings(headers, datasets, 3)
		self.loadReadings(headers, datasets, 2)
		self.loadReadings(headers, datasets, 1)
		self.loadReadings(headers, datasets, 0)

		self.deleteReadings(headers, datasets, 3, -5)
		self.deleteReadings(headers, datasets, 2, -10)
		self.deleteReadings(headers, datasets, 1, -15)
		self.deleteReadings(headers, datasets, 0)

	def createReadings(self, headers, datasets, level, count):
		st = time.time()
		n = 0
		r = 0
		t = 0
		datas = []
		for dataset in datasets:
			for node in dataset['nodes']:
				for sensor in node['sensors']:
					for i in range(count):
						data = {
							'datasetName': dataset['name'],
							'nodeName': node['name'],
							'sensorName': sensor['name'],
							'time': str(-t)
						}
						t += 0.01
						datas.append(data)

					if level == 3:
						helper.createReadings(headers, dataset['name'], node['name'], sensor['name'], datas)
						n += len(datas)
						r += 1
						datas = []
				if level == 2:
					helper.createReadings(headers, dataset['name'], node['name'], None, datas)
					n += len(datas)
					r += 1
					datas = []
			if level == 1:
				helper.createReadings(headers, dataset['name'], None, None, datas)
				n += len(datas)
				r += 1
				datas = []
		if level == 0:
			helper.createReadings(headers, None, None, None, datas)
			n += len(datas)
			r += 1
			datas = []

		log('Created {} readings in {} requests'.format(n, r), st)

	def loadReadings(self, headers, datasets, level):
		st = time.time()
		n = 0
		r = 0
		for dataset in datasets:
			for node in dataset['nodes']:
				for sensor in node['sensors']:
					if level == 3:
						readings = helper.getReadings(headers, dataset['name'], node['name'], sensor['name'])
						n += len(readings)
						r += 1
				if level == 2:
					readings = helper.getReadings(headers, dataset['name'], node['name'], None)
					n += len(readings)
					r += 1
			if level == 1:
				readings = helper.getReadings(headers, dataset['name'], None, None)
				n += len(readings)
				r += 1
		if level == 0:
			readings = helper.getReadings(headers, None, None, None)
			n += len(readings)
			r += 1

		log('Loaded {} readings in {} requests'.format(n, r), st)

	def deleteReadings(self, headers, datasets, level, after=-120):
		st = time.time()
		n = 0
		r = 0
		for dataset in datasets:
			for node in dataset['nodes']:
				for sensor in node['sensors']:
					if level == 3:
						n += helper.deleteReadings(headers, dataset['name'], node['name'], sensor['name'], after)
						r += 1
				if level == 2:
					n += helper.deleteReadings(headers, dataset['name'], node['name'], None, after)
					r += 1
			if level == 1:
				n += helper.deleteReadings(headers, dataset['name'], None, None, after)
				r += 1
		if level == 0:
			n += helper.deleteReadings(headers, None, None, None, after)
			r += 1

		log('Deleted {} readings (before={}) in {} requests'.format(n, after, r), st)

def log(text, startTime=None):
	if standalone:
		message = text
		if startTime:
			message += ' in {0:.3f} seconds'.format(time.time() - startTime)
		print(message)

if __name__ == '__main__':
	standalone = True
	threads = 8
	unittest.main()
