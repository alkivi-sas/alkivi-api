"""
OpenERP wrapper that use oerplib
"""

import oerplib
import json
import time
import hashlib
import os
import re

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append('/')

from alkivi.common import logger

class API:
    """Simple wrapper that use oerplib
    """

    def __init__(self, use_data,
                protocol='xmlrpc',
                port='8069',
                url='localhost',
                version='7.0' ):


        # Going to extract data from /alkivi/.secureData
        base = '/alkivi/.secureData/api_openerp/'
        credentials = base + use_data

        if not os.path.exists(credentials):
            raise Exception('Unable to fetch correct credentials. ' +
                            'Check that %s is readable' % (credentials))
        else:
            f_handler = open(credentials)

            # Check syntax
            regexp = re.compile('^(.*?):(.*?):(.*?)$')
            for line in f_handler:
                match = regexp.search(line)
                if match:
                    user, password, db_name = match.groups()
                    break

            f_handler.close()

        if not user or not password:
            raise Exception('Did not find credentials, bazinga')

        # First login and keep uid
        self.oerp = oerplib.OERP(url, protocol=protocol,
                                 port=port, version=version)
        self.user = self.oerp.login(user, password, db_name)

        # Create cache for product and taxes
        self.products_cache = {}
        self.taxes_cache ={}

    def execute(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.execute(*args, **kwargs)

    def get(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.get(*args, **kwargs)

    def read(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.read(*args, **kwargs)

    def search(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.search(*args, **kwargs)

    def create(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.create(*args, **kwargs)

    def write(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.write(*args, **kwargs)

    def write_record(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.write_record(*args, **kwargs)

    def unlink(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.unlink(*args, **kwargs)

    def unlink_record(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.unlink_record(*args, **kwargs)

    def exec_workflow(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.exec_workflow(*args, **kwargs)

    def browse(self, *args, **kwargs):
        """Wrapper for oerplib call
        """
        return self.oerp.browse(*args, **kwargs)

    def fetch_product(self, vat_index):
        """Fetch product object in openerp and store into cash to avoid repetition

        Fetch product with name Produits et Services %s (20 19,6 ...)
        """

        # Do we have cache ?
        if vat_index in self.products_cache:
            return self.products_cache[vat_index]

        # Fetch associated tax
        tax = self.fetch_tax(vat_index)

        if tax is None:
            text = '0'
        else:
            text = tax.amount * 100
            if text == int(text):
                text = '%2d' % int(text)
            else:
                text = '%2.1f' % text

        description = 'Produits et Services %s' % text
        description = ','.join(re.split('\.', description))

        search_args = [('name_template', 'ilike', description)]
        product_ids = self.search('product.product', search_args)

        if not product_ids:
            raise Exception('%s is missing in product.product' % description)
        elif len(product_ids) > 1:
            logger.warning('Got several ids', product_ids)
            raise Exception('More than one product %s' % description)

        product_id = product_ids[0]
        product = self.browse('product.product', product_id)

        # Update cache
        self.products_cache[vat_index] = product

        return product

    def fetch_tax(self, vat_index):
        """Fetch tax object in openerp and store into cash to avoid repetition

        default is fetch from openerp configuration
        other tax 19.6, 20, are fetch using ACH-20 ...
        0 mean no tax so return None
        """

        # No tax object when no tva
        if vat_index == '0':
            return None

        # Do we have cache ?
        if vat_index in self.taxes_cache:
            return self.taxes_cache[vat_index]

        # Fetch default value in openerp
        tax_id = None

        if vat_index == 'default':
            tax_ids = self.execute('ir.values', 'get_default', 'product.product', 'supplier_taxes_id', True, 1, False)
            tax_id = tax_ids[0]
        else:
            search_args = [('description', '=', 'ACH-%s' % vat_index)]
            tax_ids = self.search('account.tax', search_args)
            if not tax_ids:
                raise Exception('tax %s is missing in account.tax' % vat_index)
            elif len(tax_ids) > 1:
                logger.warning('Got several ids', tax_ids)
                raise Exception('More than one tax with description = %s' % vat_index)
            tax_id = tax_ids[0]


        # Check that configuration is correct
        if tax_id is None:
            raise Exception('We should have tax_id here')

        tax = self.browse('account.tax', tax_id)

        # Update cache
        self.taxes_cache[vat_index] = tax

        return tax

    def fetch_supplier(self, name):
        """Return openerp res.partner using name to search it

        First try exact name, if no match then like
        """

        search_args = [
                      ('name', '=', name),
                      ('supplier', '=', 1) ]
        supplier_ids = self.search('res.partner', search_args)
        if not supplier_ids:
            search_args = [
                          ('name', 'ilike', name),
                          ('supplier', '=', 1) ]
            supplier_ids = self.search('res.partner', search_args)

        if not supplier_ids:
            raise Exception('Supplier %s not found' % name)
        elif len(supplier_ids) > 1:
            raise Exception('Found multiple suppliers with name %s' % name)

        return self.browse('res.partner', supplier_ids[0])

    def fetch_customer(self, name):
        """Return openerp res.partner using name to search it

        First try exact name, if no match then like
        """

        search_args = [
                      ('name', '=', name),
                      ('customer', '=', 1) ]
        customer_ids = self.search('res.partner', search_args)
        if not customer_ids:
            search_args = [
                          ('name', 'ilike', name),
                          ('customer', '=', 1) ]
            customer_ids = self.search('res.partner', search_args)

        if not customer_ids:
            raise Exception('Supplier %s not found' % name)
        elif len(customer_ids) > 1:
            raise Exception('Found multiple customers with name %s' % name)

        return self.browse('res.partner', customer_ids[0])


    def create_invoice(self, invoice_data, lines_data, attachment_data=None, state='draft', tax_amount=None):
        """Global method that create an invoice and add lines to ir

        invoice_data : dict with  necessary information to create invoice
        lines_data : array with all lines data
        state : draft or open
        tax_check : TODO 
        """

        if not invoice_data:
            raise Exception('Missing invoice_data')
        if not lines_data:
            raise Exception('Missing lines_data')
        if state not in ('draft', 'open'):
            raise Exception('State %s is not valid' % state)

        # Create invoice
        logger.debug_debug('going to create invoice with', invoice_data)
        invoice_id = self.create('account.invoice', invoice_data)
        logger.debug_debug('created invoice %d' % invoice_id)

        # Create invoice_line
        for line_data in lines_data:
            line_data['invoice_id'] = invoice_id
            logger.debug_debug('going to create invoice_line with', line_data)
            invoice_line_id = self.create('account.invoice.line', line_data) 
            logger.debug_debug('created invoice.line %d' % invoice_line_id)

        # Compute taxes
        result = self.execute('account.invoice', 'button_reset_taxes', [invoice_id])
        if not result:
            raise Exception('Unable to compute taxes, WTF')

        # If tax_amount, check that taxes match
        if tax_amount:
            invoice = self.browse('account.invoice', invoice_id)
            tax_lines = invoice.tax_line

            # Check that we have only one tax line
            number_of_tax_lines = 0
            ok_tax_line = None

            for tax_line in tax_lines:
                ok_tax_line = tax_line
                number_of_tax_lines += 1
                logger.debug_debug('tax_line data', tax_line.__data__)

            if number_of_tax_lines == 0:
                raise Exception('No tax yet, we should have')

            if number_of_tax_lines != 1:
                raise Exception('Got multiple lines for tax, this is weird, should have only one line')
            else:
                # Fix amount, might be wrong usually one cents wrong
                if tax_line.amount != tax_amount:
                    message = 'Fix tax_line amount from %f to %f' % (tax_line.amount, tax_amount)
                    if abs(tax_line.amount - tax_amount) > 0.02:
                        logger.warning(message)
                    else:
                        logger.important(message)

                    tax_line.amount = tax_amount

                    # Update invoice : need to check parameters
                    self.write_record(tax_line)
                    logger.log('tax_line updated')


        if state == 'open':
            logger.debug_debug('going to execute workflow invoice_open')
            self.exec_workflow('account.invoice', 'invoice_open', invoice_id)

        if attachment_data:
            logger.debug_debug('going to attach some data to invoice')

            invoice = self.browse('account.invoice', invoice_id)
            attachment_data['res_id'] = invoice.id
            if invoice.number: 
                attachment_data['res_name'] = invoice.number

            attachment_id = self.create('ir.attachment', attachment_data)
            logger.debug_debug('attached file %s to invoice, id=%d' % (attachment_data['name'], attachment_id))

        return invoice_id


