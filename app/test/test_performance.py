import unittest
import time
import multiprocessing
import queue

import helper

standalone = False
threads = 1

class TestPerf(unittest.TestCase):

	def test(self):
		st = time.time()
		username = helper.getRandomName('perfuser-')
		headers = helper.createUserAndLogin(username)
		log('Logged in', st)

		datasetCount = 2
		nodeCount = 10
		sensorCount = 3
		readingCount = 20

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
		log('Created {} datasets, {} nodes and {} sensors'.format(datasetCount, datasetCount*nodeCount, datasetCount*nodeCount*sensorCount), st)

		# prepare stuff to do
		createTasks = multiprocessing.Queue()
		loadTasks = multiprocessing.Queue()

		for dataset in datasets:
			for node in dataset['nodes']:
				for sensor in node['sensors']:
					task = {
						'datasetName': dataset['name'],
						'nodeName': node['name'],
						'sensorName': sensor['name']
					}

					loadTasks.put(task)
					for i in range(readingCount):
						createTasks.put(task)

		log('Creating ' + str(createTasks.qsize()) + ' readings')

		runInParallel(importReadings, headers, createTasks)
		runInParallel(loadReadings, headers, loadTasks)

def log(text, startTime=None):
	if standalone:
		message = text
		if startTime:
			message += ' in {0:.3f} seconds'.format(time.time() - startTime)
		print(message)

def importReadings(headers, tasks):
	st = time.time()
	n = 0
	while True:
		try:
			task = tasks.get_nowait()
			helper.createReading(headers, task['datasetName'], task['nodeName'], task['sensorName'])
			n += 1
		except queue.Empty:
			break

	log('Created {} readings'.format(n), st)

def loadReadings(headers, tasks):
	st = time.time()
	n = 0
	while True:
		try:
			task = tasks.get_nowait()
			readings = helper.getReadings(headers, task['datasetName'], task['nodeName'], task['sensorName'])
			n += len(readings)
		except queue.Empty:
			break

	log('Loaded {} readings'.format(n), st)

def runInParallel(func, headers, tasks):
	processes = []
	for i in range(0, threads):
		p = multiprocessing.Process(target=func, args=(headers, tasks))
		processes.append(p)

	for p in processes:
		p.start()

	for p in processes:
		p.join()

if __name__ == '__main__':
	standalone = True
	threads = 8
	unittest.main()
