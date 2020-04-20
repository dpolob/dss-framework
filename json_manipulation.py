##@package json_manipulations
# Provides utils and auxiliary functions

from tinydb import TinyDB, Query

## check_jsonkeys function
#  Check if the keys of a json are according to defined keys
#  @params data_key: list of keys from a json
#  @params reference: string for api to compare
#  @return boolean: True if identical
def check_jsonkeys(data_key, reference):
    
    db = TinyDB('./db/db.json')
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