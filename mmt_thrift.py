## @imports
from flask.globals import request
from flask.json import jsonify
import errors
import logging 
from json_manipulation import check_jsonkeys, change_status
from tinydb import TinyDB, Query
import json
import globals
from api_classes import EntryPoint
import requests

import logging
import logging.config
import loggly.handlers

## @imports for Thrift
import sys
sys.path.append('gen-py')
from AFC_DSS import DssService
from AFC_DSS_Types import ttypes as dss_types
from AFC_Sensors import ttypes as sensor_types
from AFC_Types import ttypes as afc_types
from AFC_MMT import MmtService

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

# Activate logging
logging.config.fileConfig('loggly-thrift.conf')
logger = logging.getLogger('THRIFT SERVER')

# class for serving
class DssServiceHandler:
    def ping(self):
        logger.info("[THRIFT SERVER] Ping requested by MMT. Bad joke sent")
        return "Generating bad joke..."
    
    def getAlgorithmList(self):
        logger.info("[THRIFT SERVER] List requested by MMT")
        try:
            dss_response = requests.get(globals.DSS_LIST_URL, auth= ('user', 'fakepass'))
            """
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            algorithms = table.all()
            if not algorithms:
                raise errors.DBListWrongException()
            """
            algorithms = json.loads(dss_response.text)
            list = []
            for algorithm in algorithms:
                list.append(dss_types.DssAlgorithm(Id=algorithm['id'],
                                                   Name=algorithm['name'],
                                                   Description=algorithm['description'],
                                                   Status=dss_types.AlgorithmStatus.Available if algorithm['status'] == "STARTED" else dss_types.AlgorithmStatus.NotAvailable,
                                                   WebInterfaceUrl=algorithm['urlweb']
                                                   )
                            )
            
            logger.info("[THRIFT SERVER] Serving list {}".format(list))
            return list
        
        except (errors.DBListWrongException):
            logger.info("[THRIFT SERVER][DBListWrongException]. Failure in getting list or list is empty")
            return []
        except Exception as e:
            logger.info("[THRIFT SERVER][UncaughtException]. {}".format(e))

    
    def getAlgorithmStatus(self, requestId, algorithmId):
        logger.info("[THRIFT SERVER] Status of algorithm {} requested by MMT".format(algorithmId))

        try:
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query = Query()
            result = table.search(query.id == int(algorithmId))
            if not result:
                raise errors.DBAlgorithmNotExistException()

            # send command to algorithm 
            logger.info("[THRIFT SERVER] Sending /status_alg command to algorithm {} in {}".format(algorithmId, result[0]['urlapi']))
            u = globals.DSS_STATUS_URL + "/" + str(algorithmId)
            dss_response = requests.get(url=u, auth= ('user','fakepass'))
            dss_response.raise_for_status()
            """
            algorithm = EntryPoint(algorithm_url=result[0]['urlapi'],
                                   algorithm_config={},
                                   algorithm_id=algorithmId)
            data_from_alg = algorithm.status_alg()
            """
            data_from_alg = json.loads(dss_response.text)
            
            # update status
            if not change_status(id=int(algorithmId), new_status=data_from_alg['status'], table=table):
                raise errors.DBAlgorithmUpdateException()
            
            return dss_types.AlgorithmStatus.Available if data_from_alg['status']=="STARTED" else dss_types.AlgorithmStatus.NotAvailable

        except requests.exceptions.HTTPError as e:
            logger.info("[THRIFT SERVER] /status not reached at DSS {}, {}".format(a, e))
            return dss_types.AlgorithmStatus.NotAvailable

        except Exception as e:
            logger.info("[THRIFT SERVER][getAlgorithmStatus] Problems. Exception {}".format(e))
            return dss_types.AlgorithmStatus.NotAvailable            

    def startAlgorithm(self, requestId, algorithmId):
        try:
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query=Query()
            result = table.search(query.id == int(algorithmId))
            if not result:
                raise errors.DBAlgorithmNotExistException()
            
            # send command to algorithm 
            logger.info("[THRIFT SERVER] Sending/run_alg  command to algorithm in {} with requestId {} with config {}".format(result[0]['urlapi'], requestId, result[0]['config']))
            u = globals.DSS_START_URL + "/" + str(algorithmId)
            dss_response = requests.get(url=u, params={"request_id": requestId}, auth= ('user','fakepass'))
            dss_response.raise_for_status()
            """
            algorithm = EntryPoint(algorithm_url=result[0]['urlapi'],
                                   algorithm_config=result[0]['config'],
                                   algorithm_id=algorithmId
                                  )
            algorithm.run_alg(int(requestId))
            logger.info("[THRIFT SERVER] Algorithm replied STARTED")
            """
            # update status

            if not change_status(id=int(algorithmId), new_status="STARTED", table=table):
                raise errors.DBAlgorithmUpdateException()

        except (errors.DBInsertionWrongException):
            logger.info("[THIRFT SERVER] Insertion in data base NOT correct of request_id")
        
        except (errors.DBAlgorithmUpdateException):
            logger.info("[THIRFT SERVER] Cannot update algorithm status")
        
        except (errors.DDBAlgorithmNotExistException):
            logger.info("[THIRFT SERVER] Algorithm do not exist")

        except requests.exceptions.HTTPError as e:
            logger.info("[THRIFT SERVER] /start not reached DSS {}, {}".format(a, e))

        except Exception as e:
            logger.info("[THRIFT SERVER]{}".format(e))

# class for sending info


if __name__=="__main__":
    # run thrift server
    handler = DssServiceHandler()
    proc = DssService.Processor(handler)

    trans_svr = TSocket.TServerSocket(port=5001)
    trans_fac = TTransport.TBufferedTransportFactory()
    proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(proc, trans_svr, trans_fac, proto_fac)
    logger.info("[THRIFT SERVER] Started")
    print("[THRIFT SERVER] Started")
    server.serve()
