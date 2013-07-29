alkivi-api
========

alkivi-api is our python module used for scripts.
So far it can interact with :
- OVH API (api.ovh.com)
- Request Tracker (ticketing system)
- Databases using SqlAlchemy ORM

**Module architecture is still in beta, we are currently learning how to code in Python the right way ;)**

**This library is unofficial and consequently not maintained by OVH.**

Dependencies
-------
API OVH : python-requests
ORM     : python-sqlalchemy


Installation
-------

```bash
git clone https://github.com/alkivi-sas/alkivi-api.git path
# Add symlink to ease access to module
ln -s path /alkivi
```

To use OVH API, you will need to create a files containing your credentials (check www.ovh.com/fr/g934.premiers-pas-avec-l-api)
```bash
mkdir -p path/.secureData/api_ovh/
echo "applicationKey:applicationSecret:consumerKey" > path/.secureData/api_ovh/profileName
```

Examples
-------

Now let's create a simple python file test.py
```python
#!/usr/bin/python

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
```




License
-------

alkivi-api is freely distributable under the terms of the LGPLv3 license.
