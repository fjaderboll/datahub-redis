#!/usr/bin/env python3
"""
Database initialization and consistency checks between SQLite and Redis.

Usage: maintenance.py check | repair
"""
import logging
import sys

import db
import tsdb
from services import settings_service

def initialize(logger):
	existingSeriesIds = tsdb.findSeriesSensorIds() if db.getSchemaVersion() == 0 else set()

	def populate(conn):
		if existingSeriesIds:
			# never hand out an id whose series already holds readings
			raiseSequence(conn, 'sensors', max(existingSeriesIds))
			logger.warning('Redis contains {} time series without a sensor in the new database {}; see "maintenance.py check"'.format(len(existingSeriesIds), db.SQLITE_PATH))

	if db.initSchema(populate):
		logger.info('Created database ' + db.SQLITE_PATH)

	createdIds = createMissingSeries()
	if createdIds:
		logger.warning('Created missing time series for sensor ids ' + str(createdIds))

	db.closeDb()

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

	if command not in ('check', 'repair'):
		print(__doc__.strip())
		return 1

	if db.getSchemaVersion() == 0:
		logger.error('Database ' + db.SQLITE_PATH + ' is not initialized; start the application first')
		return 1

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

	if command == 'repair':
		created = createMissingSeries()
		tsdb.deleteSeries(inconsistencies['orphanedSeries'])
		logger.info('Created {} and deleted {} time series'.format(len(created), len(inconsistencies['orphanedSeries'])))

	return 0

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
