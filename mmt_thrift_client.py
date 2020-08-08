## @imports
import errors
import logging 
import globals
from tinydb import TinyDB, Query



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
logging.basicConfig(filename='thrift_log_client.log', filemode='w')
logger =logging.getLogger()
logger.setLevel(logging.DEBUG)
logger = logging.getLogger()

class MmtServiceSender:
    def __init__(self, data, request_id, algorithm_id):
        # search for mmt in database
        db = TinyDB(globals.DATABASE)
        table= db.table('mmt_ip_table')  # switch to table
        query = Query()
        result = table.search(query.id == "mmt_address")

        self.data = data
        self.algorithm_id = int(algorithm_id)
        self.request_id = int(request_id)
        self.trans_sender = TSocket.TSocket(result[0]["url"], result[0]["port"])
        #self.trans_sender = TTransport.TBufferedTransport(self.trans_sender)
        self.trans_sender = TTransport.TFramedTransport(self.trans_sender)
        self.proto_sender = TBinaryProtocol.TBinaryProtocol(self.trans_sender)
        self.client_sender = MmtService.Client(self.proto_sender)

    def convey_number(self):
        try:
            list = []
            for item in self.data:
                if item["observation"] not in sensor_types.ObservationType._NAMES_TO_VALUES.keys():
                    raise errors.NoObservationTypeException()

                list.append(dss_types.ResponseNumber(Timestamp=int(item["timestamp"]),
                                                    Observation=sensor_types.ObservationType._NAMES_TO_VALUES[item["observation"]],
                                                    Units=item["units"],
                                                    Result=float(item["result"])))

            self.trans_sender.open()
            self.client_sender.sendDssResultNumber(int(self.request_id), int(self.algorithm_id), list)
            self.trans_sender.close()
            logger.info("[THRIFT CLIENT] Number conveyed to MMT from algorithm_id {} with request_id {} and data {}".format(self.algorithm_id, self.request_id, list))
        except errors.NoObservationTypeException:
            logger.info("[THRIFT CLIENT] Observation type do not exist")
        except Exception as e:
            logger.info("[THRIFT CLIENT] {}".format(e))

    def convey_boolean(self):
        try:
            list = []
            for item in self.data:
                if item["observation"] not in sensor_types.ObservationType._NAMES_TO_VALUES.keys():
                    raise errors.NoObservationTypeException()

                list.append(dss_types.ResponseNumber(Timestamp=int(item["timestamp"]),
                                                    Observation=sensor_types.ObservationType._NAMES_TO_VALUES[item["observation"]],
                                                    Units=item["units"],
                                                    Result= True if item["result"]=="true" else False))

            self.trans_sender.open()
            self.client_sender.sendDssResultBoolean(int(self.request_id), int(self.algorithm_id), list)
            self.trans_sender.close()
            logger.info("[THRIFT CLIENT] Boolean conveyed to MMT from algorithm_id {} with request_id {} and data {}".format(self.algorithm_id, self.request_id, list))
        except errors.NoObservationTypeException:
            logger.info("[THRIFT CLIENT] Observation type do not exist")
        except Exception as e:
            logger.info("[THRIFT CLIENT] {}".format(e))
    
    def convey_string(self):
        try:
            list = []
            for item in self.data:
                if item["observation"] not in sensor_type.ObservationType._NAMES_TO_VALUES.keys():
                    raise errors.NoObservationTypeException()

                list.append(dss_types.ResponseNumber(Timestamp=int(item["timestamp"]),
                                                    Observation=sensor_types.ObservationType._NAMES_TO_VALUES[item["observation"]],
                                                    Units=item["units"],
                                                    Result= str(item["result"])))

            self.trans_sender.open()
            self.client_sender.sendDssResultString(int(self.request_id), int(self.algorithm_id), list)
            self.trans_sender.close()
            logger.info("[THRIFT CLIENT] String conveyed to MMT from algorithm_id {} with request_id {} and data {}".format(self.algorithm_id, self.request_id, list))
        except errors.NoObservationTypeException:
            logger.info("[THRIFT CLIENT] Observation type do not exist")
        except Exception as e:
            logger.info("[THRIFT CLIENT] {}".format(e))
    
    def convey_position(self):
        try:
            list = []
            for item in self.data:
                if item["observation"] not in sensor_type.ObservationType._NAMES_TO_VALUES.keys():
                    raise errors.NoObservationTypeException()

                list.append(dss_types.ResponseNumber(Timestamp=int(item["timestamp"]),
                                                    Observation=sensor_types.ObservationType._NAMES_TO_VALUES[item["observation"]],
                                                    Units=item["units"],
                                                    Result= afc_types.Position(longitude=item["result"]["longitude"],
                                                                               latitude=item["result"]["longitude"],
                                                                               altitude=item["result"]["altitude"])))

            self.trans_sender.open()
            self.client_sender.sendDssResultPosition(int(self.request_id), int(self.algorithm_id), list)
            self.trans_sender.close()
            logger.info("[THRIFT CLIENT] Position conveyed to MMT from algorithm_id {} with request_id {} and data {}".format(self.algorithm_id, self.request_id, list))
        except errors.NoObservationTypeException:
            logger.info("[THRIFT CLIENT] Observation type do not exist")
        except Exception as e:
            logger.info("[THRIFT CLIENT] {}".format(e))
