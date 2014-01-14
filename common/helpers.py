"""Alkivi helpers when using various application
"""
import ldap
import os
import re
from alkivi.exceptions import *
from alkivi.common import logger

class LdapClient(object):
    """Class used to bind to an Ldap server
    """

    def __init__(self, server=None, basedn=None):
        """Simple wrapper take a server and a basedn
        """

        if server is None:
            server = 'ldaps://localhost'

        if basedn is None:
            basedn = 'ou=people,dc=alkivi,dc=fr'


        logger.debug_debug('Initializing Ldap client on server = %s' % server)

        self.ldap = ldap.initialize(server)
        self.base = basedn

        self.anonymous_bind()

    def anonymous_bind(self):
        """Simple bind to perform search
        """
        self.ldap.simple_bind_s()

    def get_user_dn(self, user):
        """Perform a search on the ldap to get user dn ...
        """
        custom_filter = "uid=%s" % user
        results = self.ldap.search_s(self.base, 
                                     ldap.SCOPE_SUBTREE, 
                                     custom_filter)
        nb_results = len(results)
        if nb_results == 1:
            wanted_dn, dummy_entry = results[0]
            return wanted_dn
        elif(nb_results == 0):
            raise ObjectNotFound(
                'User %s does not exist' % (user))
        else:
            raise MultipleObjectFound(
                'Got multiple result for user %s ?!' % (user))

    def bind_to_user(self, user, password):
        """Bind the user to the ldap using is password
        """
        wanted_dn = self.get_user_dn(user)
        self.ldap.simple_bind_s(wanted_dn, password)

    def bind_to_admin(self, data_file):
        """Use securedata file to bind the ldap as admin
        """
        data_file = '/alkivi/.secureData/'+data_file
        # Test file is ok
        if not os.path.exists(data_file):
            logger.warning('Unable to fetch correct file. ' +
                           'Check that %s exists and is readable' 
                           % data_file)
            raise

        # Open file
        f_handler = open(data_file)

        # Check syntax
        regexp = re.compile('^(.*?):(.*?)$')
        for line in f_handler:
            match = regexp.search(line)
            if match:
                wanted_dn, password = match.groups()
                self.ldap.simple_bind_s(wanted_dn, password)
            else:
                message = 'Unable to find good pattern. '
                message = message + 'Check that file %s is ok' % data_file
                raise Exception(message)

        f_handler.close()

    def update_password(self, user, old, new):
        """Function that take old ane new password and update it on the ldap
        """
        wanted_dn = self.get_user_dn(user)
        self.ldap.simple_bind_s(wanted_dn, old)
        self.ldap.passwd_s(wanted_dn, old, new)

