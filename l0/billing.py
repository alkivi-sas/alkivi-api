from alkivi.common import sql
from sqlalchemy import Column, Integer, String, Index, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from alkivi.common import logger

Base = declarative_base()

def has_changed(local_value, linxo_value, data_type=None):
    """Perform comparaison according to type

    Parameters
    linxo_value comes from linxo_object : always str
    local_value comes from database
    """
    if data_type is None:
        return local_value != linxo_value
    elif data_type is 'int':
        return local_value != int(linxo_value)
    elif data_type is 'float':
        return local_value != float(linxo_value)
    elif data_type is 'date':
        from datetime import datetime
        linxo_value = datetime.fromtimestamp(int(linxo_value))
        return local_value != linxo_value
    else:
        raise Exception('wrong data_type')

def format_linxo_data(linxo_value, data_type=None):
    """see has_changed ...
    """
    if data_type is None:
        return linxo_value
    elif data_type == 'int':
        return int(linxo_value)
    elif data_type == 'float':
        return float(linxo_value)
    elif data_type == 'date':
        from datetime import datetime
        return datetime.fromtimestamp(int(linxo_value))
    else:
        raise Exception('wrong data_type')



def check_changes(local, linxo, translation_dict, data_type=None):
    """Generic function to call when updating object
    """
    changes = None

    for local_key, linxo_key in translation_dict.iteritems():
        if linxo_key in linxo:
            value = getattr(local, local_key)
            if has_changed(value, linxo[linxo_key], data_type):
                value = format_linxo_data(linxo[linxo_key])
                setattr(local, local_key, value)
                if changes is None:
                    logger.debug('key {} differs {} {}'.format(local_key, value, linxo[linxo_key]))
                    changes = True
    return changes

class Db():
    instance = None

    def __init__(self, echo=False):
        # Will fetch credentials in a secureData file ... check /alkivi/common/sql.py
        self = sql.Db.instance(use_data='billing', echo=echo)
        Base.metadata.create_all(self.engine)

class BankAccount(sql.Model, Base):
    __tablename__ = 'bank_accounts'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id = Column(Integer, primary_key = True)
    account_group_id = Column(Integer)
    account_group_name = Column(String(30))
    account_namber = Column(String(30))
    name = Column(String(120))
    type = Column(String(30))

    # Indexes
    indexes = []
    indexes.append(Index('idx_account_namber', account_namber))
    indexes.append(Index('idx_type', type))
    indexes.append(Index('idx_account_group_id', account_group_id))
    indexes.append(Index('idx_account_group_name', account_group_name))
    
    # Relationship
    transaction = relationship("BankTransaction", backref="bank_accounts")

    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)

    # Functions
    def __repr__(self):
        return "<BankAccount ('%d','%s', '%s')>" % (self.id or 0, self.account_group_name or 'empty', self.name or 'empty')

    def _get_translation_dict(self, data=None):
        """Link between our object name and linxo object
        """
        if data is None:
            return {
                'account_group_name' : 'accountGroupName',
                'account_namber': 'accountNumber',
                'name': 'name',
                'type': 'type' }
        elif data is 'int':
            return {
                'account_group_id': 'accountGroupId',}
        else:
            raise Exception('wrong data {}'.format(data))

    def _get_data_types(self):
        """Return data_type use to translation linxo data to database
        """
        return [None, 'int']


    def create_from_linxo(self, linxo):
        """Create object take linxo data as parameter

        Parameters
        linxo : json dict from linxo api
        """
        characteristics = { 'id' : linxo['id'] }
        self = self.fetch_or_create(characteristics=characteristics, no_save=True)

        for data_type in self._get_data_types():
            for local_key, linxo_key in self._get_translation_dict(data_type).iteritems():
                if linxo_key in linxo:
                    value = format_linxo_data(linxo[linxo_key], data_type)
                    setattr(self, local_key, value)

        self.save()
        return self

    def update_from_linxo(self, linxo):
        """Check if they are any changes and commit only when changes

        Parameters
        linxo : json dict from linxo api
        """
        changes = None
        for data_type in self._get_data_types():
            temp_changes = check_changes(self, linxo, self._get_translation_dict(data_type), data_type)
            if changes is None and temp_changes:
                changes = temp_changes

        if changes:
            logger.debug('updating object')
            self.save()
        else:
            logger.debug('not updating object')
        return self

class BankTransaction(sql.Model, Base):
    __tablename__ = 'bank_transactions'

    # Need to instanciate db (singleton) 
    Db()


    # Table Scheme
    id = Column(Integer, primary_key = True)
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'))
    openerp_id = Column(Integer)
    amount = Column(Float, nullable=False)
    budget_date = Column(DateTime)
    category_id = Column(Integer)
    date = Column(DateTime)
    label = Column(String(255))
    notes = Column(String(255))
    original_category = Column(Integer)
    original_city = Column(String(255))
    original_date_available = Column(DateTime)
    original_date_initiated = Column(DateTime)
    original_label = Column(String(255))
    original_third_party = Column(String(255))

    # Indexes
    indexes = []
    indexes.append(Index('idx_bank_account_id', bank_account_id))
    indexes.append(Index('idx_openerp_id', openerp_id))
    indexes.append(Index('idx_date', date))
    indexes.append(Index('idx_budget_date', budget_date))
    indexes.append(Index('idx_amount', amount))
    

    # Database configuration
    @declared_attr
    def __table_args__(cls):
        __table_args__ = cls.indexes
        return tuple(__table_args__)


    # Functions
    def __repr__(self):
        return "<BankStatement ('%d', '%s', '%.2f')>" % (self.id or 0, self.label or '', self.amount or '0.0')
    
    def _get_translation_dict(self, data=None):
        if data is None:
            return {
                'amount': 'amount',
                'label': 'label',
                'notes': 'notes',
                'original_city': 'originalCity',
                'original_label': 'originalLabel',
                'original_third_party': 'originalThirdParty',}
        elif data is 'int':
            return {
                'bank_account_id': 'bankAccountId',
                'original_category': 'originalCategory',
                'category_id': 'categoryId',}
        if data is 'float':
            return {
                'amount': 'amount',}
        elif data == 'date':
            return {
                'budget_date': 'budgetDate',
                'date': 'date',
                'original_date_available': 'originalDateAvailable',
                'original_date_initiated': 'originalDateInitiated',
            }
        else:
            raise Exception('wrong data {}'.format(data))

    def _get_data_types(self):
        """Return data_type use to translation linxo data to database
        """
        return [None, 'int', 'float', 'date']

    def create_from_linxo(self, linxo):
        """Create object take linxo data as parameter

        Parameters
        linxo : json dict from linxo api
        """
        characteristics = { 'id' : linxo['id'] }
        self = self.fetch_or_create(characteristics=characteristics, no_save=True)

        for data_type in self._get_data_types():
            for local_key, linxo_key in self._get_translation_dict(data_type).iteritems():
                if linxo_key in linxo:
                    value = format_linxo_data(linxo[linxo_key], data_type)
                    setattr(self, local_key, value)

        return self

    def update_from_linxo(self, linxo):
        """Check if they are any changes and commit only when changes

        Parameters
        linxo : json dict from linxo api
        """
        changes = None
        for data_type in self._get_data_types():
            temp_changes = check_changes(self, linxo, self._get_translation_dict(data_type), data_type)
            if changes is None and temp_changes:
                changes = temp_changes

        if changes:
            logger.debug('updating object')
            self.save()
        else:
            logger.debug('not updating object')
        return self
