## @package authorizations.py
#  Functions and decorators to manage user authorization and permits to access to API
#
#  Security is not implemented in the API, therefore any user and password will work
#  But permission need a correct username: 'admin' or 'user'

import os
import logging
logger =logging.getLogger()

from flask import jsonify, request
from functools import wraps
from tinydb import TinyDB, Query


## ok_userpassword function
#
#  Evaluate if user and password are correct. Not implemented
#  @param user: string username (taken from HTTP header)
#  @param permission: string permission needed. Can be 'admin', 'user', 'entrypoint'
#  @return True: boolean
def ok_userpassword(username, password):
    logger.info("User password is correct")
    return True  # no checks

## ok_permission function
#
#  Evaluate if user correspond to the specified user defined in permission
#  @param username: string username 
#  @param user_permission: string permission needed. Can be 'admin', 'user', 'entrypoint'
#  @return boolean
def ok_permission(username, user_permission):
    if username == get_permission(user_permission):
        logger.info("Permit granted")
        return True
    
    logger.info("Permit denied. Needed {} but provided {}".format(user_permission, username))
    return False

## permission_error function
#
#  Generate a json for permission error
def permission_error():
    message = {'message': "Permision not correct."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['Content-Type'] = 'application/json'
    logger.info("Sent 401 error to host")
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

## get_permission function
#
#  Get the permission required for a route
#  @param name: string name of the class
#  @return permit: string required permit
def get_permission(name: str) -> str:
    cwd = os.path.abspath(os.path.dirname(__file__))
    db = TinyDB(cwd + '/db/db.json')
    table = db.table('permits')
    query = Query()
    search = table.search(query.route == name)
    search = search[0]  # it is a list
    logger.info("Permit needed to access to {} is {}".format(name, search['permit']))
    return (search['permit'])
