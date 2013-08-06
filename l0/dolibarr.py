from alkivi.common import sql
from sqlalchemy import Column, Date, Integer, String, Index
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.mysql import DATETIME, BIGINT
from sqlalchemy.orm import relationship
from alkivi.common import logger

class Db():
    instance = None

    def __init__(self, echo=False):
        # Will fetch credentials in a secureData file ... check /alkivi/common/sql.py
        self = sql.Db.instance(useData='dolibarr', echo=echo)

class Bill(sql.Model,sql.Base):
    __tablename__ = 'llx_facture'

    # Need to instanciate db (singleton)
    Db()


    # Database configuration
    __table_args__= {'mysql_engine':'InnoDB', 'mysql_charset':'utf8', 'autoload': True }

    # Relationship
    details = relationship("BillDetail", backref="bill")


    # Functions
    def __repr__(self):
        return "<Bill('%s')>" % (self.facnumber)

class BillDetail(sql.Model, sql.Base):
    __tablename__ = 'llx_facturedet'

    # Need to instanciate db (singleton)
    Db()


    # Database configuration
    __table_args__= {'mysql_engine':'InnoDB', 'mysql_charset':'utf8', 'autoload': True }


    # Functions
    def __repr__(self):
        return "<BillDetail('%s')>" % (self.description)

class ThirdParty(sql.Model,sql.Base):
    __tablename__ = 'llx_societe'

    # Need to instanciate db (singleton)
    Db()


    # Database configuration
    __table_args__= {'mysql_engine':'InnoDB', 'mysql_charset':'utf8', 'autoload': True }


    # Relationship
    bills = relationship("Bill", backref="thirdParty")


    # Functions
    def __repr__(self):
        return "<ThirdParty('%s')>" % (self.nom)

# A customer is a thirdparty with client tag to 1 and fournisseur tag to 0
# A prospect is a thirdParty with client tag to 2 and fournisseur tag to 0
# A supplier is a thirdParty with client tag to 0 and fournisseur tag to 1

class Customer(ThirdParty):
    def __init__(self):
        sql.Model.__init__(self, fixed_characteristics = { 'client' : 1, 'fournisseur': 0 })
        ThirdParty.__init__(self)

class Prospect(ThirdParty):
    def __init__(self):
        sql.Model.__init__(self, fixed_characteristics = { 'client' : 2, 'fournisseur': 0 })
        ThirdParty.__init__(self)

class Supplier(ThirdParty):
    def __init__(self):
        sql.Model.__init__(self, fixed_characteristics = { 'client' : 0, 'fournisseur': 1 })
        ThirdParty.__init__(self)
