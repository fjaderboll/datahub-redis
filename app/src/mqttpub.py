
import threading
import time
import tsdb

class MqttPub(threading.Thread):
	def __init__(self, logger, mqttClient):
		super().__init__()
		self.logger = logger
		self.mqttClient = mqttClient
		self.stopEvent = threading.Event()

	def startup(self):
		self.logger.info('Started')
		self.pubsub = tsdb.redisDb.pubsub()
		self.pubsub.subscribe(tsdb.READINGS_TOPIC)

	def stop(self):
		self.stopEvent.set()
		self.logger.info('Stopped')

	def shutdown(self):
		self.logger.info('Shutdown')

	def handle(self):
		message = self.pubsub.get_message()
		if message:
			if message['type'] == 'message':
				self.mqttClient.publish(message['data'])

	def run(self):
		self.startup()
		self.logger.info('Running')
		while not self.stopEvent.is_set():
			self.handle()
			time.sleep(0.01)
		self.shutdown()
