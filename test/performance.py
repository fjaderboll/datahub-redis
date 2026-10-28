#!/usr/bin/env python3
#
# Measures how long it takes to insert readings over HTTP and MQTT, and to load them.
# The readings are put in a node of their own, which is removed afterwards. See README.md.

import argparse
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

host = 'localhost'
apiUrl = 'http://' + host + ':8080/api/'
mqttPort = 1883
nodeName = 'performance'
runs = 3
loads = 5 # times to load the readings of each sensor

class ApiError(Exception):
	pass

session = requests.Session()

def call(method, path, data=None, params=None):
	response = session.request(method, apiUrl + path, json=data, params=params)
	if not response.ok:
		try:
			message = response.json()['message']
		except (ValueError, KeyError):
			message = response.text
		raise ApiError(message)
	return response.json()

def readingsPath(sensorName):
	return 'datasets/{}/nodes/{}/sensors/{}/readings'.format(args.dataset, nodeName, sensorName)

def createReadings(count):
	# every reading gets its own timestamp, readings at the same millisecond would be rejected
	start = datetime.now(timezone.utc) - timedelta(milliseconds=count)
	return [{'value': i % 100, 'time': (start + timedelta(milliseconds=i)).isoformat()} for i in range(count)]

def insertHttpSingle(sensorName, readings):
	st = time.perf_counter()
	for reading in readings:
		call('POST', readingsPath(sensorName), [reading])
	return time.perf_counter() - st

def insertHttpBatch(sensorName, readings):
	st = time.perf_counter()
	call('POST', readingsPath(sensorName), readings)
	return time.perf_counter() - st

def insertMqtt(sensorName, readings):
	"""Publishes all readings over one connection and waits until all are published back out."""
	topic = readingsPath(sensorName)
	login = ['-h', host, '-p', str(mqttPort), '-u', args.user, '-P', args.password]
	timeout = 30 + len(readings) // 100

	subscriber = subprocess.Popen(['mosquitto_sub', *login, '-C', str(len(readings)), '-W', str(timeout), '-t', 'out/' + topic],
		stdout=subprocess.PIPE, text=True)
	try:
		time.sleep(1) # give it time to connect and subscribe
		if subscriber.poll() is not None:
			raise ApiError("Unable to subscribe, does '{}' have access to dataset '{}'?".format(args.user, args.dataset))

		lines = ''.join(json.dumps(reading) + '\n' for reading in readings)
		st = time.perf_counter()
		subprocess.run(['mosquitto_pub', *login, '-l', '-t', 'in/' + topic], input=lines, text=True, check=True)
		received = len(subscriber.communicate()[0].splitlines())
		elapsed = time.perf_counter() - st
	finally:
		subscriber.kill()

	if received != len(readings):
		raise ApiError('Only received {} of {} readings within {} seconds'.format(received, len(readings), timeout))
	return elapsed

def load(sensorName, count):
	st = time.perf_counter()
	readings = call('GET', readingsPath(sensorName), params={'limit': count})
	elapsed = time.perf_counter() - st

	if len(readings) != count:
		raise ApiError('Loaded {} of {} readings'.format(len(readings), count))
	return elapsed

def report(text, seconds, count):
	print('  {:36} {:7.3f} seconds ({:.0f} readings/s)'.format(text, seconds, count / seconds))

def run():
	print("Registering user '{}'".format(args.user))
	try:
		call('POST', 'users/', {'username': args.user, 'password': args.password})
	except ApiError as e:
		print('  ' + str(e))

	print('Logging in')
	token = call('POST', 'users/{}/login'.format(args.user), {'password': args.password})['token']
	session.headers['Authorization'] = 'Bearer ' + token

	print("Creating dataset '{}'".format(args.dataset))
	try:
		call('POST', 'datasets/', {'name': args.dataset})
	except ApiError as e:
		print('  ' + str(e))

	try:
		call('GET', 'datasets/{}/nodes/{}'.format(args.dataset, nodeName))
		nodeExists = True
	except ApiError:
		nodeExists = False
	if nodeExists:
		raise ApiError("Node '{}' already exists in dataset '{}', remove it first".format(nodeName, args.dataset))

	methods = [
		('HTTP, one reading per request', 'http-single', insertHttpSingle),
		('HTTP, all readings in one request', 'http-batch', insertHttpBatch),
		('MQTT, one reading per message', 'mqtt', insertMqtt)
	]
	insertTimes = {text: [] for (text, _, _) in methods}
	loadTimes = []
	try:
		for r in range(runs):
			print('Inserting {} readings, run {} of {}'.format(args.count, r + 1, runs))
			for (text, sensorPrefix, insert) in methods:
				sensorName = '{}-{}'.format(sensorPrefix, r + 1)
				seconds = insert(sensorName, createReadings(args.count))
				insertTimes[text].append(seconds)
				report(text, seconds, args.count)

				for _ in range(loads):
					loadTimes.append(load(sensorName, args.count))

		print('Median of {} runs, inserting {} readings:'.format(runs, args.count))
		for (text, seconds) in insertTimes.items():
			report(text, statistics.median(seconds), args.count)
		print('Median of {} loads, loading {} readings:'.format(len(loadTimes), args.count))
		report('HTTP, all readings in one request', statistics.median(loadTimes), args.count)
	finally:
		print("Removing node '{}'".format(nodeName))
		try:
			call('DELETE', 'datasets/{}/nodes/{}'.format(args.dataset, nodeName))
		except ApiError as e:
			print('  ' + str(e))

def positiveInt(value):
	if not value.isdigit() or int(value) == 0:
		raise argparse.ArgumentTypeError('must be a positive number')
	return int(value)

parser = argparse.ArgumentParser(description='Measures how long it takes to insert and load readings.')
parser.add_argument('-u', '--user', default='admin', help='username, registered if missing (default: %(default)s)')
parser.add_argument('-p', '--pass', dest='password', default='secret', help='password (default: %(default)s)')
parser.add_argument('-d', '--dataset', default='test', help='dataset, created if missing (default: %(default)s)')
parser.add_argument('-c', '--count', type=positiveInt, default=10000, help='number of readings to insert (default: %(default)s)')
args = parser.parse_args()

try:
	run()
except ApiError as e:
	print(e, file=sys.stderr)
	sys.exit(1)
