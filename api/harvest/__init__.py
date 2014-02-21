#!/usr/bin/env python
'''
Alkivi Harvest Wrapper
Based on https://github.com/lann/Harvest
See http://www.getharvest.com/api

'''
import urllib2
import datetime
from base64 import b64encode
from dateutil.parser import parse as parseDate
from xml.dom.minidom import parseString
from alkivi.common import logger


class HarvestError(Exception):
    """Global exeption for Harvest
    """
    pass


class HarvestConnectionError(HarvestError):
    """Special Exception related to connection
    """
    pass

# Use to auload all classes and perform the mapping in Harvest
INSTANCE_CLASSES = []

class HarvestItemGetterable(type):
    """Base object for iterable object
    """
    def __init__(mcs, name, bases, attrs):
        super(HarvestItemGetterable, mcs).__init__(name, bases, attrs)
        INSTANCE_CLASSES.append(mcs)


class HarvestItemBase(object):
    """Base object for simple object

    Note the all - and ' ' in key are replace
    """
    def __init__(self, harvest, data):
        self.harvest = harvest
        for key, value in data.items():
            key = key.replace('-','_').replace(' ','_')
            try:
                setattr(self, key, value)
            except AttributeError:
                pass


class User(HarvestItemBase):
    """User binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/people'
    element_name = 'user'
    plural_name = 'users'

    def __str__(self):
        return u'User: %s %s' % (self.first_name, self.last_name)

    def entries(self, start, end):
        """Return entries for a specific users
        
        Parameters start and end are date and should be optional 
        """
        if not start:
            start = datetime.date(1990, 01, 01)
        if not end:
            end = datetime.date.today() + datetime.timedelta(days=1)

        return self.harvest._time_entries('%s/%d/' % (self.base_url, self.id),
                                          start, end)


class Project(HarvestItemBase):
    """Project binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/projects'
    element_name = 'project'
    plural_name = 'projects'

    def __str__(self):
        return 'Project: ' + self.name

    def entries(self, start=None, end=None):
        """Return entries for a specific users
        
        Parameters start and end are date and should be optional 
        """
        if not start:
            start = datetime.date(1990, 01, 01)
        if not end:
            end = datetime.date.today() + datetime.timedelta(days=1)

        return self.harvest._time_entries('%s/%d/' % (self.base_url, self.id),
                                          start, end)

    def expenses(self, start=None, end=None):
        """Return entries for a specific users
        
        Parameters start and end are date and should be optional 
        """
        if not start:
            start = datetime.date(1990, 01, 01)
        if not end:
            end = datetime.date.today() + datetime.timedelta(days=1)

        return self.harvest._expenses('%s/%d/' % (self.base_url, self.id),
                                          start, end)

    @property
    def client(self):
        """Return associated client
        """
        return self.harvest.client(self.client_id)

    @property
    def task_assignments(self):
        """Return all ... guest what ... task_assignments !
        """
        url = '%s/%d/task_assignments' % (self.base_url, self.id)
        for element in self.harvest.get_element_values(url, 'task-assignment'):
            yield TaskAssignment(self.harvest, element)

    @property
    def user_assignments(self):
        """Return all ... guest what ... user_assignments !
        """
        url = '%s/%d/user_assignments' % (self.base_url, self.id)
        for element in self.harvest.get_element_values(url, 'user-assignment'):
            yield UserAssignment(self.harvest, element)

class ExpenseCategory(HarvestItemBase):
    """Expense Category binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/expense_categories'
    element_name = 'expense_category'
    plural_name = 'expense_categories'

    def __str__(self):
        return 'ExpenseCategory: %s' % self.name

class Expense(HarvestItemBase):
    """Expense binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/expenses'
    element_name = 'expense'
    plural_name = 'expenses'


    @property
    def project(self):
        """Return all ... guest what ... the associated project !
        """
        return self.harvest.project(self.project_id)

    @property
    def expense_category(self):
        """Weird bug ...
        """
        if not hasattr(self, '_expense_category'):
            url = '%s/%s' % ('/expense_categories', self.expense_category_id)
            self._expense_category = self.harvest.get_element_values(
                url,'expense-category').next()
        return self._expense_category


    @property
    def user(self):
        """Return all ... guest what ... the associated user !
        """
        return self.harvest.user(self.user_id)

    @property
    def receipt(self):
        """Return attachement, if any
        """
        if self.has_receipt:
            url = self.receipt_url
            return self.harvest.get_raw_data(url)
        else:
            return None
        
    def __str__(self):
        return 'Expense: %s' % self.notes


