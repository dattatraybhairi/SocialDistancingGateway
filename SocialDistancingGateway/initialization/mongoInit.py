#! /usr/bin/python3

import logging 
import logging.handlers
import time
import json
from pymongo import MongoClient  

REFERENCE_EPOCH = 1596002576
DB_NAME = "vacusdb2"

try:
    print("Creating new DB")

    #Create New db
    client = MongoClient('localhost', 27017) 
    db = client[DB_NAME]
    
    print("Adding new collection")
    # Create new collection
    collection = db["time"]

    print("Inserting default data to the collection")
    collection.insert_one({'title':'reference','epoch':int(REFERENCE_EPOCH)})
    
    currentEpoch = time.time()
    difference = int(currentEpoch) - int(REFERENCE_EPOCH)
    counterVal = int(difference/5)

    byte0 = counterVal%256
    byte1 = (counterVal - byte0)/256
    byte1 = byte1%256
    byte2 = (counterVal - byte1*10 - byte0)/65536

    collection.insert_one({"title":'counter',"value":counterVal,"byte0":int(byte0),"byte1":int(byte1),"byte2":int(byte2)})

except Exception as err:
    print("Failed to initialize the DB- " + str(err))

print("Successfully initailized the db with default data")