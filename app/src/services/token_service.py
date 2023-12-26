from flask_restx import abort
from datetime import datetime, timedelta
import pytz

from db import db, Keys
import util

def findToken(auth, id):
	for tokenInfo in db.scan_iter(match='token:*'):
		tokenInfo = db.hgetall(tokenInfo)
		if tokenInfo['username'] == auth['username'] and tokenInfo['id'] == str(id):
			return tokenInfo
	abort(404, "Unknown token with ID = " + str(id))

def createToken(username, isAdmin, ttl=None, enabled=True, desc=None):
	while True:
		token = util.getRandomString(32)
		tKey = Keys.getToken(token)
		if not db.exists(tKey):
			tokenId = db.incr(Keys.getTokenIdCounter())
			tokenInfo = {
				'id': str(tokenId),
				'token': token,
				'username': username,
				'enabled': int(enabled), # need to store as int
				'desc': desc if desc else "",
				'expire': "",
				'isAdmin': int(isAdmin)
			}
			if ttl:
				tokenInfo['expire'] = (datetime.now() + timedelta(seconds=ttl)).replace(microsecond=0).astimezone(pytz.UTC).isoformat()

			db.hset(tKey, mapping=tokenInfo)
			if ttl:
				db.expire(tKey, ttl)

			return tokenInfo

def formatToken(tokenInfo, hideToken=True):
	return {
		'id': tokenInfo['id'],
		'enabled': bool(int(tokenInfo['enabled'])),
		'expire': tokenInfo['expire'] if tokenInfo['expire'] else None,
		'desc': tokenInfo['desc'] if tokenInfo['desc'] else None,
		'token': tokenInfo['token'][0:2] + '...' + tokenInfo['token'][-2:] if hideToken else tokenInfo['token'],
		'username': tokenInfo['username'],
		'isAdmin': bool(int(tokenInfo['isAdmin']))
	}
