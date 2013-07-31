from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
import datetime
import os
import re

from alkivi.common import Singleton
from alkivi.common import logger
 
Base = declarative_base()
 
 
@Singleton
class Db(object):
 
    '''
    The DB Class should only exits once, thats why it has the @Singleton decorator.
    To Create an instance you have to use the instance method:
        db = Db.instance()
    '''
 
    engine = None
    session = None
 
    def __init__(self, useData, echo=False, charset='utf8'):

        # Going to extract data from /alkivi/.secureData
        base = '/alkivi/.secureData/sql/'
        file = base + useData

        # Test file is ok
        if(not(os.path.exists(file))):
            logger.warning('Unable to fetch correct file. Check that %s exists and is readable' % (file))
            raise

        # Open file
        f = open(file)

        # Check syntax
        rx = re.compile('^(.*?):(.*?):(.*?):(.*?)$')
        for line in f:
            m = rx.search(line)
            if(m):
                host,db,user,password = m.groups()
                self.url = 'mysql://%s:%s@%s/%s?charset=%s' % (user, password, host, db, charset)


        if(not(self.url)):
            logger.warning('No url, wtf ?', self)
            raise

        self.engine = create_engine(self.url, echo=echo)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
 
        ## Create all Tables
        Base.metadata.create_all(self.engine)
 
    def instance(self, *args, **kwargs): 
 
        '''
        Dummy method, cause several IDEs can not handel singeltons in Python
        '''
 
        pass
 
class Model():
 
    '''
    This is a baseclass with delivers all basic database operations
    '''
 
    def save(self):
        db = Db.instance()
        db.session.add(self)
        db.session.commit()
 
    def saveMultiple(self, objects = []):
        db = Db.instance()
        db.session.add_all(objects)
        db.session.commit()
 
    def update(self):
        db = Db.instance()
        db.session.commit()
 
    def delete(self):
        db = Db.instance()
        db.session.delete(self)
        db.session.commit()
 
    def queryObject(self):
        db = Db.instance()
        return db.session.query(self.__class__)

    def newListFromCharacteristics(self, *args, **kwargs):
        db = Db.instance()
        query = self.queryObject()
        for attr, value in kwargs.items():
            query = query.filter(getattr(self.__class__, attr)==value)
        return query.all()

    def newFromCharacteristics(self, *args, **kwargs):
        db = Db.instance()
        query = self.queryObject()
        #logger.debug("newFromCharacteristicsOrCreate")
        for attr, value in kwargs.items():
            #logger.debug("Going to append filter %s=%s" % (attr, value))
            query = query.filter(getattr(self.__class__, attr)==value)
        return query.one()

    def newFromCharacteristicsOrCreate(self, *args, **kwargs):
        from sqlalchemy.orm.exc import NoResultFound
        try:
            result = self.newFromCharacteristics(*args, **kwargs)
        except NoResultFound as e:
            result = self.__class__()
            for attr, value in kwargs.items():
                setattr(result, attr, value)
            result.save()
        except:
            raise

        return result




