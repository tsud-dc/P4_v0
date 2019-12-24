#!/usr/bin/env python
# coding: utf-8

import os
import time
import pymongo
from flask import Flask, render_template, request
import json
import setenv

lport = os.environ.get('port')

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    MONGOCRED = VCAP_SERVICES["mlab"][0]["credentials"]
    client = pymongo.MongoClient(MONGOCRED["uri"], retryWrites=False)
    DB_NAME = str(MONGOCRED["uri"].split("/")[-1])

# Otherwise, assume running locally with local MongoDB instance    
else:
    client = pymongo.MongoClient('127.0.0.1:27017')
    DB_NAME = os.environ.get('db_name')  ##### Make sure this matches the name of your MongoDB database ######

mng_db = client[DB_NAME]

# Create a Flask instance
app = Flask(__name__)

##### Define routes #####
# recieve data [col, date, value]
@app.route('/api/v1/store_db', methods=['GET'])
def store_db():
    req = request.args

    #requests.get(host/api/v1/storedb?vals=[xxxx,xxxxx,xxxx](json_strings)) on mq_agent on another container
    vals = json.loads(req['vals'])
    
    print(vals)
    
    env_col = mng_db[vals[0]]
    env_col.insert_one({'date':vals[1],'value':vals[2]})

    code = 200
    return '', code

##### Run the Flask instance, browse to http://<< Host IP or URL >>:80 #####
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', lport)), threaded=True)