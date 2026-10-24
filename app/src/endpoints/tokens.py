from flask_restx import Resource

from api import api, auth_required
from services import util, swagger_service, settings_service, token_service

ns = api.namespace('tokens', description='List, view, create and delete tokens')

@ns.route('/')
class TokensList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		return [token_service.formatToken(tokenInfo) for tokenInfo in token_service.getUserTokens(auth['username'])]

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect(swagger_service.createUpdateTokenData)
	def post(auth, self):
		ttl = util.getPayload('ttl', settings_service.getTokenTTL())
		desc = util.getPayload('desc')

		tokenInfo = token_service.createToken(auth, ttl=ttl, desc=desc)
		return token_service.formatToken(tokenInfo, hideToken=False)

@ns.route('/<int:id>')
@ns.param('id', 'Token ID')
class TokensView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown token')
	@auth_required
	def get(auth, self, id):
		tokenInfo = token_service.findToken(auth, id)
		return token_service.formatToken(tokenInfo)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown token')
	@auth_required
	@api.expect(swagger_service.createUpdateTokenData)
	def put(auth, self, id):
		tokenInfo = token_service.findToken(auth, id)
		tokenInfo = token_service.updateToken(tokenInfo, desc=util.getPayload('desc'), enabled=util.getPayload('enabled'), ttl=util.getPayload('ttl'))
		return token_service.formatToken(tokenInfo)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown token')
	@auth_required
	def delete(auth, self, id):
		tokenInfo = token_service.findToken(auth, id)
		token_service.deleteToken(tokenInfo['token'])

		return "Removed token with ID = " + str(id)
