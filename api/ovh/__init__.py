"""
Wrapper to use the OVH api
"""

import requests
import time
import hashlib
import os
import re
import json

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger

# Custom debug for API low level
DEBUG = False

class APIError(Exception):
    """Classs specific for OVH api, format an exception
    """

    def __init__(self, status_code, response):
        self.status_code = status_code
        self.response = response
        super(APIError, self).__init__()

    def __str__(self):
        error = self.response.json
        return 'httpCode: %s errorCode: %s message: %s' % (error['httpCode'], 
                                                           error['errorCode'], 
                                                           error['message'])

class API:
    """Wrapper that use custom credentials file to perform operation
    """

    def __init__(self, use_data, access_rules=None, 
                 application=None, secret=None, consumer_key=None,
                 url='https://api.ovh.com/1.0'):

        if access_rules is None:
            access_rules = []

        self.application = application 
        self.secret = secret
        self.consumer_key = consumer_key
        self.access_rules = access_rules
        self.url = url


        # Going to extract data from /alkivi/.secureData
        base = '/alkivi/.secureData/api_ovh/'
        credentials = base + use_data

        # Skip opening of a file
        if self.application:
            if not self.consumer_key:
                logger.info('application was passed, but not consumer_key.' +
                            'Hopes its a call for request_ck ;)')
        else:
            if not os.path.exists(credentials):
                raise Exception('Unable to fetch correct file. ' +
                                'Check that %s is readable' % (credentials))
            else:
                f_handler = open(credentials)

                # Check syntax
                regexp = re.compile('^(.*?):(.*?):(.*?)$')
                for line in f_handler:
                    match = regexp.search(line)
                    if match:
                        self.application, self.secret, self.consumer_key = match.groups()
                        break

        # consumer_key is not check because we might request_ck only
        if not self.application or not self.secret:
            raise Exception('Did not find credentials files, bazinga')

        # Fix drift
        self.drift = self.get_drift()

    def get(self, path, params=None):
        """perform get"""
        extra = []
        if params:
            for key, value in params.iteritems():
                extra.append(key+'='+value)

        if extra:
            path = path + '?' + '&'.join(extra)

        if DEBUG:
            logger.debug("[API OVH] Going to %s on %s" % ('get', path))
            
        return self._ovh_req(path, "GET", self.consumer_key)
    
    def post(self, path, params):
        """perform post"""
        if DEBUG:
            logger.debug('[API OVH] Going to %s on %s' % ('post', path) +
                         ' with params', params)

        return self._ovh_req(path, "POST", self.consumer_key, params)

    def delete(self, path):
        """perform delete"""
        if DEBUG:
            logger.debug("Going to %s on %s" % ('delete', path))

        return self._ovh_req(path, "DELETE", self.consumer_key)

    def put(self, path, params):
        """perform put"""
        if DEBUG:
            logger.debug("[API OVH] Going to %s on %s" % ('put', path))

        return self._ovh_req(path, "PUT", self.consumer_key, params)

    def request_ck(self, redirection=None):
        """Used when requesting a token on OVH side
        """
        headers = { 'Content-type': 'application/json',
                    'X-Ovh-Application': self.application}
        params = { 'access_rules': self.access_rules}

        if redirection:
            params['redirection'] = redirection

        query = requests.post(self.url+'/auth/credential', headers=headers, 
                              data=json.dumps(params))
        print query.json

    def get_drift(self):
        """Calculate the time drift between our server and ovh server
        """
        t_ovh = int(requests.get(self.url+'/auth/time').text)
        t_here = int(time.time())
        return t_ovh - t_here

    def _ovh_req(self, path, req_type, ckey, params=None):
        """Low level function that does the actual call
        """
        now = str(int(time.time()) + self.drift)

        if params:
            data = json.dumps(params)
        else:
            data = ""

        url = self.url+path

        sig1 = hashlib.sha1()
        sig1.update("+".join([self.secret, ckey, req_type, url, data, now]))
        sig = "$1$" + sig1.hexdigest()

        headers = { 'Content-type': 'application/json',
                    'X-Ovh-Application':  self.application,
                    "X-Ovh-Consumer": ckey,
                    'X-Ovh-Timestamp': now,
                    "X-Ovh-Signature": sig,
                    }

        if req_type == "GET":
            response = requests.get(url, headers=headers)
        elif req_type == "POST":
            response = requests.post(url, headers=headers, data=data)
        elif req_type == "DELETE":
            response = requests.delete(url, headers=headers)
        elif req_type == "PUT":
            response = requests.put(url, headers=headers, data=data)

        if response.status_code != 200:
            raise APIError(int(response.status_code), response)

        return json.loads(response.text)