class Client(HarvestItemBase):
    """Client binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/clients'
    element_name = 'client'
    plural_name = 'clients'

    @property
    def contacts(self):
        """Return all ... guest what ... associated contacts !
        """
        url = '%s/%d/contacts' % (self.base_url, self.id)
        for element in self.harvest.get_element_values(url, 'contact'):
            yield Contact(self.harvest, element)

    def invoices(self):
        """Return all ... guest what ... associated invoices !
        """
        url = '%s?client=%s' % (Invoice.base_url, self.id)
        for element in self.harvest.get_element_values(url, 
                                                       Invoice.element_name):
            yield Invoice(self.harvest, element)

    def __str__(self):
        return 'Client: ' + self.name


class Contact(HarvestItemBase):
    """Contact binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/contacts'
    element_name = 'contact'
    plural_name = 'contacts'

    @property
    def client(self):
        """Return all ... guest what ... client !
        """
        return self.harvest.client(self.client_id)

    def __str__(self):
        return 'Contact: %s %s' % (self.first_name, self.last_name)


class Task(HarvestItemBase):
    """Task binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/tasks'
    element_name = 'task'
    plural_name = 'tasks'

    def __str__(self):
        return 'Task: ' + self.name


class UserAssignment(HarvestItemBase):
    """User Assignement for Harvest
    """
    def __str__(self):
        return 'user %d for project %d' % (self.user_id, self.project_id)

    @property
    def project(self):
        """Return ... guest what ... associated project !
        """
        return self.harvest.project(self.project_id)

    @property
    def user(self):
        """Return ... guest what ... associated user !
        """
        return self.harvest.user(self.user_id)


class TaskAssignment(HarvestItemBase):
    """Task Assignement for Harvest
    """
    def __str__(self):
        return 'task %d for project %d' % (self.task_id, self.project_id)

    @property
    def project(self):
        """Return ... guest what ... associated project !
        """
        return self.harvest.project(self.project_id)

    @property
    def task(self):
        """Return ... guest what ... associated task !
        """
        return self.harvest.task(self.task_id)


class Entry(HarvestItemBase):
    """Project Entry for Harvest
    """
    def __str__(self):
        return '%0.02f hours for project %d' % (self.hours, self.project_id)

    @property
    def project(self):
        """Return ... guest what ... associated project !
        """
        return self.harvest.project(self.project_id)

    @property
    def task(self):
        """Return ... guest what ... associated task !
        """
        return self.harvest.task(self.task_id)


class Invoice(HarvestItemBase):
    """Invoice binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/invoices'
    element_name = 'invoice'
    plural_name = 'invoices'

    def __str__(self):
        return 'invoice %d for client %d' % (self.id, self.client_id)

    @property
    def client(self):
        """Return all ... guest what ... client !
        """
        return self.harvest.client(self.client_id)

    @property
    def csv_line_items(self):
        """Invoices from lists omit csv-line-items
        """
        if not hasattr(self, '_csv_line_items'):
            url = '%s/%s' % (self.base_url, self.id)
            self._csv_line_items = self.harvest.get_element_values(
                url, self.element_name).next().get('csv-line-items', '')
        return self._csv_line_items

    @csv_line_items.setter
    def csv_line_items(self, val):
        """Return csv line items
        """
        self._csv_line_items = val

    def line_items(self):
        """Return line_items
        Might be different from csv_line_items
        """
        import csv
        return csv.DictReader(self.csv_line_items.split('\n'))

class InvoiceItemCategory(HarvestItemBase):
    """Invoice item Cateogory binding for Harvest
    """
    __metaclass__ = HarvestItemGetterable

    base_url = '/invoice_item_categories'
    element_name = 'invoice_item_category'
    plural_name = 'invoice_item_categories'

    def __str__(self):
        return 'InvoiceItemCategory: %s' % (self.name)


