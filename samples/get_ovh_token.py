#!/usr/bin/python
# -*-coding:utf-8 -*

"""
Simple test to see how to get an ovh token using our api wrapper
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

import pprint

def main(argv):
    """main class doing the job ...
    """
    pretty_p = pprint.PrettyPrinter(indent=4)

    print "Enter application:"
    application = raw_input()
    print "Enter application secret:"
    secret = raw_input()

    rules = [ { 'method': 'GET',
                'path': '/*'},
              { 'method': 'PUT',
                'path': '/*'},
              { 'method': 'POST',
                'path': '/*'},
              { 'method': 'DELETE',
                'path': '/*'}]

    print "Here are the access rules. Press any key to continue"
    print pretty_p.pprint(rules)
    raw_input()

    from alkivi.api import ovh
    api = ovh.API(use_data='', application=application, 
                  secret=secret, access_rules=rules)

    # Will print validation URL and token
    api.request_ck()

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as exception:
        print "Something went wrong {}".format(exception)
