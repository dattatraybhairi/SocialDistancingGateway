    # import package serial
import random
import serial
import time
# import package numpy
import numpy as np
# import paho.mqtt.client
import paho.mqtt.client as mqtt
# import json package
import json
import ast
from pymongo import MongoClient

time.sleep(10)

broker = "tcs.vacustech.in" #"dhl.vacustech.in"
port = 1883
topic = "tcstracking" #"earthtracking"#"dhltracking"
gatewayMac = "5a-c2-15-d1-00-01"
bufferDict = {}

db_broker = "164.52.193.150"
db_port = 1883
db_topic = "/DEMO/vacus/Alert"
db_broker_username = "db2user"
db_broker_password = "db2user"

byteBuffer = np.zeros(2 ** 11, dtype='uint8')
byteBufferLength = 0


def systemcon():
    st = 0
    try:
        print("try exception")
        st = client.connect(broker, port, keepalive=60)  # establishing connection
        # st = dbClient.connect(db_broker, db_port, keepalive=60)
    except:
        print("exception")
        st = 1;

    finally:
        print("finalyy exception")
        if (st != 0):
            time.sleep(5)
            systemcon();


def serial_config():
    """
    function to configure the pi or computer
    receive data and returns the serial port
    """
    # Open the serial ports for the configuration and the data ports

    # Raspberry pi
    # data_port = serial.Serial('/dev/ttyS0', 9600)
    data_port = serial.Serial('/dev/ttyUSB0', 115200)

    # Windows
    # data_port = serial.Serial('COM3', 9600)

    if data_port.isOpen():
        try:
            # throwing all the data stored at port coming from sensor
            data_port.flushInput()
        # if error is been thrown print it
        except Exception as err:
            print("Error " + str(err))
            data_port.close()
            exit()

    else:
        try:
            data_port.open()
        except Exception as err:
            print("Error " + str(err))
            data_port.close()
            exit()

    return data_port


def processData(data_port,db,referenceTime):
    '''
    processes the serial data
    :return: none
    '''
    data = 0
    global byteBuffer, byteBufferLength
    max_buffer_size = 2048
    frame_size = 1200
    last_byte = 127

    # print("WAITING FOR DATA TO BE RECEIVED")
    # if data available in serial port
    if data_port.in_waiting:
        read_buffer = data_port.read(data_port.in_waiting)
        #print(read_buffer)

        byte_vec = np.frombuffer(read_buffer, dtype='uint8')
        byte_count = len(byte_vec)

        # Check that the buffer is not full, and then add the data to the buffer
        if (byteBufferLength + byte_count) < max_buffer_size:
            # byteBuffer[byteBufferLength:byteBufferLength + byte_count] = byte_vec
            byteBuffer = np.insert(byteBuffer, byteBufferLength + 1, byte_vec)
            byteBufferLength = byteBufferLength + byte_count

            # Check that the buffer has some data
            if byteBufferLength > frame_size:
                # check for all possible locations for 127
                possible_locs = np.where(byteBuffer == last_byte)[0]

                for loc in possible_locs:
                    if loc > (frame_size - 1):
                        # Code block to send the configuration parameters to the Zone monitor
                        try:
                            with open("/home/pi/Desktop/socialParams.json","r+") as fd:
                                jsonStr = fd.readline()

                            unicodeStr = json.loads(jsonStr)
                            dictObj = ast.literal_eval(unicodeStr)
                            payload = []
                            payload.append(dictObj["duration"])
                            payload.append(dictObj["distance"])        

                            collection = db["time"]
                            document = collection.find_one({'title':'counter'})    
                            payload.append(document["byte0"])
                            payload.append(document["byte1"])
                            payload.append(document["byte2"])

                            time.sleep(50/1000)
                            data_port.write(bytes(payload))

                        except Exception as err:
                            print("Failed to send the params data to the Zone Monitor")
    
                        data_frame = byteBuffer[(loc - frame_size):loc]
                        processDataFrame(data_frame)
                        # print("byteBuffer", byteBuffer[:loc])
                        # Remove the data from buffer
                        # byteBuffer[:loc] = byteBuffer[loc:byteBufferLength]
                        # byteBuffer[byteBufferLength - loc:] = np.zeros(
                        #    len(byteBuffer[byteBufferLength - loc:]),  
                        #    dtype='uint8')
                        np.pad(byteBuffer, (1, 0), mode='constant')[loc + 2:]
                        byteBufferLength = byteBufferLength - loc
                        break


def processDataFrame(data_array):
    '''
    function to process data array
    :param data_array:
    :return: none
    '''
    global client, gatewayMac , bufferDict , referenceTime
    payload = []
    db_payload = []
    split_data_array = np.split(data_array, 100)
    jsonList = []
    for pair in split_data_array:
        if pair[1]:
            tag1Mac = (pair[0]*256 + pair[1])  
            tag2Mac = (pair[2]*256 + pair[3])    
            key = "{0:04x}-{1:04x}".format(tag1Mac,tag2Mac)

            if key not in bufferDict.keys():
                bufferDict[key] = []
            temp = {}
            temp["tag1"] = "{0:02x}-{1:02x}".format(pair[0],pair[1])
            temp["tag2"] = "{0:02x}-{1:02x}".format(pair[2],pair[3])
            temp["timeStamp"] = referenceTime + 5*((256*256*pair[4]) + (256*pair[5]) + pair[6])
            temp["counter"] = int(pair[7])
            temp["distance"] = int(pair[8])
            temp["alert"] = int(pair[9])
            temp["battery"] = int(pair[10])
            
            bufferDict[key].append(temp)

    # Post the data of distinct tag pairs here
    emptyKeys = []
    if len(bufferDict)!=0:
        payload = []
        for key,val in bufferDict.items():
            temp = {}
            jsonTemp = val[0]
            temp["Tag1"] = jsonTemp["tag1"]
            temp["Tag2"] = jsonTemp["tag2"]
            temp["Gateway"] = gatewayMac
            temp["Distance"] = int(jsonTemp["distance"])
            temp["TimeStamp"] = int(jsonTemp["timeStamp"]) - int((jsonTemp["counter"]-1)*5)
            temp["Alert"] = jsonTemp["alert"]
            temp["Battery"] = jsonTemp["battery"]

            payload.append(temp)

            jsonTemp["counter"] -= 1

            if jsonTemp["counter"]<=0:
                val.pop(0)
            if len(val)==0:
                emptyKeys.append(key)

    for key in emptyKeys:
        bufferDict.pop(key,None)
    
    json_payload = json.dumps(payload)
    #json_db_payload = json.dumps(db_payload)
    ret = client.publish(topic, payload=json_payload, qos=0)
    # ret = dbClient.publish(db_topic, payload=json_db_payload, qos=0)
    if ret[0] != 0:
        systemcon()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))

def connectToDb():
    client = MongoClient('localhost', 27017) 
    db = client['vacusdb']
    
    return db    

def fetchRefTime(db):
    collection = db["time"]
    document = collection.find_one({'title':'reference'})
    return int(document['epoch'])


Data_port = serial_config()
client = mqtt.Client()
client.on_connect = on_connect
systemcon()
client.loop_start()
#Connect to mongodb
db = connectToDb()
referenceTime = fetchRefTime(db)

while True:
    try:
        # process serial data
        processData(Data_port,db,referenceTime)
    except KeyboardInterrupt:
        Data_port.close()
        client.loop_stop()
        break
