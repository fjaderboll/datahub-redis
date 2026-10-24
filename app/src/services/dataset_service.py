from flask_restx import abort

import db
import tsdb
from services import util

def verifyValidDatasetName(name):
	util.verifyValidName(name, "Name")

	if db.queryOne('SELECT 1 FROM datasets WHERE name = ?', (name,)):
		abort(400, "Dataset '" + name + "' already exists")

def getDatasetById(datasetId):
	return db.queryOne('SELECT * FROM datasets WHERE id = ?', (datasetId,))

def getUserDatasets(username):
	return db.query('''
		SELECT d.* FROM datasets d
		JOIN dataset_users du ON du.dataset_id = d.id
		JOIN users u ON u.id = du.user_id
		WHERE u.username = ?
		ORDER BY d.name
	''', (username,))

def findUserDataset(username, datasetName):
	return db.queryOne('''
		SELECT d.* FROM datasets d
		JOIN dataset_users du ON du.dataset_id = d.id
		JOIN users u ON u.id = du.user_id
		WHERE d.name = ? AND u.username = ?
	''', (datasetName, username))

def createDataset(name, username, desc=''):
	with db.transaction():
		verifyValidDatasetName(name)
		cursor = db.execute('INSERT INTO datasets (name, description) VALUES (?, ?)', (name, desc or ''))
		datasetId = cursor.lastrowid
		db.execute('INSERT INTO dataset_users (dataset_id, user_id) SELECT ?, id FROM users WHERE username = ?', (datasetId, username))

	return getDatasetById(datasetId)

def updateDataset(dataset, name=None, desc=None):
	with db.transaction():
		if name is not None:
			verifyValidDatasetName(name)
			db.execute('UPDATE datasets SET name = ? WHERE id = ?', (name, dataset['id']))

		if desc is not None:
			db.execute('UPDATE datasets SET description = ? WHERE id = ?', (desc, dataset['id']))

	return getDatasetById(dataset['id'])

def deleteDataset(dataset):
	with db.transaction():
		sensorIds = [row['id'] for row in db.query('''
			SELECT s.id FROM sensors s JOIN nodes n ON n.id = s.node_id WHERE n.dataset_id = ?
		''', (dataset['id'],))]
		db.execute('DELETE FROM datasets WHERE id = ?', (dataset['id'],))

	tsdb.deleteSeries(sensorIds)

def findDatasetUsernames(datasetId):
	rows = db.query('''
		SELECT u.username FROM users u
		JOIN dataset_users du ON du.user_id = u.id
		WHERE du.dataset_id = ?
		ORDER BY u.username
	''', (datasetId,))
	return [row['username'] for row in rows]

def addDatasetUser(datasetId, username):
	db.execute('INSERT OR IGNORE INTO dataset_users (dataset_id, user_id) SELECT ?, id FROM users WHERE username = ?', (datasetId, username))

def removeDatasetUser(datasetId, username):
	with db.transaction():
		datasetUsernames = findDatasetUsernames(datasetId)
		if username in datasetUsernames:
			if len(datasetUsernames) == 1:
				abort(400, 'This will result in dataset being orphaned; delete or share it')

			db.execute('DELETE FROM dataset_users WHERE dataset_id = ? AND user_id = (SELECT id FROM users WHERE username = ?)', (datasetId, username))
