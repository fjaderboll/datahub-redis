from flask_restx import Resource
from flask_restx import abort

import os

from api import api, auth_required
from db import db, ts, Keys
from services import util, swagger_service, settings_service, node_service, sensor_service, reading_service, user_service

ns = api.namespace('mqtt', description='MQ broker endpoints')

@ns.route('/authenticate')
class Authenticate(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@ns.response(401, 'Invalid credentials')
	@api.expect(swagger_service.mqttAuthenticateData)
	def post(self):
		username = api.payload['username']
		password = api.payload['password']

		if username == settings_service.getMqttUsername():
			if password != settings_service.getMqttPassword():
				abort(401, "Invalid credentials")
		else:
			tokenInfo = user_service.login(username, password)

		return {
			"result": "allow"
			#"is_superuser": tokenInfo['isAdmin']
		}

@ns.route('/authorize')
class Authorize(Resource):
	@api.doc(security=None)
	@ns.response(200, 'Success')
	@ns.response(400, 'Bad request')
	@ns.response(401, 'Invalid credentials')
	@api.expect(swagger_service.mqttAuthorizeData)
	def post(self):
		username = api.payload['username']
		topic = api.payload['topic']
		action = api.payload['action']

		allow = False

		if action == 'subscribe' and topic.startswith("out/"):
			allow = True
		elif action == 'publish' and topic.startswith("in/"):
			allow = True

		if allow:
			if username != settings_service.getMqttUsername():
				datasetName = ''
				# TODO check if username is allowed for dataset

		return {
			"result": 'allow' if allow else 'ignore'
		}
