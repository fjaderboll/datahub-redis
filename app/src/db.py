import redis

db = redis.Redis()

class Keys():
    USERS = "users"
