#!/usr/bin/env python3

import sys
from flask import Flask, Blueprint
from flask_cors import CORS

from api import api
from endpoints.state import ns as namespace_state
from endpoints.users import ns as namespace_users
from endpoints.tokens import ns as namespace_tokens
from endpoints.datasets import ns as namespace_datasets

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

def main(port, debug):
	blueprint = Blueprint('api', __name__, url_prefix='')
	api.init_app(blueprint)
	api.add_namespace(namespace_state)
	api.add_namespace(namespace_users)
	api.add_namespace(namespace_tokens)
	api.add_namespace(namespace_datasets)
	app.register_blueprint(blueprint)
	app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == '__main__':
	port = 2070
	if len(sys.argv) == 2:
		port = int(sys.argv[1])

	main(port, port != 80)
