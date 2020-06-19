# TODO Quitar logger mensajes de exceptions
# TODO Actualizar status

## @package ClassesAPI
#  Api code
#
#  Api implementation code

## @imports
import errors
import logging
from flask_restful import Resource
from json_manipulation import check_jsonkeys, StatusEnum, change_status
from authorizations import ok_userpassword, requires_permission
from flask_httpauth import HTTPBasicAuth
from tinydb import TinyDB, Query
from flask import request, Response, jsonify
import requests
import json
import os, sys
from globals import DATABASE, DEFAULT_URL_WEB

logger = logging.getLogger()

# Enable HTTP Basic Authorization
auth = HTTPBasicAuth()

DATABASE = './db/db.json'

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

    @auth.login_required  # check authorization
    @requires_permission("Register")  # check permission
    ## Post function
    #  Register a new algorithm inside the TinyDB database
    def post(self):
        try:
            db = TinyDB(DATABASE)
            
            data = request.get_json()
            if not check_jsonkeys(data, 'register'):
                raise errors.JsonKeysWrongException()
            
            # add status as stopped
            data['status'] = StatusEnum.STOPPED

            # add id a sequential number
            table= db.table('algorithm_list')  # switch to table
            list = table.all()
            if not list:
                data['id'] = 0
            else:
                data['id'] = len(list) + 1

            # check if url_web is provided if not provide default url_web
            if 'url_web' not in list(data.keys()):
                data['url_web'] = globals.DEFAULT_URL_WEB

            table= db.table('algorithm_list')  # switch to table
            if table.insert(data) < 0:
                raise errors.DBInsertionWrongException()
            
            logger.info("[Register API] Registration successful. Algorithm name: {} Id: {} Code 200 sent".format(data['algorithm_name'], data['id']))
            return Response("Registration sucessful with id {}".format(data['id']), status=200, mimetype='text/plain')
        
        except (errors.JsonKeysWrongException, errors.DBInsertionWrongException, Exception):
            logger.info("[Register API][JsonKeysWrongException] Failure in registration. Code 500 sent")
            return Response("Failure in registration", status=500, mimetype='text/plain')

## Delete class
#
#  Implements code for Delete an algorithm
class Delete(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Delete")  # check permission
    ## Get functionhon
    #  Delete an algorithm from the TinyDB database
    def get(self, algorithm_id):
        try:
            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            if not table.remove(query.id == algorithm_id):
                raise errors.DBDeletionWrongException()
            
            logger.info("[Delete API] Deletion sucessful. Code 200 sent")
            return Response("Deletion sucessful", status=200, mimetype='text/plain')
        
        except (errors.DBDeletionWrongException, Exception):
            logger.info("[Delete API][DBDeletionWrongException] Failure in deletion {} do not exist. Code 500 sent".format(algorithm_id))
            return Response("Failure in deletion", status=500, mimetype='text/plain')

## List class
#
#  Implements code for List API
class List(Resource):

    @auth.login_required  # check authorization
    @requires_permission("List")  # check permission
    ## Get function
    #  List algorithms from the TinyDB database
    def get(self):
        try:
            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            list = table.all()
            if not list:
                raise errors.DBListWrongException()

            logger.info("[List API] Serving list {}. Code 200 sent".format(list) )
            return Response(json.dumps(list), status=200, mimetype='application/json')
        
        except (errors.DBListWrongException, Exception):
            logger.info("[List API][DBListWrongException] Failure in getting list or list is empty")
            return Response("Failure in getting list or list is empty", status=500, mimetype='text/plain')
        
## Start class
#
#  Implements code for Star API
class Start(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Start")  # check permission
    ## Post function
    #  Start an algorithm sendind /run_alg command
    def get(self, algorithm_id):
        try:
            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == algorithm_id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['url_api'],
                                   algorithm_config = result[0]['config']
                        )

            # convey data to algorithm through /run_alg
            # as user is using API requestId it is fake
            # MMT wil provide a correct one
            algorithm.run_alg(26120)
            logger.info("[Start API] Algorithm id {} started. Code 200 sent".format(algorithm_id))

            # change status in database
            if not change_status(id=algorithm_id, new_status=StatusEnum.STARTED, table=table):
                raise errors.DBAlgorithmUpdateException()

            logger.info("[Start API] Algorithm status updated")
            return Response("Algorithm id {} started".format(algorithm_id), status=200, mimetype='text/plain')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            logger.info("[Start API][requests.exceptions.HTTPError, requests.exceptions.ConnectionError]" \
                        "Algorithm not reachable in {}. Code 501 sent".format(result[0]['url'])) 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            logger.info("[Start API][AlgorithmBadStatusException, json.decoder.JSONDecodeError]" \
                        "Command sent but algorithm reply ERROR or not a json. Code 502 sent")
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception):
            logger.info("[Start API][DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception]" \
                        "Failure in DSS to start algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to start algorithm or algorithm do not exist", status=500, mimetype='text/plain')

