import paho.mqtt.client as paho #mqtt library
import os
import json
import time
from datetime import datetime

#host name is localhost because both broker and python are Running on same 
#machine/Computer.
broker="192.168.0.38"#"earthron.vacustech.in" #host name , Replace with your IP address.
port=1883 #MQTT data listening port
ACCESS_TOKEN='M7OFDCmemyKoi461BJ4j' #not manditory

def on_publish(client,userdata,result): #create function for callback
  print("published data is : ")
  pass

client1= paho.Client("GatewayController") #create client object
client1.on_publish = on_publish #assign function to callback
client1.username_pw_set(ACCESS_TOKEN) #access token from thingsboard device
#client1.connect(broker,port,keepalive=60) #establishing connection

def systemcon():
    st=0
    try :
        print("try exception")        
        st=client1.connect(broker,port,keepalive=60) #establishing connection
        
    except:
        print("exception")
        st=1;
                
    finally:
        print("finalyy exception")        
        if(st!=0):
            time.sleep(5)
            systemcon();

systemcon();

#publishing after every 5 secs
while True:

  payload="{"
  payload+="\"status\":1";
  payload+="}"
  ret= client1.publish("Gatewaystatus",payload) #topic name is test
  if(ret[0]!=0):
      systemcon();
  #print(payload);
  #print("Please check data on your Subscriber Code \n")
  time.sleep(30)
  
