from flask_restx import Resource, fields
import json

from api import api
from db import db

ns = api.namespace('users', description='Login and get user information')

@ns.route('/')
class UsersList(Resource):
    createFields = api.model('CreateUserData', {
        'username': fields.String(description='Username, must start with [a-z] followed by [a-z0-9_-]', required=True),
        'password': fields.String(description='Password, non empty', required=True)
    })

    @ns.response(200, 'Success')
    def get(self):
        dbUsers = db.lrange('users', 0, -1)
        users = []
        for dbUser in dbUsers:
            users.append(json.loads(dbUser))
        return users
    
    @api.doc(security=None)
    @api.expect(createFields, validate=True)
    @ns.response(200, 'Success')
    @ns.response(400, 'Bad request')
    def post(self):
        input = api.payload
        user = {
            'username': input['username'],
            'password': input['password']
        }
        db.lpush('users', json.dumps(user))
        return user

@ns.route('/<string:username>')
@ns.param('username', 'Username')
class UsersGet(Resource):
    @ns.response(200, 'Success')
    @ns.response(404, 'Unknown user')
    def get(self, username):
        return username
