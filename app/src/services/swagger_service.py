from flask_restx import fields

from api import api

#class NullableString(fields.String):
#    __schema_type__ = ['string', 'null']
#    __schema_example__ = 'nullable string'
#
#class NullableInteger(fields.Integer):
#    __schema_type__ = ['string', 'null']
#    __schema_example__ = 'nullable integer'

updateSystemData = api.model('UpdateSystemData', {
    'retention': fields.Integer(description='Set default retention policy in seconds'),
    'applyRetention': fields.Boolean(description='Apply given or previously set retention to existing timeseries'),
	'allowPublicCreateUser': fields.Boolean(description='Allow anyone to create user (otherwise only administrator can do it)')
})

createUpdateTokenData = api.model('CreateUpdateTokenData', {
    'desc': fields.String(description='Description of token'),
    'ttl': fields.Integer(description='Time-to-live in seconds. Use 0 for infinite time.', min=0, default=0),
    'enabled': fields.Boolean(description='If the token should be enabled', default=True)
})

createUserData = api.model('CreateUserData', {
	'username': fields.String(description='Username, must start with [a-z] followed by [a-z0-9_-@.]', required=True),
	'password': fields.String(description='Password, non empty', required=True),
	'email': fields.String(description='E-mail')
})
updateUserData = api.model('UpdateUserData', {
	'password': fields.String(description='Password, non empty'),
	'email': fields.String(description='E-mail'),
	'isAdmin': fields.Boolean(description='Administrator. Must be administrator to update.')
})

createDatasetData = api.model('CreateDatasetData', {
    'name': fields.String(description='Name of dataset', required=True),
    'desc': fields.String(description='Description of dataset')
})
updateDatasetData = api.model('UpdateDatasetData', {
    'name': fields.String(description='Name of dataset'),
    'desc': fields.String(description='Description of dataset')
})
addDatasetUserData = api.model('AddDatasetUserData', {
    'username': fields.String(description='Username of user to share dataset with', required=True)
})

createNodeData = api.model('CreateNodeData', {
    'name': fields.String(description='Name of node', required=True),
    'desc': fields.String(description='Description of node')
})
updateNodeData = api.model('UpdateNodeData', {
    'name': fields.String(description='Name of node'),
    'desc': fields.String(description='Description of node')
})

createSensorData = api.model('CreateSensorData', {
    'name': fields.String(description='Name of sensor', required=True),
    'desc': fields.String(description='Description of sensor'),
    'unit': fields.String(description='Unit for sensor readings')
})
updateSensorData = api.model('UpdateSensorData', {
    'name': fields.String(description='Name of sensor'),
    'desc': fields.String(description='Description of sensor'),
    'unit': fields.String(description='Unit for sensor readings')
})

createReadingData = api.model('CreateReadingData', {
	'value': fields.Float(description='The value', required=True),
	'time': fields.String(description='An ISO timestamp or relative time in seconds. Defaults to now.')
})
