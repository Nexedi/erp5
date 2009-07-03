##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
  Tests accounting simulation rules and delivery builder.
This tests also do basic checks for XMLMatrix and Predicate matching the
way it is used in the invoice related simulation.
"""

# TODO : 
#   * test with a Person as destination_section
#   * test cancelling / deleting an invoice
#   * test payment rule & payment builder
#   * test simulation purge when Payment delivered or top level Order cancelled
#   * test removing cells for a line 
#

import unittest
import os
import random

import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList

from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG, INFO
from DateTime import DateTime


class PurchaseInvoiceTest:
  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_transaction_line_portal_type \
                     = "Sale Invoice Transaction Line"
  invoice_line_portal_type = "Invoice Line"
  invoice_cell_portal_type = "Invoice Cell"

class SaleInvoiceTest:
  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_transaction_line_portal_type \
                     = "Sale Invoice Transaction Line"
  invoice_line_portal_type = "Invoice Line"
  invoice_cell_portal_type = "Invoice Cell"


class TestAccountingRulesMixin:
  # define portal_types 
  account_module_portal_type           = "Account Module"
  accounting_module_portal_type        = "Accounting Module"
  product_module_portal_type           = "Product Module"
  currency_module_portal_type          = "Currency Module"
  organisation_portal_type             = "Organisation"
  account_portal_type                  = "Account"
  product_portal_type                  = "Product"
  currency_portal_type                 = "Currency"
  predicate_portal_type                = "Predicate"
  applied_rule_portal_type             = "Applied Rule"
  simulation_movement_portal_type      = "Simulation Movement"
  accounting_rule_cell_portal_type     = "Accounting Rule Cell"
  invoice_transaction_rule_portal_type \
                    = "Invoice Transaction Rule"
  
  payment_transaction_portal_type      = "Payment Transaction"

  def getBusinessTemplateList(self):
    """  Return the list of business templates. """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_accounting',
        'erp5_invoicing', 'erp5_simplified_invoicing')

  def getAccountModule(self):
    return getattr(self.getPortal(), 'account',
        getattr(self.getPortal(), 'account_module'))
  
  def getAccountingModule(self):
    return getattr(self.getPortal(), 'accounting',
        getattr(self.getPortal(), 'accounting_module'))

  def getProductModule(self):
    return getattr(self.getPortal(), 'product',
        getattr(self.getPortal(), 'product_module'))
  
  ## XXX move this to "Sequence class"
  def playSequence(self, sequence_string, quiet=0) :
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  
class TestAccountingRules(TestAccountingRulesMixin, ERP5TypeTestCase):
  """
  This should test the simulation tree and builds starting from the
  invoice.

  """
  RUN_ALL_TESTS = 1
  QUIET = 1
  
  def getTitle(self):
    return "Accounting Rules"
 
  def afterSetUp(self) :
    self.login()
    self.createCategories()
    self.validateRules()
    
  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager', 'Owner', 'Assignor'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)
  
  def createCategories(self) :
    """ create all categories that are needed for this test.
    It uses getCategoriesToCreate, so you should overload this method.
    """
    # create base categories
    for base_cat in self.getBaseCategoriesToCreate() :
      if not base_cat in self.getCategoryTool().objectIds() :
        self.getCategoryTool().newContent(
          portal_type = 'Base Category',
          id = base_cat)
    # create categories
    for cat_string in self.getCategoriesToCreate() :
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
            portal_type = 'Category',
            id = cat)
        else:
          path = getattr(path, cat)
    # check categories have been created
    for cat_string in self.getCategoriesToCreate() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)
    
  def getBaseCategoriesToCreate(self) :
    return ("hd_size", "cpu_freq")

  def getCategoriesToCreate(self):
    return (
      # regions for our organisations
      "region/europe/west/france",
      "region/africa",
      
      # those are mandatory for account, and accounting rules depends on
      # the account_type category. (ie payable, will create a Payment 
      # Transaction accordingly)
      "account_type/asset/cash",
      "account_type/asset/receivable/refundable_vat",
      "account_type/equity",
      "account_type/expense",
      "account_type/income",
      "account_type/liability/payable/collected_vat",
     
      # some products lines for our products
      "product_line/storever/notebook",
      "product_line/storever/barebone",
      "product_line/storever/openbrick",
      "product_line/not_used/not_matched",
      
      # some categories for variating our products
      "cpu_freq/1Ghz",
      "cpu_freq/2Ghz",
      "hd_size/60Go",
      "hd_size/120Go",
    )

  def stepTic(self, **kw):
    self.tic()

  def stepCreateInvoiceTransactionRule(self, sequence, **kw) :
    """ 
      Create some predicates in the Invoice Transaction Rule
    """
    invoice_transaction_rule = getattr(self.getRuleTool(),
            'default_invoice_transaction_rule')
    if invoice_transaction_rule.getValidationState() == 'validated':
      invoice_transaction_rule.invalidate()
      transaction.commit()

    # delete anything inside the rule first
    # clear the message queue, so that it does not contains unexistant paths
    self.tic()
    invoice_transaction_rule.deleteContent(
                [x for x in invoice_transaction_rule.objectIds()])
    self.assertEquals(len(invoice_transaction_rule.objectValues()), 0)
    transaction.commit()

    # and add new content, predicate product_line
    predicate_product_notebook = invoice_transaction_rule.newContent(
      id = 'product_notebook',
      title = 'Product Notebook',
      portal_type = self.predicate_portal_type,
      string_index = 'product',
      int_index = '1',
      membership_criterion_base_category_list = ['product_line',],
      membership_criterion_category_list = ['product_line/storever/notebook'],
    )
    predicate_product_barebone = invoice_transaction_rule.newContent(
      id = 'product_barebone',
      title = 'Product Barebone',
      portal_type = self.predicate_portal_type,
      string_index = 'product',
      int_index = '2',
      membership_criterion_base_category_list = ['product_line',],
      membership_criterion_category_list = ['product_line/storever/barebone'],
    )
    # ... and destination_region
    predicate_region_france = invoice_transaction_rule.newContent(
      id = 'region_france',
      title = 'Region France',
      portal_type = self.predicate_portal_type,
      string_index = 'region',
      int_index ='1',
      membership_criterion_base_category_list = ['destination_region',],
      membership_criterion_category_list =
                    ['destination_region/region/europe/west/france'],
    )
    predicate_region_africa = invoice_transaction_rule.newContent(
      id = 'region_africa',
      title = 'region_africa',
      portal_type = self.predicate_portal_type,
      string_index = 'region',
      int_index = '2',
      membership_criterion_base_category_list = ['destination_region',],
      membership_criterion_category_list = ['destination_region/region/africa'],
    )
    # sanity checks
    self.failUnless(predicate_product_notebook != None)
    self.failUnless(predicate_product_barebone != None)
    self.failUnless(predicate_region_france  != None)
    self.failUnless(predicate_region_africa  != None)
    predicate_list = invoice_transaction_rule.contentValues(
          filter = {'portal_type': self.predicate_portal_type})
    self.assertEqual(len(predicate_list), 4)
    sequence.edit(
      invoice_transaction_rule = invoice_transaction_rule,
      predicate_product_notebook = predicate_product_notebook,
      predicate_product_barebone = predicate_product_barebone,
      predicate_region_france  = predicate_region_france,
      predicate_region_africa  = predicate_region_africa,
    )
  
  def stepUpdateInvoiceTransactionRuleMatrix(self, sequence, **kw) :
    """Creates/updates the matrix of the sale invoice transaction rule """
    invoice_transaction_rule = sequence.get('invoice_transaction_rule')
    base_id = 'movement'
    kwd = {'base_id': base_id}
    
    # update the matrix, generates the accounting rule cells
    invoice_transaction_rule.edit()
    invoice_transaction_rule.updateMatrix()
    self.tic()
    
    # check the accounting rule cells inside the matrix
    cell_list = invoice_transaction_rule.contentValues(
                filter = {'portal_type':self.accounting_rule_cell_portal_type})
    self.assertEqual(len(cell_list), 4)

    # In the matrix, cells are named on the scheme :
    # ${base_id} + '_'.join(predicate_dimension ordered by int_index)
    product_notebook_region_france_cell = getattr(invoice_transaction_rule,
                                          '%s_0_0'%base_id, None)
    product_notebook_region_africa_cell = getattr(invoice_transaction_rule,
                                          '%s_0_1'%base_id, None)
    product_barebone_region_france_cell = getattr(invoice_transaction_rule,
                                          '%s_1_0'%base_id, None)
    product_barebone_region_africa_cell = getattr(invoice_transaction_rule,
                                          '%s_1_1'%base_id, None)
    
    self.failUnless(product_notebook_region_france_cell != None)
    self.failUnless(product_notebook_region_africa_cell != None)
    self.failUnless(product_barebone_region_france_cell != None)
    self.failUnless(product_barebone_region_africa_cell != None)

    sequence.edit(
      product_notebook_region_france_cell = product_notebook_region_france_cell,
      product_notebook_region_africa_cell = product_notebook_region_africa_cell,
      product_barebone_region_france_cell = product_barebone_region_france_cell,
      product_barebone_region_africa_cell = product_barebone_region_africa_cell,
    )
    
  def stepValidateInvoiceTransaction(self, sequence, **kw) :
    """validates the sale invoice transaction rule"""
    sequence.get('invoice_transaction_rule').validate()

  def stepCreateNotebookFranceCell(self, sequence, **kw):
    """ creates the content of product_notebook_region_france_cell """
    # create content in the notebook / france cell
    product_notebook_region_france_cell = sequence.get(
        'product_notebook_region_france_cell')
    product_notebook_region_france_cell_income = \
        product_notebook_region_france_cell.newContent(
            id = 'income',
            source = sequence.get('income').getRelativeUrl(),
            quantity = 1)
    product_notebook_region_france_cell_receivable = \
        product_notebook_region_france_cell.newContent(
            id = 'receivable',
            source = sequence.get('receivable').getRelativeUrl(),
            quantity = -1.196)
    product_notebook_region_france_cell_vat = \
        product_notebook_region_france_cell.newContent(
            id = 'collected_vat',
            source = sequence.get('collected_vat').getRelativeUrl(),
            quantity = 0.196)
    sequence.edit(
      invoice_transaction_rule_cell = product_notebook_region_france_cell,
      product_notebook_region_france_cell_income =
            product_notebook_region_france_cell_income,
      product_notebook_region_france_cell_receivable =
            product_notebook_region_france_cell_receivable,
      product_notebook_region_france_cell_vat =
            product_notebook_region_france_cell_vat,
    )
  
  def stepCreateBareboneFranceCell(self, sequence, **kw):
    """ creates the content of product_barebone_region_france_cell, 
      the same as product_notebook_region_france_cell, but the income
      account is differrent """
    # create content in the notebook / france cell
    product_barebone_region_france_cell = sequence.get(
        'product_barebone_region_france_cell')
    product_barebone_region_france_cell_income = \
        product_barebone_region_france_cell.newContent(
            id = 'income',
            source = sequence.get('income_barebone').getRelativeUrl(),
            quantity = 1)
    product_barebone_region_france_cell_receivable = \
        product_barebone_region_france_cell.newContent(
            id = 'receivable',
            source = sequence.get('receivable').getRelativeUrl(),
            quantity = -1.196)
    product_barebone_region_france_cell_vat = \
        product_barebone_region_france_cell.newContent(
            id = 'collected_vat',
            source = sequence.get('collected_vat').getRelativeUrl(),
            quantity = 0.196)
    sequence.edit(
      product_barebone_region_france_cell = product_barebone_region_france_cell,
      product_barebone_region_france_cell_income =\
                product_barebone_region_france_cell_income,
      product_barebone_region_france_cell_vat =\
                product_barebone_region_france_cell_vat,
      product_barebone_region_france_cell_receivable =\
                product_barebone_region_france_cell_receivable
    )
      
  
  def stepCreateAccounts(self, sequence, **kw):
    """
      Create an income, an payable and a collected_vat account
    """
    portal = self.getPortal()
    account_module = self.getAccountModule()
    if not hasattr(account_module, 'income') :
      income = account_module.newContent(
        id = "income",
        portal_type = self.account_portal_type,
        title = "Income Notebook",
        account_type = "income",
      )
      income = account_module.newContent(
        id = "income_barebone",
        portal_type = self.account_portal_type,
        title = "Income Barebone",
        account_type = "income",
      )
      receivable = account_module.newContent(
        id = "receivable",
        portal_type=self.account_portal_type,
        title = "Receivable",
        account_type = "asset/receivable",
      )
      collected_vat = account_module.newContent(
        id = "collected_vat",
        portal_type=self.account_portal_type,
        title = "Collected VAT",
        account_type = "liability/payable/collected_vat",
      )
    # store accounts in sequence object
    sequence.edit(
      income          = account_module.income,
      income_barebone = account_module.income_barebone,
      receivable      = account_module.receivable,
      collected_vat   = account_module.collected_vat,
    )
    
  def stepCreateEntities(self, sequence, **kw) :
    """ Create a vendor and a client organisation.
      The region of the client is the same as the region
      defined in the rule.
    """
    organisation_module = self.getOrganisationModule()
    if not hasattr(organisation_module, 'vendor') :
      vendor = organisation_module.newContent(
        portal_type = self.organisation_portal_type,
        id = "vendor",
        title = "Vendor",
        region = "europe/west/france",
      )
      self.assertNotEquals(vendor.getDefaultRegionValue(), None)
      client_fr = organisation_module.newContent(
        portal_type = self.organisation_portal_type,
        id = "client_fr",
        title = "French Client",
        region = "europe/west/france",
      )
      self.assertNotEquals(client_fr.getDefaultRegionValue(), None)
    sequence.edit(
      vendor      = organisation_module.vendor,
      client_fr   = organisation_module.client_fr,
      client      = organisation_module.client_fr,
    )
  
  def stepCreateProducts(self, sequence, **kw) :
    """
      Create 2 kind of products, a notebook (Varianted) 
      and a barebone not varianted.
    """
    product_module = self.getProductModule()
    if not hasattr(product_module, 'notebook') :
      # Create some products
      notebook = product_module.newContent(
        id = 'notebook',
        title = 'Notebook',
        portal_type = self.product_portal_type,
        product_line = 'storever/notebook',
        base_price = 3.0,
      )
      # sets some variation categories on the notebook product
      notebook.setVariationBaseCategoryList(["hd_size", "cpu_freq"])
      notebook.setVariationCategoryList([
        "cpu_freq/1Ghz",
        "cpu_freq/2Ghz",
        "hd_size/60Go",
        "hd_size/120Go",])
      
      barebone = product_module.newContent(
        id = 'barebone',
        title = 'Barebone',
        portal_type = self.product_portal_type,
        product_line = 'storever/barebone',
        base_price = 5.0,
      )
    sequence.edit(
      notebook = product_module.notebook,
      barebone = product_module.barebone,
      product_notebook = product_module.notebook,
      product_barebone = product_module.barebone,
    )
    
  def stepCreateCurrencies(self, sequence, **kw) :
    """
      Create EUR currency
    """
    currency_module = self.getCurrencyModule()
    if not hasattr(currency_module, 'EUR') :
      currency_module.newContent(
        id = 'EUR',
        title = 'Euro',
        portal_type = self.currency_portal_type,
        base_unit_quantity = .01,
      )
    sequence.edit(euro=currency_module.EUR, currency=currency_module.EUR)
    
  def stepCreatePaymentRule(self, **kw) :
    """ create a rule payment transaction generation """
    # XXX: for now there are no cells in payment rule, so nothing to do here
    # TODO
    
  def stepCreateEmptyInvoice(self, sequence, **kw) :
    """ Create an empty invoice that will be modified later """
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    currency = sequence.get('currency')
    
    empty_invoice = self.getAccountingModule().newContent(
                id = 'empty_invoice',
                portal_type = self.invoice_portal_type,
                resource = currency.getRelativeUrl(),
                stop_date = DateTime(2004, 01, 01),
                start_date = DateTime(2004, 01, 01),
                source_section = vendor.getRelativeUrl(),
                destination_section = client.getRelativeUrl(),
                created_by_builder = 1,
              )
    
    sequence.edit(
      simple_invoice = empty_invoice,
      invoice = empty_invoice,
    )
    
  def stepCreateSimpleInvoice(self, sequence, **kw) :
    """ creates a simple sale invoice for non varianted notebook product.
      The invoice is from `vendor` to `client_fr`, so the cell defined in
      stepUpdateInvoiceTransactionRuleMatrix should match. 
      This invoice containts one line, 10 notebook * 10 EUR, so total price
      is 100
    """
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    product_notebook = sequence.get('product_notebook')
    currency = sequence.get('currency')
    
    simple_invoice = self.getAccountingModule().newContent(
                id = 'simple_invoice',
                portal_type = self.invoice_portal_type,
                resource = currency.getRelativeUrl(),
                price_currency = currency.getRelativeUrl(),
                stop_date = DateTime(2004, 01, 01),
                start_date = DateTime(2004, 01, 01),
                source_section = vendor.getRelativeUrl(),
                destination_section = client.getRelativeUrl(),
                created_by_builder = 1,
              )
    
    invoice_line = simple_invoice.newContent(
      id = 'invoice_line',
      resource = product_notebook.getRelativeUrl(),
      quantity = 10,
      price = 10,
      portal_type = self.invoice_line_portal_type)

    self.assertEqual(invoice_line.getTotalPrice(), 100)
    
    sequence.edit(
      simple_invoice = simple_invoice,
      invoice = simple_invoice,
      invoice_line = invoice_line,
      invoice_lines = [invoice_line]
    )
  
  def stepCreateOtherSimpleInvoice(self, sequence, **kw) :
    """ creates a simple sale invoice for non varianted notebook product.
      It will contain one line that will later be changed.
    """
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    product_notebook = sequence.get('product_notebook')
    currency = sequence.get('currency')
    
    simple_invoice = self.getAccountingModule().newContent(
                id = 'other_simple_invoice',
                portal_type = self.invoice_portal_type,
                resource = currency.getRelativeUrl(),
                stop_date = DateTime(2004, 01, 01),
                start_date = DateTime(2004, 01, 01),
                source_section = vendor.getRelativeUrl(),
                destination_section = client.getRelativeUrl(),
                created_by_builder = 1,
              )
    
    invoice_line = simple_invoice.newContent(
      id = 'invoice_line',
      resource = product_notebook.getRelativeUrl(),
      quantity = 123,
      price = 456,
      portal_type = self.invoice_line_portal_type)

    sequence.edit(
      simple_invoice = simple_invoice,
      invoice = simple_invoice,
      invoice_line = invoice_line,
      invoice_lines = [invoice_line]
    )

  def stepAddInvoiceLine(self, sequence, **kw) :
    """ add an invoice line in the current invoice : 
      10 notebook * 10 EUR, so total price is 100
    """
    product_notebook = sequence.get('product_notebook')
    invoice = sequence.get('invoice')
    
    invoice_line = invoice.newContent(
      id = 'invoice_line_%s'%(int(random.random()*1000)),
      portal_type = self.invoice_line_portal_type)

    invoice_line.edit(
      resource = product_notebook.getRelativeUrl(),
      quantity = 10,
      price = 10
    )
    
    self.assertEqual(invoice_line.getTotalPrice(), 100)
    
    sequence.edit(
      invoice_line = invoice_line,
      invoice_lines = [invoice_line]
    )

  def stepEditInvoiceLine(self, sequence, **kw) :
    """ edit the invoice line : 
      10 notebook * 10 EUR, so total price is 100
    """
    invoice = sequence.get('invoice')
    invoice_line = sequence.get('invoice_line')
    invoice_line.edit(
      quantity = 10,
      price = 10)
    
    self.assertEqual(invoice_line.getTotalPrice(), 100)

   
  def stepDeleteInvoiceLine(self, sequence, **kw) :
    """ remove an invoice line from the invoice
    """
    invoice = sequence.get('invoice')
    invoice_line = sequence.get('invoice_line')
    invoice._delObject(invoice_line.getId())
    invoice.recursiveReindexObject()
 
  def stepUpdateAppliedRule(self, sequence, **kw) :
    """ update the applied rule for the invoice. In the UI, the call to
    updateAppliedRule is made in an interraction workflow when you edit
    an invoice or its content."""
    # edit is done through interaction workflow, so we just call 'edit'
    # on the invoice (but this is not necessary)
    invoice=sequence.get('invoice')
    invoice.edit()
    
  def stepCreateSimpleInvoiceTwoLines(self, sequence, **kw) :
    """ 
      similar to stepCreateSimpleInvoice, but replace 
      "10 notebook * 10 EUR, so total price is 100" by :
      "5 notebook * 10 EUR + 5 notebook * 10 EUR , so total price is 100"
    """
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    product_notebook = sequence.get('product_notebook')
    currency = sequence.get('currency')
    
    simple_invoice = self.getAccountingModule().newContent(
                id = 'simple_invoice_two_lines',
                portal_type = self.invoice_portal_type,
                resource = currency.getRelativeUrl(),
                stop_date = DateTime(2004, 01, 01),
                start_date = DateTime(2004, 01, 01),
                source_section = vendor.getRelativeUrl(),
                destination_section = client.getRelativeUrl(),
                created_by_builder = 1,
              )
    
    invoice_line1 = simple_invoice.newContent(
      id = 'invoice_line1',
      resource = product_notebook.getRelativeUrl(),
      quantity = 5,
      price = 10,
      portal_type = self.invoice_line_portal_type)
    invoice_line2 = simple_invoice.newContent(
      id = 'invoice_line2',
      REsource = product_notebook.getRelativeUrl(),
      quantity = 5,
      price = 10,
      portal_type = self.invoice_line_portal_type)

    self.assertEqual(invoice_line1.getTotalPrice()
            + invoice_line2.getTotalPrice(), 100)
    
    sequence.edit(
      simple_invoice = simple_invoice,
      invoice = simple_invoice,
      invoice_lines = [invoice_line1, invoice_line2]
    )

  def stepCreateSimpleInvoiceTwoCells(self, sequence, **kw) :
    """ 
      similar to stepCreateSimpleInvoiceTwoLines, but use two
      differents cells on the same line instead of two differents lines. 
    """
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    product_notebook = sequence.get('product_notebook')
    currency = sequence.get('currency')
    
    simple_invoice = self.getAccountingModule().newContent(
                id = 'simple_invoice_two_cells',
                portal_type = self.invoice_portal_type,
                resource = currency.getRelativeUrl(),
                stop_date = DateTime(2004, 01, 01),
                start_date = DateTime(2004, 01, 01),
                source_section = vendor.getRelativeUrl(),
                destination_section = client.getRelativeUrl(),
                created_by_builder = 1,
              )
    
    invoice_line = simple_invoice.newContent(
      id = 'invoice_line',
      resource = product_notebook.getRelativeUrl(),
      portal_type = self.invoice_line_portal_type)
      
    sequence.edit(
      simple_invoice = simple_invoice,
      invoice = simple_invoice,
      invoice_line = invoice_line,
      invoice_lines = [invoice_line]
    )
    self.stepAddCellsInInvoiceLine(sequence)

  def stepAddCellsInInvoiceLine(self, sequence, **kw):
    """ add 2 cells in the invoice line, same quantity as simple invoice
    """
    invoice_line = sequence.get('invoice_line')
    
    # initialy, the line must not contain cells
    self.assertEqual(len(invoice_line.objectIds()), 0)
    invoice_line._setVariationBaseCategoryList(['hd_size', 'cpu_freq'])
    invoice_line._setVariationCategoryList(
                    ['hd_size/60Go', 'hd_size/120Go', 'cpu_freq/1Ghz' ])
    base_id = 'movement'
    invoice_line.updateCellRange(base_id)
    cell_key_list = list(invoice_line.getCellKeyList(base_id = base_id))
    
    # this is probably not the easiest way to create cells ...
    price = 10
    quantity = 5
    for cell_key in cell_key_list:
      cell = invoice_line.newCell(base_id = base_id,
             portal_type = self.invoice_cell_portal_type, *cell_key)
      cell.edit(mapped_value_property_list = ['price','quantity'],
                price = price, quantity = quantity,
                predicate_category_list = cell_key,
                variation_category_list = cell_key)
    
    # getTotalPrice uses mysql, so we must make sure the invoice is cataloged
    # to have correct results
    invoice_line.getParentValue().recursiveImmediateReindexObject()
    self.assertEqual(invoice_line.getTotalPrice(), 100)
    self.assertEqual(invoice_line.getTotalQuantity(), 10)
    
    # then we must have 2 cells inside our line
    self.assertEqual(len(invoice_line.objectIds()), 2)

  def stepCreateMultiLineInvoice(self, sequence, **kw) :
    """ create an invoice with varianted products 
      The invoice is from `vendor` to `client_fr`, so the cell defined in
      This invoice containts two lines :
      10 notebook * 10 EUR, so total price is 100 
            (matched by product_notebook_region_france_cell)
      10 barebone * 100 EUR, so total price is 1000 
            (matched by product_notebook_region_france_cell)
      total price for the invoice is 100 + 1000
    """
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    product_notebook = sequence.get('product_notebook')
    product_barebone = sequence.get('product_barebone')
    currency = sequence.get('currency')
    
    multi_line_invoice = self.getAccountingModule().newContent(
                id = 'multi_line_invoice',
                portal_type = self.invoice_portal_type,
                resource = currency.getRelativeUrl(),
                price_currency = currency.getRelativeUrl(),
                stop_date = DateTime(2004, 01, 01),
                start_date = DateTime(2004, 01, 01),
                source_section = vendor.getRelativeUrl(),
                destination_section = client.getRelativeUrl(),
                created_by_builder = 1,
              )
    
    notebook_line = multi_line_invoice.newContent(
      portal_type = self.invoice_line_portal_type,
      id = 'notebook_line',
      resource = product_notebook.getRelativeUrl(),
      quantity = 10,
      price = 10)

    barebone_line = multi_line_invoice.newContent(
      portal_type = self.invoice_line_portal_type,
      id = 'barebone_line',
      resource = product_barebone.getRelativeUrl(),
      quantity = 10,
      price = 100)

    self.assertEqual( 10*10 + 10*100,
        notebook_line.getTotalPrice() + barebone_line.getTotalPrice())
    
    sequence.edit(
      multi_line_invoice = multi_line_invoice,
      invoice = multi_line_invoice,
      invoice_lines = [notebook_line, barebone_line],
    )
    
  def stepCheckAddPredicate(self, sequence, **kw) :
    invoice_transaction_rule = sequence.get('invoice_transaction_rule')
    # next, we add a predicate to see if it is still okay (3x2 cells)
    predicate_product3 = invoice_transaction_rule.newContent(
      id = 'product_3',
      title = 'product_3',
      portal_type = self.predicate_portal_type,
      string_index = 'product',
      int_index = '3',
      membership_criterion_base_category_list = ['product_line',],
      membership_criterion_category_list = ['product_line/storever/openbrick'],
    )
    invoice_transaction_rule.updateMatrix()
    self.tic()
    cell_list = invoice_transaction_rule.contentValues(
        filter = {'portal_type': self.accounting_rule_cell_portal_type})
    self.assertEqual(len(cell_list), 6)

  def stepCheckRemovePredicate(self, sequence, **kw) :
    invoice_transaction_rule = sequence.get('invoice_transaction_rule')
    self.tic() # make sure message queue is empty
    # then, we remove a predicate and check again (3x3 cells)
    invoice_transaction_rule.deleteContent(id = 'region_africa')
    invoice_transaction_rule.updateMatrix()
    cell_list = invoice_transaction_rule.contentValues(
                 filter = {'portal_type':self.accounting_rule_cell_portal_type})
    self.assertEqual(len(cell_list), 3)

  def stepCheckRestoreOriginalPredicates(self, sequence, **kw) :
    """ we put back the matrix in the original format (2x2 cells) """
    invoice_transaction_rule = sequence.get("invoice_transaction_rule")
    self.tic() # make sure message queue is empty
    invoice_transaction_rule.deleteContent(id='product_3')
    predicate_region_africa = invoice_transaction_rule.newContent(
      id = 'region_africa', title = 'Region Africa',
      portal_type = self.predicate_portal_type,
      string_index = 'region', int_index = '2',
      membership_criterion_base_category_list = ['destination_region',],
      membership_criterion_category_list = ['destination_region/region/africa'],
    )
    invoice_transaction_rule.updateMatrix()
    cell_list = invoice_transaction_rule.contentValues(
        filter = {'portal_type':self.accounting_rule_cell_portal_type})
    self.assertEqual(len(cell_list), 4)
   
  def stepCreateDummyInvoice(self, sequence, **kw) :
    """ Create a dummy invoice for temp movements """
    invoice = self.getAccountingModule().newContent(
                      id = "dummy_invoice",
                   )
    sequence.edit(invoice = invoice)
    
  def stepCreateMatchableInvoiceMovements(self, sequence, **kw) :
    """ Create a temp movement that will be matched by the
      default_invoice_transaction_rule """
    from Products.ERP5Type.Document import newTempMovement
    product_notebook_region_france_movement = newTempMovement(
      sequence.get('invoice'),
      'test1',
      resource = sequence.get('notebook').getRelativeUrl(),
      destination = sequence.get('client_fr').getRelativeUrl(),
    )
    product_barebone_region_france_movement = newTempMovement(
      sequence.get('invoice'),
      'test2',
      resource = sequence.get('barebone').getRelativeUrl(),
      destination = sequence.get('client_fr').getRelativeUrl(),
    )
    sequence.edit(
      product_notebook_region_france_movement =
                  product_notebook_region_france_movement ,
      product_barebone_region_france_movement =
                  product_barebone_region_france_movement ,
    )
  
  def stepCheckMatchableInvoiceMovements(self, sequence, **kw) :
    """ Check that we have a matching cell for the movement """
    invoice_transaction_rule = sequence.get("invoice_transaction_rule")
    product_barebone_region_france_movement  = sequence.get(
                          'product_barebone_region_france_movement')
    product_notebook_region_france_movement  = sequence.get(
                          'product_notebook_region_france_movement')
    
    # Make sure acquisition is working for destination_region
    self.assertEqual(
          product_barebone_region_france_movement.getDestinationRegion(),
          'region/europe/west/france')
    self.assertEqual(
          product_notebook_region_france_movement.getDestinationRegion(),
          'region/europe/west/france')
          
    # Make sure category is working for resource
    self.assertEqual(product_barebone_region_france_movement.getProductLine(),
            'storever/barebone')
    self.assertEqual(product_notebook_region_france_movement.getProductLine(),
            'storever/notebook')
    
    # check the predicates 
    predicate_product_notebook = sequence.get("predicate_product_notebook")
    predicate_product_barebone = sequence.get("predicate_product_barebone")
    predicate_region_france  = sequence.get("predicate_region_france")
    predicate_region_africa  = sequence.get("predicate_region_africa")
    
    self.assert_(not predicate_region_africa.test(
                      product_barebone_region_france_movement ))
    self.assert_( predicate_region_france.test(
                      product_barebone_region_france_movement ))
    self.assert_(not predicate_product_notebook.test(
                      product_barebone_region_france_movement ))
    self.assert_( predicate_product_barebone.test(
                      product_barebone_region_france_movement ))
    
    self.assert_(not predicate_region_africa.test(
                      product_notebook_region_france_movement ))
    self.assert_( predicate_region_france.test(
                      product_notebook_region_france_movement ))
    self.assert_(not predicate_product_barebone.test(
                      product_notebook_region_france_movement ))
    self.assert_( predicate_product_notebook.test(
                      product_notebook_region_france_movement ))
    
    # check the cells
    product_notebook_region_france_cell = sequence.get(
                     'product_notebook_region_france_cell')
    product_barebone_region_france_cell = sequence.get(
                     'product_barebone_region_france_cell')
    product_notebook_region_africa_cell = sequence.get(
                     'product_notebook_region_africa_cell')
    product_barebone_region_africa_cell = sequence.get(
                     'product_barebone_region_africa_cell')
    self.assert_(not product_notebook_region_france_cell.test(
                        product_barebone_region_france_movement ))
    self.assert_(    product_barebone_region_france_cell.test(
                        product_barebone_region_france_movement ))
    self.assert_(not product_notebook_region_africa_cell.test(
                        product_barebone_region_france_movement ))
    self.assert_(not product_barebone_region_africa_cell.test(
                        product_barebone_region_france_movement ))
    
    self.assert_(    product_notebook_region_france_cell.test(
                        product_notebook_region_france_movement ))
    self.assert_(not product_barebone_region_france_cell.test(
                        product_notebook_region_france_movement ))
    self.assert_(not product_notebook_region_africa_cell.test(
                        product_notebook_region_france_movement ))
    self.assert_(not product_barebone_region_africa_cell.test(
                        product_notebook_region_france_movement ))
    
    # finally check the matching cell is the good one
    self.assertEquals(product_notebook_region_france_cell,
              invoice_transaction_rule._getMatchingCell(
                product_notebook_region_france_movement ))
    self.assertEqual(product_barebone_region_france_cell,
              invoice_transaction_rule._getMatchingCell(
                product_barebone_region_france_movement ))
  
  def stepCreateNotMatchableInvoiceMovements(self, sequence, **kw) :
    """ create a temp movement that not any cell could match. """
    from Products.ERP5Type.Document import newTempMovement
    bad_movement1 = newTempMovement(
      sequence.get("invoice"),
      'test3',
      product = None,
      destination = sequence.get('client').getRelativeUrl(),
    )
    bad_movement2 = newTempMovement(
      sequence.get("invoice"),
      'test4',
      gap = 'gap/1',
      destination = sequence.get('client').getRelativeUrl(),
    )
    sequence.edit(
      bad_movement1 = bad_movement1,
      bad_movement2 = bad_movement2,
    )

  def stepCheckNotMatchableInvoiceMovements(self, sequence, **kw) :
    """ check that temp movement that cannot be matched is not matched. """
    invoice_transaction_rule = sequence.get('invoice_transaction_rule')
    self.assertEqual(None,
      invoice_transaction_rule._getMatchingCell(
        sequence.get('bad_movement1')))
    self.assertEqual(None,
      invoice_transaction_rule._getMatchingCell(
        sequence.get('bad_movement2')))

  def stepClearSimulation(self, sequence, **kw) :
    """ clear the content of portal_simulation """
    self.tic() # make sure message queue is empty
    self.getSimulationTool().deleteContent(
        list(self.getSimulationTool().objectIds()))
    
  def stepClearAccountingModule(self, sequence, **kw) :
    """ clear the content of accounting module """
    self.tic() # make sure message queue is empty
    # delete
    self.getAccountingModule().deleteContent(
        list(self.getAccountingModule().objectIds()))
    
  def stepCheckFirstRuleIsApplied(self, sequence, **kw) :
    """ check every level of the simulation """
    invoice = sequence.get('invoice')
    invoice_line = sequence.get('invoice_line')
    invoice_transaction_rule = sequence.get('invoice_transaction_rule')
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    currency = sequence.get('currency')
    invoice_transaction_rule_cell = sequence.get(
                                  'invoice_transaction_rule_cell')
    
    # content of the simulation tool is a list of invoice rules
    applied_rule_list = self.getSimulationTool().contentValues()
    
    self.assertEqual(len(applied_rule_list), 1)
    applied_rule = applied_rule_list[0]
    self.assertEqual( applied_rule.getPortalType(),
                      self.applied_rule_portal_type)
    self.assertEqual( applied_rule.getSpecialise(),
                      'portal_rules/default_invoice_rule')
    self.assertEqual( applied_rule.getCausality(),
                      invoice.getRelativeUrl())
    
    # inside the rule there are simulation movements
    simulation_movement_list = applied_rule.contentValues()
    # the first one is a mirror of the movement in the invoice line
    # this applied rule can also contain movement related to those
    # created in the init script, so we only take into account sim.
    # movement linked to an invoice line
    invoice_line_simulation_movement_list = []
    for simulation_movement in simulation_movement_list :
      self.assertNotEquals(simulation_movement.getOrderValue(), None)
      if simulation_movement.getOrderValue().getPortalType() == \
              self.invoice_line_portal_type :
        invoice_line_simulation_movement_list.append(simulation_movement)
    
    self.assertEqual( len(invoice_line_simulation_movement_list), 1)
    simulation_movement = invoice_line_simulation_movement_list[0]
    
    self.assertEqual( simulation_movement.getPortalType(),
                      self.simulation_movement_portal_type)
    self.assertEqual( invoice_line.getResource(),
                      simulation_movement.getResource())
    self.assertEqual( invoice_line.getQuantity(),
                      simulation_movement.getQuantity())
    self.assertEqual( invoice_line.getStopDate(),
                      simulation_movement.getStopDate())
    self.assertEqual( invoice_line.getStartDate(),
                      simulation_movement.getStartDate())
    self.assertEqual( invoice_line.getSourceSection(),
                      simulation_movement.getSourceSection())
    self.assertEqual( invoice_line.getDestinationSection(),
                      simulation_movement.getDestinationSection())
    self.assertEqual( invoice_line.getSource(),
                      simulation_movement.getSource())
    self.assertEqual( invoice_line.getDestination(),
                      simulation_movement.getDestination())
    
    # inside this movement there are applied rules which specialize
    # invoice_transaction_rule and trade_model_rule...
    applied_rule_list = simulation_movement.contentValues()
    self.assertEquals( len(applied_rule_list), 2)
    # ...but only invoice_transaction_rule is interesting
    applied_rule = [applied_rule for applied_rule in applied_rule_list if 
      applied_rule.getSpecialiseValue().getPortalType() == 
      'Invoice Transaction Rule'][0]
    self.assertEquals( applied_rule.getPortalType(),
                      self.applied_rule_portal_type)
    self.assertEquals( applied_rule.getSpecialise(),
                      invoice_transaction_rule.getRelativeUrl())
    
    # and in this applied rule, we got simulation movements, 
    # based on those inside product_notebook_region_france_cell
    simulation_movement_list = applied_rule.contentValues()
    self.assertEqual( len(simulation_movement_list), 3)
    rule_movement_found = {}
    for simulation_movement in simulation_movement_list :
      self.assertEquals( simulation_movement.getSourceSection(),
                        vendor.getRelativeUrl())
      self.assertEquals( simulation_movement.getDestinationSection(),
                        client.getRelativeUrl())
      self.assertEquals( simulation_movement.getResource(),
                        currency.getRelativeUrl())
      self.assertEquals( simulation_movement.getCausalityState(),
                         'expanded')
      for rule_movement in invoice_transaction_rule_cell.contentValues() :
        if simulation_movement.getSource() == rule_movement.getSource() :
          rule_movement_found[rule_movement.getSource()] = 1
          self.assertEquals(simulation_movement.getQuantity(),
                rule_movement.getQuantity() * invoice_line.getTotalPrice())
          self.assertEquals(simulation_movement.getSourceCredit(),
                rule_movement.getSourceCredit() * invoice_line.getTotalPrice())
          self.assertEquals(simulation_movement.getSourceDebit(),
                rule_movement.getSourceDebit() * invoice_line.getTotalPrice())
      self.assert_(len(rule_movement_found.keys()), 3)
    sequence.edit( simulation_movement_list = simulation_movement_list )

      
  def stepCollectSimulationMovements(self, sequence, **kw) :
    """ put some simulation movements in sequence for later checkings """
    invoice = sequence.get('invoice')
    invoice_line = sequence.get('invoice_line')
    
    applied_rule_list = self.getSimulationTool().contentValues()
    self.assertEquals(len(applied_rule_list), 1)
    simulation_movement_list = []
    simulation_movement_quantities = {}
    simulation_movement_resources = {}
    simulation_movement_paths = {}
    simulation_movement_section_paths = {}
    
    applied_rule = applied_rule_list[0]
    for invoice_simulation_movement in applied_rule.objectValues() :
      for invoice_transaction_applied_rule in \
                        invoice_simulation_movement.objectValues() :
        for simulation_movement in \
                   invoice_transaction_applied_rule.objectValues() :
          path = simulation_movement.getPath()
          simulation_movement_list.append(simulation_movement)
          simulation_movement_quantities[path] = \
                                    simulation_movement.getQuantity()
          simulation_movement_resources[path] = \
                                    simulation_movement.getResource()
          simulation_movement_paths[path] = (
                      simulation_movement.getSource(),
                      simulation_movement.getDestination())
          simulation_movement_section_paths[path] = (
                      simulation_movement.getSourceSection(),
                      simulation_movement.getDestinationSection())
    sequence.edit(
         simulation_movement_list = simulation_movement_list
      ,  simulation_movement_quantities = simulation_movement_quantities
      ,  simulation_movement_resources = simulation_movement_resources
      ,  simulation_movement_paths = simulation_movement_paths
      ,  simulation_movement_section_paths = simulation_movement_section_paths
    )

  def stepCheckSimulationMovements(self, sequence, **kw) :
    """ checks simulation movements from the sequence object """
    simulation_movement_list = sequence.get(
                                        'simulation_movement_list')
    simulation_movement_quantities = sequence.get(
                                  'simulation_movement_quantities')
    simulation_movement_resources = sequence.get(
                                   'simulation_movement_resources')
    simulation_movement_paths = sequence.get(
                                       'simulation_movement_paths')
    simulation_movement_section_paths = sequence.get(
                               'simulation_movement_section_paths')
    
    for simulation_movement in simulation_movement_list :
      path = simulation_movement.getPath()
      self.assertEquals(
        simulation_movement.getQuantity(),
        simulation_movement_quantities[path]
      )
      self.assertEquals(
        simulation_movement.getResource(),
        simulation_movement_resources[path]
      )
      self.assertEquals(
        (simulation_movement.getSource(), simulation_movement.getDestination()),
        simulation_movement_paths[path]
      )
      self.assertEquals(
           ( simulation_movement.getSourceSection(),
             simulation_movement.getDestinationSection()),
        simulation_movement_section_paths[path]
      )
  
  def stepCheckPaymentRuleIsApplied(self, sequence, **kw) :
    """ checks that a payment rule is applied for the total amount
      of receivable """
    # TODO
  
  def stepPlanInvoice(self, sequence, **kw) :
    """ put the invoice in the `planned` state, which will 
      start the simulation process. """
    invoice = sequence.get('invoice')
    self.getPortal().portal_workflow.doActionFor(
      invoice, 'plan_action',
      skip_period_validation=1
    )
    self.assertEquals(invoice.getSimulationState(), 'planned')

  def stepConfirmInvoice(self, sequence, **kw) :
    """ put the invoice in the `confirmed` state, which does nothing specific,
    the delivery builder is invoked when starting the invoice.
    """
    invoice = sequence.get('invoice')
    self.getPortal().portal_workflow.doActionFor(
      invoice, 'confirm_action',
      wf_id = 'accounting_workflow',
      skip_period_validation = 1
    )
    self.assertEquals(invoice.getSimulationState(), 'confirmed')
  
  def stepCheckNoAccountingLinesBuiltYet(self, sequence, **kw) :
    invoice = sequence.get('invoice')
    self.assertEquals(0, len(invoice.getMovementList(
                    portal_type=invoice.getPortalAccountingMovementTypeList())))
  
  def stepStartInvoice(self, sequence, **kw) :
    """ put the invoice in the `started` state, which starts the delivery
    builder.
    """
    invoice = sequence.get('invoice')
    self.getPortal().portal_workflow.doActionFor(
      invoice, 'start_action',
      wf_id = 'accounting_workflow',
      skip_period_validation = 1
    )
    self.assertEquals(invoice.getSimulationState(), 'started')


  def stepCheckAccountingLinesCoherantWithSimulation(self, sequence, **kw) :
    """ checks that accounting lines are created on the sale invoice 
    transaction """
    invoice  = sequence.get('invoice')
    vendor   = sequence.get('vendor')
    client   = sequence.get('client')
    currency = sequence.get('currency')
    invoice_line = sequence.get('invoice_line')
    simulation_movement_list = sequence.get('simulation_movement_list')
    invoice_transaction_rule_cell = sequence.get(
                          'invoice_transaction_rule_cell')
    invoice_transaction_line_list = invoice.contentValues(
        filter = {'portal_type':
                  self.invoice_transaction_line_portal_type})
    self.assertEquals( len(invoice_transaction_line_list),
                       len(simulation_movement_list))
    
    simulation_movement_found = {}
    for invoice_transaction_line in invoice_transaction_line_list :
      self.assertEquals( invoice_transaction_line.getSourceSection(),
                         vendor.getRelativeUrl())
      self.assertEquals( invoice_transaction_line.getDestinationSection(),
                         client.getRelativeUrl())
      self.assertEquals( invoice_transaction_line.getResource(),
                         currency.getRelativeUrl())
      for simulation_movement in simulation_movement_list :
        if simulation_movement.getSource() == \
                            invoice_transaction_line.getSource() :
          simulation_movement_found[simulation_movement.getSource()] = 1
          self.assertEquals(simulation_movement.getQuantity(),
                            invoice_transaction_line.getQuantity())
          self.assertEquals(simulation_movement.getSourceCredit(),
                            invoice_transaction_line.getSourceCredit())
          self.assertEquals(simulation_movement.getSourceDebit(),
                            invoice_transaction_line.getSourceDebit())

          self.assertEquals(simulation_movement.getDelivery(),
                            invoice_transaction_line.getRelativeUrl())
      self.assert_(len(simulation_movement_found.keys()), 3)
  
  
  def stepCheckAccountingLinesCreatedForSimpleInvoice(
            self, sequence, **kw) :
    """ Checks that accounting lines are created on the sale invoice 
    transaction and that all movement are correctly aggregated.
    The price of the invoice was 100, it should result in the following
    accounting layout :
    
      ===============   =======   =======
      account           Debit     Credit
      ===============   =======   =======
      income                       100
      collected_vat                 19.60
      receivable         119.60 
      ===============   =======   =======
    """
    invoice  = sequence.get('invoice')
    vendor   = sequence.get('vendor')
    client   = sequence.get('client')
    currency = sequence.get('currency')
    invoice_lines = sequence.get('invoice_lines')
    
    invoice_transaction_line_list = invoice.contentValues(
        filter = {'portal_type': self.invoice_transaction_line_portal_type})
    self.assertEquals(len(invoice_transaction_line_list), 3)
    
    accounting_lines_layout = {
      'income'            : (0, 100),
      'collected_vat'     : (0, 19.60),
      'receivable'        : (119.60, 0),
    }

    for invoice_transaction_line in invoice_transaction_line_list :
      self.assert_(
          invoice_transaction_line.getSourceId() in accounting_lines_layout.keys(),
          'unexepected source_id %s' % invoice_transaction_line.getSourceId())
      debit, credit = accounting_lines_layout[
                            invoice_transaction_line.getSourceId()]
      self.assertEquals(debit, invoice_transaction_line.getSourceDebit())
      self.assertEquals(credit, invoice_transaction_line.getSourceCredit())
      self.assertNotEquals(
              len(invoice_transaction_line.getDeliveryRelatedValueList(
                              portal_type='Simulation Movement')), 0)
      
  def stepCheckAccountingLinesCreatedForMultiLineInvoice(
            self, sequence, **kw) :
    """ Checks that accounting lines are created on the sale invoice 
    transaction and that all movement are correctly aggregated.
    The price of the invoice was 1100, it should result in the following
    accounting layout :
    
      ===============   =======   =======
      account           Debit     Credit
      ===============   =======   =======
      income                       100
      income_barebone              1000
      collected_vat                215.60
      receivable        1315.60 
      ===============   =======   =======
    """
    invoice  = sequence.get('invoice')
    vendor   = sequence.get('vendor')
    client   = sequence.get('client')
    currency = sequence.get('currency')
    invoice_lines = sequence.get('invoice_lines')
    
    invoice_transaction_line_list = invoice.contentValues(
        filter = {'portal_type': self.invoice_transaction_line_portal_type})
    self.assertEquals(len(invoice_transaction_line_list), 4)
    
    accounting_lines_layout = {
      'income'            : (0, 100),
      'income_barebone'   : (0, 1000),
      'collected_vat'     : (0, 215.60),
      'receivable'        : (1315.60, 0),
    }
  
    for invoice_transaction_line in invoice_transaction_line_list :
      debit, credit = accounting_lines_layout[
                                    invoice_transaction_line.getSourceId()]
      self.assertEquals(debit, invoice_transaction_line.getSourceDebit())
      self.assertEquals(credit, invoice_transaction_line.getSourceCredit())
      self.assertNotEquals(
              len(invoice_transaction_line.getDeliveryRelatedValueList(
                              portal_type='Simulation Movement')), 0)

  def stepRebuildAndCheckNothingIsCreated(self, sequence, **kw) :
    """ Calls the DeliveryBuilder again and checks that the accounting module
    remains unchanged.
    """
    accounting_transaction_count = len(self.getAccountingModule().objectIds())
    accounting_lines_dict = {}
    for transaction in self.getAccountingModule().objectValues():
      transaction_dict = {}
      for accounting_line in transaction.objectValues() :
        if accounting_line.getPortalType() != \
                          self.invoice_line_portal_type :
          transaction_dict[accounting_line.getId()] = \
                accounting_line.getTotalQuantity()
      accounting_lines_dict[transaction.getId()] = transaction_dict
    
    # reindex the simulation for testing purposes
    self.getSimulationTool().recursiveReindexObject()
    self.tic()
    delivery_tool = self.getPortal().portal_deliveries
    # and build again ...
    delivery_tool.sale_invoice_transaction_builder.build()
    if hasattr(delivery_tool, 'pay_sheet_transaction_builder') :
      # TODO: conflict with pay_sheet_transaction_builder must be tested too
      delivery_tool.pay_sheet_transaction_builder.build()
    self.tic()
    
    # nothing should have changed
    self.assertEquals(accounting_transaction_count,
            len(self.getAccountingModule().objectIds()))
      
    for transaction in self.getAccountingModule().objectValues() :
      transaction_dict = accounting_lines_dict[transaction.getId()]
      for accounting_line in transaction.objectValues() :
        if accounting_line.getPortalType() != \
                          self.invoice_line_portal_type :
          self.assertEquals(
              transaction_dict[accounting_line.getId()],
              accounting_line.getTotalQuantity())
    
  def stepCheckInvoiceSimulation(self, sequence=None, \
                                    sequence_list=None, **kw):
    invoice = sequence.get('invoice')

    applied_rule_list = invoice.getCausalityRelatedValueList(
      portal_type = self.applied_rule_portal_type,
        )

    self.assertEquals(
        1,
        len(applied_rule_list)
    )

    applied_rule = applied_rule_list[0]

    self.assertEquals(
      'portal_rules/default_invoice_rule',
      applied_rule.getSpecialise()
    )

    self.assertEquals(
      # reduntant?
      invoice.getRelativeUrl(),
      applied_rule.getCausality()
    )

    simulation_movement_list = applied_rule.objectValues()

    self.assertEquals(
        1,
        len(simulation_movement_list)
    )

    simulation_movement = simulation_movement_list[0]

    invoice_line = sequence.get('invoice_line')
    resource = sequence.get('product_notebook')
    vendor = sequence.get('vendor')
    client = sequence.get('client')
    currency = sequence.get('currency')

    self.assertEquals(
      resource.getRelativeUrl(),
      simulation_movement.getResource()
    )

    self.assertEquals(
      currency.getRelativeUrl(),
      simulation_movement.getPriceCurrency()
    )

    self.assertEquals(
      vendor.getRelativeUrl(),
      simulation_movement.getSourceSection()
    )

    self.assertEquals(
      client.getRelativeUrl(),
      simulation_movement.getDestinationSection()
    )

    self.assertEquals(
      invoice_line.getRelativeUrl(),
      simulation_movement.getOrder()
    )

    self.assertEquals(
      invoice_line.getRelativeUrl(),
      simulation_movement.getDelivery()
    )

    self.assertEquals(
      10,
      simulation_movement.getQuantity()
    )

    self.assertEquals(
      10,
      simulation_movement.getPrice()
    )
    
  def test_01_HasEverything(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ check necessary tools and modules are present. """
    if not run:
      return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ', INFO, 'testHasEverything')
    self.failUnless(self.getCategoryTool() != None)
    self.failUnless(self.getSimulationTool() != None)
    self.failUnless(self.getTypeTool() != None)
    self.failUnless(self.getSQLConnection() != None)
    self.failUnless(self.getCatalogTool() != None)
    self.failUnless(self.getRuleTool() != None)
    self.failUnless(self.getAccountModule() != None)
    self.failUnless(self.getAccountingModule() != None)
    self.failUnless(self.getOrganisationModule() != None)
    self.failUnless(self.getProductModule() != None)
    self.failUnless(self.getCurrencyModule() != None)

  def test_02_UpdateInvoiceTransactionRuleMatrix(self, quiet=QUIET,
                                              run=RUN_ALL_TESTS):
    """ test edition of matrix and rule.
    Try to update the matrix after adding some predicates, 
    and check if all objects were created
    """
    if not run:
      return
    if not quiet:
      message = 'Test Update Invoice Transaction Rule Matrix'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)
    
    self.playSequence("""
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepTic
      stepCheckAddPredicate
      stepTic
      stepCheckRemovePredicate
      stepTic
      stepCheckRestoreOriginalPredicates
    """, quiet=quiet)

  def test_03_invoiceTransactionRule_getMatchingCell(self,
                                    quiet=QUIET, run=RUN_ALL_TESTS):
    """ test predicates for the cells of invoice transaction rule
    """
    if not run:
      return
    if not quiet:
      message = 'Test Invoice Transaction Rule getMatchingCell '
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)
    
    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepTic
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateProducts
      stepTic
      stepCreateDummyInvoice
      stepCreateMatchableInvoiceMovements
      stepCheckMatchableInvoiceMovements
      stepCreateNotMatchableInvoiceMovements
      stepCheckNotMatchableInvoiceMovements
    """, quiet=quiet)
  
  def test_04_SimpleInvoice(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ Simple Invoice.
    Try to expand an invoice containing only one simple Invoice Line.
    Check that the build is correct.
    """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateSimpleInvoice
      stepPlanInvoice
      stepTic
      stepCheckFirstRuleIsApplied 
      stepCheckPaymentRuleIsApplied
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCoherantWithSimulation
      """, quiet=quiet )

  def test_04b_SimpleInvoiceConfirm(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """  Same test as SimpleInvoice but directly confirm the invoice
    without planning it """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (without plan)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateSimpleInvoice
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )
  
  def test_04c_SimpleInvoiceTwoLines(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ Simple Invoice, 2 lines.
    Same test as SimpleInvoice but use 2 lines of quantity 5 instead of
    1 line of quantity 10.
    """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (with 2 lines)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateSimpleInvoiceTwoLines
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )
      
  def test_04d_SimpleInvoiceTwoCells(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ Simple Invoice, 2 cells.
    Same test as SimpleInvoice but use 2 cells of quantity 5 instead of
    1 line of quantity 10.
    """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (with 2 cells)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateSimpleInvoiceTwoCells
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )
   
  # next 5 tests will check update of applied rules. 
  def test_05a_SimpleInvoiceReExpandAddLine(self, quiet=QUIET,
        run=RUN_ALL_TESTS):
    """ Add a new line then updateAppliedRule.
    Create an empty invoice, plan, add a line so that this
    invoice is the same as `SimpleInvoice`, confirm it then check
    accounting lines
    """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (add invoice line and reexpand)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateEmptyInvoice
      stepPlanInvoice
      stepTic
      stepAddInvoiceLine
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )
      
  def test_05b_SimpleInvoiceReExpandEditLine(self, quiet=QUIET,
              run = RUN_ALL_TESTS):
    """ Tests that editing a line updates simulation correctly """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (edit line and reexpand)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateOtherSimpleInvoice
      stepPlanInvoice
      stepTic
      stepEditInvoiceLine
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )

  def test_05c_SimpleInvoiceReExpandDeleteLine(
                        self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ Tests that removing a line updates simulation correctly """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (delete line and reexpand)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateSimpleInvoice
      stepAddInvoiceLine
      stepPlanInvoice
      stepTic
      stepDeleteInvoiceLine
      stepTic
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )
      
  def test_05d_SimpleInvoiceReExpandCreateCell(self, quiet=QUIET,
                  run=RUN_ALL_TESTS):
    """ Tests that replacing a line by cells updates simulation correctly """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (add cells in a line and reexpand)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateOtherSimpleInvoice
      stepPlanInvoice
      stepTic
      stepAddCellsInInvoiceLine
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet)
                     
  def test_05e_SimpleInvoiceExpandManyTimes(
                                self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ Tests that updating an applied rule many times doesn't break the
    build """
    if not run:
      return
    if not quiet:
      message = 'Test Simple Invoice Rule (many updateAppliedRule)'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepCreateNotebookFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateSimpleInvoice 
      stepPlanInvoice
      stepTic """ +
      ("""
      stepEditInvoiceLine
      stepUpdateAppliedRule
      stepTic""" * 4) +
      """
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForSimpleInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )

  def test_06_MultiLineInvoice(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ Multiple lines invoice.
    Try to expand an invoice containing multiples Invoice Line.
    Check that the build is correct, ie similar movements are aggregated.
    """
    if not run:
      return
    if not quiet:
      message = 'Test Multi Line Invoice Rule'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', INFO, message)

    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepTic
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepTic
      stepCreateNotebookFranceCell
      stepCreateBareboneFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateMultiLineInvoice
      stepPlanInvoice
      stepConfirmInvoice
      stepTic
      stepCheckNoAccountingLinesBuiltYet
      stepStartInvoice
      stepTic
      stepCheckAccountingLinesCreatedForMultiLineInvoice
      stepRebuildAndCheckNothingIsCreated
      """, quiet=quiet )
    
  def TODO_test_07_PaymentRuleForInvoice(self, quiet=QUIET, run=RUN_ALL_TESTS):
    """ Payment Rule.
      checks the payment rule is applied on invoice simulation
      movement. """
    # checks :
    #   date from trade condition
    #   quantity from sum of receivable movement
    #   link to sale invoice
 
  def test_planning_invoice_creates_simulation(self, quiet=QUIET):
    # http://mail.nexedi.com/pipermail/erp5-dev/2008-June/001969.html
    self.playSequence("""
      stepCreateAccounts
      stepCreateEntities
      stepCreateCurrencies
      stepCreateProducts
      stepCreateInvoiceTransactionRule
      stepTic
      stepUpdateInvoiceTransactionRuleMatrix
      stepValidateInvoiceTransaction
      stepTic
      stepCreateNotebookFranceCell
      stepCreateBareboneFranceCell
      stepTic
      stepClearSimulation
      stepClearAccountingModule
      stepCreateSimpleInvoice
      stepTic
      stepPlanInvoice
      stepTic
      stepCheckInvoiceSimulation
      """, quiet=quiet)

class TestSaleAccountingRules(SaleInvoiceTest, TestAccountingRules):
  pass


class TestPurchaseAccountingRules(PurchaseInvoiceTest, TestAccountingRules):
  # XXX this test is not really complete, originally we were testing Sale only,
  # so the test steps just test that source is correct, and not the
  # destination. For now it just tests that workflows for Purchase invokes
  # building correctly ...
  pass


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSaleAccountingRules))
  suite.addTest(unittest.makeSuite(TestPurchaseAccountingRules))
  return suite
