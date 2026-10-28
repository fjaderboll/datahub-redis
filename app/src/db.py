import os
import sqlite3
import threading
import time
from contextlib import contextmanager

SQLITE_PATH = os.environ.get('SQLITE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datahub.db'))

# Each entry upgrades the schema by one version (tracked in PRAGMA user_version).
# Ids use AUTOINCREMENT so a deleted sensor's id, and thereby its Redis key, is never reused.
MIGRATIONS = [
	[
		"""CREATE TABLE settings (
			key TEXT PRIMARY KEY,
			value TEXT NOT NULL
		)""",
		"""CREATE TABLE users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password_hash TEXT NOT NULL,
			email TEXT NOT NULL DEFAULT '',
			is_admin INTEGER NOT NULL DEFAULT 0
		)""",
		"""CREATE TABLE tokens (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			token_hash TEXT NOT NULL UNIQUE,
			label TEXT NOT NULL,
			user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
			description TEXT NOT NULL DEFAULT '',
			enabled INTEGER NOT NULL DEFAULT 1,
			expires_at INTEGER
		)""",
		"CREATE INDEX tokens_user_id ON tokens(user_id)",
		"""CREATE TABLE datasets (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL UNIQUE,
			description TEXT NOT NULL DEFAULT ''
		)""",
		"""CREATE TABLE dataset_users (
			dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
			user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
			PRIMARY KEY (dataset_id, user_id)
		) WITHOUT ROWID""",
		"CREATE INDEX dataset_users_user_id ON dataset_users(user_id)",
		"""CREATE TABLE nodes (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
			name TEXT NOT NULL,
			description TEXT NOT NULL DEFAULT '',
			UNIQUE (dataset_id, name)
		)""",
		"""CREATE TABLE sensors (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			node_id INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
			name TEXT NOT NULL,
			description TEXT NOT NULL DEFAULT '',
			unit TEXT NOT NULL DEFAULT '',
			UNIQUE (node_id, name)
		)"""
	]
]

_local = threading.local()

def _dictFactory(cursor, row):
	return {column[0]: row[i] for i, column in enumerate(cursor.description)}

def connect(path=SQLITE_PATH):
	# isolation_level=None leaves transaction control to transaction() below
	conn = sqlite3.connect(path, isolation_level=None)
	conn.row_factory = _dictFactory
	conn.execute('PRAGMA busy_timeout = 5000')
	conn.execute('PRAGMA foreign_keys = ON')
	return conn

def getDb():
	conn = getattr(_local, 'conn', None)
	if conn is None:
		conn = connect()
		_local.conn = conn
	return conn

def closeDb():
	conn = getattr(_local, 'conn', None)
	if conn is not None:
		_local.conn = None
		conn.close()

def query(sql, params=()):
	return getDb().execute(sql, params).fetchall()

def queryOne(sql, params=()):
	return getDb().execute(sql, params).fetchone()

def execute(sql, params=()):
	return getDb().execute(sql, params)

@contextmanager
def transaction():
	# Do not call Redis (or anything else that yields to gevent) inside a transaction:
	# another greenlet in the same worker waiting for the write lock would block the
	# whole process, so the lock holder could never resume and finish.
	conn = getDb()
	if conn.in_transaction:
		yield conn
		return

	conn.execute('BEGIN IMMEDIATE')
	try:
		yield conn
	except BaseException:
		conn.execute('ROLLBACK')
		raise
	conn.execute('COMMIT')

def getSchemaVersion():
	return queryOne('PRAGMA user_version')['user_version']

def initSchema(populate=None):
	"""Create or upgrade the schema. 'populate(conn)' runs in the same transaction when the database is new."""
	conn = getDb()
	# changing the journal mode fails at once, instead of waiting, while another worker holds a lock
	for attempt in range(50):
		try:
			conn.execute('PRAGMA journal_mode = WAL')
			break
		except sqlite3.OperationalError:
			if attempt == 49:
				raise
			time.sleep(0.1)

	if getSchemaVersion() == len(MIGRATIONS):
		return False

	with transaction():
		version = getSchemaVersion()
		if version == len(MIGRATIONS):
			return False # another worker got here first

		for statements in MIGRATIONS[version:]:
			for statement in statements:
				conn.execute(statement)
		conn.execute('PRAGMA user_version = ' + str(len(MIGRATIONS)))

		if version == 0 and populate:
			populate(conn)

	return version == 0
