from datetime import datetime, timedelta
from flask_restx import Resource, abort

from api import api, auth_required
from db import db, Keys
from services import util, swagger_service, settings_service, token_service

ns = api.namespace('tokens', description='List, view, create and delete tokens')

@ns.route('/')
class TokensList(Resource):
	@ns.response(200, 'Success')
	@auth_required
	def get(auth, self):
		tokenInfos = []
		for tokenInfo in db.scan_iter(match='token:*'):
			tokenInfo = db.hgetall(tokenInfo)
			if tokenInfo['username'] == auth['username']:
				tokenInfos.append(token_service.formatToken(tokenInfo))

		return tokenInfos

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect(swagger_service.createUpdateTokenData)
	def post(auth, self):
		ttl = util.getPayload('ttl', settings_service.getTokenTTL())
		desc = util.getPayload('desc')

		tokenInfo = token_service.createToken(auth['username'], auth['isAdmin'], ttl=ttl, desc=desc)
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
		tKey = Keys.getToken(tokenInfo['token'])

		payload = api.payload
		if 'desc' in payload:
			db.hset(tKey, 'desc', payload['desc'])

		if 'enabled' in payload:
			db.hset(tKey, 'enabled', int(payload['enabled']))

		if 'ttl' in payload:
			ttl = payload['ttl']
			if ttl == 0:
				db.persist(tKey)
				db.hset(tKey, 'expire', '')
			else:
				db.expire(tKey, ttl)
				db.hset(tKey, 'expire', (datetime.now() + timedelta(seconds=ttl)).replace(microsecond=0).isoformat())

		tokenInfo = db.hgetall(tKey)
		return token_service.formatToken(tokenInfo)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown token')
	@auth_required
	def delete(auth, self, id):
		tokenInfo = token_service.findToken(auth, id)
		db.delete(Keys.getToken(tokenInfo['token']))

		return "Removed token with ID = " + str(id)
