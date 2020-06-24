import os, sys

DEFAULT_URL_WEB = 'localhost:8080'
cwd = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.abspath(cwd + '/db/db.json')
DSSURL = 'http://ec2-35-181-5-77.eu-west-3.compute.amazonaws.com:5000/conveymmt'
PORT = 5000
