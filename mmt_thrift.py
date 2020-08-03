## @imports
import errors
import logging 
import json
import globals
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
        #logger.info("[THRIFT SERVER] List requested by MMT")
        try:
            dss_response = requests.get(globals.DSS_LIST_URL, auth= ('user', 'fakepass'))
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
            return []

    def getAlgorithmStatus(self, requestId, algorithmId):
        logger.info("[THRIFT SERVER] Status of algorithm {} requested by MMT".format(algorithmId))

        try:
            # send command to algorithm 
            logger.info("[THRIFT SERVER] Sending /status_alg command to algorithm id:{} ".format(algorithmId))
            u = globals.DSS_STATUS_URL + "/" + str(algorithmId)
            dss_response = requests.get(url=u, auth= ('user','fakepass'))
            dss_response.raise_for_status()
            data_from_alg = json.loads(dss_response.text)
            
            return dss_types.AlgorithmStatus.Available if data_from_alg['status']=="STARTED" else dss_types.AlgorithmStatus.NotAvailable

        except requests.exceptions.HTTPError as e:
            logger.info("[THRIFT SERVER] /status not reached at DSS. Exception: {}".format(e))
            return dss_types.AlgorithmStatus.NotAvailable

        except Exception as e:
            logger.info("[THRIFT SERVER][getAlgorithmStatus] Problems. Exception {}".format(e))
            return dss_types.AlgorithmStatus.NotAvailable            

    def startAlgorithm(self, requestId, algorithmId):
        try:
            """
            db = TinyDB(globals.DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query=Query()
            result = table.search(query.id == int(algorithmId))
            if not result:
                raise errors.DBAlgorithmNotExistException()
            """

            # send command to algorithm 
            logger.info("[THRIFT SERVER] Sending/run_alg  command to algorithm id: {} with requestId {}".format(algorithmId, requestId))
            u = globals.DSS_START_URL + "/" + str(algorithmId)
            dss_response = requests.get(url=u, params={"request_id": requestId}, auth= ('user','fakepass'))
            dss_response.raise_for_status()
            
        except (errors.DBInsertionWrongException):
            logger.info("[THIRFT SERVER] Insertion in data base NOT correct of request_id")
        
        except (errors.DDBAlgorithmNotExistException):
            logger.info("[THIRFT SERVER] Algorithm do not exist")

        except requests.exceptions.HTTPError as e:
            logger.info("[THRIFT SERVER] /start not reached DSS {}".format(e))

        except Exception as e:
            logger.info("[THRIFT SERVER]{}".format(e))

if __name__=="__main__":
    # run thrift server
    handler = DssServiceHandler()
    proc = DssService.Processor(handler)

    trans_svr = TSocket.TServerSocket(port=globals.MMTPORT)
    #trans_fac = TTransport.TBufferedTransportFactory()
    trans_fac = TTransport.TFramedTransportFactory()
    proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(proc, trans_svr, trans_fac, proto_fac)
    logger.info("[THRIFT SERVER] Started in port {}".format(globals.MMTPORT))
    print("[THRIFT SERVER] Started in port {}".format(globals.MMTPORT))
    server.serve()