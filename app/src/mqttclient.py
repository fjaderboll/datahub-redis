
import json
import traceback

from db import db, Keys
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
				print(client)
				mqtt.subscribe('in/users/+/datasets/+/nodes/+/sensors/+/readings')
				mqtt.subscribe('in/users/+/datasets/+/nodes/+/readings')
				mqtt.subscribe('in/users/+/datasets/readings')
				mqtt.subscribe('in/users/+/readings')
			else:
				logger.info('Bad connection. Code:', rc)

		@mqtt.on_message()
		def on_message(client, userdata, message):
			topic = message.topic
			payload = message.payload.decode()
			topicParts = topic.split('/')
			auth = {
				'username': topicParts[2]
			}

			try:
				data = json.loads(payload)
				datasetName = topicParts[4] if len(topicParts) >= 5 else data['datasetName']
				nodeName    = topicParts[6] if len(topicParts) >= 7 else data['nodeName']
				sensorName  = topicParts[8] if len(topicParts) >= 9 else data['sensorName']

				dataset = finder.findDataset(auth, datasetName, create=True)
				node = finder.findNode(dataset['id'], nodeName, create=True)
				sensor = finder.findSensor(node['id'], sensorName, create=True)
				value = data['value']
				time = data['time'] if 'time' in data else None

				reading = reading_service.createReading(dataset, node, sensor, value, time)
				print(reading)
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
