## @package main
#  Main program for flask with routing logic and allowed methods
#
#  The main program routes the following routes under main prefix '/'.
#  As database use TinyDB, a json format database easy to use, view and
#  modify
#  All operations are logged into afc_dss.log file

import os
import sys
import logging  # logger
import globals


from flask import Flask
from flask_restful import Api

#  compatibility with flask run as api_classes is not in the same directory
#  as /flask/cly.py
cwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(cwd)
from api_classes import Register, Delete, List, Start, Stop, Status, Update, ConveyMMT

app = Flask(__name__)

# routes configuration 
api = Api(app, prefix='/')
api.add_resource(Register, '/register')
api.add_resource(Delete, '/delete/<string:algorithm_id>')
api.add_resource(List, '/list')
api.add_resource(Start, '/start/<string:algorithm_id>')
api.add_resource(Stop, '/stop/<string:algorithm_id>')
api.add_resource(Status, '/status/<string:algorithm_id>')
api.add_resource(Update, '/update/<string:algorithm_id>')
api.add_resource(ConveyMMT, '/conveymmt')

# setting up logger
logging.basicConfig(filename="dss_log.log", filemode='w')
logger =logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info("[DSS] Execution started")

#TODO check if bd exists

## TO RUN FROM FLASH: python3 main.py
app.run(host='0.0.0.0', port=globals.PORT, debug=True)

## TO RUN WITH GUNICORN: gunicorn --bind 0.0.0.0:5000 main:app