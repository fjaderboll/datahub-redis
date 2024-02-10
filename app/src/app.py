#!/usr/bin/env python3

import os
import sys
import signal
from flask import Flask, Blueprint
from flask_cors import CORS

from api import api
from endpoints.state import ns as namespace_state
from endpoints.users import ns as namespace_users
from endpoints.tokens import ns as namespace_tokens
from endpoints.readings import ns as namespace_readings
from endpoints.datasets_nodes_sensors_readings import ns as namespace_datasets
import mqttclient
from mqttpub import MqttPub

def createApp():
	app = Flask(__name__)
	cors = CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

	blueprint = Blueprint('api', __name__, url_prefix='')
	api.init_app(blueprint)
	api.add_namespace(namespace_state)
	api.add_namespace(namespace_users)
	api.add_namespace(namespace_tokens)
	api.add_namespace(namespace_readings)
	api.add_namespace(namespace_datasets)
	app.register_blueprint(blueprint)

	app.config['MQTT_BROKER_URL'] = 'localhost'
	app.config['MQTT_BROKER_PORT'] = 1883
	#app.config['MQTT_USERNAME'] = ''
	#app.config['MQTT_PASSWORD'] = ''
	app.config['MQTT_CLIENT_ID'] = 'flask-app'
	app.config['MQTT_TLS_ENABLED'] = False

	if not (app.debug or os.environ.get('FLASK_ENV') == 'development') or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
		mqttClient = mqttclient.create(app)

		mqttPubThread = MqttPub(app.logger, mqttClient)
		originalHandler = signal.getsignal(signal.SIGINT) # ctrl+c
		def sigintHandler(signum, frame):
			mqttPubThread.stop()
			originalHandler(signum, frame)
		signal.signal(signal.SIGINT, sigintHandler)
		mqttPubThread.start()

	return app

if __name__ == '__main__': # running from command line
	port = 2070
	if len(sys.argv) == 2:
		port = int(sys.argv[1])

	app = createApp()
	app.run(host="0.0.0.0", port=port, debug=True)
else: # running via flask
	app = createApp()
