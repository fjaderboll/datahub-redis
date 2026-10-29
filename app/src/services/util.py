import re
import secrets
import string
import hashlib
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from flask_restx import abort

from api import api

def getPayload(name, defaultValue=None):
	if name in api.payload:
		return api.payload[name]
	return defaultValue

def verifyAdmin(auth):
	if not auth or not auth['isAdmin']:
		abort(403, "Forbidden")

def verifyAdminOrUser(auth, username):
	if not auth['isAdmin'] and auth['username'] != username:
		abort(403, "Forbidden")

def verifyValidName(name, attributeName="Attribute", fail=True):
	regex = r"^[a-z0-9][a-z0-9_\-@.]*[a-z0-9]$"
	if re.search(regex, name) is None:
		if fail:
			abort(400, attributeName + " '" + name + "' does not match pattern " + regex)
		return False
	return True

def verifyNoneEmpty(value, attributeName):
	if value is None or len(value) == 0:
		abort(400, attributeName + " cannot be empty")

# Argon2id with OWASP's recommended minimum (19 MiB, 2 passes). Hashing blocks the gunicorn
# worker while it runs, so the cost is kept modest.
# The salt and these parameters are stored in the hash itself.
passwordHasher = PasswordHasher(time_cost=2, memory_cost=19 * 1024, parallelism=1)

def createPasswordHash(password):
	return passwordHasher.hash(password)

def verifyPassword(password, passwordHash):
	try:
		return passwordHasher.verify(passwordHash, password)
	except (VerificationError, InvalidHashError):
		return False

def passwordNeedsRehash(passwordHash):
	"""True when the hash was made with other parameters than the current ones."""
	return passwordHasher.check_needs_rehash(passwordHash)

def createTokenHash(token):
	# tokens are long and random, so a fast hash protects them as well as a slow one, and can be looked up
	return hashlib.sha256(token.encode('utf-8')).hexdigest()

def getRandomString(length):
	alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
	return ''.join(secrets.choice(alphabet) for _ in range(length))

def cleanObject(obj, fields):
	"""Copy 'fields' (API name -> internal name) that are present in 'obj'."""
	newObj = {}
	for apiName, internalName in fields.items():
		if internalName in obj:
			newObj[apiName] = obj[internalName]
	return newObj
