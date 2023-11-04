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
			security='default')

@api.errorhandler
def default_error_handler(e):
	message = 'An unhandled exception occurred.'
	return {'message': message}, 500

def auth_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if "Authorization" in request.headers:
			parts = request.headers["Authorization"].split(" ")
			if len(parts) == 2:
				token = parts[1]
				tKey = Keys.getToken(token)
				user = db.hgetall(tKey)
				if user:
					auth = user
					return f(auth, *args, **kwargs)

		abort(401, "Unauthorized")

	return decorated
