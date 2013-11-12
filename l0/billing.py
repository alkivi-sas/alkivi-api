from alkivi.common import sql
from sqlalchemy import Column, Date, Integer, String, Index, ForeignKey, Float
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

class BankStatement(sql.Model,Base):
    __tablename__ = 'bank_statement'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id             = Column(Integer, primary_key = True)
    bankId         = Column(String(30))
    bankAccount    = Column(String(30))
    operationDate  = Column(Date)
    valueDate      = Column(Date, nullable=False)
    amount         = Column(Float, nullable=False)
    title          = Column(String(100), nullable=False)
    openerpId      = Column(Integer)
    md5line        = Column(String(32), nullable=False)

    # Indexes
    indexes = []
    indexes.append(Index('idx_operationDate', operationDate))
    indexes.append(Index('idx_valueDate', valueDate))
    indexes.append(Index('idx_md5', md5line, unique=True))
    indexes.append(Index('idx_amount', amount))
    indexes.append(Index('idx_openerpId', openerpId))
    indexes.append(Index('idx_bankId', bankId))
    indexes.append(Index('idx_bankAccount', bankAccount))
    

    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)


    # Functions
    def __repr__(self):
        return "<BankStatement ('%s')>" % (self.id)
