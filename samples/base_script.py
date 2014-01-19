#!/usr/bin/python
# -*-coding:utf-8 -*

"""
Explanation for the scripts
Refer to --help maybe ?
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import lock
from alkivi.common import logger

# Define the global logger
logger.Logger.instance(
        min_log_level_to_mail   = logger.WARNING,
        min_log_level_to_save   = logger.INFO,
        min_log_level_to_print  = logger.INFO,
        min_log_level_to_syslog = None,
        filename                = '/var/log/alkivi/toto',
        emails                  = ['anthony@alkivi.fr'])

# Optional lock file
lock.Lock()

def usage():
    """Small helper to use when --help is pass
    """
    print 'Usage: '+sys.argv[0]+' -h -d -your own options'+"\n"
    print "-h     --help      Display help"
    print "-d     --debug     Toggle debug printing on stdout"
    print "-f     --files     BLABLABLALBAL"

def main(argv):
    """Where the magic happen
    """

    import getopt

    # Variable that opt use
    logger.debug('Parsing option')
    try:                                
        opts, dummy_args = getopt.getopt(argv, "hs:d", ["help", "toto=", "debug"])
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:                
        logger.log('Looking at arg', opt, arg)
        if opt in ("-h", "--help"):      
            usage()                     
            sys.exit()                  
        elif opt in ("-d", "--debug"):
            logger.set_min_level_to_print(logger.DEBUG)
            logger.debug('debug activated')
        elif opt in ("-t", "--toto"): 
            dummy_toto = arg

    # Do your code here
    logger.info('Program start')

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as exception:
        logger.log_exception(exception)
