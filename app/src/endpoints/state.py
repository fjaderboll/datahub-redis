from flask import Response, stream_with_context
from flask_restx import Resource

from datetime import datetime
import os
import psutil
import json

from api import api, auth_required
import db
import tsdb
from services import util, cleaner, swagger_service, settings_service, user_service, dataset_service, node_service, reading_service, broker_service

ns = api.namespace('state', description='Get application state')

@ns.route('/health')
class StateHealth(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	def get(self):
		db.queryOne('SELECT 1')
		return tsdb.redisDb.info()['uptime_in_seconds']

@ns.route('/users')
class StateLogin(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	def get(self):
		return {
			'createFirstUserRequired': (user_service.getUserCount() == 0),
			'allowPublicCreateUser': settings_service.getAllowPublicCreateUser()
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
				'database': tsdb.redisDb.info()['used_memory']
			}
		}

@ns.route('/broker')
class StateBroker(Resource):
	@ns.response(200, 'Success')
	@ns.response(503, 'The MQ broker is not reachable')
	@auth_required
	def get(auth, self):
		util.verifyAdmin(auth)

		return broker_service.getState()

@ns.route('/settings')
class StateSettings(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		util.verifyAdmin(auth)

		return {
			'retention': settings_service.getReadingsRetention() / 1000,
			'allowPublicCreateUser': settings_service.getAllowPublicCreateUser(),
			'allowNonAdminLogin': settings_service.getAllowNonAdminLogin(),
			'tokenTTL': settings_service.getTokenTTL()
		}

	@ns.response(200, 'Success')
	@auth_required
	@api.expect(swagger_service.updateSystemSettingsData)
	def put(auth, self):
		util.verifyAdmin(auth)

		n = 0
		if 'retention' in api.payload:
			retention = api.payload['retention']
			settings_service.setReadingsRetention(retention * 1000)
			n += 1

		if 'applyRetention' in api.payload:
			applyRetention = api.payload['applyRetention']
			if applyRetention:
				retention_msecs = settings_service.getReadingsRetention()
				sensorIds = [row['id'] for row in db.query('SELECT id FROM sensors')]
				results = reading_service.runPerSensor(sensorIds, lambda pipe, key: pipe.alter(key, retention_msecs=retention_msecs))
				n += sum(1 for result in results.values() if result)

		if 'allowPublicCreateUser' in api.payload:
			allowPublicCreateUser = api.payload['allowPublicCreateUser']
			settings_service.setAllowPublicCreateUser(allowPublicCreateUser)
			n += 1

		if 'allowNonAdminLogin' in api.payload:
			allowNonAdminLogin = api.payload['allowNonAdminLogin']
			settings_service.setAllowNonAdminLogin(allowNonAdminLogin)
			n += 1

		if 'tokenTTL' in api.payload:
			tokenTTL = api.payload['tokenTTL']
			settings_service.setTokenTTL(tokenTTL)
			n += 1

		return 'Updated {} settings'.format(n)

@ns.route('/timeseries')
class StateTimeseries(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		util.verifyAdmin(auth)

		sensors = db.query('''
			SELECT s.id, s.name, n.name AS node_name, d.name AS dataset_name
			FROM sensors s
			JOIN nodes n ON n.id = s.node_id
			JOIN datasets d ON d.id = n.dataset_id
			ORDER BY d.name, n.name, s.name
		''')
		statsBySensorId = reading_service.getReadingStatsMany([sensor['id'] for sensor in sensors])

		timeseries = []
		for sensor in sensors:
			stats = statsBySensorId[sensor['id']]
			timeseries.append({
				'datasetName': sensor['dataset_name'],
				'nodeName': sensor['node_name'],
				'sensorName': sensor['name'],
				'memory': stats['memory'],
				'samples': stats['count'],
				'retention': stats['retention']
			})

		return timeseries

RECENT_NODES = 10

@ns.route('/overview')
class StateOverview(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		sensors = reading_service.findRequestedSensors(auth, None, None, None)
		sensorIds = [sensor['id'] for sensor in sensors]
		now = int(datetime.now().timestamp() * 1000)
		readingsBySensorId = reading_service.getRecentReadingsMany(sensorIds, reading_service.PATTERN_READINGS)
		countBySensorId = reading_service.getReadingCountsSince(sensorIds, now - 24 * 3600 * 1000)

		nodes = {}
		for sensor in sensors:
			readings = readingsBySensorId[sensor['id']]
			interval = reading_service.getUsualInterval(readings)
			node = nodes.setdefault((sensor['dataset_name'], sensor['node_name']), {
				'datasetName': sensor['dataset_name'],
				'nodeName': sensor['node_name'],
				'lastTimestamp': None,
				'sensors': [],
				'lastTime': 0, # in milliseconds, for sorting
				'silentTime': 0 # last reading of its newest silent sensor
			})
			node['sensors'].append({
				'name': sensor['name'],
				'unit': sensor['unit'],
				'lastReading': cleaner.cleanReading(readings[0] if readings else None, sensor['dataset_name'], sensor['node_name'], sensor),
				'interval': interval / 1000 if interval is not None else None,
				'silent': reading_service.isSilent(readings, now)
			})
			if readings and readings[0][0] > node['lastTime']:
				node['lastTime'] = readings[0][0]
				node['lastTimestamp'] = node['sensors'][-1]['lastReading']['timestamp']
			if node['sensors'][-1]['silent']:
				node['silentTime'] = max(node['silentTime'], readings[0][0])

		activeNodes = [node for node in nodes.values() if node['lastTime']]
		recentNodes = sorted(activeNodes, key=lambda node: node['lastTime'], reverse=True)[:RECENT_NODES]
		silentNodes = sorted([node for node in activeNodes if node['silentTime']], key=lambda node: node['silentTime'], reverse=True)
		clean = lambda node: {key: value for key, value in node.items() if key not in ('lastTime', 'silentTime')}

		return {
			'datasets': len(dataset_service.getUserDatasets(auth['username'])),
			'nodes': node_service.countUserNodes(auth['username']),
			'sensors': len(sensors),
			'readings24h': sum(countBySensorId.values()),
			'silentSensors': sum(1 for node in nodes.values() for sensor in node['sensors'] if sensor['silent']),
			'recentNodes': [clean(node) for node in recentNodes],
			'silentNodes': [clean(node) for node in silentNodes]
		}

@ns.route('/readings')
class StateReadings(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		sub = ReadingSubscriber(auth['username'])
		return Response(stream_with_context(sub), content_type='plain/text')

class ReadingSubscriber:
	def __init__(self, username):
		self.datasetIds = {dataset['id'] for dataset in dataset_service.getUserDatasets(username)}
		self.pubsub = tsdb.redisDb.pubsub()
		self.pubsub.subscribe(tsdb.READINGS_TOPIC)

	def __iter__(self):
		return self

	def __next__(self):
		for message in self.pubsub.listen():
			if message['type'] == 'message':
				reading = json.loads(message['data'])
				dataset = db.queryOne('SELECT id FROM datasets WHERE name = ?', (reading['datasetName'],))
				if dataset and dataset['id'] in self.datasetIds:
					return message['data'] + '\n'
		raise StopIteration
