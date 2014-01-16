"""
Global wrapper to use to fetch object in our database
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import re

from alkivi.common import Singleton
from alkivi.common import logger
 
 
@Singleton
class Db(object):
    """
    The DB Class should only exits once, thats why it has the @Singleton decorator.
    To Create an instance you have to use the instance method:
        db = Db.instance()
    """
 
    #engine = None
    #session = None
 
    def __init__(self, use_data, echo=False, charset='utf8'):

        # Going to extract data from /alkivi/.secureData
        base = '/alkivi/.secureData/sql/'
        credentials = base + use_data

        # Test file is ok
        if not os.path.exists(credentials):
            raise Exception(
                'Unable to fetch credentials.' +
                'Check that %s exists and is readable' % (credentials))

        # Open file
        f_handler = open(credentials)

        # Check syntax
        regexp = re.compile('^(.*?):(.*?):(.*?):(.*?):(.*?):(.*?)$')
        db_type = None
        host = None
        port = None
        db_name = None
        user = None
        password = None

        for line in f_handler:
            match = regexp.search(line)
            if match:
                db_type, host, port, db_name, user, password = match.groups()

        if not password:
            raise Exception('Password is not set.' +
                            ' Check that file %s is correct' % credentials)

        if db_type == 'mysql':
            self.url = '%s://%s:%s@%s:%s/%s?charset=%s' % (db_type, user, 
                                                           password, host, 
                                                           port, db_name, 
                                                           charset)
        elif db_type == 'postgres':
            self.url = '%s://%s:%s@%s:%s/%s' % (db_type, user, password, 
                                                host, port, db_name )
        else:
            raise Exception('Unknow engin type %s' % db_type)


        if not self.url:
            raise Exception('No url here, WTF ?')

        self.engine = create_engine(self.url, echo=echo)
        session = sessionmaker(bind=self.engine)
        self.session = session()
 
class Model():
    """
    This is a baseclass with delivers all basic database operations
    """
    def __init__(self, *args, **kwargs):
        if('fixed_characteristics' in kwargs):
            self.fixed_characteristics = kwargs['fixed_characteristics']

    def save(self):
        """Save object to database, two steps : add and commit. 

        To just commit, use update
        """
        db = Db.instance()
        db.session.add(self)
        db.session.commit()
 
    #def saveMultiple(self, objects = None):
    #    """Save multiple object at once
    #    """
    #    if objects is None:
    #        objects = []

    #    db = Db.instance()
    #    db.session.add_all(objects)
    #    db.session.commit()
 
    def update(self):
        """Just perform a small update
        """
        db = Db.instance()
        db.session.commit()
 
    def delete(self):
        """Delete an object from a session
        """
        db = Db.instance()
        db.session.delete(self)
        db.session.commit()
 
    def query(self):
        """Perform a query
        """
        db = Db.instance()
        return db.session.query(self.__class__)

    def new(self, *args, **kwargs):
        """Create an object given characteristics, not committing it
        """
        result = self.__class__()
        characteristics = kwargs.get('characteristics')
        # TODO : throw errors if no characteristics ?
        for attr, value in characteristics.items():
            setattr(result, attr, value)

        return result

    def fetch_list(self, *args, **kwargs):
        """Fetch a list of object having the same characteristics
        """
        query = self._handle_characteristics(*args, **kwargs)
        return query.all()


    def fetch(self, *args, **kwargs):
        """Same as fetch_list but raise exception if multiple found
        """
        query = self._handle_characteristics(*args, **kwargs)
        return query.one()

    def _handle_characteristics(self, *args, **kwargs):
        """Parse arguments for characteristics 
        return a query that has been prepared
        """
        query = self.query()
        characteristics = kwargs.get('characteristics')

        try:
            getattr(self, 'fixed_characteristics')
            if not characteristics:
                kwargs['characteristics'] = self.fixed_characteristics
            else:
                for key, value in self.fixed_characteristics.items():
                    if key in characteristics and characteristics[key] != value:
                        message = 'Malformed characteristics. Fixing '
                        message += ' {}'.format(key)
                        message += ' from {}'.format(characteristics[key])
                        message += ' to {}'.format(value)
                        logger.warning(message)
                    characteristics[key] = value

        except AttributeError:
            pass

        # Todo empty ?
        if(characteristics):
            for attr, value in characteristics.items():
                # We have potentially other filter
                if isinstance(value, dict):
                    operator = value['operator']
                    fvalue = value['value']
                    logger.debug_debug(
                        "Going to append filter %s and operator %s=%s" % 
                        (attr, operator, fvalue))
                    # TODO : so far only like ...
                    attr = getattr(self.__class__, attr)
                    query = query.filter(attr.like(fvalue))
                else:
                    logger.debug_debug(
                        "Going to append filter %s=%s" % (attr, value))
                    query = query.filter(getattr(self.__class__, attr)==value)
        return query


    def fetch_or_create(self, *args, **kwargs):
        """Try to find an object in database.
        If no object is found, create one

        By default object is save to database
        
        Extra parameters : 
            - no_save : dont save object on creation
        """
        no_save = None
        if 'no_save' in kwargs:
            no_save = kwargs['no_save']

        from sqlalchemy.orm.exc import NoResultFound
        try:
            result = self.fetch(*args, **kwargs)
        except NoResultFound:
            result = self.new(*args, **kwargs)
            if no_save:
                logger.debug_debug('no_save activated')
            else:
                result.save()
        except:
            raise

        return result


    def as_dict(self):
        """To be able to dump data
        """
        columns = self.__table__.columns
        return { c.name: str(getattr(self, c.name)) for c in columns }


