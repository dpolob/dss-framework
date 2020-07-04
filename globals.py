import os, sys

DEFAULT_URL_WEB = 'http://ec2-35-181-5-77.eu-west-3.compute.amazonaws.com:5000'
cwd = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.abspath(cwd + '/db/db.json')
DSSURL = 'http://ec2-35-181-5-77.eu-west-3.compute.amazonaws.com:5000/conveymmt'
#DSSURL = 'http://0.0.0.0:5000/conveymmt'
MMTURL = 'localhost'
MMTPORT = 6000

PORT = 5000
