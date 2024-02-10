
import threading
import time
from paho.mqtt import client
from db import db, Keys

class PubSubThread(threading.Thread):
	def __init__(self, logger):
		super().__init__()
		self.logger = logger
		self.stopEvent = threading.Event()

	def startup(self):
		self.logger.info('Started')
		self.pubsub = db.pubsub()
		self.pubsub.subscribe(Keys.getReadingsTopic())
		self.i = 0

	def stop(self):
		self.stopEvent.set()
		self.logger.info('Stopped')

	def shutdown(self):
		self.logger.info('Shutdown')

	def handle(self):
		message = self.pubsub.get_message()
		if message:
			if message['type'] == 'message':
				self.i += 1
				self.logger.info(str(self.i) + " " + message['data'])

	def run(self):
		self.startup()
		self.logger.info('Running')
		while not self.stopEvent.is_set():
			self.handle()
			time.sleep(0.1)
			#self.client.loop()
		self.shutdown()
