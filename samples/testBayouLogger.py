#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger
from alkivi.common.logger import Logger

#
# Define Logger
#
logger = Logger.instance(
        min_log_level_to_mail  = logger.ERROR,
        min_log_level_to_save  = logger.DEBUG_DEBUG,
        min_log_level_to_print = logger.DEBUG,
        emails=['luc@alkivi.fr'])

#
# Never use print for debug, it's not store anywhere :)
#
for i in range(0,10):
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
example = { 'test':'toto', 'dzajndnzadjnazkdjnazdkjnazkdaz':'dzadzadaz' }
import datetime
bis = ['toto', { ',akd,zakd,azkdza' : 'dzjakdjazkdaz' }, datetime.datetime.now() ]
logger.log('Test with example object which fallow', example)
logger.log('We have a probleme with example test with bis', example, bis)



#
# Now let's do some loop
#
logger.newLoopLogger()
for i in range(0,11):
    logger.newIteration(prefix='i=%i' % (i))
    logger.debug("We are now prefixing all logger")
    if(i==9):
        logger.debug("Lets do another loop")
        logger.newLoopLogger()
        for j in range(0,5):
            logger.newIteration(prefix='j=%i' % (j))
            logger.debug("Alkivi pow@")

        # Dont forget to close logger or shit will happen
        logger.delLoopLogger()
    if(i==10):
        logger.critical("We shall receive only mail for last loop")

logger.delLoopLogger()
logger.debug('We now remove an loop, thus a prefix')
logger.critical('test')
