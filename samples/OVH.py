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
logger.Logger.instance(
        min_log_level_to_mail  = None,
        min_log_level_to_save  = logger.DEBUG,
        min_log_level_to_print = logger.DEBUG,
        emails=['anthony@alkivi.fr'])


#
# Define OVH API
#
from alkivi.api import ovh
api = ovh.API(use_data='alkivi')


#
# Basic Me Info
#
from alkivi.api.ovh import me
Me = me.Me(api=api)
logger.log(Me.getMyInfo())


#
# Init a pca
#
service_name    = 'toto'
pca_service_name = 'toto'
from alkivi.api.ovh import PCA
PCA = PCA.PCA(api=api, service_name=service_name, pca_service_name=pca_service_name)
logger.log(PCA.getSessions())
