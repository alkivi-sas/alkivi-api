"""
Class that represents OVH object in our database
"""
from alkivi.common import sql
from sqlalchemy import Column, Integer, String, Index, ForeignKey
from sqlalchemy import DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from alkivi.common import logger

Base = declarative_base()

class Db():
    """Class that handle our database
    """
    instance = None

    def __init__(self, echo=False):
        self = sql.Db.instance(use_data='archive', echo=echo)
        Base.metadata.create_all(self.engine)

class PCA(sql.Model, Base):
    """Store OVH PCA information
    """
    __tablename__ = 'pca'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id = Column(Integer, primary_key = True)
    service_name = Column(String(30))
    pca_service_name = Column(String(30))


    # Indexes
    indexes = []
    indexes.append(Index('idx_unique_pca',
                         service_name, 
                         pca_service_name, unique=True))
    

    # Relationship
    sessions = relationship("Session", backref="pca")


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)


    # Functions
    def __repr__(self):
        return "<PCA('%d', '%s','%s')>" % (self.id or 0, self.service_name or '', self.pca_service_name or '')

class Session(sql.Model, Base):
    """Store OVH PCA Sessions informations
    """
    __tablename__ = 'sessions'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id = Column(String(45), primary_key = True)
    pca_id = Column(Integer, ForeignKey('pca.id'))
    size = Column(BigInteger)
    ovh_state = Column(String(20))
    local_state = Column(String(20))
    start_date = Column(DateTime)
    end_date = Column(DateTime)


    # Indexes
    indexes = []
    indexes.append(Index('idx_pca_id', pca_id))
    indexes.append(Index('idx_ovh_state', ovh_state))
    indexes.append(Index('idx_local_state', local_state))


    # Relationship
    files = relationship("File", backref="sessions")


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)

       
    # Functions
    def __repr__(self):
        return "<Session(id=%s, ovh=%s, local=%s)>" % (self.id or '', self.ovh_state or '', self.local_state or '')

    def sync_with_remote(self, remote):
        """Sync between ovh data and local
        """
        if self.local_state == 'synced' and self.ovh_state == remote['state']:
            return self
        else:
            changes = False
            ovh_dict = { 'size': 'size', 'ovh_state': 'state' }
            for local_attr, remote_attr in ovh_dict.iteritems(): 
                if getattr(self, local_attr) != remote[remote_attr]:
                    setattr(self, local_attr, remote[remote_attr])
                    changes = True

            from dateutil.parser import parse
            for attr in ['start_date', 'end_date']:
                # Might be null in some case
                if attr in remote and remote[attr]:
                    date = parse(remote[attr], fuzzy=True)
                    new_date = date.strftime("%Y-%m-%d %H:%M:%S")
                    if getattr(self, attr) != new_date:
                        setattr(self, attr, new_date)
                        changes = True

            if changes:
                self.update()

            # Test is made with all file inside ...
            return self

    def delete_all_files(self):
        """Delete all files in a sessions, might be very very long
        """
        files = self.files
        for todo_file in files:
            logger.debug('Going to delete file %s' %(todo_file))
            todo_file.delete()


class File(sql.Model, Base):
    """Wrapper to represents files
    """
    __tablename__ = 'files'

    # Need to instanciate db (singleton) 
    Db()

    # Table Scheme
    id = Column(String(45), primary_key=True)
    session_id = Column(String(45), ForeignKey('sessions.id'))
    name = Column(String(255))
    file_name = Column(String(60))
    file_type = Column(String(50))
    size = Column(BigInteger)
    sha1 = Column(String(40))
    sha256 = Column(String(64))
    md5 = Column(String(32))
    ovh_state = Column(String(20))
    local_state = Column(String(20))


    # Indexes
    indexes = []
    indexes.append(Index('idx_session_id', session_id))
    indexes.append(Index('idx_name', name))
    indexes.append(Index('idx_file_name', file_name))
    indexes.append(Index('idx_type', file_type))
    indexes.append(Index('idx_sha1', sha1))
    indexes.append(Index('idx_sha256', sha256))
    indexes.append(Index('idx_md5', md5))
    indexes.append(Index('idx_ovh_state', ovh_state))
    indexes.append(Index('idx_local_state', local_state))


    # Relationship


    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)

       
    # Functions
    def __repr__(self):
        return "<File('%s','%s', '%s')>" % (self.id or 0, self.name or '', self.size or '')

    def sync_with_remote(self, remote):
        """Sync information between ovh API and our database
        """

        if self.ovh_state == remote['state']:
            return self.ovh_state == 'done'
        else:
            changes = False
            # Use a dict to be able to map different key names
            ovh_dict = { 
                    'name': 'name',
                    'file_type': 'type',
                    'size': 'size',
                    'sha1': 'SHA1',
                    'sha256': 'SHA256',
                    'md5': 'MD5',
                    'ovh_state': 'state',
                }

            for local_attr, remote_attr in ovh_dict.iteritems(): 
                if getattr(self, local_attr) != remote[remote_attr]:
                    # Fix file_name by splitting path
                    if local_attr == 'name':
                        self.file_name = remote[remote_attr].split('/')[-1]

                    setattr(self, local_attr, remote[remote_attr])
                    changes = True

            # At this point, we are synced
            if self.local_state != 'synced':
                self.local_state = 'synced'
                changes = True

            # Well well
            if changes:
                self.update()

            # Return true is remote state is done
            return self.ovh_state == 'done'
