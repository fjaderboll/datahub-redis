from flask_restx import abort

import db
from services import util, settings_service, token_service

def getAllUsers():
	return db.query('SELECT * FROM users ORDER BY username')

def getUserCount():
	return db.queryOne('SELECT COUNT(*) AS n FROM users')['n']

def findUser(username, statusCode=404):
	validName = util.verifyValidName(username, "Username", fail=False)
	if validName:
		user = db.queryOne('SELECT * FROM users WHERE username = ?', (username,))
		if user:
			return user

	abort(statusCode, "Unknown user '" + username + "'")

def createUser(username, password):
	util.verifyValidName(username, "Username")
	util.verifyNoneEmpty(password, 'Password')

	if username == settings_service.getMqttUsername():
		abort(400, "Username '" + username + "' already exists")

	hash = util.createPasswordHash(password)

	with db.transaction():
		if db.queryOne('SELECT 1 FROM users WHERE username = ?', (username,)):
			abort(400, "Username '" + username + "' already exists")

		isAdmin = getUserCount() == 0
		db.execute('INSERT INTO users (username, password_hash, email, is_admin) VALUES (?, ?, ?, ?)',
			(username, hash, '', int(isAdmin)))

	return findUser(username)

def updateUser(username, email=None, isAdmin=None, password=None):
	user = findUser(username)
	hash = util.createPasswordHash(password) if password is not None else None # slow, so not while holding the write lock

	with db.transaction():
		if email is not None:
			db.execute('UPDATE users SET email = ? WHERE id = ?', (email, user['id']))

		if isAdmin is not None:
			db.execute('UPDATE users SET is_admin = ? WHERE id = ?', (int(isAdmin), user['id']))

		if hash is not None:
			db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hash, user['id']))

	return findUser(username)

def authenticate(username, password):
	"""Return the user if the credentials are valid and the user may log in, otherwise None."""
	if not util.verifyValidName(username, "Username", fail=False):
		return None

	user = db.queryOne('SELECT * FROM users WHERE username = ?', (username,))
	if not user:
		return None

	if not settings_service.isLoginAllowed(user['is_admin']):
		return None

	if not util.verifyPassword(password, user['password_hash']):
		return None

	# keeps the hashes up to date if the hash parameters are changed
	if util.passwordNeedsRehash(user['password_hash']):
		db.execute('UPDATE users SET password_hash = ? WHERE id = ?', (util.createPasswordHash(password), user['id']))

	return user

def login(username, password, ttl, desc):
	user = authenticate(username, password)
	if not user:
		abort(401, "Invalid credentials")

	tokenInfo = token_service.createToken(user, ttl=ttl, desc=desc)
	return token_service.formatToken(tokenInfo, hideToken=False)

def deleteUser(username):
	user = findUser(username)

	with db.transaction():
		orphanCount = db.queryOne('''
			SELECT COUNT(*) AS n FROM dataset_users du
			WHERE du.user_id = ?
			AND NOT EXISTS (SELECT 1 FROM dataset_users other WHERE other.dataset_id = du.dataset_id AND other.user_id != du.user_id)
		''', (user['id'],))['n']

		if orphanCount > 0:
			abort(400, 'This will result in ' + str(orphanCount) + ' orphaned dataset(s); delete or share them first')

		db.execute('DELETE FROM users WHERE id = ?', (user['id'],))
