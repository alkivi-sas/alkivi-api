"""API wrapper for linxo"""
import json
import re
import requests
import os
import random

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger

def _get_headers():
    """Define header to use in requests
    """
    return { 'X-LINXO-API-Version' : '1.4',
              'Content-Type' : 'application/json' }

class APIError(Exception):
    """Exception that handle return format of the linxo API
    """

    def __init__(self, result):
        self.result = result
        super(APIError, self).__init__()

    def __str__(self):
        return '%s errorMessage: %s failedAction: %s' % (
            self.result['errorCode'],
            self.result['errorMessage'], 
            self.result['failedAction'])

class API(object):
    """Wrapper to use linxo api to fetch bank account and transactions
    """

    def __init__(self, use_data, base_domain=None, verify_ssl=None):

        if base_domain is None:
            self.base_domain = 'partners.linxo.com'
        else:
            self.base_domain = base_domain

        if verify_ssl is None:
            self.verify_ssl = True
        else:
            self.verify_ssl = verify_ssl

        self.url = 'https://%s/json' % self.base_domain
        self.logged_in = False

        # Going to extract data from /alkivi/.secureData
        base = '/alkivi/.secureData/api_linxo/'
        credentials_file = base + use_data

        if not os.path.exists(credentials_file):
            raise Exception(
                'Unable to fetch correct file.' +
                'Check that %s exists and is readable' % (credentials_file))

        file_handler = open(credentials_file)

        # Check syntax
        regexp = re.compile('^(.*?):(.*?):(.*?):(.*?)$')
        for line in file_handler:
            match = regexp.search(line)
            if match:
                api_key, api_secret, login, password = match.groups()
                self.api_key = api_key
                self.api_secret = api_secret
                self.login = login
                self.password = password


        file_handler.close()


        # Check that we are good to go
        if not self.api_key or not self.api_secret :
            raise Exception(
                'Some credentials are missing.' + 
                'Check secureData file %s contains key:secret:login:password' 
                % file)

        self.session = requests.Session()

        # Generate nonce 
        self.nonce = '%030x' % random.randrange(16**30)

        # Set cookies
        self._set_cookies()

        # Set headers
        self.session.headers.update(_get_headers())

    def get_bank_accounts(self):
        """Fetch list of bank account on linxo
        """
        payload = {
            'actionName' : 'com.linxo.gwt.rpc.client.pfm.GetBankAccountListAction',
            'action' : {
                'includeClosed' : False,
            }
        }

        if not self.logged_in:
            self._login()

        return self._perform_query(payload)

    def get_transactions(self, account):
        """Fetch latest operation on linxo, specific to one account
        """

        payload = {
            'actionName' : 'com.linxo.gwt.rpc.client.pfm.GetTransactionsAction',
            'action' : {
                'accountType' : account['type'],
                'accountId' : account['id'],
                'labels' : [],
                'categoryId' : None,
                'tagId' : None,
                'startRow' : 0,
                'numRows' : 100,
            }
        }
        return self._perform_query(payload)

    def _login(self):
        """Perform authentification on linxo, using secureData extracted data
        """
        payload = {
            'actionName' : 'com.linxo.gwt.rpc.client.auth.LoginAction',
            'action' : {
                'email'    : self.login,
                'password' : self.password,
            },
        }

        self._perform_query(payload)
        self.logged_in = True

    def _logout(self):
        """Perform logout, called by __del__
        """
        payload = { 
            'actionName' : 'com.linxo.gwt.rpc.client.auth.LogoutAction' }
        self._perform_query(payload)

    def _set_cookies(self):
        """Fetch cookies from auth page
        """
        auth_page = 'https://%s/auth.page' % self.base_domain
        self.session.get(auth_page, verify=self.verify_ssl)



    def _get_hash(self):
        """Low level function that generate hash needed for linxo security
        """

        import time
        import base64
        import hashlib
        timestamp = int(time.time())
        sha1 = hashlib.sha1("%s%s%s" % (self.nonce, timestamp, self.api_secret))
        signature = base64.b64encode(sha1.hexdigest())

        return {
            'nonce'     : self.nonce,
            'timeStamp' : timestamp,
            'apiKey'    : self.api_key,
            'signature' : signature
        }



    def _perform_query(self, payload):
        """Low level function that does the get action on linxo
        """

        # No action in payload yell
        if 'actionName' not in payload:
            raise Exception('Missing key actionName is payload')

        # If no hash, add it
        if 'hash' not in payload:
            payload['hash'] = self._get_hash()

        # If no secret, add it
        if 'action' not in payload:
            payload['action'] = {}

        if 'secret' not in payload['action']:
            payload['action']['secret'] = self.session.cookies['LinxoSession']

        # Debug only if not doing login (we dont want clear password in logs)
        if payload['actionName'] != 'com.linxo.gwt.rpc.client.auth.LoginAction':
            logger.debug_debug('LINXO sending', payload)

        result = self.session.post(self.url, 
                                   data=json.dumps(payload), 
                                   verify=self.verify_ssl)

        # Now r.text should contain )]}'\n , remove that and jsonize
        raw_json = re.compile('\)\]\}\'\n').sub('', result.text)

        # Result are check according to functions called
        json_response = json.loads(raw_json)
        if json_response['resultName'] == 'com.linxo.gwt.server.support.json.ErrorResult':
            raise APIError(json_response['result'])

        return json_response['result']


    def __del__(self):
        if self.logged_in:
            self._logout()


