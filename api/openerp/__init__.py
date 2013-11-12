# Based on ovh_app of Antoine Sirinelli <antoine@monte-stello.com> 
# https://github.com/asirinelli/ovh_app

import oerplib
import json
import time
import hashlib
import os
import re

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger

class API:

    def __init__(self, useData,
                protocol = 'xmlrpc',
                port     = '8069',
                url      = 'localhost',
                version  = '7.0' ):

        self.protocol = 'xmlrpc'
        self.port     = port
        self.url      = url
        self.dbname   = 'openerp'

        # Going to extract data from /alkivi/.secureData
        base = '/alkivi/.secureData/api_openerp/'
        file = base + useData

        if(not(os.path.exists(file))):
            logger.warning('Unable to fetch correct file. Check that %s exists and is readable' % (file))
            raise
        else:
            # Open file
            f = open(file)

            # Check syntax
            rx = re.compile('^(.*?):(.*?):(.*?)$')
            for line in f:
                m = rx.search(line)
                if(m):
                    self.user, self.password, self.dbname= m.groups()


        # Check that we are good to go, dont check consumerKey, we might just want to get credentials ...
        if(not(self.user) or not(self.password)):
            logger.warning('Did not find any file that contains correct data, bazinga')
            raise
        else:
            pass

        # First login and keep uid
        self.oerp = oerplib.OERP(url , protocol=protocol, port=port, version=version)
        self.user = self.oerp.login(self.user, self.password, self.dbname)

    def execute(self, *args, **kwargs):
        return self.oerp.execute(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.oerp.get(*args, **kwargs)

    def read(self, *args, **kwargs):
        return self.oerp.read(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self.oerp.search(*args, **kwargs)

    def create(self, *args, **kwargs):
        return self.oerp.create(*args, **kwargs)

    def write(self, *args, **kwargs):
        return self.oerp.write(*args, **kwargs)

    def write_record(self, *args, **kwargs):
        return self.oerp.write_record(*args, **kwargs)

    def exec_workflow(self, *args, **kwargs):
        return self.oerp.exec_workflow(*args, **kwargs)

    def browse(self, *args, **kwargs):
        return self.oerp.browse(*args, **kwargs)
