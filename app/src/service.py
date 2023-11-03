from datetime import datetime, timedelta
from flask_restx import abort

from db import db, Keys
import util

def findUser(username, verifyUsername=True, dbObj=False):
	if verifyUsername:
		util.verifyValidName(username, "Username")

	dbUser = db.hgetall(Keys.getUserKey(str(username)))
	if len(dbUser) == 0:
		abort(404, "Unknown user '" + username + "'")

	if dbObj:
		return dbUser
	else:
		return util.copy(dbUser, ['username', 'email', 'isAdmin'])

def createToken(username, isAdmin, name=None, ttl=None):
	while True:
		token = util.getRandomString(32)
		tKey = Keys.getTokenKey(token, username)
		if not db.exists(tKey):
			tokenInfo = {
				'token': token,
				'username': username,
				'isAdmin': int(isAdmin)     # need to store as int
			}
			if name:
				tokenInfo['name'] = name
			if ttl:
				tokenInfo['expire'] = (datetime.now() + timedelta(seconds=ttl)).replace(microsecond=0).isoformat()

			db.hset(tKey, mapping=tokenInfo)
			if ttl:
				db.expire(tKey, ttl)

			tokenInfo['isAdmin'] = isAdmin  # return as bool
			return tokenInfo
