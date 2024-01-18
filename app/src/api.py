from functools import wraps
from flask import request
from flask_restx import Api, abort

from db import db, Keys

authorizations = {
	'default': {
		'type': 'apiKey',
		'in': 'header',
		'name': 'Authorization'
	}
}

api = Api(version='2.0',
			title='datahub-redis',
			description='A speedy REST API for all your sensor readings',
			authorizations=authorizations,
			security='default',
			validate=True)

@api.errorhandler
def default_error_handler(e):
	message = 'An unhandled exception occurred.'
	return {'message': message}, 500

def get_auth():
	auth = None
	if "Authorization" in request.headers:
		parts = request.headers["Authorization"].split(" ")
		if len(parts) == 2:
			token = parts[1]
			tokenInfo = db.hgetall(Keys.getToken(token))
			if tokenInfo and int(tokenInfo['enabled']):
				isAdmin = db.hget(Keys.getUser(tokenInfo['username']), 'isAdmin')
				auth = {
					'username': tokenInfo['username'],
					'token': tokenInfo['token'],
					'isAdmin': bool(int(isAdmin))
				}
	return auth

def auth_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = get_auth()
		if auth:
			return f(auth, *args, **kwargs)
		abort(401, "Unauthorized")

	return decorated

def auth_optional(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = get_auth()
		return f(auth, *args, **kwargs)

	return decorated
