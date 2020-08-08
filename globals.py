import os, sys

DEFAULT_URL_WEB = 'https://app.swaggerhub.com/apis/dpolob/api_afc_dss/1.0.0-oas3'

#FLASK APP
PORT = 5000

# database
cwd = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.abspath(cwd + '/db/db.json')

# DSS 
DSS_LOCAL = False
if DSS_LOCAL:
    DSS_BASE ='http://0.0.0.0:' +str(PORT)
else:
    DSS_BASE = 'http://ec2-35-181-5-77.eu-west-3.compute.amazonaws.com:5000'

DSSURL = DSS_BASE + "/conveymmt"
DSS_START_URL = DSS_BASE + "/start"
DSS_STATUS_URL = DSS_BASE + "/status"
DSS_LIST_URL = DSS_BASE + "/list"
DSS_SENDIP_URL = DSS_BASE + "/sendip"

# MMT
MMT_SERVER_PORT = 5001
MMT_SERVER_URL = 'http://ec2-35-181-5-77.eu-west-3.compute.amazonaws.com:' + str(MMT_SERVER_PORT)


