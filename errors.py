## @package Errors
#  Handles exceptions from code
import logging

## JsonKeysWrongException class
#
#  Handle a exception in case of json schema is not correct
class JsonKeysWrongException(Exception):
    logging.debug("[JsonKeysWrongException] : Json schema is not dss compliant")

## DBInsertionWrongException class
#
#  Handle a exception in case of json schema is not correct
class DBInsertionWrongException(Exception):
    logging.debug("[DBInsertionWrongException] : Cannot insert in database")

## DBDeletionWrongException class
#
#  Handle a exception in case of json schema is not correct
class DBDeletionWrongException(Exception):
    logging.debug("[DBDeletionWrongException] : Cannot delete from database")

## DBListWrongException class
#
#  Handle a exception in case of listing not possible
class DBListWrongException(Exception):
    logging.debug("[DBListWrongException] : Cannot retrieve list from database")

## DBAlgorithmNotExistException class
#
#  Handle a exception in case of listing not possible
class DBAlgorithmNotExistException(Exception):
    logging.debug("[DBAlgorithmNotExistException] : Cannot retrieve list from database")

## AlgorithmNotReachableException class
class AlgorithmBadStatusException(Exception):
    logging.debug("[AlgorithmBadStatusException] : STARTED not sent")