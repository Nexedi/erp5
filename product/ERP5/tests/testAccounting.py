#############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

"""
  Tests some functionnalities of accounting.

"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from testPackingList import TestPackingListMixin
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList

class TestAccounting(ERP5TypeTestCase):
  """Test Accounting. """
  
  def getAccountingModule(self):
    return getattr(self.getPortal(), 'accounting_module',
           getattr(self.getPortal(), 'accounting', None))
  
  def getAccountModule(self) :
    return getattr(self.getPortal(), 'account_module',
           getattr(self.getPortal(), 'account', None))
  
  # XXX
  def playSequence(self, sequence_string) :
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
 
  RUN_ALL_TESTS = 1

  account_portal_type           = 'Account'
  currency_portal_type          = 'Currency'
  organisation_portal_type      = 'Organisation'
  sale_invoice_portal_type      = 'Sale Invoice Transaction'
  sale_invoice_line_portal_type = 'Sale Invoice Line' 
  sale_invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'
  sale_invoice_cell_portal_type = 'Invoice Cell'
  purchase_invoice_portal_type      = 'Purchase Invoice Transaction'
  purchase_invoice_line_portal_type = 'Purchase Invoice Line' 
  purchase_invoice_transaction_line_portal_type = \
                'Purchase Invoice Transaction Line'
  purchase_invoice_cell_portal_type = 'Invoice Cell'

  def getTitle(self):
    return "Accounting"
  
  def login(self) :
    """sets the security manager"""
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Member', 'Assignee', 'Assignor',
                               'Auditor', 'Author', 'Manager'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)
  
  def createCategories(self):
    """Create the categories for our test. """
    TestPackingListMixin.createCategories(self)
    # create categories
    for cat_string in self.getNeededCategoryList() :
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
            portal_type = 'Category',
            id = cat,
            immediate_reindex = 1 )
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)
                
  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('group/client', 'group/vendor' )
  
  def getBusinessTemplateList(self):
    """ """
    return ('erp5_pdm', 'erp5_trade', 'erp5_accounting',)

  def stepTic(self, **kw):
    self.tic()

  def stepCreateEntities(self, sequence, **kw) :
    """Create a vendor and a client. """
    client = self.getOrganisationModule().newContent(
        portal_type = self.organisation_portal_type,
        group = "group/client",
        price_currency = "currency_module/USD")
    vendor = self.getOrganisationModule().newContent(
        portal_type = self.organisation_portal_type,
        group = "group/vendor",
        price_currency = "currency_module/EUR")
    sequence.edit( client = client, vendor = vendor)
  
  def stepCreateCurrencies(self, sequence, **kw) :
    """Create a some currencies. """
    EUR = self.getCurrencyModule().newContent(
          portal_type = self.currency_portal_type,
          reference = "EUR",
          id = "EUR" )
    USD = self.getCurrencyModule().newContent(
          portal_type = self.currency_portal_type,
          reference = "USD",
          id = "USD" )
    YEN = self.getCurrencyModule().newContent(
          portal_type = self.currency_portal_type,
          reference = "YEN",
          id = "YEN" )
    sequence.edit( EUR = EUR, USD = USD, YEN = YEN )
  
  def stepCreateAccounts(self, sequence, **kw) :
    """Create necessary accounts. """
    receivable = self.getAccountModule().newContent(
          title = 'receivable',
          portal_type = self.account_portal_type,
          account_type = 'asset/receivable' )
    payable = self.getAccountModule().newContent(
          title = 'payable',
          portal_type = self.account_portal_type,
          account_type = 'liability/payable' )
    expense = self.getAccountModule().newContent(
          title = 'expense',
          portal_type = self.account_portal_type,
          account_type = 'expense' )
    income = self.getAccountModule().newContent(
          title = 'income',
          portal_type = self.account_portal_type,
          account_type = 'income' )
    collected_vat = self.getAccountModule().newContent(
          title = 'collected_vat',
          portal_type = self.account_portal_type,
          account_type = 'liability/payable/collected_vat' )
    refundable_vat = self.getAccountModule().newContent(
          title = 'refundable_vat',
          portal_type = self.account_portal_type,
          account_type = 'asset/receivable/refundable_vat' )
    bank = self.getAccountModule().newContent(
          title = 'bank',
          portal_type = self.account_portal_type,
          account_type = 'asset/cash/bank')
    
    # set mirror accounts.
    receivable.setDestinationValue(payable)
    payable.setDestinationValue(receivable)
    expense.setDestinationValue(income)
    income.setDestinationValue(expense)
    collected_vat.setDestinationValue(refundable_vat)
    refundable_vat.setDestinationValue(collected_vat)
    bank.setDestinationValue(bank)
    
    sequence.edit( receivable_account = receivable,
                   payable_account = payable,
                   expense_account = expense,
                   income_account = income,
                   collected_vat_account = collected_vat,
                   refundable_vat_account = refundable_vat,
                   bank = bank, )

  def getInvoicePropertyList(self):
    """Returns the list of properties for invoices, stored as 
      a list of dictionnaries. """
    # source currency is EUR
    # destination currency is USD
    return [
      # in currency of destination, converted for source
      { 'income' : -200,             'source_converted_income' : -180,
        'collected_vat' : -40,       'source_converted_collected_vat' : -36,
        'receivable' : 240,          'source_converted_receivable' : 216,
        'currency' : 'currency_module/USD' },
      
      # in currency of source, converted for destination
      { 'income' : -100,        'destination_converted_expense' : -200,
        'collected_vat' : 10,   'destination_converted_refundable_vat' : -100,
        'receivable' : 90,      'destination_converted_payable' : 100,
        'currency' : 'currency_module/EUR' },
      
      { 'income' : -100,        'destination_converted_expense' : -200,
        'collected_vat' : 10,   'destination_converted_refundable_vat' : -100,
        'receivable' : 90,      'destination_converted_payable' : 100,
        'currency' : 'currency_module/EUR' },
      
      # in an external currency, converted for both source and dest.
      { 'income' : -300,
                    'source_converted_income' : -200,
                    'destination_converted_expense' : -400,
        'collected_vat' : 40,
                    'source_converted_collected_vat' : 36,
                    'destination_converted_refundable_vat' : 50,
        'receivable' : 260,
                    'source_converted_receivable' : 164,
                    'destination_converted_payable': 350,
        'currency' : 'currency_module/YEN' },
      
      # currency of source, not converted for destination -> 0
      # FIXME: validation should be refused by accounting workflow ?
      { 'income' : -100,
        'collected_vat' : -20,
        'receivable' : 120,
        'currency' : 'currency_module/EUR' },
      
    ]
  
  def stepCreateInvoices(self, sequence, **kw) :
    """Create invoices with properties from getInvoicePropertyList. """
    invoice_prop_list = self.getInvoicePropertyList()
    invoice_list = []
    for invoice_prop in invoice_prop_list :
      invoice = self.getAccountingModule().newContent(
          portal_type = self.sale_invoice_portal_type,
          source_section_value = sequence.get('vendor'),
          source_value = sequence.get('vendor'),
          destination_section_value = sequence.get('client'),
          destination_value = sequence.get('client'),
          resource = invoice_prop['currency'],
          bypass_init_script = 0,
      )
      
      for line_type in ['income', 'receivable', 'collected_vat'] :
        source_account = sequence.get('%s_account' % line_type)
        line = invoice.newContent(
          portal_type = self.sale_invoice_transaction_line_portal_type,
          quantity = invoice_prop[line_type],
          source_value = source_account
        )
        source_converted = invoice_prop.get(
                          'source_converted_%s' % line_type, None)
        if source_converted is not None :
          line.setSourceTotalAssetPrice(source_converted)
        
        destination_account = source_account.getDestinationValue(
                                                portal_type = 'Account' )
        destination_converted = invoice_prop.get(
                          'destination_converted_%s' %
                          destination_account.getAccountTypeId(), None)
        if destination_converted is not None :
          line.setDestinationTotalAssetPrice(destination_converted)
 
      invoice_list.append(invoice)
    sequence.edit( invoice_list = invoice_list )
  
  def checkAccountBalanceInCurrency(self, section, currency,
                                          sequence, **kw) :
    """ Checks accounts balances in a given currency."""
    invoice_list = sequence.get('invoice_list')
    for account_type in [ 'income', 'receivable', 'collected_vat',
                          'expense', 'payable', 'refundable_vat' ] :
      account = sequence.get('%s_account' % account_type)
      calculated_balance = 0
      for invoice in invoice_list :
        for line in invoice.getMovementList():
          # source
          if line.getSourceValue() == account and\
             line.getResourceValue() == currency and\
             section == line.getSourceSectionValue() :
              calculated_balance += (
                    line.getSourceDebit() - line.getSourceCredit())
          # dest.
          elif line.getDestinationValue() == account and\
             line.getResourceValue() == currency and\
             section == line.getDestinationSectionValue() :
              calculated_balance += (
                    line.getDestinationDebit() - line.getDestinationCredit())
      
      self.assertEquals(calculated_balance,
          self.getPortal().portal_simulation.getInventory(
            node_uid = account.getUid(),
            section_uid = section.getUid(),
            # resource_uid = currency.getUid()   # FIXME: raises a KeyError in SQLCatalog.buildSQLQuery
            resource = currency.getRelativeUrl()
          ))
  
  def stepCheckAccountBalanceLocalCurrency(self, sequence, **kw) :
    """ Checks accounts balances in the organisation default currency."""
    for section in (sequence.get('vendor'), sequence.get('client')) :
      currency = section.getPriceCurrencyValue()
      self.checkAccountBalanceInCurrency(section, currency, sequence)
  
  def stepCheckAccountBalanceExternalCurrency(self, sequence, **kw) :
    """ Checks accounts balances in external currencies ."""
    for section in (sequence.get('vendor'), sequence.get('client')) :
      for currency in (sequence.get('USD'), sequence.get('YEN')) :
        self.checkAccountBalanceInCurrency(section, currency, sequence)
    
  def checkAccountBalanceInConvertedCurrency(self, section, sequence, **kw) :
    """ Checks accounts balances converted in section default currency."""
    invoice_list = sequence.get('invoice_list')
    for account_type in [ 'income', 'receivable', 'collected_vat',
                          'expense', 'payable', 'refundable_vat' ] :
      account = sequence.get('%s_account' % account_type)
      calculated_balance = 0
      for invoice in invoice_list :
        for line in invoice.getMovementList() :
          if line.getSourceValue() == account and \
             section == line.getSourceSectionValue() :
            calculated_balance += line.getSourceInventoriatedTotalAssetPrice()
          elif line.getDestinationValue() == account and\
               section == line.getDestinationSectionValue() :
            calculated_balance += \
                             line.getDestinationInventoriatedTotalAssetPrice()
      self.assertEquals(calculated_balance,
          self.getPortal().portal_simulation.getInventoryAssetPrice(
            node_uid = account.getUid(),
            section_uid = section.getUid(),
          ))
  
  def stepCheckAccountBalanceConvertedCurrency(self, sequence, **kw):
    """Checks accounts balances converted in the organisation default
    currency."""
    for section in (sequence.get('vendor'), sequence.get('client')) :
      self.checkAccountBalanceInConvertedCurrency(section, sequence)
    
  def test_MultiCurrencyInvoice(self, quiet=0, run=RUN_ALL_TESTS):
    """Basic test for multi currency accounting"""
    self.playSequence("""
      stepCreateCurrencies
      stepCreateEntities
      stepCreateAccounts
      stepCreateInvoices
      stepTic
      stepCheckAccountBalanceLocalCurrency
      stepCheckAccountBalanceExternalCurrency
      stepCheckAccountBalanceConvertedCurrency
    """)
    
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAccounting))
    return suite

