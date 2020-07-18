
# Script para el cliente

import sys
sys.path.append('gen-py')
from AFC_DSS import DssService

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

trans = TSocket.TSocket("0.0.0.0", 5001)
trans = TTransport.TBufferedTransport(trans)
proto = TBinaryProtocol.TBinaryProtocol(trans)
client = DssService.Client(proto)

trans.open()

#msg = client.startAlgorithm(int(1111), int(83020))
msg = client.getAlgorithmStatus(int(1111), int(83020))
print("[CLIENT] recieved %s" % msg)

#client.startAlgorithm(int(1111), int(40492))

trans.close()