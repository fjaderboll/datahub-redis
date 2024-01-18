from flask_restx import Resource, fields, abort

from api import api, auth_required, auth_optional
from db import db, Keys
from services import util, cleaner, swagger_service, user_service, token_service, settings_service

ns = api.namespace('users', description='Login and get user information')

@ns.route('/')
class UsersList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		util.verifyAdmin(auth)

		users = user_service.getAllUsers()
		return cleaner.cleanUsers(users)

	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@api.expect(swagger_service.createUserData)
	@auth_optional
	def post(auth, self):
		if not settings_service.getAllowPublicCreateUser():
			util.verifyAdmin(auth)

		username = util.getPayload('username')
		password = util.getPayload('password')

		util.verifyValidName(username, "Username")
		util.verifyNoneEmpty(password, 'Password')

		if db.sismember(Keys.getUsers(), username):
			abort(400, "Username '" + username + "' already exists")

		salt = util.createPasswordSalt()
		hash = util.createPasswordHash(password, salt)
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
	@api.expect(swagger_service.updateUserData)
	def put(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		user_service.findUser(username)

		if 'email' in api.payload:
			db.hset(Keys.getUser(username), 'email', api.payload['email'])

		if 'isAdmin' in api.payload:
			util.verifyAdmin(auth)
			db.hset(Keys.getUser(username), 'isAdmin', int(api.payload['isAdmin']))

		if 'password' in api.payload:
			newPassword = api.payload['password']
			salt = util.createPasswordSalt()
			hash = util.createPasswordHash(newPassword, salt)
			db.hset(Keys.getUser(username), 'passwordHash', hash, 'passwordSalt', salt)

		return cleaner.cleanUser(user_service.findUser(username))

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def delete(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		user_service.findUser(username)

		user_service.deleteUser(username)

		return "Removed user '" + username + "'"

@ns.route('/<string:username>/login')
@ns.param('username', 'Username')
class UsersLogin(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad parameters')
	@ns.response(401, 'Invalid credentials')
	@api.expect(swagger_service.loginUserData)
	def post(self, username):
		validName = util.verifyValidName(username, "Username", fail=False)
		if not validName:
			abort(401, "Invalid credentials")

		user = db.hgetall(Keys.getUser(username))
		if len(user) == 0:
			abort(401, "Invalid credentials")

		if not settings_service.getAllowNonAdminLogin() and not bool(int(user['isAdmin'])):
			abort(401, "Invalid credentials")

		hash = util.createPasswordHash(api.payload['password'], user['passwordSalt'])
		if hash == user['passwordHash']:
			tokenInfo = token_service.createToken(username, user['isAdmin'], ttl=settings_service.getTokenTTL(), desc='Login')
			return token_service.formatToken(tokenInfo, hideToken=False)
		else:
			abort(401, "Invalid credentials")

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
		tokenInfo = token_service.createToken(username, user['isAdmin'], ttl=settings_service.getTokenTTL(), desc='Impersonate')
		return token_service.formatToken(tokenInfo, hideToken=False)