## Update class
#
#  Implements code for Update API
class Update(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Update")  # check permission
    ## Post function
    #  Update algorithm's config
    def post(self, algorithm_id):
        try:
            data = request.get_json()
            if not data:
                raise json.decoder.JSONDecodeError()

            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == algorithm_id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
            # check json keys
            if not check_jsonkeys(data, 'update'):
                raise errors.JsonKeysWrongException()

            if not table.update({"config": request.get_json['config']}, query.id == algorithm_id):
                raise errors.DBAlgorithmUpdateException()
            
            logger.info("[Update API] Algorithm config updated")
            return Response("Algorithm config updated", status=200, mimetype='text/plain')

        except (errors.JsonKeysWrongException):
            logger.info("[Update API][JsonKeysWrongException] Failure in update. Code 500 sent")
            return Response("Failure in updating config", status=500, mimetype='text/plain')

        except (json.decoder.JSONDecodeError):
            logger.info("[Update API][json.decoder.JSONDecodeError] \
                    not a json. Code 502 sent")
            return Response("Not a valid json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception):
            logger.info("[Update API][DBAlgorithmNotExistException, Exception] \
                        Failure in DSS to update algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to update algorithm or algorithm do not exist", status=501, mimetype='text/plain')

## Status class
#
#  Implements code for Status API
class Status(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Status")  # check permission
    ## Get function
    #  Show algorithm status sending /status_alg
    def get(self, algorithm_id):
        try:
            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == algorithm_id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['url'],
                                   algorithm_config = {}
                        )
            # convey data to algorithm through /status_alg
            response = algorithm.status_alg()
            logger.info("[Status API] Algorithm sent status. Code 200 sent")
            # check if status is correct
            if not response["status"] in ("STARTED", "STOPPED"):
                raise errors.AlgorithmBadStatusException()
            # update status
            if not change_status(id=algorithm_id, new_status=response["status"], table=table):
                raise errors.DBAlgorithmUpdateException()

            return Response(json.dumps(response), status=200, mimetype='application/json')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError): 
            logger.info("[Status API][requests.exceptions.HTTPError, requests.exceptions.ConnectionError]" \
                        "Algorithm not reachable in {}. Code 501 sent".format(result[0]['url'])) 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            logger.info("[Status API][AlgorithmBadStatusException, json.decoder.JSONDecodeError]" \
                        "Command sent but algorithm reply ERROR or not a json. Code 502 sent")
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception):
            logger.info("[Status API][errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception] " \
                        "Failure in DSS to update algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to get status of algorithm", status=500, mimetype='text/plain')

