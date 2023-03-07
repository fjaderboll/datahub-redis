from flask_restx import Resource, fields, abort

from api import api
from db import db, Keys
import util
import service

ns = api.namespace('users', description='Login and get user information')

@ns.route('/')
class UsersList(Resource):
	createFields = api.model('CreateUserData', {
		'username': fields.String(description='Username, must start with [a-z] followed by [a-z0-9_-@.]', required=True),
		'password': fields.String(description='Password, non empty', required=True)
	})

	@ns.response(200, 'Success')
	def get(self):
		usernames = db.smembers(Keys.USERS)
		users = []
		for username in usernames:
			user = service.findUser(username, verifyUsername=False)
			if user:
				users.append(user)
		return users

	@api.doc(security=None)
	@api.expect(createFields, validate=True)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	def post(self):
		input = api.payload

		util.verifyValidName(input['username'], "Username")
		util.verifyNoneEmpty(input['password'], 'Password')

		username = input['username']
		if db.sismember(Keys.USERS, username):
			abort(400, "Username '" + username + "' already exists")

		salt = util.createPasswordSalt()
		hash = util.createPasswordHash(input['password'], salt)
		userCount = db.scard(Keys.USERS)

		user = {
			'username': username,
			'passwordHash': hash,
			'passwordSalt': salt,
			'email': "",
			'isAdmin': int(userCount == 0)
		}
		db.hset(Keys.getUserKey(username), mapping=user)
		db.sadd(Keys.USERS, username)
		return service.findUser(username)

@ns.route('/<string:username>')
@ns.param('username', 'Username')
class UsersGet(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	def get(self, username):
		return service.findUser(username)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	def put(self, username):
		input = api.payload

		user = service.findUser(username)

		if 'email' in input:
			db.hset(Keys.getUserKey(username), 'email', input['email'])

		if 'isAdmin' in input:
			db.hset(Keys.getUserKey(username), 'isAdmin', input['isAdmin'])

		if 'password' in input:
			db.hset(Keys.getUserKey(username), 'password', input['isAdmin'])

		return service.findUser(username)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	def delete(self, username):
		service.findUser(username)

		db.delete(Keys.getUserKey(username))
		db.lrem(Keys.USERS, 0, username)

		return username

@ns.route('/<string:username>/login')
@ns.param('username', 'Username')
class UsersLogin(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	def post(self, username):
		util.verifyValidName(username, "Username")
		dbUser = db.hgetall(Keys.getUserKey(username))
		if len(dbUser) == 0:
			abort(401, "Invalid credentials")

		input = api.payload
		if 'password' in input and input['password'] is not None:
			hash = util.createPasswordHash(input['password'], dbUser['passwordSalt'])
			if hash == dbUser['passwordHash']:
				return service.createToken(username, ttl=30)
			else:
				abort(401, "Invalid credentials")
		else:
			abort(400, "Missing password")

@ns.route('/<string:username>/impersonate')
@ns.param('username', 'Username')
class UsersImpersonate(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	def get(self, username):
		service.findUser(username)
		return service.createToken(username, ttl=30)
