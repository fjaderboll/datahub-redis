#!/usr/bin/env python3
"""
Database initialization, import of data from the Redis-only version and consistency checks.

Usage: maintenance.py check | repair | remove-legacy-keys
"""
import logging
import math
import sqlite3
import sys
import time

import db
import tsdb
from services import settings_service

# Keys used by the Redis-only version for everything except the readings themselves
LEGACY_KEY_PATTERNS = [
	'settings', 'users', 'user:*', 'token:*', 'id-counter-*',
	'user-dataset-ids:*', 'dataset:*', 'dataset-name:*', 'dataset-node-ids:*', 'dataset-node-name:*',
	'node:*', 'node-sensor-ids:*', 'node-sensor-name:*', 'sensor:*'
]
LEGACY_ID_COUNTERS = {
	'datasets': 'id-counter-dataset',
	'nodes': 'id-counter-node',
	'sensors': 'id-counter-sensor',
	'tokens': 'id-counter-token'
}

def initialize(logger):
	legacyData = None
	existingSeriesIds = set()
	if db.getSchemaVersion() == 0:
		existingSeriesIds = tsdb.findSeriesSensorIds()
		if hasLegacyData():
			legacyData = readLegacyData()

	seriesMerges = []
	def populate(conn):
		if legacyData:
			seriesMerges.extend(importLegacyData(conn, legacyData, logger))
		if existingSeriesIds:
			# never hand out an id whose series already holds readings
			raiseSequence(conn, 'sensors', max(existingSeriesIds))
			sensorIds = {row['id'] for row in conn.execute('SELECT id FROM sensors').fetchall()}
			unknownCount = len(existingSeriesIds - sensorIds - {fromId for fromId, _ in seriesMerges})
			if unknownCount > 0:
				logger.warning('Redis contains {} time series without a sensor in the new database {}; see "maintenance.py check"'.format(unknownCount, db.SQLITE_PATH))

	if db.initSchema(populate):
		logger.info('Created database ' + db.SQLITE_PATH)

	createdIds = createMissingSeries()
	if createdIds:
		logger.warning('Created missing time series for sensor ids ' + str(createdIds))

	for fromSensorId, toSensorId in seriesMerges:
		copied, failed = tsdb.mergeSeries(fromSensorId, toSensorId)
		if failed:
			logger.warning('Copied {} readings from duplicate sensor {} to sensor {}; {} could not be copied so {} was kept'.format(
				copied, fromSensorId, toSensorId, failed, tsdb.readingsKey(fromSensorId)))
		else:
			logger.warning('Moved {} readings from duplicate sensor {} to sensor {}'.format(copied, fromSensorId, toSensorId))

	db.closeDb()

def findLegacyKeys():
	r = tsdb.redisDb
	keys = []
	for pattern in LEGACY_KEY_PATTERNS:
		if '*' in pattern:
			keys.extend(r.scan_iter(match=pattern, count=1000))
		elif r.exists(pattern):
			keys.append(pattern)
	return keys

def hasLegacyData():
	return tsdb.redisDb.exists('users', 'settings', *LEGACY_ID_COUNTERS.values()) > 0

def readLegacyData():
	r = tsdb.redisDb

	def readHashes(pattern):
		keys = list(r.scan_iter(match=pattern, count=1000))
		pipe = r.pipeline(transaction=False)
		for key in keys:
			pipe.hgetall(key)
			pipe.pttl(key)
		results = pipe.execute()
		return [(results[i], results[i + 1]) for i in range(0, len(results), 2) if results[i]]

	users = [user for user, _ in readHashes('user:*')]
	return {
		'settings': r.hgetall('settings'),
		'users': users,
		'userDatasetIds': {user['username']: r.smembers('user-dataset-ids:' + user['username']) for user in users if 'username' in user},
		'datasets': [dataset for dataset, _ in readHashes('dataset:*')],
		'nodes': [node for node, _ in readHashes('node:*')],
		'sensors': [sensor for sensor, _ in readHashes('sensor:*')],
		'tokens': readHashes('token:*'),
		'counters': {table: int(r.get(key) or 0) for table, key in LEGACY_ID_COUNTERS.items()}
	}

