from alkivi.common import sql
from sqlalchemy import Column, Date, Integer, String, Index, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from alkivi.common import logger

Base = declarative_base()

class Db():
    instance = None

    def __init__(self, echo=False):
        # Will fetch credentials in a secureData file ... check /alkivi/common/sql.py
        self = sql.Db.instance(useData='billing', echo=echo)
        Base.metadata.create_all(self.engine)

class BankAccount(sql.Model, Base):
    __tablename__ = 'bank_accounts'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id = Column(Integer, primary_key = True)
    accountGroupId = Column(Integer)
    accountGroupName = Column(String(30))
    accountNumber = Column(String(30))
    name = Column(String(120))
    type = Column(String(30))

    # Indexes
    indexes = []
    indexes.append(Index('idx_accountNumber', accountNumber))
    indexes.append(Index('idx_type', type))
    indexes.append(Index('idx_accountGroupId', accountGroupId))
    indexes.append(Index('idx_accountGroupName', accountGroupName))
    

    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)

    # Functions
    def __repr__(self):
        return "<BankAccount ('%d','%s', '%s')>" % (self.id or 0, self.accountGroupName or 'empty', self.name or 'empty')

    def new_from_linxo(self, object):
        characteristics = { 'id' : object['id'] }
        self = self.newFromCharacteristicsOrCreate(characteristics = characteristics)

        for key in ['accountGroupId', 'accountGroupName', 'accountNumber', 'name', 'type']:
            setattr(self, key, object[key])

        self.save()
        return self


class BankTransaction(sql.Model,Base):
    __tablename__ = 'bank_transactions'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id = Column(Integer, primary_key = True)
    bankAccountId = Column(Integer)
    openerpId = Column(Integer)
    amount = Column(Float, nullable=False)
    budgetDate = Column(DateTime)
    categoryId = Column(Integer)
    date = Column(DateTime)
    label = Column(String(32))
    notes = Column(String(255))
    originalCategory = Column(Integer)
    originalCity = Column(String(32))
    originalDateAvailable = Column(DateTime)
    originalDateInitiated = Column(DateTime)
    originalLabel = Column(String(32))
    originalThirdParty = Column(String(32))

    # Indexes
    indexes = []
    indexes.append(Index('idx_bankAccountId', bankAccountId))
    indexes.append(Index('idx_date', date))
    indexes.append(Index('idx_budgetDate', budgetDate))
    indexes.append(Index('idx_amount', amount))
    

    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)


    # Functions
    def __repr__(self):
        return "<BankStatement ('%d', '%s', '%.2f')>" % (self.id or 0, self.label or '', self.amount or '0.0')

    def new_from_linxo(self, object):
        characteristics = { 'id' : object['id'] }
        self = self.newFromCharacteristicsOrCreate(characteristics = characteristics)

        for key in ['bankAccountId', 'amount', 'categoryId', 'label', 'notes', 'originalCategory', 'originalCity', 'originalLabel', 'originalThirdParty']:
            # According to linxo bank, we dont have the same info. Some keys might be missing
            if key in object:
                setattr(self, key, object[key])

        # Special treatment for timestamp
        from datetime import datetime
        for key in ['budgetDate', 'date', 'originalDateAvailable', 'originalDateInitiated']:
            # According to linxo bank, we dont have the same info. Some keys might be missing
            if key in object:
                value = datetime.fromtimestamp(int(object[key]))
                setattr(self, key, value)


        return self
