from flask_restx import Resource

import os
import psutil

from api import api, auth_required
from db import db, ts, Keys
from services import util, settings_service, node_service, sensor_service, reading_service

ns = api.namespace('state', description='Get application state')

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
	def put(auth, self):
		util.verifyAdmin(auth)

		input = api.payload
		if 'retention' in input:
			settings_service.setReadingsRetention(int(input['retention']) * 1000)

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