def importLegacyData(conn, data, logger):
	"""
	Insert data read by readLegacyData(). Dataset, node, sensor and token ids are kept so existing time series keys stay valid.
	Duplicates (same name within the same parent) are merged into the one with the lowest id. Returns the
	(duplicate sensor id, kept sensor id) pairs whose readings should be moved with tsdb.mergeSeries().
	"""
	skipped = []
	merged = []
	seriesMerges = []
	def insert(description, sql, params):
		try:
			return conn.execute(sql, params).lastrowid
		except sqlite3.IntegrityError as e:
			skipped.append(description + ': ' + str(e))
			return None

	def byId(items):
		return sorted((item for item in items if str(item.get('id', '')).isdigit()), key=lambda item: int(item['id']))

	for key, value in data['settings'].items():
		conn.execute('INSERT INTO settings (key, value) VALUES (?, ?)', (key, value))

	userIds = {}
	for user in sorted(data['users'], key=lambda user: user.get('username', '')):
		userId = insert('user ' + str(user.get('username')),
			'INSERT INTO users (username, password_hash, password_salt, email, is_admin) VALUES (?, ?, ?, ?, ?)',
			(user['username'], user['passwordHash'], user['passwordSalt'], user.get('email', ''), int(user.get('isAdmin') or 0)))
		if userId:
			userIds[user['username']] = userId

	def findExisting(sql, params):
		row = conn.execute(sql, params).fetchone()
		return row['id'] if row else None

	datasetIdMap = {} # legacy id -> imported id
	for dataset in byId(data['datasets']):
		description = 'dataset ' + dataset['id'] + ' ' + str(dataset.get('name'))
		existingId = findExisting('SELECT id FROM datasets WHERE name = ?', (dataset.get('name'),))
		if existingId:
			datasetIdMap[int(dataset['id'])] = existingId
			merged.append(description + ' into dataset ' + str(existingId))
		elif insert(description, 'INSERT INTO datasets (id, name, description) VALUES (?, ?, ?)',
				(int(dataset['id']), dataset['name'], dataset.get('desc', ''))):
			datasetIdMap[int(dataset['id'])] = int(dataset['id'])

	for username, ids in data['userDatasetIds'].items():
		for datasetId in ids:
			if username in userIds and datasetId.isdigit() and int(datasetId) in datasetIdMap:
				conn.execute('INSERT OR IGNORE INTO dataset_users (dataset_id, user_id) VALUES (?, ?)', (datasetIdMap[int(datasetId)], userIds[username]))

	for row in conn.execute('SELECT name FROM datasets WHERE id NOT IN (SELECT dataset_id FROM dataset_users)').fetchall():
		logger.warning("Imported dataset '" + row['name'] + "' is not shared with any user")

	nodeIdMap = {}
	for node in byId(data['nodes']):
		description = 'node ' + node['id'] + ' ' + str(node.get('name'))
		datasetId = datasetIdMap.get(int(node.get('datasetId') or 0))
		existingId = findExisting('SELECT id FROM nodes WHERE dataset_id = ? AND name = ?', (datasetId, node.get('name')))
		if not datasetId:
			skipped.append(description + ': unknown dataset ' + str(node.get('datasetId')))
		elif existingId:
			nodeIdMap[int(node['id'])] = existingId
			merged.append(description + ' into node ' + str(existingId))
		elif insert(description, 'INSERT INTO nodes (id, dataset_id, name, description) VALUES (?, ?, ?, ?)',
				(int(node['id']), datasetId, node['name'], node.get('desc', ''))):
			nodeIdMap[int(node['id'])] = int(node['id'])

	sensorCount = 0
	for sensor in byId(data['sensors']):
		description = 'sensor ' + sensor['id'] + ' ' + str(sensor.get('name'))
		nodeId = nodeIdMap.get(int(sensor.get('nodeId') or 0))
		existingId = findExisting('SELECT id FROM sensors WHERE node_id = ? AND name = ?', (nodeId, sensor.get('name')))
		if not nodeId:
			skipped.append(description + ': unknown node ' + str(sensor.get('nodeId')))
		elif existingId:
			seriesMerges.append((int(sensor['id']), existingId))
			merged.append(description + ' into sensor ' + str(existingId))
		elif insert(description, 'INSERT INTO sensors (id, node_id, name, description, unit) VALUES (?, ?, ?, ?, ?)',
				(int(sensor['id']), nodeId, sensor['name'], sensor.get('desc', ''), sensor.get('unit', ''))):
			sensorCount += 1

	now = int(time.time())
	tokenCount = 0
	for token, pttl in data['tokens']:
		description = 'token ' + str(token.get('id'))
		if token.get('username') not in userIds:
			skipped.append(description + ': unknown user ' + str(token.get('username')))
			continue
		if pttl == -2 or not str(token.get('id', '')).isdigit():
			continue # expired while reading, or malformed
		expiresAt = now + math.ceil(pttl / 1000) if pttl > 0 else None
		if insert(description, 'INSERT INTO tokens (id, token, user_id, description, enabled, expires_at) VALUES (?, ?, ?, ?, ?, ?)',
				(int(token['id']), token['token'], userIds[token['username']], token.get('desc', ''), int(token.get('enabled') or 0), expiresAt)):
			tokenCount += 1

	for table, counter in data['counters'].items():
		raiseSequence(conn, table, counter)

	for message in merged:
		logger.warning('Merged duplicate legacy ' + message)
	for message in skipped:
		logger.warning('Skipped legacy ' + message)
	logger.warning('Imported legacy data from Redis: {} users, {} datasets, {} nodes, {} sensors, {} tokens ({} duplicates merged, {} skipped). '
		'Run "maintenance.py check" to verify and "maintenance.py remove-legacy-keys" to clean up.'.format(
			len(userIds), len(set(datasetIdMap.values())), len(set(nodeIdMap.values())), sensorCount, tokenCount, len(merged), len(skipped)))

	return seriesMerges

