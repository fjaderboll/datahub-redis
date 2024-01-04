from flask import Response, stream_with_context
from flask_restx import Resource

import os
import psutil
import json

from api import api, auth_required
from db import db, ts, Keys
from services import util, swagger_service, settings_service, node_service, sensor_service, reading_service

ns = api.namespace('state', description='Get application state')

@ns.route('/health')
class StateHealth(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	def get(self):
		return db.info()['uptime_in_seconds']

@ns.route('/users')
class StateLogin(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	def get(self):
		userCount = db.scard(Keys.getUsers())
		return {
			'createFirstUserRequired': (userCount == 0),
			'createUserAllowed': True
		}

@ns.route('/system')
class StateSystem(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		util.verifyAdmin(auth)

		process = psutil.Process()

		return {
			'cpu': {
				'loadAvg': psutil.getloadavg(),
				'count': os.cpu_count(),
				'percent': process.cpu_percent()
			},
			'memory': {
				'total': psutil.virtual_memory().total,
				'available': psutil.virtual_memory().available,
				'percent': psutil.virtual_memory().percent,
				'application': process.memory_info().rss,
				'database': db.info()['used_memory']
			},
			'retention': {
				'default': settings_service.getReadingsRetention() / 1000
			}
		}

	@ns.response(200, 'Success')
	@auth_required
	@api.expect(swagger_service.updateSystemData)
	def put(auth, self):
		util.verifyAdmin(auth)

		message = ''
		if 'retention' in api.payload:
			retention = api.payload['retention']
			settings_service.setReadingsRetention(retention * 1000)
			message = 'Updated default retention'

		if 'applyRetention' in api.payload:
			applyRetention = api.payload['applyRetention']
			if applyRetention:
				retention_msecs = settings_service.getReadingsRetention()
				i = 0
				for tsKey in db.scan_iter(match='sensor-readings:*'):
					ts.alter(tsKey, retention_msecs=retention_msecs)
					i += 1

				message = (message + ' and applied' if message else 'Updated default retention') + ' on {} timeseries'.format(i)

		return message

@ns.route('/timeseries')
class StateTimeseries(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		util.verifyAdmin(auth)

		timeseries = []
		for dKey in db.scan_iter(match='dataset:*'):
			dataset = db.hgetall(dKey)
			for node in node_service.getDatasetNodes(dataset['id']):
				for sensor in sensor_service.getNodeSensors(node['id'], dataset, node):
					stats = reading_service.getReadingStats(sensor['id'])

					timeserie = {
						'datasetName': dataset['name'],
						'nodeName': node['name'],
						'sensorName': sensor['name'],
						'memory': stats['memory'],
						'samples': stats['count'],
						'retention': stats['retention']
					}

					timeseries.append(timeserie)

		return timeseries

@ns.route('/readings')
class StateReadings(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		sub = ReadingSubscriber(auth['username'])
		return Response(stream_with_context(sub), content_type='plain/text')

class ReadingSubscriber:
	def __init__(self, username):
		self.datasetIds = db.smembers(Keys.getUserDatasetIds(username))
		self.pubsub = db.pubsub()
		self.pubsub.subscribe(Keys.getReadingsTopic())

	def __iter__(self):
		return self

	def __next__(self):
		for message in self.pubsub.listen():
			if message['type'] == 'message':
				reading = json.loads(message['data'])
				datasetId = db.get(Keys.getDatasetIdByName(reading['datasetName']))
				if datasetId in self.datasetIds:
					return message['data'] + '\n'
		raise StopIteration
