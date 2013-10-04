alkivi-api
========

alkivi-api is our python module used for scripts.
So far it can interact with :
- OVH API (api.ovh.com)
- OpenERP api
- Databases using SqlAlchemy ORM

**Module architecture is still in beta, we are currently learning how to code in Python the right way ;)**

**This library is unofficial and consequently not maintained by OVH.**

Dependencies
-------
API OVH : python-requests
ORM     : python-sqlalchemy
LDAP    : python-ldap
OpenERP : pip install oerplib


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

check samples directory :)


License
-------

alkivi-api is freely distributable under the terms of the LGPLv3 license.
