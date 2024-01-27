from flask_restx import fields

from api import api

#class NullableString(fields.String):
#    __schema_type__ = ['string', 'null']
#    __schema_example__ = 'nullable string'
#
#class NullableInteger(fields.Integer):
#    __schema_type__ = ['string', 'null']
#    __schema_example__ = 'nullable integer'

updateSystemSettingsData = api.model('UpdateSystemSettingsData', {
    'retention': fields.Integer(description='Set default retention policy in seconds'),
    'applyRetention': fields.Boolean(description='Apply given or previously set retention to existing timeseries'),
	'allowPublicCreateUser': fields.Boolean(description='Allow anyone to create user (otherwise only administrator can do it)'),
	'allowNonAdminLogin': fields.Boolean(description='Allow anyone to login (otherwise only administrator can do it)'),
	'tokenTTL': fields.Integer(description='Default time-to-live value in seconds for newly created tokens')
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
loginUserData = api.model('LoginUserData', {
	'password': fields.String(description='Password, non empty', required=True)
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

createSensorReadingData = api.model('CreateSensorReadingData', {
	'value': fields.Float(description='The value', required=True),
	'time': fields.String(description='An ISO timestamp or relative time in seconds. Defaults to now.')
})
createNodeReadingData = api.model('CreateNodeReadingData', {
	'value': fields.Float(description='The value', required=True),
	'time': fields.String(description='An ISO timestamp or relative time in seconds. Defaults to now.'),
	'sensorName': fields.String(description='Name of sensor', required=True)
})
createDatasetReadingData = api.model('CreateDatasetReadingData', {
	'value': fields.Float(description='The value', required=True),
	'time': fields.String(description='An ISO timestamp or relative time in seconds. Defaults to now.'),
	'sensorName': fields.String(description='Name of sensor', required=True),
	'nodeName': fields.String(description='Name of node', required=True)
})
createReadingData = api.model('CreateReadingData', {
	'value': fields.Float(description='The value', required=True),
	'time': fields.String(description='An ISO timestamp or relative time in seconds. Defaults to now.'),
	'sensorName': fields.String(description='Name of sensor', required=True),
	'nodeName': fields.String(description='Name of node', required=True),
	'datasetName': fields.String(description='Name of dataset', required=True)
})
getReadingsParams = {
	'after':  {'in': 'query', 'description': 'Only return readings after this ISO timestamp or relative time in seconds', 'example': '-3600'},
	'before': {'in': 'query', 'description': 'Only return readings before this ISO timestamp or relative time in seconds', 'example': '2023-12-26T10:15:30+01:00'},
	'limit':  {'in': 'query', 'description': 'Limits the result to this number of readings', 'default': '1000'}
}
deleteReadingsParams={
	'after':  {'in': 'query', 'description': 'Only delete readings after this ISO timestamp or relative time in seconds', 'example': '-3600'},
	'before': {'in': 'query', 'description': 'Only delete readings before this ISO timestamp or relative time in seconds', 'example': '2023-12-26T10:15:30+01:00'}
}
