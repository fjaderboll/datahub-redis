import redis

db = redis.Redis(decode_responses=True)

class Keys():
	USERS = "users"

	def getUserKey(username):
		return Keys.USERS + ':' + username

	def getTokenKey(token):
		return 'token:' + token
