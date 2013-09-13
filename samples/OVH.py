#!/usr/bin/python
# -*-coding:utf-8 -*

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

#
# Define Logger : check samples script in alkivi-api/sample/testLogger.py
#
from alkivi.common import logger
from alkivi.common.logger import Logger
logger = Logger.instance(
        min_log_level_to_mail  = None,
        min_log_level_to_save  = logger.DEBUG,
        min_log_level_to_print = logger.DEBUG,
        emails=['anthony@alkivi.fr'])


#
# Define OVH API
#
from alkivi.api import ovh
api = ovh.API(useData='alkivi')


#
# Basic Me Info
#
from alkivi.api.ovh import me
OVH_Me = me.OVH_Me(api=api)
logger.log(OVH_Me.getMyInfo())


#
# Init a pca
#
serviceName    = 'toto'
pcaServiceName = 'toto'
from alkivi.api.ovh import PCA
OVH_PCA = PCA.OVH_PCA(api=api, serviceName=serviceName, pcaServiceName=pcaServiceName)
logger.log(OVH_PCA.getSessions())
