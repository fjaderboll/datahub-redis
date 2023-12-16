from datetime import datetime, timedelta
from flask_restx import Resource, abort

from api import api, auth_required
from db import db, Keys
import service

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
				tokenInfos.append(service.formatToken(tokenInfo))

		return tokenInfos

	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	def post(auth, self):
		input = api.payload
		ttl = input['ttl']
		desc = input['desc']

		ttlInt = None
		if ttl:
			try:
				ttlInt = int(input['ttl'])
				if ttlInt <= 0:
					raise ValueError()
			except ValueError:
				abort(400, 'Invalid TTL')

		tokenInfo = service.createToken(auth['username'], ttl=ttlInt, desc=desc)
		return service.formatToken(tokenInfo, hideToken=False)

@ns.route('/<int:id>')
@ns.param('id', 'Token ID')
class TokensView(Resource):
	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown token')
	@auth_required
	def get(auth, self, id):
		tokenInfo = service.findToken(auth, id)
		return service.formatToken(tokenInfo)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown token')
	@auth_required
	def put(auth, self, id):
		tokenInfo = service.findToken(auth, id)
		tKey = Keys.getToken(tokenInfo['token'])

		input = api.payload
		if 'desc' in input:
			db.hset(tKey, 'desc', input['desc'])

		if 'enabled' in input:
			db.hset(tKey, 'enabled', int(input['enabled'] == "true"))

		if 'ttl' in input:
			try:
				ttlInt = int(input['ttl'])
				if ttlInt <= 0:
					raise ValueError()
				db.expire(tKey, ttlInt)
				db.hset(tKey, 'expire', (datetime.now() + timedelta(seconds=ttlInt)).replace(microsecond=0).isoformat())
			except ValueError:
				abort(400, 'Invalid TTL')

		tokenInfo = db.hgetall(tKey)
		return service.formatToken(tokenInfo)

	@ns.response(200, 'Success')
	@ns.response(404, 'Unknown token')
	@auth_required
	def delete(auth, self, id):
		tokenInfo = service.findToken(auth, id)
		db.delete(Keys.getToken(tokenInfo['token']))

		return "Removed token with ID = " + str(id)
