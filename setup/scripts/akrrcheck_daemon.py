import inspect
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if (cur_dir+"/../../src") not in sys.path:
    sys.path.append(cur_dir+"/../../src")

from util import logging as log
import akrr

from requests.auth import HTTPBasicAuth
import requests
#modify python_path so that we can get /src on the path

ssl_verify = False

restapi_host = akrr.restapi_host
if akrr.restapi_host!="":
    restapi_host=akrr.restapi_host
#set full address
api_url = 'https://'+restapi_host+':'+str(akrr.restapi_port)+akrr.restapi_apiroot
ssl_cert=None
#akrr.restapi_certfile
# Holds the user token returned by the auth request.
token = None


def populate_token():
    request = requests.get(api_url + "/token", auth=HTTPBasicAuth(akrr.restapi_rw_username, akrr.restapi_rw_password), verify=ssl_verify, cert=ssl_cert)
    if request.status_code == 200:
        global token
        token = request.json()['data']['token']
    else:
        log.error('Something went wrong when attempting to contact the REST API.')

    return token is not None


def is_api_up():
    request = requests.get(api_url + "/scheduled_tasks", auth=(token, ""), verify=ssl_verify, cert=ssl_cert)
    if request.status_code == 200:
        return True
    else:
        log.error('Unable to successfully contact the REST API: {0}: {1}', request.status_code, request.text)
        return False

if __name__ == '__main__':
    log.info('Beginning check of the AKRR Rest API...')
    token_populated = populate_token()
    if token_populated:
        is_up = is_api_up()
        if is_up:
            log.info('REST API is up and running!')
        else:
            exit(1)
    else:
        log.error('Unable to retrieve authentication token.')
        exit(1)