from flask_restx import Resource, fields, abort

from api import api, auth_required
from db import db, Keys
import util
import service
from services import cleaner, user_service, token_service

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

		users = user_service.getAllUsers()
		return cleaner.cleanUsers(users)

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
		return cleaner.cleanUser(user_service.findUser(username))

@ns.route('/<string:username>')
@ns.param('username', 'Username')
class UsersGet(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def get(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		user = user_service.findUser(username)
		return cleaner.cleanUser(user)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def put(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		user_service.findUser(username)

		input = api.payload
		if 'email' in input:
			db.hset(Keys.getUser(username), 'email', input['email'])

		if 'isAdmin' in input:
			db.hset(Keys.getUser(username), 'isAdmin', int(input['isAdmin'] == 1))

		if 'password' in input and input['password'] is not None and input['password'] != "":
			salt = util.createPasswordSalt()
			hash = util.createPasswordHash(input['password'], salt)
			db.hset(Keys.getUser(username), 'passwordHash', hash, 'passwordSalt', salt)

		return cleaner.cleanUser(user_service.findUser(username))

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def delete(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		user_service.findUser(username)

		# TODO abort if the only user for connected datasets

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

		user = db.hgetall(Keys.getUser(username))
		if len(user) == 0:
			abort(401, "Invalid credentials")

		input = api.payload
		if 'password' in input and input['password'] is not None:
			hash = util.createPasswordHash(input['password'], user['passwordSalt'])
			if hash == user['passwordHash']:
				tokenInfo = token_service.createToken(username, user['isAdmin'], ttl=3600, desc='Login')
				return token_service.formatToken(tokenInfo, hideToken=False)
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
		user = user_service.findUser(username)
		tokenInfo = token_service.createToken(username, user['isAdmin'], ttl=3600, desc='Impersonate')
		return token_service.formatToken(tokenInfo, hideToken=False)
