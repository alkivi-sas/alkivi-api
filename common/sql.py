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
        rx = re.compile('^(.*?):(.*?):(.*?):(.*?):(.*?):(.*?)$')
        type,host,port,db,user,password = (None, None, None, None, None, None)
        for line in f:
            m = rx.search(line)
            if(m):
                type,host,port,db,user,password = m.groups()

        if(not(password)):
            logger.warning('Password is not set, meaning that %s file is not correctly formatted, check it out' % file)
            raise

        if(type == 'mysql'):
            self.url = '%s://%s:%s@%s:%s/%s?charset=%s' % (type, user, password, host, port, db, charset)
        elif(type == 'postgres'):
            self.url = '%s://%s:%s@%s:%s/%s' % (type, user, password, host, port, db )
        else:
            logger.warning('Unknow engin type %s' % type)
            raise


        if(not(self.url)):
            logger.warning('No url, wtf ?', self)
            raise

        self.engine = create_engine(self.url, echo=echo)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
 
 
    def instance(self, *args, **kwargs): 
 
        '''
        Dummy method, cause several IDEs can not handel singeltons in Python
        '''
 
        pass
 
class Model():
 
    '''
    This is a baseclass with delivers all basic database operations
    '''
    def __init__(self, *args, **kwargs):
        if('fixed_characteristics' in kwargs):
            self.fixed_characteristics = kwargs['fixed_characteristics']

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

    # Create an object with characteristics, but dont commit it
    def new(self, *args, **kwargs):
        result = self.__class__()
        characteristics = kwargs.get('characteristics')
        # TODO : throw errors if no characteristics ?
        for attr, value in characteristics.items():
            setattr(result, attr, value)

        return result

    # Fetch a list of object having all the following characteristics
    def newListFromCharacteristics(self, *args, **kwargs):
        db = Db.instance()
        query = self.queryObject()
        characteristics = kwargs.get('characteristics')

        try:
            getattr(self, 'fixed_characteristics')
            if(not(characteristics)):
                kwargs['characteristics'] = self.fixed_characteristics
            else:
                for key, value in self.fixed_characteristics.items():
                    if((key in characteristics) and (characteristics[key] != value)):
                        logger.warning('You are trying to fetch a customer with wrong characteristics, going to fix %s to %s' % (key, value))

                    characteristics[key] = value

        except AttributeError:
            pass

        # Todo empty ?
        if(characteristics):
            for attr, value in characteristics.items():
                # We have potentially other filter
                if(isinstance(value, dict)):
                    operator = value['operator']
                    fvalue   = value['value']
                    logger.debug_debug("Going to append filter %s and operator %s=%s" % (attr, operator, fvalue))
                    query = query.filter(getattr(self.__class__, attr).like(fvalue))


                else:
                    logger.debug_debug("Going to append filter %s=%s" % (attr, value))
                    query = query.filter(getattr(self.__class__, attr)==value)
        return query.all()




    # Same as list but query.one() -> will raise an exception if multiple found
    def newFromCharacteristics(self, *args, **kwargs):
        db = Db.instance()
        query = self.queryObject()
        #logger.debug("newFromCharacteristicsOrCreate")
        characteristics = kwargs.get('characteristics')
        # TODO : throw errors if no characteristics
        for attr, value in characteristics.items():
            logger.debug_debug("Going to append filter %s=%s" % (attr, value))
            query = query.filter(getattr(self.__class__, attr)==value)
        return query.one()


    # First newFromCharacteristics if no one found, the new and still dont commit
    def newFromCharacteristicsOrCreate(self, *args, **kwargs):
        from sqlalchemy.orm.exc import NoResultFound
        try:
            result = self.newFromCharacteristics(*args, **kwargs)
        except NoResultFound as e:
            result = self.new(*args, **kwargs)
        except:
            raise

        return result


    # TODO : make this better according to type ?
    def as_dict(self):
           return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


