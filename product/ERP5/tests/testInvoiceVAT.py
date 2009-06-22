##############################################################################
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
  Tests VAT for invoices.
  
Warning: this tests an obsolete API; the test is disabled.
"""

import unittest
import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Testing.ZopeTestCase import _print
from DateTime import DateTime

class TestInvoiceVAT(ERP5TypeTestCase):
  """Test VAT for invoices.

  """
  
  RUN_ALL_TESTS = 1

  default_region = "europe/west/france"
  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  invoice_cell_portal_type = 'Invoice Cell'
  invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'

  def getTitle(self):
    return "Invoices and VAT"
  
  def afterSetUp(self):
    """set up """
    self.createCategories()
    self.login()
    self.validateRules()
  
  def _safeTic(self):
    """Like tic, but swallowing errors, usefull for teardown"""
    try:
      transaction.commit()
      self.tic()
    except RuntimeError:
      pass

  def beforeTearDown(self):
    """Clear everything for next test."""
    self._safeTic()
    for module in [ 'sale_packing_list_module',
                    'organisation_module',
                    'person_module',
                    'currency_module',
                    'product_module',
                    'portal_simulation' ]:
      folder = getattr(self.getPortal(), module, None)
      if folder:
        [x.unindexObject() for x in folder.objectValues()]
        self._safeTic()
        folder.manage_delObjects([x.getId() for x in folder.objectValues()])
    accounting_module = self.getPortal().accounting_module
    [x.cancel() for x in accounting_module.objectValues()]
    accounting_module.manage_delObjects([x.getId() for x in
                                         accounting_module.objectValues()])
    self._safeTic()
    # cancel remaining messages
    activity_tool = self.getPortal().portal_activities
    for message in activity_tool.getMessageList():
      activity_tool.manageCancel(message.object_path, message.method_id)
      _print('\nCancelling active message %s.%s()\n'
             % (message.object_path, message.method_id) )
    transaction.commit()

  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)
  
  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList() :
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
                    portal_type='Category',
                    id=cat,
                    immediate_reindex=1 )
        else:
          path = path[cat]
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)
                
  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return (  'account_type/asset' 
              'account_type/asset/cash',
              'account_type/asset/cash/bank',
              'account_type/asset/receivable',
              'account_type/asset/receivable/refundable_vat',
              'account_type/equity',
              'account_type/expense',
              'account_type/income',
              'account_type/liability',
              'account_type/liability/payable',
              'account_type/liability/payable/collected_vat',
              'region/%s' % self.default_region,
            )
  
  def getBusinessTemplateList(self):
    """ """
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_simplified_invoicing')
  
  def _makeAccount(self, **kw):
    """Creates an Account."""
    account = self.getPortal().account_module.newContent(
          portal_type='Account',
          **kw)
    transaction.commit()
    self.tic()
    return account

  def _makeOrganisation(self, **kw):
    """Creates an organisation."""
    org = self.getPortal().organisation_module.newContent(
          portal_type='Organisation',
          **kw)
    transaction.commit()
    self.tic()
    return org

  def _makeSalePackingList(self, **kw):
    """Creates a sale packing list."""
    spl = self.getPortal().sale_packing_list_module.newContent(
          portal_type='Sale Packing List',)
    spl.edit(**kw)
    transaction.commit()
    self.tic()
    return spl
  
  def _makeSaleInvoice(self, created_by_builder=0, **kw):
    """Creates a sale invoice."""
    sit = self.getPortal().accounting_module.newContent(
          portal_type='Sale Invoice Transaction',
          created_by_builder=created_by_builder)
    sit.edit(**kw)
    transaction.commit()
    self.tic()
    return sit

  def _makeCurrency(self, **kw):
    """Creates a currency."""
    currency = self.getCurrencyModule().newContent(
            portal_type = 'Currency', **kw)
    transaction.commit()
    self.tic()
    return currency
  
  def _makeResource(self, **kw):
    """Creates a resource."""
    resource = self.getPortal().product_module.newContent(
                      portal_type='Product', **kw)
    transaction.commit()
    self.tic()
    return resource

  def _makeSimpleInvoiceTransactionRule(self, resource, receivable_account,
                                        vat_account, income_account):
    """A simple invoice transaction rule, with only one accounting cell,

                          Debit        Credit
    receivable account     1.1
    vat account                          0.1
    income account                        1

    """
    itr = self.getPortal().portal_rules.default_invoice_transaction_rule
    itr.manage_delObjects([x for x in itr.objectIds()])
    pred = itr.newContent(portal_type='Predicate')
    pred.setStringIndex('product')
    pred.setIntIndex(1) # XXX is it usefull ?
    pred.setMembershipCriterionBaseCategoryList('resource')
    pred.setMembershipCriterionCategoryList(['resource/%s' %
                                             resource.getRelativeUrl()])
    transaction.commit()
    self.tic()
    itr.updateMatrix()

    cell_list = itr.getCellValueList(base_id='movement')
    self.assertEquals(len(cell_list), 1)
    cell = cell_list[0]
    cell.newContent(
              portal_type = 'Accounting Transaction Line',
              source_value = receivable_account,
              quantity=-1.1 )
    cell.newContent(
              portal_type = 'Accounting Transaction Line',
              source_value = vat_account,
              quantity=.1 )
    cell.newContent(
              portal_type = 'Accounting Transaction Line',
              source_value = income_account,
              quantity=1 )

  def _stopPackingList(self, packing_list):
    """Stop a packing list, this will trigger invoice generation with
    the builder.
    """
    packing_list.confirm()
    packing_list.setReady()
    packing_list.start()
    transaction.commit()
    self.tic()
    packing_list.stop()
    self.assertEquals(packing_list.getSimulationState(), 'stopped')
    transaction.commit()
    self.tic()
    
  def _makeOnePackingList(self):
    """Returns currency, resource, receivable_account, vat_account,
      income_account, section, mirror_section and packing_list.

      The packing list is ready to test.
    """
    currency = self._makeCurrency()
    resource = self._makeResource()
    receivable_account = self._makeAccount(
                    account_type='asset/receivable')
    self.assertNotEquals(receivable_account.getAccountTypeValue(), None)
    vat_account = self._makeAccount(
                    account_type='liability/payable/collected_vat')
    self.assertNotEquals(vat_account.getAccountTypeValue(), None)
    income_account = self._makeAccount(account_type='income')
    self.assertNotEquals(income_account.getAccountTypeValue(), None)

    self._makeSimpleInvoiceTransactionRule(
                        resource=resource,
                        receivable_account=receivable_account,
                        vat_account=vat_account,
                        income_account=income_account )

    section = self._makeOrganisation(title='Section')
    mirror_section = self._makeOrganisation(title='Mirror Section')
    packing_list = self._makeSalePackingList(
                                source_value=section,
                                source_section_value=section,
                                destination_value=mirror_section,
                                destination_section_value=mirror_section,
                                price_currency_value=currency,
                                start_date=DateTime())
    return (currency, resource, receivable_account, vat_account,
            income_account, section, mirror_section, packing_list)
  
  def _makeOneInvoice(self):
    """Returns currency, resource, receivable_account, vat_account,
      income_account, section, mirror_section and invoice

      The invoice is ready to test.
    """
    currency = self._makeCurrency()
    resource = self._makeResource()
    receivable_account = self._makeAccount(
                    account_type='asset/receivable')
    self.assertNotEquals(receivable_account.getAccountTypeValue(), None)
    vat_account = self._makeAccount(
                    account_type='liability/payable/collected_vat')
    self.assertNotEquals(vat_account.getAccountTypeValue(), None)
    income_account = self._makeAccount(account_type='income')
    self.assertNotEquals(income_account.getAccountTypeValue(), None)

    self._makeSimpleInvoiceTransactionRule(
                        resource=resource,
                        receivable_account=receivable_account,
                        vat_account=vat_account,
                        income_account=income_account )

    section = self._makeOrganisation(title='Section')
    mirror_section = self._makeOrganisation(title='Mirror Section')
    sale_invoice = self._makeSaleInvoice(
                                source_value=section,
                                source_section_value=section,
                                destination_value=mirror_section,
                                destination_section_value=mirror_section,
                                price_currency_value=currency,
                                created_by_builder=1, # XXX this prevent
                                                      # init scripts from
                                                      # creating lines
                                start_date=DateTime())
    return (currency, resource, receivable_account, vat_account,
            income_account, section, mirror_section, sale_invoice)
  
  def _checkInvoiceVAT(self, invoice, total_price, vat_ratio,
                    total_vat_amount):
    """Check the VAT for this invoice.
    This check will first check VAT on the invoice, then confirm the
    invoice, so that transaction lines are generated, and make sure
    values are still correct when read on the accounting lines rather
    than on the simulation. 

      o invoice: The Invoice object
      o total_price: The total price that this invoice is supposed to
          have (ie. the receivable quantity)
      o vat_ratio: The VAT ratio.
      o total_vat_amount: The value for the VAT.
    """
    # check vat informations
    vat_info = invoice.SaleInvoiceTransaction_getVAT()
    self.assertEquals(total_price, sum([line.getTotalPrice() for line in
                                        invoice.getMovementList()]))
    self.assertEquals(vat_info['total'], total_vat_amount)
    self.assertEquals(vat_info['ratio'], vat_ratio)
    
    # confirm the invoice, 
    invoice.confirm()
    transaction.commit()
    self.tic()
    # this will generate accounting lines
    self.assertNotEquals(len(invoice.getMovementList(
      portal_type=self.getPortal().getPortalAccountingMovementTypeList())), 0)
    # and vat information will still be OK
    vat_info = invoice.SaleInvoiceTransaction_getVAT()
    self.assertEquals(total_price, sum([line.getTotalPrice() for line in
                                        invoice.getMovementList()]))
    self.assertEquals(vat_info['total'], total_vat_amount)
    self.assertEquals(vat_info['ratio'], vat_ratio)


  # invoice without packing list related

  def test_SimpleInvoice(self, quiet=0, run=RUN_ALL_TESTS):
    """Test VAT for a simple invoice created directly. """
    ( currency, resource, receivable_account, vat_account,
      income_account, section, mirror_section, invoice
     ) = self._makeOneInvoice()
    
    # add lines in the invoice
    for i in (1, 2):
      line = invoice.newContent(
                    portal_type='Invoice Line',)
      line.edit(quantity=10,
                price=100,
                resource_value=resource )
    invoice.plan()
    transaction.commit();
    self.tic()

    # actual values on invoice line should be:
    total_price = 2 * 10 * 100
    vat_ratio = .1
    total_vat_amount = total_price * vat_ratio
    self._checkInvoiceVAT(invoice, total_price, vat_ratio,
                          total_vat_amount)
  
  def test_SimpleInvoiceEmptyLines(self, quiet=0, run=RUN_ALL_TESTS):
    """Test VAT for a simple invoice created directly; empty lines should not
    be a problem."""
    ( currency, resource, receivable_account, vat_account,
      income_account, section, mirror_section, invoice
     ) = self._makeOneInvoice()
    
    # add lines in the invoice
    for i in (1, 2):
      line = invoice.newContent(
                    portal_type='Invoice Line',)
      line.edit(quantity=10,
                price=100,
                resource_value=resource )
    invoice.plan()
    transaction.commit();
    self.tic()
    
    # actual values on invoice line should be:
    total_price = 2 * 10 * 100
    vat_ratio = .1
    total_vat_amount = total_price * vat_ratio
    self._checkInvoiceVAT(invoice, total_price, vat_ratio,
                          total_vat_amount)

    # same if we add an empty invoice line
    invoice.newContent(portal_type='Invoice Line')
    self._checkInvoiceVAT(invoice, total_price, vat_ratio,
                          total_vat_amount)
    # ... or an empty accouting line
    invoice.newContent(portal_type='Sale Invoice Transaction Line')
    self._checkInvoiceVAT(invoice, total_price, vat_ratio,
                          total_vat_amount)

  def TODOtest_SimpleInvoiceTwoResources(self, quiet=0, run=RUN_ALL_TESTS):
    """Test VAT, for two resources, where only one requires VAT """
    ( currency, resource, receivable_account, vat_account,
      income_account, section, mirror_section, invoice
     ) = self._makeOneInvoice()
    
    another_resource = self._makeResource(title='Another resource')

    # add lines in the invoice
    for res in (resource, another_resource):
      line = invoice.newContent(
                    portal_type='Invoice Line',)
      line.edit(quantity=10,
                price=100,
                resource_value=res )
    invoice.plan()
    transaction.commit();
    self.tic()

    # actual values on invoice line should be:
    total_price = 2 * 10 * 100
    vat_ratio = .1
    total_vat_amount = 10 * 100 * vat_ratio # only one line with VAT
    self._checkInvoiceVAT(invoice, total_price, vat_ratio,
                          total_vat_amount)

  # invoice from a packing list

  def test_InvoiceTwoLinesWithSameResource(self, quiet=0,
                                           run=RUN_ALL_TESTS):
    """Test VAT for an invoice that cames from a packing list with two
    lines of the same resource.
    """
    ( currency, resource, receivable_account, vat_account,
      income_account, section, mirror_section, packing_list
     ) = self._makeOnePackingList()
    
    # add lines in the packing list
    for i in (1, 2):
      line = packing_list.newContent(
                    portal_type='Sale Packing List Line',)
      line.edit(quantity=10,
                price=100,
                resource_value=resource )
    
    self._stopPackingList(packing_list)
    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type='Sale Invoice Transaction')
    self.assertNotEquals(invoice, None)

    # actual values on invoice line should be:
    total_price = 2 * 10 * 100
    vat_ratio = .1
    total_vat_amount = total_price * vat_ratio

    self._checkInvoiceVAT(invoice, total_price, vat_ratio,
                          total_vat_amount)
  
  def test_InvoiceTwoLinesWithSameResourceDifferentDate(self, quiet=0,
                                                   run=RUN_ALL_TESTS):
    """Test VAT for an invoice that cames from a packing list with two
    lines of the same resource, with different dates.
    """
    ( currency, resource, receivable_account, vat_account,
      income_account, section, mirror_section, packing_list
     ) = self._makeOnePackingList()
    
    date = DateTime()
    # add lines in the packing list
    for i in (1, 2):
      line = packing_list.newContent(
                    portal_type='Sale Packing List Line',)
      line.edit(quantity=10,
                price=100,
                date=date + i,
                resource_value=resource )
    
    self._stopPackingList(packing_list)
    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type='Sale Invoice Transaction')
    self.assertNotEquals(invoice, None)

    # actual values on invoice line should be:
    total_price = 2 * 10 * 100
    vat_ratio = .1
    total_vat_amount = total_price * vat_ratio
    
    self._checkInvoiceVAT(invoice, total_price, vat_ratio,
                          total_vat_amount)

def test_suite():
  suite = unittest.TestSuite()
  #suite.addTest(unittest.makeSuite(TestInvoiceVAT))
  return suite

