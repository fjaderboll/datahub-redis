#!/usr/bin/env python3

import sys
from flask import Flask, Blueprint

from api import api
from endpoints.users import ns as namespace_users

app = Flask(__name__)

def main(port, debug):
    blueprint = Blueprint('api', __name__, url_prefix='')
    api.init_app(blueprint)
    api.add_namespace(namespace_users)
    app.register_blueprint(blueprint)
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == '__main__':
    port = 2070
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    main(port, port != 80)
