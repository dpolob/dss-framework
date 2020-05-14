## @package Errors
#  Handles exceptions from code

import logging
logger = logging.getLogger()

## JsonKeysWrongException class
#
#  Handle a exception in case of json schema is not correct
class JsonKeysWrongException(Exception):
    logger.info("[JsonKeysWrongException] : Json schema is not dss compliant")

## DBInsertionWrongException class
#
#  Handle a exception if insertion in database is not correct
class DBInsertionWrongException(Exception):
    logger.info("[DBInsertionWrongException] : Cannot insert in database")

## DBDeletionWrongException class
#
#  Handle a exception in if deletion in database is not correct
class DBDeletionWrongException(Exception):
    logger.info("[DBDeletionWrongException] : Cannot delete from database")

## DBListWrongException class
#
#  Handle a exception in case of listing not possible
class DBListWrongException(Exception):
    logger.info("[DBListWrongException] : Cannot retrieve list from database")

## DBAlgorithmNotExistException class
#
#  Handle a exception in case an algorithm does not exist
class DBAlgorithmNotExistException(Exception):
    logger.info("[DBAlgorithmNotExistException] : Cannot retrieve list from database")

## AlgorithmNotReachableException class
class AlgorithmBadStatusException(Exception):
    logger.info("[AlgorithmBadStatusException] : STARTED not sent")

## DBAlgorithmUpdateException class
class DBAlgorithmUpdateException(Exception):
    logger.info("[DBAlgorithmUpdateException] : update not done")
