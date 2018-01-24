"""
AKRR REST-API Client,

This module will get token automatically and when it expired will get a new.
Yet another abstraction from url but will allowed us to hide authorization and many other details,
which might change 


"""
from . import akrrcfg
import os
import random
import string
import time
import re
import traceback
import datetime
import requests
import json
import time
from socket import error as SocketError
import errno
import time
import sys
#initialization



restapi_host="127.0.0.1"
#restapi_host='appkernel'
restapi_host='localhost'
if akrrcfg.restapi_host!="":
    restapi_host=akrrcfg.restapi_host
#set full address
restapi_host='https://'+restapi_host+':'+str(akrrcfg.restapi_port)+akrrcfg.restapi_apiroot

ssl_verify=False
ssl_cert=akrrcfg.restapi_certfile

waitingTimeOnBusyServer=0.1
numberOfRepeatConnnectionOnBusyServer=20

token="None"

def get_token():
    attemptsToConnect=0
    #the cycle is walk around for 104 error (busy server)
    while attemptsToConnect<numberOfRepeatConnnectionOnBusyServer:
        try:
            r = requests.get(restapi_host+'/token', auth=(akrrcfg.restapi_rw_username, akrrcfg.restapi_rw_password), verify=ssl_verify, cert=ssl_cert)
            if r.status_code!=200:
                raise Exception("Can not get token for AKRR REST API ( "+restapi_host+" )\n"+
                   "See server response below\n"+json.dumps(r.json(),indent=4))
            global token
            token=r.json()['data']['token']
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise # Not 104 error
            time.sleep(waitingTimeOnBusyServer*random.uniform(0.0,1.0))
            attemptsToConnect+=1

def get(url,**kwargs):
    attemptsToConnect=0
    #the cycle is walk around for 104 error (busy server)
    while attemptsToConnect<numberOfRepeatConnnectionOnBusyServer:
        try:
            r=requests.get(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            if r.status_code==401:
                #renew token
                get_token()
                r=requests.get(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise # Not 104 error
            time.sleep(waitingTimeOnBusyServer*random.uniform(0.0,1.0))
            attemptsToConnect+=1
        except requests.exceptions.ConnectionError as e:
            get_token()
            attemptsToConnect+=1
    return r

def post(url,**kwargs):
    attemptsToConnect=0
    #the cycle is walk around for 104 error (busy server)
    while attemptsToConnect<numberOfRepeatConnnectionOnBusyServer:
        try:
            r=requests.post(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            if r.status_code==401:
                #renew token
                get_token()
                r=requests.post(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise # Not 104 error
            time.sleep(waitingTimeOnBusyServer*random.uniform(0.0,1.0))
            attemptsToConnect+=1
        except requests.exceptions.ConnectionError as e:
            get_token()
            attemptsToConnect+=1
    return r  
def put(url,**kwargs):
    attemptsToConnect=0
    #the cycle is walk around for 104 error (busy server)
    while attemptsToConnect<numberOfRepeatConnnectionOnBusyServer:
        try:
            r=requests.put(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            if r.status_code==401:
                #renew token
                get_token()
                r=requests.put(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise # Not 104 error
            time.sleep(waitingTimeOnBusyServer*random.uniform(0.0,1.0))
            attemptsToConnect+=1
        except requests.exceptions.ConnectionError as e:
            get_token()
            attemptsToConnect+=1
    return r

def delete(url,**kwargs):
    attemptsToConnect=0
    #the cycle is walk around for 104 error (busy server)
    while attemptsToConnect<numberOfRepeatConnnectionOnBusyServer:
        try:
            r=requests.delete(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            if r.status_code==401:
                #renew token
                get_token()
                r=requests.delete(restapi_host+url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert,**kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise # Not 104 error
            time.sleep(waitingTimeOnBusyServer*random.uniform(0.0,1.0))
            attemptsToConnect+=1
        except requests.exceptions.ConnectionError as e:
            get_token()
            attemptsToConnect+=1
    return r

if __name__ == '__main__':
    #do some testing
    r=get("scheduled_tasks")
