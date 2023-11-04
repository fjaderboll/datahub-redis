from flask_restx import Resource, fields, abort

from api import api, auth_required
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
	@auth_required
	def get(auth, self):
		util.verifyAdmin(auth)

		usernames = db.smembers(Keys.getUsers())
		users = []
		for username in usernames:
			user = service.findUser(username)
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
		if db.sismember(Keys.getUsers(), username):
			abort(400, "Username '" + username + "' already exists")

		salt = util.createPasswordSalt()
		hash = util.createPasswordHash(input['password'], salt)
		userCount = db.scard(Keys.getUsers())

		user = {
			'username': username,
			'passwordHash': hash,
			'passwordSalt': salt,
			'email': "",
			'isAdmin': int(userCount == 0)
		}
		db.hset(Keys.getUser(username), mapping=user)
		db.sadd(Keys.getUsers(), username)
		return service.findUser(username)

@ns.route('/<string:username>')
@ns.param('username', 'Username')
class UsersGet(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def get(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		return service.findUser(username)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def put(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		service.findUser(username)

		input = api.payload
		if 'email' in input:
			db.hset(Keys.getUser(username), 'email', input['email'])

		if 'isAdmin' in input:
			db.hset(Keys.getUser(username), 'isAdmin', int(input['isAdmin'] == 1))

		if 'password' in input and input['password'] is not None and input['password'] != "":
			salt = util.createPasswordSalt()
			hash = util.createPasswordHash(input['password'], salt)
			db.hset(Keys.getUser(username), 'passwordHash', hash, 'passwordSalt', salt)

		return service.findUser(username)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def delete(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		service.findUser(username)

		# TODO stop if only user for connected datasets

		db.delete(Keys.getUser(username))
		db.srem(Keys.getUsers(), 0, username)

		return "Removed user '" + username + "'"

@ns.route('/<string:username>/login')
@ns.param('username', 'Username')
class UsersLogin(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad parameters')
	@ns.response(401, 'Invalid credentials')
	def post(self, username):
		validName = util.verifyValidName(username, "Username", fail=False)
		if not validName:
			abort(401, "Invalid credentials")

		dbUser = db.hgetall(Keys.getUser(username))
		if len(dbUser) == 0:
			abort(401, "Invalid credentials")

		input = api.payload
		if 'password' in input and input['password'] is not None:
			hash = util.createPasswordHash(input['password'], dbUser['passwordSalt'])
			if hash == dbUser['passwordHash']:
				return service.createToken(username, str(dbUser['isAdmin']) == "1", ttl=3600)
			else:
				abort(401, "Invalid credentials")
		else:
			abort(400, "Missing password")

@ns.route('/<string:username>/logout')
@ns.param('username', 'Username')
class UsersLogout(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def post(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		tKey = Keys.getToken(auth['token'])
		db.delete(tKey)
		return "Token invalidated"

@ns.route('/<string:username>/impersonate')
@ns.param('username', 'Username')
class UsersImpersonate(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def post(auth, self, username):
		util.verifyAdmin(auth)
		dbUser = service.findUser(username, dbObj=True)
		return service.createToken(username, str(dbUser['isAdmin']) == "1", ttl=1200)
