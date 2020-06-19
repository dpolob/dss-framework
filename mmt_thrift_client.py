
# Script para el cliente

import sys
sys.path.append('gen-py')
from Link import mmtLink

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

trans = TSocket.TSocket("localhost", 4001)
trans = TTransport.TBufferedTransport(trans)
proto = TBinaryProtocol.TBinaryProtocol(trans)
client = mmtLink.Client(proto)

trans.open()
msg = client.start(1)
print("[CLIENT] recieved %s" % msg)

trans.close()