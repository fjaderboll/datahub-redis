import re
import random
import hashlib
from flask_restx import abort

def verifyValidName(name, attributeName):
    regex = "^[a-z][a-z0-9_\-]*[a-z0-9]$"
    if re.search(regex, name) is None:
        abort(400, attributeName + " '" + name + "' does not match pattern " + regex)

def verifyNoneEmpty(value, attributeName):
    if value is None or len(value) == 0:
        abort(400, attributeName + " cannot be empty")

def createPasswordSalt():
    return random.randint(1000, 9999)

def createPasswordHash(password, salt):
    s = str(password) + str(salt)
    return hashlib.md5(s.encode('utf-8')).hexdigest()
