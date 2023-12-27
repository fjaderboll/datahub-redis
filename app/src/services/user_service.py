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
