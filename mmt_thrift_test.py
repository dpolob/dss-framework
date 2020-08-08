
# Script para el cliente

import sys
sys.path.append('gen-py')
from AFC_DSS import DssService
from tinydb import TinyDB, Query
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

#remove https from url to work
#trans = TSocket.TSocket("ec2-35-181-5-77.eu-west-3.compute.amazonaws.com", 5001)
trans=TSocket.TSocket("0.0.0.0", 5001)
#trans = TTransport.TBufferedTransport(trans)
trans = TTransport.TFramedTransport(trans)
proto = TBinaryProtocol.TBinaryProtocol(trans)
client = DssService.Client(proto)

trans.open()

#msg = client.ping()
#msg = client.startAlgorithm(int(1111), int(83020))
#msg = client.getAlgorithmStatus(int(1111), int(83020))
#msg = client.getAlgorithmList()
msg = client.sendIpAddress("http://192.168.1.1:9082")
print("[CLIENT] recieved %s" % msg)

#client.startAlgorithm(int(1111), int(40492))

trans.close()