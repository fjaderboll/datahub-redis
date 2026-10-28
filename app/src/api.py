from functools import wraps
from flask import request, current_app
from flask_restx import Api, abort


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
	current_app.logger.exception('Unhandled exception in %s %s', request.method, request.path)
	message = 'An unhandled exception occurred.'
	return {'message': message}, 500

def get_auth():
	from services import token_service # services import this module

	auth = None
	if "Authorization" in request.headers:
		parts = request.headers["Authorization"].split(" ")
		if len(parts) == 2:
			tokenInfo = token_service.getAuth(parts[1])
			if tokenInfo:
				auth = {
					'id': tokenInfo['user_id'],
					'username': tokenInfo['username'],
					'tokenId': tokenInfo['id'],
					'isAdmin': bool(tokenInfo['is_admin'])
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
