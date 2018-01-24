''' Formats output in a json schema. To be used for making json based API 
servers '''

from bottle import Bottle 
from bottle import response
from bottle import request
from bottle import template
from bottle import tob
from bottle import ERROR_PAGE_TEMPLATE

# Co-opted the Bottle json import strategy
try:
    #pylint: disable=F0401 
    from json import dumps as json_dumps
except ImportError: # pragma: no cover
    try: 
        #pylint: disable=F0401 
        from simplejson import dumps as json_dumps
    except ImportError:
        try: 
            #pylint: disable=F0401
            from django.utils.simplejson import dumps as json_dumps
        except ImportError:
            #pylint: disable=W0613
            def json_dumps(data):
                ''' Place holder for lack of appropriate json lib '''
                raise ImportError(
                    'JSON support requires Python 2.6 or simplejson.')


class JsonFormatting(object):
    ''' Bottle plugin which encapsulates results and error in a json object. 
    Intended for instances where you want to use Bottle as an api server. '''

    name = 'json_formatting'
    api = 2

    #pylint: disable=C0103,W0102
    ALL_TYPES = '*/*'

    statuses = {
            0: 'success',
            1: 'error',
            2: 'internal failure',
        }

    def __init__(self, supported_types=['*/*'], 
            debug=False):
        self.debug = debug
        self.app = None
        self.function_type = None
        self.function_original = None
        self.supported_types = supported_types
        self.ALL_TYPES = JsonFormatting.ALL_TYPES

    def setup(self, app):
        ''' Handle plugin install '''
        self.app = app
        self.function_type = type(app.default_error_handler)
        self.function_original = app.default_error_handler
        self.app.default_error_handler = self.function_type(
                self.custom_error_handler, app)

    #pylint: disable=W0613
    def apply(self, callback, route):
        ''' Handle route callbacks '''
        if not json_dumps: 
            return callback
        def wrapper(*a, **ka):
            ''' Encapsulate the result in json '''
            output = callback(*a, **ka)
            if self.in_supported_types(request.headers.get('Accept', '')):
                response_object = self.get_response_object(0)
                response_object['data'] = output
                json_response = json_dumps(response_object)
                response.content_type = 'application/json'
                return json_response
            else:
                return output
        return wrapper

    def in_supported_types(self, accept_request_header):
        ''' Test accept request header in supprted types '''
        if self.ALL_TYPES in self.supported_types:
            return True
        accepts = []
        for item in accept_request_header.split(','):
            accepts.append(item.strip().split(';')[0])
        if self.ALL_TYPES in accepts:
            return True
        for this_type in self.supported_types:
            if this_type in accepts:
                return True
        return False

    def close(self):
        ''' Put the original function back on uninstall '''
        self.app.default_error_handler = self.function_type(
                self.function_original, self.app, Bottle)

    def get_response_object(self, status):
        ''' Helper for building the json object '''
        #global statuses
        if status in self.statuses:
            json_response = {
                    'status': self.statuses.get(status),
                    'status_code': status,
                    'data': None,
                }
            return json_response
        else:
            self.get_response_object(2)
        
    def custom_error_handler(self, res, error):
        ''' Monkey patch method for json formatting error responses '''
        # when the accept type matches the jsonFormatting configuration
        if self.in_supported_types(request.headers.get('Accept', '')):
            response_object = self.get_response_object(1)
            response_object['error'] = {
                    'status_code': error.status_code,
                    'status': error.status_line,
                    'message': error.body,
                }
            if self.debug:
                response_object['debug'] = {
                        'exception': repr(error.exception),
                        'traceback': error.traceback,
                    }
            json_response = json_dumps(response_object)
            response.content_type = 'application/json'
            return json_response
        else:
            return tob(template(ERROR_PAGE_TEMPLATE, e=error))
