import os, sys

DEFAULT_URL_WEB = 'localhost:8080'
cwd = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.abspath(cwd + '/db/db.json')
