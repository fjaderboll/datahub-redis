import time
from datetime import datetime, timezone

from flask_restx import abort

import db
from services import util

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
	return db.queryOne(TOKEN_SELECT + ' WHERE t.token = ? AND t.enabled = 1 AND ' + NOT_EXPIRED, (token, now()))

def getUserTokens(username):
	return db.query(TOKEN_SELECT + ' WHERE u.username = ? AND ' + NOT_EXPIRED + ' ORDER BY t.id', (username, now()))

def findToken(auth, id):
	tokenInfo = db.queryOne(TOKEN_SELECT + ' WHERE t.id = ? AND u.username = ? AND ' + NOT_EXPIRED, (id, auth['username'], now()))
	if tokenInfo:
		return tokenInfo
	abort(404, "Unknown token with ID = " + str(id))

def createToken(user, ttl=0, enabled=True, desc=''):
	token = util.getRandomString(32)
	with db.transaction():
		db.execute('DELETE FROM tokens WHERE expires_at <= ?', (now(),))
		cursor = db.execute('INSERT INTO tokens (token, user_id, description, enabled, expires_at) VALUES (?, ?, ?, ?, ?)',
			(token, user['id'], desc or '', int(enabled), getExpiresAt(ttl)))
	return db.queryOne(TOKEN_SELECT + ' WHERE t.id = ?', (cursor.lastrowid,))

def updateToken(tokenInfo, desc=None, enabled=None, ttl=None):
	with db.transaction():
		if desc is not None:
			db.execute('UPDATE tokens SET description = ? WHERE id = ?', (desc, tokenInfo['id']))

		if enabled is not None:
			db.execute('UPDATE tokens SET enabled = ? WHERE id = ?', (int(enabled), tokenInfo['id']))

		if ttl is not None:
			db.execute('UPDATE tokens SET expires_at = ? WHERE id = ?', (getExpiresAt(ttl), tokenInfo['id']))

	return db.queryOne(TOKEN_SELECT + ' WHERE t.id = ?', (tokenInfo['id'],))

def deleteToken(token):
	db.execute('DELETE FROM tokens WHERE token = ?', (token,))

def formatToken(tokenInfo, hideToken=True):
	expiresAt = tokenInfo['expires_at']
	return {
		'id': str(tokenInfo['id']),
		'enabled': bool(tokenInfo['enabled']),
		'expire': datetime.fromtimestamp(expiresAt, timezone.utc).isoformat() if expiresAt else None,
		'desc': tokenInfo['description'] if tokenInfo['description'] else None,
		'token': tokenInfo['token'][0:2] + '...' + tokenInfo['token'][-2:] if hideToken else tokenInfo['token'],
		'username': tokenInfo['username'],
		'isAdmin': bool(tokenInfo['is_admin'])
	}
