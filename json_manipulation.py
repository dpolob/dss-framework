##@package json_manipulations
# Provides utils and auxiliary functions for manipulation of json

from tinydb import TinyDB, Query
import os
import globals

## check_jsonkeys function
#  Check if the keys of a json are according to defined keys
#  @params data_key: list of keys from a json
#  @params reference: string for api to compare
#  @return boolean: True if identical
def check_jsonkeys(data_key, reference):
    
    # avoid hardcoded paths
    cwd = os.path.abspath(os.path.dirname(__file__))
    db = TinyDB(globals.DATABASE)
    table = db.table('json_keys')
    query = Query()
    search = table.search(query.route == reference)
    search = search[0]  # it is a list
    keys = search['keys']
    keys.sort()


    data_keys = list(data_key)
    data_keys.sort()

    if keys == data_keys:

        return True
    else:
        return False

# change status in database
def change_status(id, new_status, table):
    query = Query()
    return table.update({'status' : new_status}, query.id == id)



class StatusEnum:
    STARTED = 1
    STOPPED = 2

    _VALUES_TO_NAMES = {
        1: "STARTED",
        2: "STOPPED",
    }

    _NAMES_TO_VALUES = {
        "STARTED": 1,
        "STOPPED": 2,
    }
