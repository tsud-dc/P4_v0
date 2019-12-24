#!/usr/bin/env python
# coding: utf-8

import paho.mqtt.client as mqtt
import os
import time
import requests
import json
import setenv

broker_address = os.environ.get('broker_address')
Topic = os.environ.get('Topic')
col_name = os.environ.get('col_name')
db_url = os.environ.get('db_url')

def on_message(client, userdata, message):
    m = str(message.payload.decode("utf-8")).split(',')
    print("message received: {}".format(m))
    #vals = db_url + '?vals=' + json.dumps([col_name, m[1], m[3]])
    url = '{}?vals={}'.format(db_url, json.dumps([col_name,m[1],m[3]]))
    print(url)
    ret_val = requests.get(url)
    print(ret_val.status_code, ret_val.text)

print("creating new instance")
client = mqtt.Client() #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker

client.loop_start() #start the loop

while True:
    client.subscribe(Topic)
    time.sleep(2) # wait

client.loop_stop() #stop the loop

