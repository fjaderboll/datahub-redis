from datetime import datetime, timedelta
from flask_restx import abort

from db import db, Keys
import util

def findUser(username, dbObj=False):
	validName = util.verifyValidName(username, "Username", fail=False)
	if not validName:
		abort(404, "Unknown user '" + username + "'")

	dbUser = db.hgetall(Keys.getUser(str(username)))
	if len(dbUser) == 0:
		abort(404, "Unknown user '" + username + "'")

	if dbObj:
		return dbUser
	else:
		return util.copy(dbUser, ['username', 'email', 'isAdmin'])

def findDataset(auth, datasetName):
	validName = util.verifyValidName(datasetName, fail=False)
	if validName:
		datasetId = db.get(Keys.getDatasetByName(datasetName))
		if datasetId:
			if db.sismember(Keys.getUserDatasetIds(auth['username']), datasetId):
				dataset = db.hgetall(Keys.getDatasetById(datasetId))
				return dataset

	abort(404, "Unknown dataset '" + datasetName + "'")

def findToken(auth, id):
	for tokenInfo in db.scan_iter(match='token:*'):
		tokenInfo = db.hgetall(tokenInfo)
		if tokenInfo['username'] == auth['username'] and tokenInfo['id'] == str(id):
			return tokenInfo
	abort(404, "Unknown token with ID = " + str(id))

def cleanObject(obj, fieldsToKeep):
	newObj = {}
	for field in fieldsToKeep:
		if field in obj:
			newObj[field] = obj[field]
	return newObj

def createToken(username, ttl=None, enabled=True, desc=None):
	while True:
		token = util.getRandomString(32)
		tKey = Keys.getToken(token)
		if not db.exists(tKey):
			tokenId = db.incr(Keys.getTokenIdCounter())
			tokenInfo = {
				'id': tokenId,
				'token': token,
				'username': username,
				'enabled': int(enabled), # need to store as int
				'desc': desc if desc else "",
				'expire': ""
			}
			if ttl:
				tokenInfo['expire'] = (datetime.now() + timedelta(seconds=ttl)).replace(microsecond=0).isoformat()

			db.hset(tKey, mapping=tokenInfo)
			if ttl:
				db.expire(tKey, ttl)

			return tokenInfo

def cleanToken(tokenInfo):
	return {
		'id': tokenInfo['id'],
		'enabled': bool(int(tokenInfo['enabled'])),
		'expire': tokenInfo['expire'] if tokenInfo['expire'] else None,
		'desc': tokenInfo['desc'] if tokenInfo['desc'] else None,
		'token': tokenInfo['token'][0:2] + '...' + tokenInfo['token'][-2:]
	}
