from flask_restx import Resource
from flask import request

from api import api, auth_required
from services import cleaner, finder, swagger_service, reading_service

ns = api.namespace('readings', description='Access to all readings')

@ns.route('/')
class ReadingsList(Resource):
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@auth_required
	@api.expect([swagger_service.createReadingData])
	def post(auth, self):
		return reading_service.createReadings(auth, None, None, None)
