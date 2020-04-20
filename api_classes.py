## @package ClassesAPI
#  Api code
#
#  Api implementation code

## @imports
import errors
import logging 
from flask_restful import Resource
from json_manipulation import check_jsonkeys
from authorizations import ok_userpassword, requires_permission
from flask_httpauth import HTTPBasicAuth
from tinydb import TinyDB, Query
from flask import request, Response, jsonify
import requests
import json

# Enable HTTP Basic Authorization
auth = HTTPBasicAuth()

## verify_password decorator
#
#  Override of method verify_password from HTTPBasicAuth package
#  @param username: string. Got from HTTP header
#  @param password: string. Got from HTTP header
#  @return boolean
@auth.verify_password
def verify_password(username, password):
    return ok_userpassword(username, password)


## Register class
#
#  Implements code for Register API
class Register(Resource):
    permit = "admin"

    @auth.login_required  # check authorization
    @requires_permission(permit)  # check permission
    ## Post function
    #  Register a new algorithm inside the TinyDB database
    def post(self):
        try:
            db = TinyDB('./db/db.json')
            
            data = request.get_json()
            if not check_jsonkeys(data, 'register'):
                raise errors.JsonKeysWrongException()
            
            table= db.table('algorithm_list')  # switch to table
            if table.insert(data) < 0:
                raise errors.DBInsertionWrongException()
            
            return Response("Registration sucessful", status=200, mimetype='text/plain')
        
        except (errors.JsonKeysWrongException, errors.DBInsertionWrongException, Exception):
            return Response("Failure in registration", status=500, mimetype='text/plain')

## Delete class
#
#  Implements code for Delete API
class Delete(Resource):
    permit = "admin"

    @auth.login_required  # check authorization
    @requires_permission(permit)  # check permission
    ## Get function
    #  Register a new algorithm inside the TinyDB database
    def get(self, algorithm_name):
        try:
            db = TinyDB('./db/db.json')
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            if not table.remove(query.algorithm_name == algorithm_name):
                raise errors.DBDeletionWrongException()
            
            return Response("Deletion sucessful", status=200, mimetype='text/plain')
        
        except (errors.DBInsertionWrongException, Exception):
            return Response("Failure in deletion", status=500, mimetype='text/plain')

## List class
#
#  Implements code for List API
class List(Resource):
    permit = "user"

    @auth.login_required  # check authorization
    @requires_permission(permit)  # check permission
    ## Get function
    #  List algorithm inside the TinyDB database
    def get(self):
        try:
            db = TinyDB('./db/db.json')
            table= db.table('algorithm_list')  # switch to table
            list = table.all()
            if not list:
                raise errors.DBListWrongException()
            
            return Response(json.dumps(list), status=200, mimetype='application/json')
        
        except (errors.DBListWrongException, Exception):
            return Response("Failure in getting list", status=500, mimetype='text/plain')
        
## Start class
#
#  Implements code for Star API
class Start(Resource):
    permit = "user"

    @auth.login_required  # check authorization
    @requires_permission(permit)  # check permission
    ## Post function
    #  List algorithm inside the TinyDB database
    def post(self, algorithm_name):
        try:
            db = TinyDB('./db/db.json')
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.algorithm_name == algorithm_name)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['url'],
                                    algorithm_config = request.get_json()['config']
                        )

            # convey data to algorithm through /run_alg
            algorithm.run_alg()
            return Response("Algorithm started", status=200, mimetype='text/plain')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError): 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, Exception):
            return Response("Failure in DSS to start algorithm", status=500, mimetype='text/plain')

## Start class
#
#  Implements code for Star API
class Status(Resource):
    permit = "user"

    @auth.login_required  # check authorization
    @requires_permission(permit)  # check permission
    ## Post function
    #  List algorithm inside the TinyDB database
    def get(self, algorithm_name):
        try:
            db = TinyDB('./db/db.json')
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.algorithm_name == algorithm_name)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['url'],
                                    algorithm_config = request.get_json()['config']
                        )

            # convey data to algorithm through /run_alg
            response = algorithm.status_alg()
            return Response(json.dumps(response), status=200, mimetype='application/json')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError): 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, Exception):
            return Response("Failure in DSS to start algorithm", status=500, mimetype='text/plain')