## Stop class
#
#  Implements code for Stop API
class Stop(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Stop")  # check permission
    ## Get function
    #  Stop an algorithm sending stop_alg
    def get(self, algorithm_id):
        try:
            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == algorithm_id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['url'],
                                   algorithm_config = {}
                        )

            # convey data to algorithm through /stop_alg
            algorithm.stop_alg()
            logger.info("[Stop API] Algorithm stoped. Code 200 sent")
            return Response("Algorithm stopped", status=200, mimetype='text/plain')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError): 
            logger.info("[Stop API][requests.exceptions.HTTPError, requests.exceptions.ConnectionError] \
                        Algorithm not reachable in {}. Code 501 sent".format(result[0]['url'])) 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            logger.info("[Stop API][AlgorithmBadStatusException, json.decoder.JSONDecodeError] \
                        Command sent but algorithm reply ERROR or not a json. Code 502 sent")
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, Exception):
            logger.info("[Stop API][DBAlgorithmNotExistException, Exception] \
                        Failure in DSS to stop algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to start algorithm or algorithm do not exist", status=500, mimetype='text/plain')

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
    def run_alg(self, request_id):
        response = requests.post(self.algorithm_url + "/run_alg",
                                data=json.dumps(dict({
                                    "config" :self.algorithm_config,
                                    "request_id" :request_id })),
                                headers={"Content-Type": "application/json"},
                                auth= ('entrypoint','fakepass'),
                                timeout = 3.0
                                )
        response.raise_for_status()  # if not 200 raise an exception requests.exceptions.HTTPError
        
        data_from_alg = json.loads(response.text)
        if data_from_alg['status'] != 'STARTED':
            if not data_from_alg['msg']:
                logger.info("[RUN_ALG]Algorithm status: {}. Reason: Unable to find. Json not sent or not compliant".format(data_from_alg['status']))
            else:
                logger.info("[RUN_ALG]Algorithm status: {}. Reason: {}".format(data_from_alg['status'], data_from_alg['msg']))
        
            raise errors.AlgorithmBadStatusException()
        
        logger.info("[RUN_ALG]Algorithm status: {}. Info: {}".format(data_from_alg['status'], data_from_alg['msg']))

    ## stop_alg function
    #  Implement stop_alg query to the algorithm 
    def stop_alg(self):
        response = requests.get(self.algorithm_url + "/stop_alg",
                                headers={"Content-Type": "text/plain"},
                                auth= ('entrypoint','fakepass'),
                                timeout= 5.0
                                )
        response.raise_for_status()  # if not 200 raise an exception requests.exceptions.HTTPError
        
        data_from_alg = json.loads(response.text)
        if data_from_alg['status'] != 'STOPPED':
            if not data_from_alg['msg']:
                logger.info("[STOP_ALG]Algorithm status: {}. Reason: Unable to find. Json not sent or not compliant".format(data_from_alg['status']))
            else:
                logger.info("[STOP_ALG]Algorithm status: {}. Reason: {}".format(data_from_alg['status'], data_from_alg['msg']))
      
            raise errors.AlgorithmBadStatusException()
        
        logger.info("[STOP_ALG]Algorithm status: {}. Info: {}".format(data_from_alg['status'], data_from_alg['msg']))

    ## status_alg function
    #  Implement stop_alg query to the algorithm 
    def status_alg(self):
        response = requests.get(self.algorithm_url + "/status_alg",
                                headers={"Content-Type": "text/plain"},
                                auth= ('entrypoint','fakepass'),
                                timeout= 3.0
                                )
        response.raise_for_status()  # if not 200 raise an exception requests.exceptions.HTTPError
        
        data_from_alg = json.loads(response.text)
        if data_from_alg['status'] == 'ERROR':
            if not data_from_alg['msg']:
                logger.info("[STATUS_ALG]Algorithm status: {}. Reason: Unable to find. Json not sent or not compliant".format(data_from_alg['status']))
            else:
                logger.info("[STATUS_ALG]Algorithm status: {}. Reason: {}".format(data_from_alg['status'], data_from_alg['msg']))
      
            raise errors.AlgorithmBadStatusException()
        
        logger.info("[STATUS_ALG]Algorithm status: {}. Info: {}".format(data_from_alg['status'], data_from_alg['msg']))
        return data_from_alg

class Response(Resource):

    ## Post function
    #  Register a new algorithm inside the TinyDB database
    def post(self):
        try:
            data = request.get_json()
            if not check_jsonkeys(data, 'response'):
                raise errors.JsonKeysWrongException()
            
            if data['data_type'] not in ("number", "boolean", "string", "position"):
                raise errors.DataTypeMissingException()
            
            # TODO
            # convey to MMT format 
            # convey_MMT(data['data'], data['data_type'], data['request_id'])
            
            logger.info("[Response API] Data {} sent to MMT. Code 200 sent".format(data['data']))
            return Response("Data sent to MMT", status=200, mimetype='text/plain')
        
        except (errors.DataTypeMissingException):
            logger.info("[Response API][DataTypeMissingException] Data_type does not exist. Code 501 sent")
            return Response("Failure in response of algorithm. Check datatypes.", status=501, mimetype='text/plain')           

        except (errors.JsonKeysWrongException, Exception):
            logger.info("[Response API][JsonKeysWrongException] Failure in response of algorithm. Check json. Code 500 sent")
            return Response("Failure in response of algorithm. Check json.", status=500, mimetype='text/plain')

