"""
OpenERP wrapper that use oerplib
"""

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
    """Simple wrapper that use oerplib
    """

    def __init__(self, use_data,
                protocol='xmlrpc',
                port='8069',
                url='localhost',
                version='7.0' ):


        # Going to extract data from /alkivi/.secureData
        base = '/alkivi/.secureData/api_openerp/'
        credentials = base + use_data

        if not os.path.exists(credentials):
            raise Exception('Unable to fetch correct credentials. ' +
                            'Check that %s is readable' % (credentials))
        else:
            f_handler = open(credentials)

            # Check syntax
            regexp = re.compile('^(.*?):(.*?):(.*?)$')
            for line in f_handler:
                match = regexp.search(line)
                if match:
                    user, password, db_name = match.groups()
                    break

            f_handler.close()

        if not user or not password:
            raise Exception('Did not find credentials, bazinga')

        # First login and keep uid
        self.oerp = oerplib.OERP(url, protocol=protocol,
                                 port=port, version=version)
        self.user = self.oerp.login(user, password, db_name)

    def execute(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.execute(*args, **kwargs)

    def get(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.get(*args, **kwargs)

    def read(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.read(*args, **kwargs)

    def search(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.search(*args, **kwargs)

    def create(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.create(*args, **kwargs)

    def write(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.write(*args, **kwargs)

    def write_record(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.write_record(*args, **kwargs)

    def exec_workflow(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.exec_workflow(*args, **kwargs)

    def browse(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.browse(*args, **kwargs)
