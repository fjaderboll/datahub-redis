import json
import re
import time
from datetime import datetime, timezone

import requests
from flask import current_app
from flask_restx import abort

import tsdb
from services import settings_service

# NanoMQ doesn't tell when or from where a client connected, so that is recorded at each login,
# per client ID. Entries of clients no longer connected are removed when the clients are listed.
LOGINS_KEY = 'mqtt-logins'

PROTOCOL_VERSIONS = {3: '3.1', 4: '3.1.1', 5: '5.0'}

def recordLogin(clientId, username, address):
	try:
		login = {'username': username, 'address': address, 'time': int(time.time() * 1000)}
		tsdb.redisDb.hset(LOGINS_KEY, clientId, json.dumps(login))
	except Exception:
		current_app.logger.exception('Unable to record the MQTT login of %s', clientId) # the login itself is still allowed

def callApi(path):
	try:
		response = requests.get(settings_service.getBrokerApiUrl() + path, auth=settings_service.getBrokerApiLogin(), timeout=5)
		response.raise_for_status()
		return response
	except requests.ConnectionError:
		abort(503, 'Unable to reach the MQ broker')
	except requests.RequestException as e:
		abort(503, 'Unable to get the state of the MQ broker: ' + str(e))

def parseMetrics(text):
	"""Prometheus' text format, a 'name value' line per metric."""
	metrics = {}
	for line in text.splitlines():
		parts = line.split()
		if len(parts) == 2 and not line.startswith('#'):
			metrics[parts[0]] = float(parts[1])
	return metrics

def parseUptime(text):
	match = re.fullmatch(r'(\d+) Hours, (\d+) minutes, (\d+) seconds', text)
	if match:
		return int(match[1]) * 3600 + int(match[2]) * 60 + int(match[3])
	return None

def getLogins(clientIds, since):
	logins = {clientId: json.loads(login) for (clientId, login) in tsdb.redisDb.hgetall(LOGINS_KEY).items()}
	# a client that has just logged in may not be listed yet
	gone = [clientId for (clientId, login) in logins.items() if clientId not in clientIds and login['time'] < since - 60000]
	if gone:
		tsdb.redisDb.hdel(LOGINS_KEY, *gone)
	return logins

def toIsoTime(milliseconds):
	return datetime.fromtimestamp(milliseconds / 1000, timezone.utc).isoformat()

def getState():
	since = int(time.time() * 1000)
	broker = callApi('brokers').json()['data'][0]
	metrics = parseMetrics(callApi('prometheus').text)
	clients = callApi('clients').json()['data']
	subscriptions = callApi('subscriptions').json()['data']
	logins = getLogins({client['client_id'] for client in clients}, since)

	def metric(name):
		value = metrics.get(name)
		return int(value) if value is not None else None

	def formatClient(client):
		clientId = client['client_id']
		login = logins.get(clientId)
		# the login may be from another client that used the same client ID before
		if login and login['username'] != client['username']:
			login = None
		return {
			'clientId': clientId,
			'username': client['username'],
			'isApp': client['username'] == settings_service.getMqttUsername(),
			'connected': client['conn_state'] == 'connected',
			'address': login['address'] if login else None,
			'connectedAt': toIsoTime(login['time']) if login else None,
			'protocolVersion': PROTOCOL_VERSIONS.get(client['proto_ver'], str(client['proto_ver'])),
			'keepAlive': client['keepalive'],
			'subscriptions': [{'topic': s['topic'], 'qos': s['qos']} for s in subscriptions if s['clientid'] == clientId]
		}

	return {
		'version': broker['version'],
		'status': broker['node_status'],
		'uptime': parseUptime(broker['uptime']),
		'connections': metric('nanomq_connections_count'),
		'subscriptions': len(subscriptions),
		'messagesReceived': metric('nanomq_messages_received'),
		'messagesSent': metric('nanomq_messages_sent'),
		'messagesDropped': metric('nanomq_messages_dropped'),
		'memory': metric('nanomq_memory_usage'),
		'cpu': metrics.get('nanomq_cpu_usage'),
		'clients': [formatClient(client) for client in clients]
	}
