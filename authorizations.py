## @package authorizations.py
#  Functions an decorators to manage user authorization and permits to access to API

from flask import jsonify, request
from functools import wraps

## ok_userpassword function
#
#  Evaluate if user and password are correct. Not implemented
#  @param user: string username (taken from HTTP header)
#  @param permission: string permission needed. Can be 'admin', 'user', 'entrypoint'
#  @return True: boolean
def ok_userpassword(username, password):
    return True  # no checks

## ok_permission function
#
#  Evaluate if user correspond to the specified user defined in permission
#  @param username: string username 
#  @param user_permission: string permission needed. Can be 'admin', 'user', 'entrypoint'
#  @return boolean
def ok_permission(username, user_permission):
    if username == user_permission: return True
    return False

## permission_error function
#
#  Generate a json for permission error
def permission_error():
    message = {'message': "Permision not correct."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Main"'
    return resp

## requires_permission decorator
#  Check if the username corresponds to the permission need to access API
#  @param user: string username (taken from HTTP header)
#  @param permission: string permission needed. Can be 'admin', 'user', 'entrypoint'
#  @return boolean
def requires_permission(permit):
    def decorator(f):
        def decorated_permision(*args, **kwargs):
            auth = request.authorization
            if not auth or not ok_permission(auth['username'], permit):
                return permission_error()
            return f(*args, **kwargs)
        return decorated_permision
    return decorator