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
       
    id        = Column(String(45), primary_key = True)
    pca_id    = Column(Integer, index=True)
    size      = Column(BIGINT)
    state     = Column(String(20), index=True)
    startDate = Column(DATETIME)
    endDate   = Column(DATETIME)

    # Linked objects


    # Database configuration
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}

       
    # Functions
    def __repr__(self):
        return "<Session(id='%s',size='%i', state='%s')>" % (self.id, self.size, self.state)

    def syncWithRemote(self, remote):
        if(self.state == 'done' or self.state == 'synced'):
            return self
        else:
            changes=False
            for attr in ['size', 'state']:
                if(getattr(self,attr) != remote[attr]):
                    setattr(self, attr, remote[attr])
                    changes=True

            # Special data for date
            from dateutil.parser import parse
            for attr in ['startDate', 'endDate']:
                date = parse(remote[attr], fuzzy=True)
                setattr(self, attr, date.strftime("%Y-%m-%d %H:%M:%S"))

            if(changes):
                self.update()
            return self


class File(sql.Model, sql.Base):
    __tablename__ = 'files'
       
    id         = Column(String(45), primary_key = True)
    session_id = Column(String(45), index=True)
    name       = Column(String(255), index=True)
    type       = Column(String(50), index=True)
    size       = Column(BIGINT)
    state      = Column(String(20), index=True)

    # Linked objects


    # Database configuration
    __table_args__ = {'mysql_engine':'InnoDB','mysql_charset':'utf8'}

       
    # Functions
    def __repr__(self):
        return "<PCA('%s','%s', '%s')>" % (self.serviceName, self.pcaServiceName)

    def syncWithRemote(self, remote):
        if(self.state == 'done'):
            return True
        else:
            changes=False
            for attr in ['name', 'type', 'size', 'state']:
                if(getattr(self,attr) != remote[attr]):
                    setattr(self, attr, remote[attr])
                    changes=True
            if(changes):
                self.update()
            return self.state == 'done'
