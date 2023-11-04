from flask_restx import Resource, fields, abort

from api import api
from db import db, Keys
import util
import service

ns = api.namespace('state', description='Get application state')

@ns.route('/users')
class StateLogin(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	def get(self):
		userCount = db.scard(Keys.getUsers())
		return {
			'createFirstUserRequired': (userCount == 0),
			'createUserAllowed': True
		}
