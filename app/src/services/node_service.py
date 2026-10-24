from flask_restx import abort

import db
import tsdb
from services import util

def verifyValidNodeName(datasetId, nodeName):
	util.verifyValidName(nodeName, "Name")

	if db.queryOne('SELECT 1 FROM nodes WHERE dataset_id = ? AND name = ?', (datasetId, nodeName)):
		abort(400, "Node '" + nodeName + "' already exists")

def getNodeById(nodeId):
	return db.queryOne('SELECT * FROM nodes WHERE id = ?', (nodeId,))

def getNodeByName(datasetId, name):
	return db.queryOne('SELECT * FROM nodes WHERE dataset_id = ? AND name = ?', (datasetId, name))

def getDatasetNodes(datasetId):
	return db.query('SELECT * FROM nodes WHERE dataset_id = ? ORDER BY name', (datasetId,))

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
