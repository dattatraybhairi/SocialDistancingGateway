#! /usr/bin/python3

import time
import json
from pymongo import MongoClient  

def connectToDb():
    client = MongoClient('localhost', 27017) 
    db = client['vacusdb']
    
    return db

if __name__ == '__main__':
    print("Updating local time counter script")

    db = connectToDb()
    
    while True:
        time.sleep(5)

        collection = db["time"]
        document = collection.find_one({'title':'counter'})
        counterVal = document["value"]

        counterVal += 1
        byte0 = counterVal%256
        byte1 = (counterVal - byte0)/256
        byte1 = byte1%256
        byte2 = (counterVal - byte1*10 - byte0)/65536 

        try:
            ret = collection.update_one({"title":"counter"},{"$set":{"value":counterVal,"byte0":int(byte0),"byte1":int(byte1),"byte2":int(byte2)}})
        except Exception as err:
            print("Failed to updated the localtime")    
        else:
            print("Updated the localtime")
                