class Harvest(object):
    """Global object that will map everything
    """
    def __init__(self, use_data=None, uri=None, email=None, password=None):
        """Wrapper to call the api

        use_data fetch credentials in /alkivi/.secureData
        you can pass uri and email directly if needed
        """

        if use_data:
            uri, email, password = self._fetch_secure_data(use_data)

        if not uri:
            raise Exception('You need an uri')
        if not email:
            raise Exception('You need an email')
        if not password:
            raise Exception('You need a password')

        self.uri = uri
        self.headers = {
            'Authorization':'Basic '+b64encode('%s:%s' % (email,password)),
            'Accept':'application/xml',
            'Content-Type':'application/xml',
            'User-Agent':'harvest.py',
        }

        # create getters
        for mcs in INSTANCE_CLASSES:
            self._create_getters(mcs)

    def _fetch_secure_data(self, use_data):
        """Extract credentials from a file
        """

        base = '/alkivi/.secureData/api_harvest/'
        credentials = base + use_data

        # Test file is ok
        import os
        if not os.path.exists(credentials):
            raise Exception(
                'Unable to fetch credentials.' +
                'Check that %s exists and is readable' % (credentials))

        # Open file
        f_handler = open(credentials)

        # Check syntax
        import re
        regexp = re.compile('^(.*?) (.*?) (.*?)$')
        for line in f_handler:
            match = regexp.search(line)
            if match:
                return match.groups()

        raise Exception('Unable to find good credentials in %s' % credentials)


    def _create_getters(self, klass):
        """
        This method creates both the singular and plural getters for various
        Harvest object classes.
        """
        flag_name = '_got_' + klass.element_name
        cache_name = '_' + klass.element_name

        setattr(self, cache_name, {})
        setattr(self, flag_name, False)

        cache = getattr(self, cache_name)

        def _get_item(id):
            if id in cache:
                return cache[id]
            else:
                url = '%s/%d' % (klass.base_url, id)
                item = self.get_element_values(url, klass.element_name).next()
                item = klass(self, item)
                cache[id] = item
                return item

        setattr(self, klass.element_name, _get_item)

        def _get_items():
            if getattr(self, flag_name):
                for item in cache.values():
                    yield item
            else:
                for element in self.get_element_values(
                    klass.base_url, klass.element_name):
                    item = klass(self, element)
                    cache[ item.id ] = item
                    yield item

                setattr(self, flag_name, True)

        setattr(self, klass.plural_name, _get_items)

    def find_user(self, first_name, last_name):
        """Return a person based on first_name and last_name
        """
        for person in self.users():
            if (first_name.lower() in person.first_name.lower()) and (
               last_name.lower() in person.last_name.lower()):
                return person

        return None

    def _time_entries(self, root, start, end):
        url = root + 'entries?from=%s&to=%s' % (start.strftime('%Y%m%d'), 
                                                end.strftime('%Y%m%d'))

        for element in self.get_element_values(url, 'day-entry'):
            yield Entry(self, element)

    def _expenses(self, root, start, end, closed=None, billed=None, unbilled=None):
        """Helper to get expenses from a specific object

        Parameters :
        start and end are datetime object
        close billed unbilled allow filtering
        """

        url = root + 'expenses?from=%s&to=%s' % (start.strftime('%Y%m%d'), 
                                                end.strftime('%Y%m%d'))

        for element in self.get_element_values(url, 'expense'):
            yield Expense(self, element)

    def _request(self, url, raw=False):
        """Perform low level request
        """
        if raw:
            final_url = url
        else:
            final_url = self.uri+url
        request = urllib2.Request(url=final_url, headers=self.headers)
        try:
            response = urllib2.urlopen(request)
            data = response.read()
            if raw:
                return data
            else:
                return parseString(data)
        except urllib2.URLError as exception:
            raise HarvestConnectionError(exception)

    def get_raw_data(self, url):
        return self._request(url, True)


    def get_element_values(self, url, tagname):
        """Parse returned xml and extract data
        """
        def get_element(element):
            data = []
            for node in element.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    data.append(node.data)

            text = ''.join(data)
            try:
                entry_type = element.getAttribute('type')
                if entry_type == 'integer':
                    try:
                        return int(text)
                    except ValueError:
                        return 0
                elif entry_type in ('date','datetime'):
                    return parseDate(text)
                elif entry_type == 'boolean':
                    try:
                        return text.strip().lower() in ('true', '1')
                    except ValueError:
                        return False
                elif entry_type == 'decimal':
                    try:
                        return float(text)
                    except ValueError:
                        return 0.0
                else:
                    return text
            except:
                return text

        xml = self._request(url)
        for entry in xml.getElementsByTagName(tagname):
            value = {}
            for attr in entry.childNodes:
                if attr.nodeType == attr.ELEMENT_NODE:
                    tag = attr.tagName
                    value[tag] = get_element(attr)

            if value:
                yield value
