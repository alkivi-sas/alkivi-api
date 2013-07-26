#
# API to interact with request tracker
#
import requests
import json
import time
import hashlib


class APIError(Exception):
    def __init__(self, status_code, r):
        self.status_code = status_code
        self.response = r
    def __str__(self):
        return repr(self.status_code)


class RT_API:
    def __init__(self, user, password, url='https://admin.alkivi.fr/rt/REST/1.0'):
        self.user     = user
        self.password = password
        self.url      = url
        self.cookies  = self.get_cookies()

    def get(self, path):
        return self._rt_req(path, "GET")
    
    def post(self, path, params):
        return self._rt_req(path, "POST", params)

    def delete(self, path):
        return self._rt_req(path, "DELETE")

    def put(self, path, params):
        return self._rt_req(path, "PUT", params)

    def get_cookies(self):
        params = { 'user': self.user, 'pass': self.password } 

        q = requests.post(self.url, data=json.dumps(params), verify=False)
        return q.cookies

    def _rt_req(self, path, req_type, params=None):
        if params:
            data = json.dumps(params)
        else:
            data = ""

        url = self.url+path

        if req_type == "GET":
            r = requests.get(url, cookies=self.cookies, verify=False)
        elif req_type == "POST":
            r = requests.post(url, data=data, cookies=self.cookies, verify=False)
        elif req_type == "DELETE":
            r = requests.delete(url, cookies=self.cookies, verify=False)
        elif req_type == "PUT":
            r = requests.put(url, data=data, cookies=self.cookies, verify=False)

        return r.text

