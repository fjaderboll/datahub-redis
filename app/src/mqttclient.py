
import json
import traceback

from flask_mqtt import Mqtt

from services import finder, reading_service

def create(app):
	mqtt = Mqtt(app)
	logger = app.logger

	class MqttClient():
		def __init__(self):
			pass

		@mqtt.on_connect()
		def on_connect(client, userdata, flags, rc):
			if rc == 0:
				logger.info('Connected successfully')
				topics = [
					'$queue/in/datasets/+/nodes/+/sensors/+/readings',
					'$queue/in/datasets/+/nodes/+/readings',
					'$queue/in/datasets/+/readings'
				]
				for topic in topics:
					(result, mid) = mqtt.subscribe(topic)
					if result == 0:
						logger.info('Subscribed to: ' + topic)
					else:
						logger.error('Unable to subscribe to: ' + topic)
			else:
				logger.info('Bad connection. Code:', rc)

		@mqtt.on_message()
		def on_message(client, userdata, message):
			topic = message.topic
			payload = message.payload.decode()
			topicParts = topic.split('/')
			auth = None # user<->dataset validation already done in 'authorize'

			try:
				data = json.loads(payload)
				datasetName = topicParts[2]
				nodeName    = topicParts[4] if len(topicParts) >= 5 else data['nodeName']
				sensorName  = topicParts[6] if len(topicParts) >= 7 else data['sensorName']

				dataset = finder.findDataset(auth, datasetName, create=False, validateUser=False) # dataset created in 'authorize'
				node = finder.findNode(dataset['id'], nodeName, create=True)
				sensor = finder.findSensor(node['id'], sensorName, create=True)
				value = data['value']
				time = data['time'] if 'time' in data else None

				reading = reading_service.createReading(dataset, node, sensor, value, time)
				#print(reading)
			except Exception as e:
				logger.error('Unable to process message on topic {} with payload: {}\n{}'.format(topic, payload, e))
				traceback.print_exc()

		def publish(self, message):
			reading = json.loads(message)
			topic = 'out/datasets/{}/nodes/{}/sensors/{}/readings'.format(reading['datasetName'], reading['nodeName'], reading['sensorName'])
			mqtt.publish(topic, message)
			#logger.info('Published to {}: {}'.format(topic, message))

	client = MqttClient()
	logger.info('MQTT initiated')
	return client
