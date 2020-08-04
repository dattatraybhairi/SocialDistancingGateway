import paho.mqtt.client as paho #mqtt library
import os
import json
import time
import ast
from datetime import datetime
import getpass
from random import randint

broker="tcs.vacustech.in" #host name , Replace with your IP address.
port=1883 #MQTT data listening port
ACCESS_TOKEN='M7OFDCmemyKoi461BJ4j' #not manditory

PubTopic="parameterACK"
SubTopic="tcsparameter"



def on_publish(client,userdata,result): #create function for callback
    print("Ack Sent")
    client1.subscribe(SubTopic)#subscribe topic test


def on_message(client, userdata, message):
    client1.connect(broker,port,keepalive=60) #establishing connection

    #Check the macID received in the payload   
    with open("/home/pi/Desktop/configuration/macid.conf","r+") as fd:
        lines = fd.read().splitlines()
    macid = lines[0]  
    dictObj = ast.literal_eval(message.payload.decode("utf-8"))

    # If macid received is system's mac id, send the response else discard the message
    if macid==dictObj.get("macid"):
        print("FOUND")
        with open("/home/pi/Desktop/socialParams.json","w+") as fd:
            fd.write(json.dumps(message.payload.decode('utf-8')))
        
        payload="{"
        payload+="\"status\":1";
        payload+="}"
        print("PUSBLISHING")
        ret= client1.publish(PubTopic,payload) #topic name is test
        if(ret[0]!=0):
            systemcon();
    else:
        pass  

def systemcon():
    st=0
    try :
        st=client1.connect(broker,port,keepalive=60) #establishing connection
        
    except:
        st=1;
                
    finally:
        if(st!=0):
            time.sleep(5)
            systemcon();

def on_connect(client, userdata, flags, rc):
    print("Connected to broker")
    client1.subscribe(SubTopic)#subscribe topic test

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        client1.subscribe(SubTopic)#subscribe topic test
    

client1= paho.Client("gateway" + str(randint(1,10000))) #create client object

client1.on_publish = on_publish #assign function to callback
client1.on_message=on_message
client1.on_connect = on_connect
client1.on_disconnect = on_disconnect

client1.username_pw_set(ACCESS_TOKEN) #access token from thingsboard device
systemcon();
client1.subscribe(SubTopic)#subscribe topic test


while True:
    client1.loop_start() #contineously checking for message 







