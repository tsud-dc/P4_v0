#!/usr/bin/env python
# coding: utf-8

import os
from flask import Flask, render_template, request, send_from_directory
import requests
import matplotlib.pyplot as plt
import json
import glob
import random
import platform
import setenv

uri = os.environ.get('uri')
lport = os.environ.get('port')

config_f = './config.txt'

with open(config_f, 'r')  as conf:
    conf_list = conf.readlines()
    
for param in conf_list:
    params = param.split('=')
    params[1] = params[1].lstrip().rstrip()
    if params[0] == 'api_hosts':
        api_host= [a_host for a_host in params[1].split(',')]

# Create a Flask instance
app = Flask(__name__)

def draw_chart(data_list, f_name):
    time_list = []
    vals_list = []
    for elem in data_list:
        time_list.append(elem[0])
        vals_list.append(float(elem[1]))
        
    if f_name in 'bri_':
        plt.ylabel = 'Brightness'
    elif f_name in 'temp_':
        plt.ylabel = 'Temperature'
        
    plt.figure()
    plt.xticks(color="None")
    plt.tick_params(length=0)
    plt.title('{} to {}'.format(time_list[0], time_list[-1]))
    plt.plot(time_list, vals_list)

    plt.savefig('./charts/{}.png'.format(f_name))
    plt.show()

##### Define routes #####
@app.route('/', methods=['GET', 'POST'])
def home():
    req = request.args
    
    if len(req) > 0:
        req_uri = '{}?records={}'.format(uri, req['records'])
    else:
        req_uri = uri
        
    i = 0
    try:
        print(api_host[i])
        req_url = 'http://{}'.format(api_host[i]) + req_uri
        ret_vals = requests.get(req_url)
    except:
        try:
            if len(api_host) > 1:
                i += 1
                print(api_host[i])
                req_url = 'http://{}'.format(api_host[i]) + req_uri
                ret_vals = requests.get(req_url)
            else:
                raise
        except:
            i = 0
            return 'DB is not running'

    text_vals = ret_vals.text
     
    vals_list = json.loads(text_vals)
    
    light_list = vals_list.pop(3)
    temp_list = vals_list.pop(6)
    
    
    ch_path = './charts'
    ch_list = glob.glob('{}/*.png'.format(ch_path))
    if len(ch_list) > 0:
        for ch in ch_list:
            if platform.system() == 'Windows': ch=ch.replace("\\", '/')
            os.remove(ch)
    
    rand_fn = random.randrange(10**4, 10**5)
    bri_fname = 'bri_' + str(rand_fn)
    temp_fname = 'temp_' + str(rand_fn)
    
    draw_chart(light_list, bri_fname)
    draw_chart(temp_list, temp_fname)
    
    bri_ch_val = 'src=/charts/{}.png'.format(bri_fname)
    temp_ch_val = 'src=/charts/{}.png'.format(temp_fname)
    
    return render_template('default.html', b_max_val = vals_list[0], b_min_val = vals_list[1], b_ave_val = vals_list[2], t_max_val = vals_list[3], t_min_val = vals_list[4], t_ave_val = vals_list[5], bri_ch = bri_ch_val, temp_ch = temp_ch_val)
    

@app.route('/charts/<chart_name>')
def ret_chart(chart_name):  
    return send_from_directory('./charts', chart_name)

##### Run the Flask instance, browse to http://<< Host IP or URL >>:80 #####
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', lport)))





