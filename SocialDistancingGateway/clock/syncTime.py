#! /usr/bin/python3

import logging 
import logging.handlers
import time
import json
from pymongo import MongoClient  

def connectToDb():
    client = MongoClient('localhost', 27017) 
    db = client['vacusdb']
     
    return db

if __name__ == '__main__':

    # Create the logger for the application and bind the output to /sys/log/ #
    logger = logging.getLogger('airport-data-processing')
    logger.setLevel(logging.INFO)
    logHandler = logging.handlers.SysLogHandler(address='/dev/log')
    logHandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)s - %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    logger.info("Syncing time with the cloud")

    db = connectToDb()
    collection = db["time"]
    document = collection.find_one({'title':'reference'})
    refEpoch = int(document['epoch'])

    currentEpoch = time.time()
    difference = int(currentEpoch) - int(refEpoch)
    counterVal = int(difference/5)

    byte0 = counterVal%256
    byte1 = (counterVal - byte0)/256
    byte1 = byte1%256
    byte2 = (counterVal - byte1*10 - byte0)/65536

    try:
        ret = collection.update_one({"title":"counter"},{"$set":{"value":counterVal,"byte0":int(byte0),"byte1":int(byte1),"byte2":int(byte2)}})
    except Exception as err:
        logger.info("Failed to sync the time with cloud")
    else:
        logger.info("Successfully synced the localtime with cloud")
            