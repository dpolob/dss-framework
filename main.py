import time
import datetime
import os.path
import logging

from flask import Flask, jsonify, request
from flask import Response, make_response

from flask_restful import Api
import api_classes

app = Flask(__name__)
api = Api(app, prefix='/')

api.add_resource(api_classes.Register, '/register')
api.add_resource(api_classes.Delete, '/delete/<string:algorithm_name>')
api.add_resource(api_classes.List, '/list')
api.add_resource(api_classes.Start, '/start/<string:algorithm_name>')
api.add_resource(api_classes.Stop, '/stop/<string:algorithm_name>')
api.add_resource(api_classes.Status, '/status/<string:algorithm_name>')

if __name__ == '__main__':
    # Setting up logger
    logging.basicConfig(filename='afc_dss.log', level=logging.INFO)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')    
    
    app.run(debug=True, host='0.0.0.0', port=5000)
