#TODO : dive in postgre ? :)
from alkivi.common import sql
from sqlalchemy import Column, Date, Integer, String, Index
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.mysql import DATETIME, BIGINT

class Db():
    instance = None

    def __init__(self, echo=False):
        # Will fetch credentials in a secureData file ... check /alkivi/common/sql.py
        self = sql.Db.instance(useData='archive', echo=echo)

class PCA(sql.Model,sql.Base):
    __tablename__ = 'pca'
       
    # Table Scheme
    id             = Column(Integer, primary_key = True)
    serviceName    = Column(String(30))
    pcaServiceName = Column(String(30))


    # Indexes
    indexes = []
    indexes.append(Index('unique_pca', serviceName, pcaServiceName, unique=True))
    

    # Linked objects


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        __table_args__.append({'mysql_engine':'InnoDB', 'mysql_charset':'utf8'})
        return tuple(__table_args__)


    # Functions
    def __repr__(self):
        return "<PCA('%s','%s')>" % (self.serviceName, self.pcaServiceName)

class Session(sql.Model,sql.Base):
    __tablename__ = 'sessions'
       
    # Table Scheme
    id          = Column(String(45), primary_key = True)
    pca_id      = Column(Integer)
    size        = Column(BIGINT)
    ovh_state   = Column(String(20))
    local_state = Column(String(20))
    startDate   = Column(DATETIME)
    endDate     = Column(DATETIME)

    # Indexes
    indexes = []
    indexes.append(Index('pca_id'      , pca_id))
    indexes.append(Index('ovh_state'   , ovh_state))
    indexes.append(Index('local_state' , local_state))


    # Linked objects


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        __table_args__.append({'mysql_engine':'InnoDB', 'mysql_charset':'utf8'})
        return tuple(__table_args__)

       
    # Functions
    def __repr__(self):
        return "<Session(id='%s',size='%i', state='%s')>" % (self.id, self.size, self.state)

    def syncWithRemote(self, remote):
        if(self.local_state == 'synced' and self.ovh_state == remote['state']):
            return self
        else:
            changes=False
            dict = { 'size': 'size', 'ovh_state': 'state' }
            for local_attr, remote_attr in dict.iteritems(): 
                if(getattr(self,local_attr) != remote[remote_attr]):
                    setattr(self, local_attr, remote[remote_attr])
                    changes=True

            # Special data for date 
            # TODO : use hash as well ?
            from dateutil.parser import parse
            for attr in ['startDate', 'endDate']:
                date = parse(remote[attr], fuzzy=True)
                newDate = date.strftime("%Y-%m-%d %H:%M:%S")
                if(getattr(self,attr) != newDate):
                    setattr(self, attr, newDate)
                    changes=True

            # Well well
            if(changes):
                self.update()

            # Test is made with all file inside ...
            return self


class File(sql.Model, sql.Base):
    __tablename__ = 'files'
       
    id          = Column(String(45), primary_key = True)
    session_id  = Column(String(45))
    name        = Column(String(255))
    fileName    = Column(String(60))
    type        = Column(String(50))
    size        = Column(BIGINT)
    sha1        = Column(String(40))
    sha256      = Column(String(64))
    md5         = Column(String(32))
    ovh_state   = Column(String(20))
    local_state = Column(String(20))


    # Indexes
    indexes = []
    indexes.append(Index('session_id'  , session_id))
    indexes.append(Index('name'        , name))
    indexes.append(Index('fileName'    , fileName))
    indexes.append(Index('type'        , type))
    indexes.append(Index('sha1'        , sha1         , mysql_length=10))
    indexes.append(Index('sha256'      , sha256       , mysql_length=16))
    indexes.append(Index('md5'         , sha256       , mysql_length=8))
    indexes.append(Index('ovh_state'   , ovh_state))
    indexes.append(Index('local_state' , local_state))


    # Linked objects


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        __table_args__.append({'mysql_engine':'InnoDB', 'mysql_charset':'utf8'})
        return tuple(__table_args__)

       
    # Functions
    def __repr__(self):
        return "<PCA('%s','%s', '%s')>" % (self.serviceName, self.pcaServiceName)

    def syncWithRemote(self, remote):
        # Do we have an update from remote ?
        if(self.ovh_state == remote['state']):
            return self.ovh_state == 'done'
        else:
            changes=False
            # Use a dict to be able to map different key names
            dict = { 
                    'name'      : 'name',
                    'type'      : 'type',
                    'size'      : 'size',
                    'sha1'      : 'SHA1',
                    'sha256'    : 'SHA256',
                    'md5'       : 'MD5',
                    'ovh_state' : 'state',
                    }

            for local_attr, remote_attr in dict.iteritems(): 
                if(getattr(self,local_attr) != remote[remote_attr]):
                    # Fix fileName by splitting path
                    if(local_attr=='name'):
                        self.fileName = remote[remote_attr].split('/')[-1]

                    setattr(self, local_attr, remote[remote_attr])
                    changes=True

            # At this point, we are synced
            if(self.local_state != 'synced'):
                self.local_state = 'synced'
                changes = True

            # Well well
            if(changes):
                self.update()

            # Return true is remote state is done
            return self.ovh_state == 'done'
