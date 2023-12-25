import util

def cleanSensor(sensor):
	return util.cleanObject(sensor, ['name', 'desc', 'unit'])
