from flask_restx import Api

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
