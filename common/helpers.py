import ldap
from alkivi.exceptions import *
from alkivi.common import logger


class LdapClient :

    """
        Class used to bind to an Ldap server
    """

    def __init__(self, server='ldaps://localhost', basedn='ou=people,dc=alkivi,dc=fr'):
        logger.debug_debug('Initializing Ldap client on server = %s' % server)

        self.ldap = ldap.initialize(server)
        self.base = basedn

        self.anonymousBind()

    def anonymousBind(self):
        self.ldap.simple_bind_s()

    def getUserDn(self, user):
        filter = "uid=%s" % user
        results = self.ldap.search_s(self.base,ldap.SCOPE_SUBTREE,filter)
        nb      = len(results)
        if(nb == 1):
            dn, entry = results[0]
            return dn
        elif(nb == 0):
            raise ObjectNotFound('User %s does not exist' % (user))
        else:
            raise NoUniqueObjectFound('Got multiple result for user %s ?!' % (user))

    def bindToUser(self, user, password):
        dn = self.getUserDn(user)
        self.ldap.simple_bind_s(dn, password)

    def updatePassword(self, user, old, new):
        dn = self.getUserDn(user)
        self.ldap.simple_bind_s(dn, old)
        self.ldap.passwd_s(dn, old, new)

