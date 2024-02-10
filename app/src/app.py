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
from pubsubthread import PubSubThread

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

	print('started')
	pubSubThread = PubSubThread(app.logger)

	## this condition is needed to prevent creating duplicated thread in Flask debug mode
	if not (app.debug or os.environ.get('FLASK_ENV') == 'development') or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
		originalHandler = signal.getsignal(signal.SIGINT) # ctrl+c
		def sigintHandler(signum, frame):
			pubSubThread.stop()
			originalHandler(signum, frame)
		signal.signal(signal.SIGINT, sigintHandler)

		pubSubThread.start()

	return app

if __name__ == '__main__': # running from command line
	port = 2070
	if len(sys.argv) == 2:
		port = int(sys.argv[1])

	app = createApp()
	app.run(host="0.0.0.0", port=port, debug=True)
else: # running via flask
	app = createApp()
