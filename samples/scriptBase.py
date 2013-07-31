#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import lock
from alkivi.common import logger

# Define the global logger
logger.Logger.instance(
        min_log_level_to_mail  = logger.WARNING,
        min_log_level_to_save  = logger.INFO,
        min_log_level_to_print = logger.INFO,
        emails=['anthony@alkivi.fr'])

# Optional lock file
lock = lock.Lock()

