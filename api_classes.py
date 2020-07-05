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
from flask import request, jsonify, make_response, Response
from random import randint
from mmt_thrift_client import MmtServiceSender

import requests
import json
import os, sys
import globals

logger = logging.getLogger()

# Enable HTTP Basic Authorization
auth = HTTPBasicAuth()

#DATABASE = './db/db.json'

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
            db = TinyDB(globals.DATABASE)
            data = request.get_json()

            if not check_jsonkeys(data, 'Register'):
                 raise errors.JsonKeysWrongException()
            
            # add status as stopped
            data['status'] = StatusEnum.STOPPED

            # add id a sequential number
            table= db.table('algorithm_list')  # switch to table
            list = table.all()

            data['id'] = randint(0,99999)

            # check if url_web is provided if not provide default url_web
            if 'urlweb' not in data.keys():
                logger.info("[Register API] Url web not provided. Used: {}}".format(globals.DEFAULT_URL_WEB))
                data['urlweb'] = globals.DEFAULT_URL_WEB
            
            table= db.table('algorithm_list')  # switch to table

            if table.insert(data) < 0:
                raise errors.DBInsertionWrongException()
            logger.info("[Register API] Insetion in data base correct")
            
            logger.info("[Register API] Registration successful. Algorithm name: {} Id: {} Code 200 sent".format(data['name'], data['id']))
            return Response("Registration sucessful with id {}".format(data['id']), status=200, mimetype='text/plain')
        
        except (errors.DBInsertionWrongException):
            logger.info("[Register API][DBInsertionWrongException] Failure in registration. Code 500 sent")
            return Response("Registration failure", status=500, mimetype='text/plain')
        except (errors.JsonKeysWrongException, errors.DBInsertionWrongException):
            logger.info("[Register API][JsonKeysWrongException] Failure in registration. Code 500 sent")
            return Response("Registration failure", status=500, mimetype='text/plain')
        except Exception as e:
            logger.info("[Register API][UncaughtException] {}".format(e))
            return Response("Registration failure. Check log", status=500, mimetype='text/plain')


## Delete class
#
#  Implements code for Delete an algorithm
class Delete(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Delete")  # check permission
    ## Get functionhon
    #  Delete an algorithm from the TinyDB database
    def get(self, algorithm_id):
        self.algorithm_id = int(algorithm_id)
        try:
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            
            if not table.remove(query.id == self.algorithm_id):
                raise errors.DBDeletionWrongException()
            
            logger.info("[Delete API] Deletion sucessful. Code 200 sent")
            return Response("Deletion sucessful", status=200, mimetype='text/plain')
        
        except (errors.DBDeletionWrongException):
            logger.info("[Delete API][DBDeletionWrongException] Failure in deletion id {} do not exist. Code 500 sent".format(self.algorithm_id))
            return Response("Failure in deletion", status=500, mimetype='text/plain')
        except Exception as e:
            logger.info("[Delete API][UncaughtException] {}".format(e))
            return Response("Failure in deletion. Check log", status=500, mimetype='text/plain')

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
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            list = table.all()
            if not list:
                raise errors.DBListWrongException()

            logger.info("[List API] Serving list {}. Code 200 sent".format(list) )
            return Response(json.dumps(list), status=200, mimetype='application/json')
        
        except (errors.DBListWrongException):
            logger.info("[List API][DBListWrongException] Failure in getting list or list is empty")
            return Response("Failure in getting list or list is empty", status=500, mimetype='text/plain')

        except Exception as e:
            logger.info("[List API][UncaughtException] {}".format(e))
            return Response("Failure in getting list or list is empty. Check log", status=500, mimetype='text/plain')     
## Start class
#
#  Implements code for Star API
class Start(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Start")  # check permission
    ## Post function
    #  Start an algorithm sendind /run_alg command
    def get(self, algorithm_id):
        self.algorithm_id = int(algorithm_id)
        try:
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == self.algorithm_id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['urlapi'],
                                   algorithm_config = result[0]['config'],
                                   algorithm_id=self.algorithm_id
                        )
           

            # convey data to algorithm through /run_alg
            # as user is using API requestId it is fake
            # MMT wil provide a correct one
            algorithm.run_alg(randint(0,999999))
            logger.info("[Start API] Algorithm id {} started. Code 200 sent".format(self.algorithm_id))

            # change status in database
            if not change_status(id=self.algorithm_id, new_status="STARTED", table=table):
                raise errors.DBAlgorithmUpdateException()

            logger.info("[Start API] Algorithm status updated")
            return Response("Algorithm id {} started".format(self.algorithm_id), status=200, mimetype='text/plain')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
            logger.info("[Start API][requests.exceptions.HTTPError, requests.exceptions.ConnectionError]" \
                        "Algorithm not reachable in {}. Code 501 sent".format(result[0]['urlapi'])) 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            logger.info("[Start API][AlgorithmBadStatusException, json.decoder.JSONDecodeError]" \
                        "Command sent but algorithm reply ERROR or not a json. Code 502 sent")
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException):
            logger.info("[Start API][DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception]" \
                        "Failure in DSS to start algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to start algorithm or algorithm do not exist", status=500, mimetype='text/plain')
        
        except Exception as e:
            logger.info("[Start API][UncaughtException] {}".format(e))
            return Response("Failure in DSS to start algorithm or algorithm do not exist. Check logs", status=500, mimetype='text/plain')
        
