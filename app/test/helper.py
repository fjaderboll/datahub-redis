import os
import requests
import json
import random
import string

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:2070/')

def getRandomName(prefix='', length=5):
	return prefix + ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def getRandomString(length):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def createUser(username=None):
	username = username if username else getRandomName('testuser-')
	password = 'abc123'
	headers = {
		'Content-Type': 'application/json'
	}

	# create
	createData = {
		'username': username,
		'password': password
	}
	response = requests.post(BASE_URL + 'users/', headers=headers, data=json.dumps(createData))
	response.raise_for_status()

	return (username, password)

def createUserAndLogin(username=None):
	(username, password) = createUser(username)

	# login
	headers = {
		'Content-Type': 'application/json'
	}
	loginData = {
		'password': password
	}
	response = requests.post(BASE_URL + 'users/' + username + '/login', headers=headers, data=json.dumps(loginData))
	response.raise_for_status()

	tokenInfo = response.json()
	headers['Authorization'] = 'Bearer ' + tokenInfo['token']
	return headers

def createDataset(headers, name=None, desc='description1'):
	createData = {
		'name': name if name else getRandomName('dataset-'),
		'desc': desc
	}
	response = requests.post(BASE_URL + 'datasets/', headers=headers, data=json.dumps(createData))
	response.raise_for_status()
	return response.json()

def createNode(headers, datasetName, name=None, desc='description2'):
	createData = {
		'name': name if name else getRandomName('node-'),
		'desc': desc
	}
	response = requests.post(BASE_URL + 'datasets/' + datasetName + '/nodes', headers=headers, data=json.dumps(createData))
	response.raise_for_status()
	return response.json()

def createSensor(headers, datasetName, nodeName, name=None, desc='description3', unit='unit3'):
	createData = {
		'name': name if name else getRandomName('sensor-'),
		'desc': desc,
		'unit': unit
	}
	response = requests.post(BASE_URL + 'datasets/' + datasetName + '/nodes/' + nodeName + '/sensors', headers=headers, data=json.dumps(createData))
	response.raise_for_status()
	return response.json()

def createReading(headers, datasetName, nodeName, sensorName, value=None):
	createData = {
		'value': value if value else random.randint(0, 100000) / 100,
		'time': str(-random.randint(0, 10000000) / 1000)
	}
	response = requests.post(BASE_URL + 'datasets/' + datasetName + '/nodes/' + nodeName + '/sensors/' + sensorName + '/readings', headers=headers, data=json.dumps(createData))
	if not response:
		print(response.text)
	response.raise_for_status()
	return response.json()

def getReadings(headers, datasetName, nodeName, sensorName):
	response = requests.get(BASE_URL + 'datasets/' + datasetName + '/nodes/' + nodeName + '/sensors/' + sensorName + '/readings', headers=headers)
	response.raise_for_status()
	return response.json()
