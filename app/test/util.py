import os
import requests
import json
import random

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:2070/')

def createUser(username=None):
	username = username if username else 'laban-' + str(random.randint(0, 1000))
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

def createUserAndLogin():
	(username, password) = createUser()

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
