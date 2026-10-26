from flask_restx import Resource

from api import api, auth_required, auth_optional
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

		user = user_service.createUser(username, password)
		return cleaner.cleanUser(user)

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

		if 'isAdmin' in api.payload:
			util.verifyAdmin(auth)

		if 'password' in api.payload:
			util.verifyNoneEmpty(api.payload['password'], 'Password')

		user = user_service.updateUser(username, email=util.getPayload('email'), isAdmin=util.getPayload('isAdmin'), password=util.getPayload('password'))
		return cleaner.cleanUser(user)

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
	@ns.response(400, 'Bad request')
	@ns.response(401, 'Invalid credentials')
	@api.expect(swagger_service.loginUserData)
	def post(self, username):
		desc = ''
		if 'referrer' in api.payload:
			desc = api.payload['referrer']
		ttl = settings_service.getTokenTTL()
		return user_service.login(username, api.payload['password'], ttl, desc)

@ns.route('/<string:username>/logout')
@ns.param('username', 'Username')
class UsersLogout(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown user')
	@auth_required
	def post(auth, self, username):
		util.verifyAdminOrUser(auth, username)
		token_service.deleteToken(auth['tokenId'])
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
		tokenInfo = token_service.createToken(user, ttl=settings_service.getTokenTTL(), desc='Impersonate')
		return token_service.formatToken(tokenInfo, hideToken=False)
