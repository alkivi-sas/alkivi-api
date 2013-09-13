#!/usr/bin/python
# -*-coding:utf-8 -*

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

import pprint
pp = pprint.PrettyPrinter(indent=4)

print "Enter application:"
application = raw_input()
print "Enter application secret:"
applicationSecret = raw_input()

accessRules = [ { 'method': 'GET',
                  'path': '/*'},
                { 'method': 'PUT',
                  'path': '/*'},
                { 'method': 'POST',
                  'path': '/*'},
                { 'method': 'DELETE',
                  'path': '/*'}]

print "Here are the access rules. Edit this script if you want to change it. Press any key to continue"
print pp.pprint(accessRules)
raw_input()

from alkivi.api import ovh
api = ovh.API(useData='',application=application, secret=applicationSecret, accessRules=accessRules)

# Will print validation URL and token
api.request_CK()
