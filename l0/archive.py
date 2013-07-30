#TODO : dive in postgre ? :)
from alkivi.common import sql
from sqlalchemy import Column, Date, Integer, String, Index
from sqlalchemy.dialects.mysql import DATETIME, BIGINT

class Db():
    instance = None

    def __init__(self, echo=False):
        # Will fetch credentials in a secureData file ... check /alkivi/common/sql.py
        self = sql.Db.instance(useData='archive', echo=echo)

class PCA(sql.Model,sql.Base):
    __tablename__ = 'pca'
       
    # Default column with index
    id             = Column(Integer, primary_key = True)
    serviceName    = Column(String(30))
    pcaServiceName = Column(String(30))


    # Linked objects


    # Database configuration
    __table_args__ = (Index('unique_pca', serviceName, pcaServiceName, unique=True), {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'} )


    # Functions
    def __repr__(self):
        return "<PCA('%s','%s')>" % (self.serviceName, self.pcaServiceName)

class Session(sql.Model,sql.Base):
    __tablename__ = 'sessions'
       
    id          = Column(String(45), primary_key = True)
    pca_id      = Column(Integer, index=True)
    size        = Column(BIGINT)
    ovh_state   = Column(String(20), index=True)
    local_state = Column(String(20), index=True)
    startDate   = Column(DATETIME)
    endDate     = Column(DATETIME)

    # Linked objects


    # Database configuration
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}

       
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
    session_id  = Column(String(45), index=True)
    name        = Column(String(255), index=True)
    type        = Column(String(50), index=True)
    size        = Column(BIGINT)
    ovh_state   = Column(String(20), index=True)
    local_state = Column(String(20), index=True)

    # Linked objects


    # Database configuration
    __table_args__ = {'mysql_engine':'InnoDB','mysql_charset':'utf8'}

       
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
            dict = { 'name': 'name', 
                     'type': 'type',
                     'size': 'size',
                     'ovh_state': 'state',
                    }

            for local_attr, remote_attr in dict.iteritems(): 
                if(getattr(self,local_attr) != remote[remote_attr]):
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
