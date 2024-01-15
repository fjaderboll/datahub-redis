from flask_restx import abort

from db import db, Keys
from services import util

def getAllUsers():
	usernames = db.smembers(Keys.getUsers())
	users = []
	for username in usernames:
		user = findUser(username)
		users.append(user)
	return users

def findUser(username):
	validName = util.verifyValidName(username, "Username", fail=False)
	if not validName:
		abort(404, "Unknown user '" + username + "'")

	user = db.hgetall(Keys.getUser(str(username)))
	if len(user) == 0:
		abort(404, "Unknown user '" + username + "'")

	return user

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
