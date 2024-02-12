from flask_restx import abort

from db import db, Keys
from services import util, settings_service, token_service

def getAllUsers():
	usernames = db.smembers(Keys.getUsers())
	users = []
	for username in usernames:
		user = findUser(username)
		users.append(user)
	return users

def findUser(username, statusCode=404):
	validName = util.verifyValidName(username, "Username", fail=False)
	if not validName:
		abort(statusCode, "Unknown user '" + username + "'")

	user = db.hgetall(Keys.getUser(str(username)))
	if len(user) == 0:
		abort(statusCode, "Unknown user '" + username + "'")

	return user

def login(username, password):
	validName = util.verifyValidName(username, "Username", fail=False)
	if not validName:
		abort(401, "Invalid credentials")

	user = db.hgetall(Keys.getUser(username))
	if len(user) == 0:
		abort(401, "Invalid credentials")

	if not settings_service.getAllowNonAdminLogin() and not bool(int(user['isAdmin'])):
		abort(401, "Invalid credentials")

	hash = util.createPasswordHash(password, user['passwordSalt'])
	if hash == user['passwordHash']:
		tokenInfo = token_service.createToken(username, user['isAdmin'], ttl=settings_service.getTokenTTL(), desc='Login')
		return token_service.formatToken(tokenInfo, hideToken=False)
	else:
		abort(401, "Invalid credentials")

def deleteUser(username):
	userDatasetIds = db.smembers(Keys.getUserDatasetIds(username))

	otherUsernames = db.smembers(Keys.getUsers()) - {username}
	for otherUsername in otherUsernames:
		otherUserDatasetIds = db.smembers(Keys.getUserDatasetIds(otherUsername))
		userDatasetIds -= otherUserDatasetIds

	if len(userDatasetIds) > 0:
		abort(400, 'This will result in ' + str(len(userDatasetIds)) + ' orphaned dataset(s); delete or share them first')

	db.delete(Keys.getUser(username))
	db.delete(Keys.getUserDatasetIds(username))
	db.srem(Keys.getUsers(), username)
