#!/usr/bin/python
# -*-coding:utf-8 -*

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import lock
from alkivi.common import logger

logger.Logger.instance(
        min_log_level_to_mail  = logger.ERROR,
        min_log_level_to_save  = None,
        min_log_level_to_print = logger.DEBUG,
        emails=['anthony@alkivi.fr'])

lock = lock.Lock()
logger.log('Script begins')
raw_input()

