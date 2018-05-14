"""
AKRR REST-API Client,

This module will get token automatically and when it expired will get a new.
Yet another abstraction from url but will allowed us to hide authorization and many other details,
which might change 


"""
from . import cfg
import random
import json
from socket import error as SocketError
import errno
import time
import warnings
import requests

# Here we are ignoring SubjectAltNameWarning warning:
# Certificate for {0} has no `subjectAltName`, falling back to check for a
# `commonName` for now. This feature is being removed by major browsers and
# deprecated by RFC 2818. (See https://github.com/shazow/urllib3/issues/497
# for details.)
warnings.filterwarnings("ignore", message=r'.*Certificate for .* has no .*subjectAltName.*')


# initialization

# restapi_host = "127.0.0.1"
restapi_host = 'localhost'

if cfg.restapi_host != "":
    restapi_host = cfg.restapi_host
# set full address
restapi_host = 'https://' + restapi_host + ':' + str(cfg.restapi_port) + cfg.restapi_apiroot

ssl_verify = cfg.restapi_certfile
ssl_cert = cfg.restapi_certfile

waitingTimeOnBusyServer = 0.1
numberOfRepeatConnnectionOnBusyServer = 20

token = "None"


def get_token():
    attempts_to_connect = 0
    # the cycle is walk around for 104 error (busy server)
    while attempts_to_connect < numberOfRepeatConnnectionOnBusyServer:
        try:
            r = requests.get(restapi_host + '/token', auth=(cfg.restapi_rw_username, cfg.restapi_rw_password),
                             verify=ssl_verify, cert=ssl_cert)
            if r.status_code != 200:
                raise Exception("Can not get token for AKRR REST API ( " + restapi_host + " )\n" +
                                "See server response below\n" + json.dumps(r.json(), indent=4))
            global token
            token = r.json()['data']['token']
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not 104 error
            time.sleep(waitingTimeOnBusyServer * random.uniform(0.0, 1.0))
            attempts_to_connect += 1
    return token


def get(url, **kwargs):
    r = None
    attempts_to_connect = 0
    # the cycle is walk around for 104 error (busy server)
    while attempts_to_connect < numberOfRepeatConnnectionOnBusyServer:
        try:
            r = requests.get(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            if r.status_code == 401:
                # renew token
                get_token()
                r = requests.get(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not 104 error
            time.sleep(waitingTimeOnBusyServer * random.uniform(0.0, 1.0))
            attempts_to_connect += 1
        except requests.exceptions.ConnectionError:
            get_token()
            attempts_to_connect += 1
    if r is None:
        raise ValueError
    return r


def post(url, **kwargs):
    r = None
    attempts_to_connect = 0
    # the cycle is walk around for 104 error (busy server)
    while attempts_to_connect < numberOfRepeatConnnectionOnBusyServer:
        try:
            r = requests.post(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            if r.status_code == 401:
                # renew token
                get_token()
                r = requests.post(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not 104 error
            time.sleep(waitingTimeOnBusyServer * random.uniform(0.0, 1.0))
            attempts_to_connect += 1
        except requests.exceptions.ConnectionError:
            get_token()
            attempts_to_connect += 1
    if r is None:
        raise ValueError
    return r


def put(url, **kwargs):
    r = None
    attempts_to_connect = 0
    # the cycle is walk around for 104 error (busy server)
    while attempts_to_connect < numberOfRepeatConnnectionOnBusyServer:
        try:
            r = requests.put(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            if r.status_code == 401:
                # renew token
                get_token()
                r = requests.put(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not 104 error
            time.sleep(waitingTimeOnBusyServer * random.uniform(0.0, 1.0))
            attempts_to_connect += 1
        except requests.exceptions.ConnectionError:
            get_token()
            attempts_to_connect += 1
    if r is None:
        raise ValueError
    return r


def delete(url, **kwargs):
    r = None
    attempts_to_connect = 0
    # the cycle is walk around for 104 error (busy server)
    while attempts_to_connect < numberOfRepeatConnnectionOnBusyServer:
        try:
            r = requests.delete(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            if r.status_code == 401:
                # renew token
                get_token()
                r = requests.delete(restapi_host + url, auth=(token, ""), verify=ssl_verify, cert=ssl_cert, **kwargs)
            break
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not 104 error
            time.sleep(waitingTimeOnBusyServer * random.uniform(0.0, 1.0))
            attempts_to_connect += 1
        except requests.exceptions.ConnectionError:
            get_token()
            attempts_to_connect += 1
    if r is None:
        raise ValueError
    return r


if __name__ == '__main__':
    # do some testing
    get("scheduled_tasks")