## Update class
#
#  Implements code for Update API
class Update(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Update")  # check permission
    ## Post function
    #  Update algorithm's config
    def post(self, algorithm_id):
        self.algorithm_id = int(algorithm_id)
        try:
            data = request.get_json()
            
            if not data:
                raise json.decoder.JSONDecodeError()

            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == self.algorithm_id)

            if not result:
                raise errors.DBAlgorithmNotExistException()
            # check json keys
            if not check_jsonkeys(data, 'Update'):
                raise errors.JsonKeysWrongException()

            if not table.update({"config": request.get_json()['config']}, query.id == self.algorithm_id):
                raise errors.DBAlgorithmUpdateException()
            
            logger.info("[Update API] Algorithm config updated")
            return Response("Algorithm config updated", status=200, mimetype='text/plain')

        except (errors.JsonKeysWrongException):
            logger.info("[Update API][JsonKeysWrongException] Failure in update. Code 500 sent")
            return Response("Failure in updating config", status=500, mimetype='text/plain')

        except (json.decoder.JSONDecodeError):
            logger.info("[Update API][json.decoder.JSONDecodeError] Not a json. Code 502 sent")
            return Response("Not a valid json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException):
            logger.info("[Update API][DBAlgorithmNotExistException, Exception] Failure in DSS to update algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to update algorithm or algorithm do not exist", status=501, mimetype='text/plain')
        
        except Exception as e:
            logger.info("[Update API][UncaughtException] {}".format(e))
            return Response("Failure in DSS to update algorithm or algorithm do not exist. Check log", status=501, mimetype='text/plain')
## Status class
#
#  Implements code for Status API
class Status(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Status")  # check permission
    ## Get function
    #  Show algorithm status sending /status_alg
    def get(self, algorithm_id):
        self.algorithm_id = int(algorithm_id)
        try:
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == self.algorithm_id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['urlapi'],
                                   algorithm_config = {},
                                   algorithm_id=self.algorithm_id
                        )
            # convey data to algorithm through /status_alg
            response = algorithm.status_alg()
            logger.info("[Status API] Algorithm sent status. Code 200 sent")
            # check if status is correct
            if not response['status'] in ("STARTED", "STOPPED"):
                raise errors.AlgorithmBadStatusException()
            # update status
            if not change_status(id=self.algorithm_id, new_status=response['status'], table=table):
                raise errors.DBAlgorithmUpdateException()

            return Response(json.dumps(response), status=200, mimetype='application/json')

        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError): 
            logger.info("[Status API][requests.exceptions.HTTPError, requests.exceptions.ConnectionError]" \
                        "Algorithm not reachable in {}. Code 501 sent".format(result[0]['urlapi'])) 
            return Response("Algorithm api not reachable", status=501, mimetype='text/plain')

        except (errors.AlgorithmBadStatusException, json.decoder.JSONDecodeError):
            logger.info("[Status API][AlgorithmBadStatusException, json.decoder.JSONDecodeError]" \
                        "Command sent but algorithm reply ERROR or not a json. Code 502 sent")
            return Response("Command sent but algorithm reply ERROR or not a json", status=502, mimetype='text/plain')

        except (errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException):
            logger.info("[Status API][errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception] " \
                        "Failure in DSS to update algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to get status of algorithm", status=500, mimetype='text/plain')
        except Exception as e:
            logger.info("[Status API][UncaughtException] {}".format(e))
            return Response("Failure in DSS to get status of algorithm. Check log", status=500, mimetype='text/plain')
