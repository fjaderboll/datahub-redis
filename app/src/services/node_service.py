from flask_restx import abort

import db
import tsdb
from services import util, cleaner, reading_service

def verifyValidNodeName(datasetId, nodeName):
	util.verifyValidName(nodeName, "Name")

	if db.queryOne('SELECT 1 FROM nodes WHERE dataset_id = ? AND name = ?', (datasetId, nodeName)):
		abort(400, "Node '" + nodeName + "' already exists")

def getNodeById(nodeId):
	return db.queryOne('SELECT * FROM nodes WHERE id = ?', (nodeId,))

def getNodeByName(datasetId, name):
	return db.queryOne('SELECT * FROM nodes WHERE dataset_id = ? AND name = ?', (datasetId, name))

def getDatasetNodes(datasetId):
	nodes = db.query('''
		SELECT n.*, (SELECT COUNT(*) FROM sensors s WHERE s.node_id = n.id) AS sensor_count FROM nodes n
		WHERE n.dataset_id = ?
		ORDER BY n.name
	''', (datasetId,))

	sensors = db.query('''
		SELECT s.id, s.node_id FROM sensors s
		JOIN nodes n ON n.id = s.node_id
		WHERE n.dataset_id = ?
	''', (datasetId,))
	lastReadings = reading_service.getLastReadings([sensor['id'] for sensor in sensors])

	lastTimes = {} # node id -> newest reading of its sensors, in milliseconds
	for sensor in sensors:
		reading = lastReadings[sensor['id']]
		if reading:
			lastTimes[sensor['node_id']] = max(reading[0], lastTimes.get(sensor['node_id'], reading[0]))

	for node in nodes:
		lastTime = lastTimes.get(node['id'])
		node['last_timestamp'] = cleaner.cleanTimestamp(lastTime) if lastTime is not None else None
	return nodes

def countUserNodes(username):
	return db.queryOne('''
		SELECT COUNT(*) AS count FROM nodes n
		JOIN dataset_users du ON du.dataset_id = n.dataset_id
		JOIN users u ON u.id = du.user_id
		WHERE u.username = ?
	''', (username,))['count']

def createNode(datasetId, name, desc=''):
	with db.transaction():
		verifyValidNodeName(datasetId, name)
		cursor = db.execute('INSERT INTO nodes (dataset_id, name, description) VALUES (?, ?, ?)', (datasetId, name, desc or ''))

	return getNodeById(cursor.lastrowid)

def getOrCreateNode(datasetId, name):
	db.execute('INSERT INTO nodes (dataset_id, name) VALUES (?, ?) ON CONFLICT (dataset_id, name) DO NOTHING', (datasetId, name))
	return getNodeByName(datasetId, name)

def updateNode(node, name=None, desc=None):
	with db.transaction():
		if name is not None:
			verifyValidNodeName(node['dataset_id'], name)
			db.execute('UPDATE nodes SET name = ? WHERE id = ?', (name, node['id']))

		if desc is not None:
			db.execute('UPDATE nodes SET description = ? WHERE id = ?', (desc, node['id']))

	return getNodeById(node['id'])

def deleteNode(node):
	with db.transaction():
		sensorIds = [row['id'] for row in db.query('SELECT id FROM sensors WHERE node_id = ?', (node['id'],))]
		db.execute('DELETE FROM nodes WHERE id = ?', (node['id'],))

	tsdb.deleteSeries(sensorIds)
