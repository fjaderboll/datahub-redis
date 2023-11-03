import re
import random
import string
import hashlib
from flask_restx import abort

def verifyAdmin(auth):
	if not auth['isAdmin']:
		abort(403, "Forbidden")

def verifyAdminOrUser(auth, username):
	if not auth['isAdmin'] and auth['username'] != username:
		abort(403, "Forbidden")

def verifyValidName(name, attributeName="Attribute", fail=True):
	regex = "^[a-z][a-z0-9_\-@.]*[a-z0-9]$"
	if re.search(regex, name) is None:
		if fail:
			abort(400, attributeName + " '" + name + "' does not match pattern " + regex)
		return False
	return True

def verifyNoneEmpty(value, attributeName):
	if value is None or len(value) == 0:
		abort(400, attributeName + " cannot be empty")

def createPasswordSalt():
	return random.randint(1000, 9999)

def createPasswordHash(password, salt):
	s = str(password) + str(salt)
	return hashlib.md5(s.encode('utf-8')).hexdigest()

def getRandomString(length):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def copy(obj, attributes):
	newObj = {}
	for attr in attributes:
		if attr in obj:
			if len(attr) >= 3 and attr[0:2] == 'is' and attr[2:3].isupper():
				newObj[attr] = int(obj[attr]) != 0
			else:
				newObj[attr] = obj[attr]
		else:
			newObj[attr] = None
	return newObj