def raiseSequence(conn, table, value):
	"""Make AUTOINCREMENT ids of 'table' continue above 'value'."""
	row = conn.execute('SELECT seq FROM sqlite_sequence WHERE name = ?', (table,)).fetchone()
	if row is None:
		conn.execute('INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)', (table, value))
	elif row['seq'] < value:
		conn.execute('UPDATE sqlite_sequence SET seq = ? WHERE name = ?', (value, table))

def findInconsistencies():
	# Redis is scanned before SQLite is read; sensors are always committed to SQLite before their series
	# is created, so a series created meanwhile is never mistaken for an orphan.
	seriesSensorIds = tsdb.findSeriesSensorIds()
	sensorIds = {row['id'] for row in db.query('SELECT id FROM sensors')}
	return {
		'missingSeries': sorted(sensorIds - seriesSensorIds),
		'orphanedSeries': sorted(seriesSensorIds - sensorIds)
	}

def createMissingSeries():
	sensorIds = [row['id'] for row in db.query('SELECT id FROM sensors')]
	pipe = tsdb.redisDb.pipeline(transaction=False)
	for sensorId in sensorIds:
		pipe.exists(tsdb.readingsKey(sensorId))
	missingIds = [sensorId for sensorId, exists in zip(sensorIds, pipe.execute()) if not exists]

	if missingIds:
		retention = settings_service.getReadingsRetention()
		for sensorId in missingIds:
			tsdb.createSeries(sensorId, retention)
	return missingIds

def main(args):
	logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
	logger = logging.getLogger('maintenance')
	command = args[0] if args else None

	if command not in ('check', 'repair', 'remove-legacy-keys'):
		print(__doc__.strip())
		return 1

	if db.getSchemaVersion() == 0:
		logger.error('Database ' + db.SQLITE_PATH + ' is not initialized; start the application first')
		return 1

	if command in ('check', 'repair'):
		inconsistencies = findInconsistencies()
		counts = db.queryOne('''SELECT
			(SELECT COUNT(*) FROM users) AS users,
			(SELECT COUNT(*) FROM datasets) AS datasets,
			(SELECT COUNT(*) FROM nodes) AS nodes,
			(SELECT COUNT(*) FROM sensors) AS sensors,
			(SELECT COUNT(*) FROM tokens) AS tokens''')
		logger.info('SQLite: ' + ', '.join('{} {}'.format(n, name) for name, n in counts.items()))
		logger.info('Sensors without time series: ' + str(inconsistencies['missingSeries']))
		logger.info('Time series without sensor: ' + str(inconsistencies['orphanedSeries']))
		logger.info('Legacy keys in Redis: ' + str(len(findLegacyKeys())))

		if command == 'repair':
			created = createMissingSeries()
			tsdb.deleteSeries(inconsistencies['orphanedSeries'])
			logger.info('Created {} and deleted {} time series'.format(len(created), len(inconsistencies['orphanedSeries'])))

	elif command == 'remove-legacy-keys':
		keys = findLegacyKeys()
		for i in range(0, len(keys), 500):
			tsdb.redisDb.delete(*keys[i:i + 500])
		logger.info('Removed {} legacy keys'.format(len(keys)))

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