## Stop class
#
#  Implements code for Stop API
class Stop(Resource):
    permit = "user"

    @auth.login_required  # check authorization
    @requires_permission(permit)  # check permission
    ## Get function
    #  List algorithm inside the TinyDB database
    def get(self, algorithm_name):
        try:
            db = TinyDB('./db/db.json')
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.algorithm_name == algorithm_name)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['url'],
                                    algorithm_config = request.get_json()['config']
                        )

            # convey data to algorithm through /stop_alg
            algorithm.stop_alg()
            return Response("Algorithm stopped", status=200, mimetype='text/plain')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError): 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, Exception):
            return Response("Failure in DSS to start algorithm", status=500, mimetype='text/plain')

## EntryPoint class
#
#  Implements the queries to the algorithms
class EntryPoint():
    ## Constructor
    #  @param algorithm_url: string Url of the base api of the algorithm
    #  @param algorithm_config: dict Content of 'config' key send by the user
    def __init__(self, algorithm_url, algorithm_config):
        self.algorithm_url = algorithm_url
        self.algorithm_config = algorithm_config
    
    ## run_alg function
    #  Implement run_alg query to the algorithm 
    def run_alg(self):
        response = requests.post(self.algorithm_url + "/run_alg",
                                data=json.dumps(dict({"config" :self.algorithm_config})),
                                headers={"Content-Type": "application/json"},
                                auth= ('entrypoint','fakepass')
                                )
        response.raise_for_status()  # if not 200 raise an exception requests.exceptions.HTTPError
        
        data_from_alg = json.loads(response.text)
        if data_from_alg['status'] != 'STARTED':
            if not data_from_alg['msg']:
                logging.debug("Algorithm status: {}. Reason: Unable to find. Json not sent or not compliant".format(data_from_alg['status']))
            else:
                logging.debug("Algorithm status: {}. Reason: {}".format(data_from_alg['status'], data_from_alg['msg']))
        
            raise errors.AlgorithmBadStatusException()
        
        logging.debug("Algorithm status: {}. Info: {}".format(data_from_alg['status'], data_from_alg['msg']))

    ## stop_alg function
    #  Implement stop_alg query to the algorithm 
    def stop_alg(self):
        response = requests.get(self.algorithm_url + "/stop_alg",
                                headers={"Content-Type": "text/plain"},
                                auth= ('entrypoint','fakepass')
                                )
        response.raise_for_status()  # if not 200 raise an exception requests.exceptions.HTTPError
        
        data_from_alg = json.loads(response.text)
        if data_from_alg['status'] != 'STOPPED':
            if not data_from_alg['msg']:
                logging.debug("Algorithm status: {}. Reason: Unable to find. Json not sent or not compliant".format(data_from_alg['status']))
            else:
                logging.debug("Algorithm status: {}. Reason: {}".format(data_from_alg['status'], data_from_alg['msg']))
      
            raise errors.AlgorithmBadStatusException()
        
        logging.debug("Algorithm status: {}. Info: {}".format(data_from_alg['status'], data_from_alg['msg']))

    ## status_alg function
    #  Implement stop_alg query to the algorithm 
    def status_alg(self):
        response = requests.get(self.algorithm_url + "/status_alg",
                                headers={"Content-Type": "text/plain"},
                                auth= ('entrypoint','fakepass')
                                )
        response.raise_for_status()  # if not 200 raise an exception requests.exceptions.HTTPError
        
        data_from_alg = json.loads(response.text)
        if data_from_alg['status'] == 'ERROR':
            if not data_from_alg['msg']:
                logging.debug("Algorithm status: {}. Reason: Unable to find. Json not sent or not compliant".format(data_from_alg['status']))
            else:
                logging.debug("Algorithm status: {}. Reason: {}".format(data_from_alg['status'], data_from_alg['msg']))
      
            raise errors.AlgorithmBadStatusException()
        
        logging.debug("Algorithm status: {}. Info: {}".format(data_from_alg['status'], data_from_alg['msg']))
        return data_from_alg