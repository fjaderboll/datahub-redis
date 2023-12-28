from flask_restx import Resource

import os
import resource
import psutil

from api import api, auth_required
from db import db, ts, Keys
from services import util, node_service, sensor_service, reading_service

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

		timeseries = []
		for dKey in db.scan_iter(match='dataset:*'):
			dataset = db.hgetall(dKey)
			for node in node_service.getDatasetNodes(dataset['id']):
				for sensor in sensor_service.getNodeSensors(node['id'], dataset, node):
					timeserie = reading_service.getReadingStats(sensor['id'])
					timeserie['sensorName'] = sensor['name']
					timeserie['nodeName'] = node['name']
					timeserie['datasetName'] = dataset['name']

					timeseries.append(timeserie)

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
				'app': process.memory_info().rss,
				'database': db.info()['used_memory'],
				'timeseries': timeseries
			}
		}
