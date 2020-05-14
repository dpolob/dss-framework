## @imports
import errors
import logging 
from json_manipulation import check_jsonkeys, change_status
from tinydb import TinyDB, Query
import json
from globals import DATABASE
from api_classes import EntryPoint

## @imports for Thrift
import sys
sys.path.append('gen-py')
from Link import mmtLink
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from Link import ttypes

# Activate loggin
logging.basicConfig(filename='thrift_log.log', filemode='a')
logger =logging.getLogger()
logger.setLevel(logging.DEBUG)
logger = logging.getLogger()

class MmtLinkHandler:
    def ping(self):
        logger.info("[THRIFT SERVER] Ping requested by MMT. Bad joke sent")
        return "It should be a bad joke..."
    
    def getList(self):
        try:
            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            algorithms = table.all()
            if not algorithms:
                raise errors.DBListWrongException()
            
            list = []
            for algorithm in algorithms:
                list.append(ttypes.AlgorithmStruct(algorithm_name=algorithm['algorithm_name'],
                                            id=algorithm['id'],
                                            description=algorithm['description'],
                                            status=algorithm['status'],
                                            url_api=algorithm['url_api'],
                                            url_web=algorithm['url_web']
                                            )
                            )
            
            logger.info("[THRIFT SERVER] Serving list {}".format(list))
            return list
        
        except (errors.DBListWrongException, Exception):
            logger.info("[THRIFT SERVER][DBListWrongException, Exception]" \
                        "Failure in getting list or list is empty")
            return []

    def start(self, id):
        try:
            db = TinyDB(DATABASE)
            table= db.table('algorithm_list')  # switch to table
            query=Query()

            result = table.search(query.id == id)
            if not result:
                raise errors.DBAlgorithmNotExistException()
            
            # send command to algorithm 
            logger.info("[THRIFT SERVER] Sending command to algorithm in {} with config {}"
                        .format(result[0]['url_api'], result[0]['config'])
                        )
            
            algorithm = EntryPoint(algorithm_url=result[0]['url_api'],
                                   algorithm_config=result[0]['config']
                                  )
            algorithm.run_alg()
            logger.info("[THRIFT SERVER] Algorithm send STARTED")
            # update status
            if not change_status(name=result[0]['algorithm_name'], new_status=ttypes.StatusEnum.STARTED, table=table):
                raise errors.DBAlgorithmUpdateException()

            logger.info("[THRIFT SERVER] Algorithm status started")
            return ttypes.ReplyEnun.OK

            logger.info("[THRIFT SERVER] Algorith {}".format(list))
            return list
        
        except (errors.DBAlgorithmNotExistException, errors.DBAlgorithmUpdateException, Exception):
            logger.info("[THRIFT SERVER][DBListWrongException, errors.DBAlgorithmUpdateException, Exception]" \
                        "Failure in getting list or list is empty")
            return ttypes.ReplyEnun.ERROR

# run thrift server
handler = MmtLinkHandler()
proc = mmtLink.Processor(handler)

trans_svr = TSocket.TServerSocket(port=4001)
trans_fac = TTransport.TBufferedTransportFactory()
proto_fac = TBinaryProtocol.TBinaryProtocolFactory()
server = TServer.TSimpleServer(proc, trans_svr, trans_fac, proto_fac)
server.serve()