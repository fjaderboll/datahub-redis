import time
from datetime import datetime, timezone

from flask_restx import abort

import db
from services import util, settings_service

TOKEN_SELECT = '''
	SELECT t.*, u.username, u.is_admin
	FROM tokens t JOIN users u ON u.id = t.user_id
'''
NOT_EXPIRED = '(t.expires_at IS NULL OR t.expires_at > ?)'

def now():
	return int(time.time())

def getExpiresAt(ttl):
	return now() + ttl if ttl else None

def getAuth(token):
	return ifLoginAllowed(db.queryOne(TOKEN_SELECT + ' WHERE t.token_hash = ? AND t.enabled = 1 AND t.mqtt_only = 0 AND ' + NOT_EXPIRED, (util.createTokenHash(token), now())))

def getMqttAuth(username, token):
	return ifLoginAllowed(db.queryOne(TOKEN_SELECT + ' WHERE t.token_hash = ? AND u.username = ? AND t.enabled = 1 AND ' + NOT_EXPIRED, (util.createTokenHash(token), username, now())))

def ifLoginAllowed(tokenInfo):
	if tokenInfo and settings_service.isLoginAllowed(tokenInfo['is_admin']):
		return tokenInfo
	return None

def getUserTokens(username):
	return db.query(TOKEN_SELECT + ' WHERE u.username = ? AND ' + NOT_EXPIRED + ' ORDER BY t.id', (username, now()))

def findToken(auth, id):
	tokenInfo = db.queryOne(TOKEN_SELECT + ' WHERE t.id = ? AND u.username = ? AND ' + NOT_EXPIRED, (id, auth['username'], now()))
	if tokenInfo:
		return tokenInfo
	abort(404, "Unknown token with ID = " + str(id))

def createToken(user, ttl=0, enabled=True, desc='', mqttOnly=False):
	"""Only the token's hash is stored, so this is the only time the token itself is available."""
	token = util.getRandomString(32)
	label = token[0:2] + '...' + token[-2:]
	with db.transaction():
		db.execute('DELETE FROM tokens WHERE expires_at <= ?', (now(),))
		cursor = db.execute('INSERT INTO tokens (token_hash, label, user_id, description, enabled, expires_at, mqtt_only) VALUES (?, ?, ?, ?, ?, ?, ?)',
			(util.createTokenHash(token), label, user['id'], desc or '', int(enabled), getExpiresAt(ttl), int(mqttOnly)))
	tokenInfo = db.queryOne(TOKEN_SELECT + ' WHERE t.id = ?', (cursor.lastrowid,))
	tokenInfo['token'] = token
	return tokenInfo

def updateToken(tokenInfo, desc=None, enabled=None, ttl=None, mqttOnly=None):
	with db.transaction():
		if desc is not None:
			db.execute('UPDATE tokens SET description = ? WHERE id = ?', (desc, tokenInfo['id']))

		if enabled is not None:
			db.execute('UPDATE tokens SET enabled = ? WHERE id = ?', (int(enabled), tokenInfo['id']))

		if mqttOnly is not None:
			db.execute('UPDATE tokens SET mqtt_only = ? WHERE id = ?', (int(mqttOnly), tokenInfo['id']))

		if ttl is not None:
			db.execute('UPDATE tokens SET expires_at = ? WHERE id = ?', (getExpiresAt(ttl), tokenInfo['id']))

	return db.queryOne(TOKEN_SELECT + ' WHERE t.id = ?', (tokenInfo['id'],))

def deleteToken(id):
	db.execute('DELETE FROM tokens WHERE id = ?', (id,))

def formatToken(tokenInfo, hideToken=True):
	expiresAt = tokenInfo['expires_at']
	return {
		'id': str(tokenInfo['id']),
		'enabled': bool(tokenInfo['enabled']),
		'mqttOnly': bool(tokenInfo['mqtt_only']),
		'expire': datetime.fromtimestamp(expiresAt, timezone.utc).isoformat() if expiresAt else None,
		'desc': tokenInfo['description'] if tokenInfo['description'] else None,
		'token': tokenInfo['label'] if hideToken else tokenInfo['token'],
		'username': tokenInfo['username'],
		'isAdmin': bool(tokenInfo['is_admin'])
	}
