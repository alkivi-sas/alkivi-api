#!/usr/bin/python
# -*-coding:utf-8 -*

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
        #filename                = '/var/log/toto',
        emails                  = ['anthony@alkivi.fr'])

# Optional lock file
lock = lock.Lock()

def main():
    # Do your code here
    logger.info('Program start')

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(e)
