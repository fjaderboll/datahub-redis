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

def cleanObject(obj, fieldsToKeep):
	newObj = {}
	for field in fieldsToKeep:
		if field in obj:
			newObj[field] = obj[field]
	return newObj

def createToken(username, isAdmin, name=None, ttl=None):
	while True:
		token = util.getRandomString(32)
		tKey = Keys.getToken(token)
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
