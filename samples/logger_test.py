#!/usr/bin/python
# -*-coding:utf-8 -*

"""
Sample script to show the use of our logger
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger

#
# Define Logger
#
logger.Logger.instance(
        min_log_level_to_mail   = logger.ERROR,
        min_log_level_to_save   = logger.DEBUG_DEBUG,
        min_log_level_to_print  = logger.DEBUG,
        min_log_level_to_syslog = None,
        emails=['anthony@alkivi.fr'])

#
# Never use print for debug, it's not store anywhere :)
#
for i in range(0, 10):
    print "Useless print for i = %d" % (i)

#
# All log level, from bottom to top
#
logger.debug_debug('This is a very low level debug')
logger.debug('This is a debug comment')
logger.log('This is a basic log')
logger.info('This is a info comment')
logger.important('This is an important comment')
logger.warning('This is a warning comment')
logger.error('This is a error comment')
logger.critical('THis is very dangerous, please have a look !')

#
# You can pass any object, it will be dumped in display
#
EXAMPLE = { 'test':'toto', 'dzajndnzadjnazkdjnazdkjnazkdaz':'dzadzadaz' }
import datetime
BIS = ['toto', 
        { ',akd,zakd,azkdza' : 'dzjakdjazkdaz' }, 
        datetime.datetime.now() ]
logger.log('Test with example object which fallow', EXAMPLE)
logger.log('We have a probleme with example test with bis', EXAMPLE, BIS)



#
# Now let's do some loop
#
logger.new_loop_logger()
for i in range(0, 11):
    logger.new_iteration(prefix='i=%i' % (i))
    logger.debug("We are now prefixing all logger")
    if i == 9:
        logger.debug("Lets do another loop")
        logger.new_loop_logger()
        for j in range(0, 5):
            logger.new_iteration(prefix='j=%i' % (j))
            logger.debug("Alkivi pow@")

        # Dont forget to close logger or shit will happen
        logger.del_loop_logger()
    if i == 10:
        logger.critical("We shall receive only mail for last loop")

logger.del_loop_logger()
logger.debug('We now remove an loop, thus a prefix')
logger.critical('test')

# You can set the level after creation
logger.set_min_log_level_to_print(logger.DEBUG)