## Stop class
#
#  Implements code for Stop API
class Stop(Resource):

    @auth.login_required  # check authorization
    @requires_permission("Stop")  # check permission
    ## Get function
    #  Stop an algorithm sending stop_alg
    def get(self, algorithm_id):
        self.algorithm_id = int(algorithm_id)
        try:
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == self.algorithm_id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
 
            algorithm = EntryPoint(algorithm_url = result[0]['urlapi'],
                                   algorithm_config = {},
                                   algorithm_id=self.algorithm_id
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

        except (errors.DBAlgorithmNotExistException):
            logger.info("[Stop API][DBAlgorithmNotExistException, Exception] \
                        Failure in DSS to stop algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to start algorithm or algorithm do not exist", status=500, mimetype='text/plain')
        
        except Exception as e:
            logger.info("[Stop API][UncaughtException] \
                        Failure in DSS to stop algorithm or algorithm do not exist. Code 500 sent")
            return Response("Failure in DSS to start algorithm or algorithm do not exist. Check log", status=500, mimetype='text/plain')
## EntryPoint class
#
#  Implements the queries to the algorithms
class EntryPoint():
    ## Constructor
    #  @param algorithm_url: string Url of the base api of the algorithm
    #  @param algorithm_config: dict Content of 'config' key send by the user
    def __init__(self, algorithm_url, algorithm_config, algorithm_id):
        self.algorithm_url = algorithm_url
        self.algorithm_config = algorithm_config
        self.algorithm_id = int(algorithm_id)
    
    ## run_alg function
    #  Implement run_alg query to the algorithm 
    def run_alg(self, request_id):

        # Update database of request_id
        # Save request_id asociated to algorithm
        data={}
        data['algorithm_id'] = self.algorithm_id
        data['request_id'] = int(request_id)
        db = TinyDB(globals.DATABASE)
        table = db.table('request_table')
        if table.insert(data) < 0:
            raise errors.DBInsertionWrongException()
        logger.info("[THIRFT SERVER] Insertion in data base correct of request_id")

        response = requests.post(self.algorithm_url + "/run_alg", 
                                data=json.dumps(dict({
                                                        "config" :self.algorithm_config,
                                                        "request_id" :request_id,
                                                        "dss_api_endpoint": globals.DSSURL })),
                                headers={"Content-Type": "application/json"},
                                auth= ('entrypoint','fakepass'),
                                timeout = 10.0
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

class ConveyMMT(Resource):

    ## Post function
    #  Register a new algorithm inside the TinyDB database
    def post(self):
        try:
            data = request.get_json()
            if not check_jsonkeys(data, 'response'):
                raise errors.JsonKeysWrongException()
            
            if data['data_type'] not in ("number", "boolean", "string", "position"):
                raise errors.DataTypeMissingException()
            
            
            # convey to MMT format
            db = TinyDB(globals.DATABASE)
            table= db.table('request_table')  # switch to table
            query = Query()
            result = table.search(query.request_id == int(data['request_id']))
            if not result:
                raise errors.DBRequestNotExistException()
 
            sender = MmtServiceSender(data['data'], data['request_id'], result[0]['algorithm_id'])
            if data['data_type'] == "number":
                sender.convey_number()
            elif data['data_type'] == "boolean":
                sender.convey_boolean()
            elif data['data_type'] == "string":
                sender.convey_string()
            elif data['data_type'] == "position":
                sender.convey_position()

            # remove request_id from database
            table= db.table('request_table')  # switch to table
            query = Query()

            if not table.remove(query.request_id == int(data['request_id'])):
                raise errors.DBDeletionWrongException()
            
            logger.info("[Response API] Data {} sent to MMT. Code 200 sent".format(data['data']))
            return Response("Data sent to MMT", status=200, mimetype='text/plain')
        
        except (errors.DataTypeMissingException):
            logger.info("[Response API][DataTypeMissingException] Data_type does not exist. Code 501 sent")
            return Response("Failure in response of algorithm. Check datatypes.", status=501, mimetype='text/plain')    

        except (errors.DBRequestNotExistException, errors.DBDeletionWrongException):
            logger.info("[Response API][DBRequestNotExistException] Request_id does not exist. Code 502 sent")
            return Response("Request_id does not exist", status=502, mimetype='text/plain')        

        except (errors.JsonKeysWrongException):
            logger.info("[Response API][JsonKeysWrongException] Failure in response of algorithm. Check json. Code 500 sent")
            return Response("Failure in response of algorithm. Check json.", status=500, mimetype='text/plain')
        except Exception as e:
            logger.info("[Response API][UncaughtException] {}".format(e))
            return Response("Failure in response of algorithm. Check log.", status=500, mimetype='text/plain')

