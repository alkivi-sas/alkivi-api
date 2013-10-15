#TODO : dive in postgre ? :)
from alkivi.common import sql
from sqlalchemy import Column, Date, Integer, String, Index, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.dialects.mysql import DATETIME, BIGINT, FLOAT
from alkivi.common import logger

Base = declarative_base()

class Db():
    instance = None

    def __init__(self, echo=False):
        # Will fetch credentials in a secureData file ... check /alkivi/common/sql.py
        self = sql.Db.instance(useData='welsh', echo=echo)
        Base.metadata.create_all(self.engine)

class Restaurant(sql.Model,Base):
    __tablename__ = 'restaurants'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id             = Column(Integer, primary_key=True, autoincrement=True)
    name           = Column(String(60))
    lat            = Column(FLOAT(33,15))
    lng            = Column(FLOAT(33,15))
    town           = Column(String(60))
    address        = Column(String(80))
    zipCode        = Column(Integer(5))
    phone          = Column(String(17))
    price          = Column(FLOAT(6,2))
    noon           = Column(Boolean)
    night          = Column(Boolean)
    weekends       = Column(Boolean)
    late           = Column(Boolean)
    rsvp           = Column(Boolean)
    validated      = Column(Boolean, server_default='0')
    creationDate   = Column(Date)


    # Indexes
    indexes = []
    indexes.append(Index('idx_name', name))
    indexes.append(Index('idx_zip', zipCode))
    indexes.append(Index('idx_town', town))
    

    # Relationship
    comments = relationship("Comment", backref="restaurant")


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        __table_args__.append({'mysql_engine':'InnoDB', 'mysql_charset':'utf8'})
        return tuple(__table_args__)


    # Functions
    def __repr__(self):
        return "<WelshRestaurant('%s','%s %d %s')>" % (self.name, self.address, self.zipCode, self.town)

class Comment(sql.Model,Base):
    __tablename__ = 'comments'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id             = Column(Integer, primary_key=True, autoincrement=True)
    restaurantId   = Column(Integer, ForeignKey('restaurants.id'))
    internal       = Column(Boolean, server_default='0')
    comment        = Column(Text)
    grade          = Column(Integer(2))
    date           = Column(Date)

    # Indexes
    indexes = []
    indexes.append(Index('idx_restaurantId', restaurantId))
    indexes.append(Index('idx_grade', grade))
    


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        __table_args__.append({'mysql_engine':'InnoDB', 'mysql_charset':'utf8'})
        return tuple(__table_args__)


    # Functions
    def __repr__(self):
        return "<WelshComment('id=%d','grade=%d', 'comment=%s')>" % (self.id, self.grade, self.comment)
