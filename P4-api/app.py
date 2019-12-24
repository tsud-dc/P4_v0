#!/usr/bin/env python
# coding: utf-8

import os
from flask import Flask, render_template, request
import json
import pymongo
import setenv

col0 = os.environ.get('col0')
col1 = os.environ.get('col1')
lport = os.environ.get('port')

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    MONGOCRED = VCAP_SERVICES["mlab"][0]["credentials"]
    client = pymongo.MongoClient(MONGOCRED["uri"])
    DB_NAME = str(MONGOCRED["uri"].split("/")[-1])

# Otherwise, assume running locally with local MongoDB instance    
else:
    client = pymongo.MongoClient('127.0.0.1:27017')
    DB_NAME = os.environ.get('db_name')  ##### Make sure this matches the name of your MongoDB database ######

mng_db = client[DB_NAME]



def db_to_list(db_data):
    ret_list = []
    for data in db_data:
        data_list = list(data.values())
        ret_list.append(data_list)
    return ret_list

def val_to_float(data_list):
    ret_list = []
    for data in data_list:
        ret_list.append(float(data[1]))
    return ret_list

def calc_vals(data_list):
    d_max = max(data_list)
    d_min = min(data_list)
    
    val = 0
    n_val = len(data_list)
    for i in data_list:
        val += i
    d_ave = round(val/n_val, 2)
    
    return d_max, d_min, d_ave

# Create a Flask instance
app = Flask(__name__)

##### Define routes #####
@app.route('/api/v1/getvals', methods=['GET'])
def proc_data():
    # collect data from DB
    # return type is list as date and temperature
    req = request.args
    if len(req) > 0:
        n_records = int(req['records'])
    else:
        n_records = -1
    
    #mng_client = pymongo.MongoClient('mongodb://{}:{}@{}:{}/'.format(db_host, db_port))
    #mng_db = mng_client[db_name]
    env_light = mng_db[col0]
    
    light_data = env_light.find(projection={'_id':0, 'date':1, 'value':1}) 

    env_light_data = db_to_list(light_data)

    if n_records == -1:
        last = min(len(env_light_data), 50)
    else:
        last = min(len(env_light_data), n_records)
    
    env_light_data = env_light_data[-last:]
    val_light_list = val_to_float(env_light_data)
    
    li_max, li_min, li_ave = calc_vals(val_light_list)
    
    env_temp = mng_db[col1]
    temp_data = env_temp.find(projection={'_id':0, 'date':1, 'value':1}) 
    env_temp_data = db_to_list(temp_data)
    
    if n_records == -1:
        last = min(len(env_temp_data), 50)
    else:
        last = min(len(env_temp_data), n_records)
    
    env_temp_data = env_temp_data[-last:]
    val_temp_list = val_to_float(env_temp_data)
    
    te_max, te_min, te_ave = calc_vals(val_temp_list)
    
    ret_list = [li_max, li_min, li_ave, env_light_data, te_max, te_min, te_ave, env_temp_data]
    
    data_json = json.dumps(ret_list)
    
    '''transfer list to some API to get max, min and average value'''
    
    code = 200
    return data_json, code

##### Run the Flask instance, browse to http://<< Host IP or URL >>:80 #####
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', lport)), threaded=True)





