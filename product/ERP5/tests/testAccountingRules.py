##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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



#
# Skeleton ZopeTestCase
#

#from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
import os
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
#from DateTime import DateTime
#from Acquisition import aq_base, aq_inner
from zLOG import LOG
#from Products.ERP5Type.DateUtils import addToDate
#import time
#from Products.ERP5Type import product_path
#from DateTime import DateTime

class TestAccountingRules(ERP5TypeTestCase):
  """
  This should test these functions :
  - in InvoiceRule.py :
    - expand
    - collectSimulationMovements

  - in InvoiceTransactionRule.py :
    - test
    - expand
    - newCellContent
    - updateMatrix
    - getCellByPredicate
  """

  # Different variables used for this test
  run_all_test = 1
  #source_company_id = 'Nexedi'
  #destination_company_id = 'Coramy'
  #component_id = 'brick'
  #sales_order_id = '1'
  #quantity = 10
  #base_price = 0.7832

  def getTitle(self):
    return "Accouting Rules"

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_accounting',)

  def getRuleTool(self):
    return getattr(self.getPortal(), 'portal_rules', None)

  def getAccountModule(self):
    return getattr(self.getPortal(), 'account', None)

  def getAccountingModule(self):
    return getattr(self.getPortal(), 'accounting', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def getProductModule(self):
    return getattr(self.getPortal(), 'product', None)

  def getCurrencyModule(self) :
    return getattr(self.getPortal(), 'currency', None)

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    # Must add some accounts, accounting transactions, products, etc.
    account_module = self.getAccountModule()
    self.accounting_module = self.getAccountingModule()
    self.currency_module = self.getCurrencyModule()
    organisation_module = self.getOrganisationModule()
    product_module = self.getProductModule()
    self.catalog_tool = self.getCatalogTool()
    self.category_tool = self.getCategoryTool()
    self.simulation_tool = self.getSimulationTool()
    # Create some currencies
    euro = self.currency_module.newContent(id='EUR', title='Euro', portal_type='Currency')
    # Create some accounts
    account_module.newContent(id='prestation_service', title='prestation_service', portal_type='Account')
    account_module.newContent(id='creance_client', title='creance_client', portal_type='Account')
    account_module.newContent(id='tva_collectee_196', title='tva_collectee_196', portal_type='Account')
    account_module.newContent(id='account1', title='Account1', portal_type='Account')
    account_module.newContent(id='account2', title='Account2', portal_type='Account')
    account_module.newContent(id='account3', title='Account3', portal_type='Account')
    account_module.newContent(id='account4', title='Account4', portal_type='Account')
    # Create some organisations
    organisation1 = organisation_module.newContent(id='nexedi', title='Nexedi', portal_type='Organisation')
    organisation1.newContent(id='default_address', portal_type='Address', region='europe/west/france')
    organisation2 = organisation_module.newContent(id='client1', title='Client1', portal_type='Organisation')
    organisation2.newContent(id='default_address', portal_type='Address', region='europe/west/france')
    # Create some products
    self.product1 = product_module.newContent(id='product1', title='Product1', product_line='storever/notebook', base_price=3.0)
    self.product2 = product_module.newContent(id='product2', title='Product2', product_line='storever/barebone', base_price=5.0)
    # Create some predicates in the Invoice Transaction Rule
    self.invoice_transaction_rule = getattr(self.getRuleTool(), 'default_invoice_transaction_rule')
    self.invoice_transaction_rule.deleteContent(self.invoice_transaction_rule.contentIds()) # delete anything inside the rule first

    self.predicate_product1 = self.invoice_transaction_rule.newContent(id='product_1', title='product_1', portal_type='Predicate Group', string_index='product', int_index='1', membership_criterion_base_category_list=['product_line',], membership_criterion_category_list=['product_line/storever/notebook'])
    self.predicate_product2 = self.invoice_transaction_rule.newContent(id='product_2', title='product_2', portal_type='Predicate Group', string_index='product', int_index='2', membership_criterion_base_category_list=['product_line',], membership_criterion_category_list=['product_line/storever/barebone'])
    self.predicate_region1 = self.invoice_transaction_rule.newContent(id='region_1', title='region_1', portal_type='Predicate Group', string_index='region', int_index='1', membership_criterion_base_category_list=['region',], membership_criterion_category_list=['region/europe/west/france'])
    self.predicate_region2 = self.invoice_transaction_rule.newContent(id='region_2', title='region_2', portal_type='Predicate Group', string_index='region', int_index='2', membership_criterion_base_category_list=['region',], membership_criterion_category_list=['region/africa'])
    # Create some invoices (now that there is nothing harmful inside the rule)
    self.invoice = self.accounting_module.newContent(id='invoice1', portal_type='Sale Invoice Transaction', destination='organisation/client1', destination_section='organisation/client1', resource='currency/EUR')
    invoice_line = self.invoice.newContent(id='1', portal_type='Invoice Line', resource='product/product1', quantity=7.0, price=11.0)

  def updateInvoiceTransactionRuleMatrix(self) :

    base_id = 'vat_per_region'
    kwd = {'base_id': base_id}

    # update the matrix, generates the accounting rule cells
    self.invoice_transaction_rule.recursiveImmediateReindexObject()
    self.invoice_transaction_rule.updateMatrix()
    # check the accounting rule cells inside the matrix
    cell_list = self.invoice_transaction_rule.contentValues(filter={'portal_type':'Accounting Rule Cell'})
    self.assertEqual(len(cell_list), 4)

    self.product1_region1_cell = getattr(self.invoice_transaction_rule, 'vat_per_region_0_0', None)
    self.product1_region2_cell = getattr(self.invoice_transaction_rule, 'vat_per_region_0_1', None)
    self.product2_region1_cell = getattr(self.invoice_transaction_rule, 'vat_per_region_1_0', None)
    self.product2_region2_cell = getattr(self.invoice_transaction_rule, 'vat_per_region_1_1', None)

    self.failUnless(self.product1_region1_cell != None)
    self.failUnless(self.product1_region2_cell != None)
    self.failUnless(self.product2_region1_cell != None)
    self.failUnless(self.product2_region2_cell != None)

    self.product1_region1_line1 = getattr(self.product1_region1_cell, 'income', None)
    self.failUnless(self.product1_region1_line1 != None)
    self.product1_region1_line1.edit(title='income', source='account/account1', destination='account/account2', quantity=19.0)

  def test_01_HasEverything(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoryTool() != None)
    self.failUnless(self.getSimulationTool() != None)
    self.failUnless(self.getTypeTool() != None)
    self.failUnless(self.getSqlConnection() != None)
    self.failUnless(self.getCatalogTool() != None)
    self.failUnless(self.getRuleTool() != None)
    self.failUnless(self.getAccountModule() != None)
    self.failUnless(self.getAccountingModule() != None)
    self.failUnless(self.getOrganisationModule() != None)
    self.failUnless(self.getProductModule() != None)
    self.failUnless(self.getCurrencyModule() != None)

  def test_02_UpdateInvoiceTransactionRuleMatrix(self, quiet=0, run=run_all_test):
    """
    Try to update the matrix after adding some predicates, and check if all objects were created
    """
    if not run: return
    if not quiet:
      message = 'Test Update Invoice Transaction Rule Matrix'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    # before the tests, we need to be sure we have four predicates
    self.failUnless(self.predicate_product1 != None)
    self.failUnless(self.predicate_product2 != None)
    self.failUnless(self.predicate_region1 != None)
    self.failUnless(self.predicate_region2 != None)
    predicate_list = self.invoice_transaction_rule.contentValues(filter={'portal_type':'Predicate Group'})
    self.assertEqual(len(predicate_list), 4)

    # first, we check the matrix was initialized correctly (2x2 cells)
    self.updateInvoiceTransactionRuleMatrix()
    cell_list = self.invoice_transaction_rule.contentValues(filter={'portal_type':'Accounting Rule Cell'})
    self.assertEqual(len(cell_list), 4)

    # next, we add a predicate to see if it is still okay (3x2 cells)
    self.predicate_product3 = self.invoice_transaction_rule.newContent(id='product_3', title='product_3', portal_type='Predicate Group', string_index='product', int_index='3', membership_criterion_base_category_list=['product_line',], membership_criterion_category_list=['product_line/storever/openbrick'], immediate_reindex=1)
    self.invoice_transaction_rule.updateMatrix()
    cell_list = self.invoice_transaction_rule.contentValues(filter={'portal_type':'Accounting Rule Cell'})
    self.assertEqual(len(cell_list), 6)

    # then, we remove a predicate and check again (3x1 cells)
    self.invoice_transaction_rule.deleteContent(id='region_2')
    self.invoice_transaction_rule.updateMatrix()
    cell_list = self.invoice_transaction_rule.contentValues(filter={'portal_type':'Accounting Rule Cell'})
    self.assertEqual(len(cell_list), 3)

  def test_03_invoiceTransactionRule_getCellByPredicate(self, quiet=0, run=run_all_test):
    """
    test InvoiceTransactionRule.getCellByPredicate()
    """
    if not run: return
    if not quiet:
      message = 'Test Invoice Transaction Rule getCellByPredicate '
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    # before the tests, we must update the matrix
    self.updateInvoiceTransactionRuleMatrix()
    # define objects
    france = self.category_tool.restrictedTraverse('region/europe/west/france')
    notebook = self.category_tool.restrictedTraverse('product_line/storever/notebook')
    erp5 = self.category_tool.restrictedTraverse('product_line/erp5')
    pcg = self.category_tool.restrictedTraverse('pcg/1')
    # correct cell
    kw = (('product', notebook), ('region', france), )
    self.assertEqual(self.product1_region1_cell, self.invoice_transaction_rule.getCellByPredicate(*kw))
    # no predicate for this category
    kw = (('product', erp5), ('region', france), )
    self.assertEqual(None, self.invoice_transaction_rule.getCellByPredicate(*kw))
    # incorrect category
    kw = (('product', None), ('region', france), )
    self.assertEqual(None, self.invoice_transaction_rule.getCellByPredicate(*kw))
    # incorrect dimension
    kw = (('pcg', pcg), ('region', france), )
    self.assertEqual(None, self.invoice_transaction_rule.getCellByPredicate(*kw))

  def test_04_invoiceRule_expand(self, quiet=0, run=run_all_test):
    """
    Try to expand an invoice containing Invoice Lines
    """
    if not run: return
    if not quiet:
      message = 'Test Invoice Rule Expand '
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    # before the tests, we must update the matrix
    self.updateInvoiceTransactionRuleMatrix()

    ####
    # TEST NO 1 : one Invoice Line (quantity * price) * tax == (7 * 11) * 19
    ####
    # the invoice is expanded by the invoice_edit_workflow when it is edited.
    self.invoice.edit(title='Invoice1')

    # check every level of the simulation
    applied_rule_list = self.simulation_tool.contentValues() # list of Invoice Rules
    self.assertEqual(len(applied_rule_list), 1)

    applied_rule = applied_rule_list[0]
    self.assertEqual(applied_rule.getPortalType(), 'Applied Rule')
    self.assertEqual(applied_rule.getSpecialise(), 'portal_rules/default_invoice_rule')
    self.assertEqual(applied_rule.getCausality(), 'accounting/invoice1')

    movement_list = applied_rule.contentValues() # list of Invoice Lines
    self.assertEqual(len(movement_list), 1)

    movement = movement_list[0]
    self.assertEqual(movement.getId(), '1')
    self.assertEqual(movement.getPortalType(), 'Simulation Movement')
    self.assertEqual(movement.getDelivery(), 'accounting/invoice1/1')

    sub_applied_rule_list = movement.contentValues() # list of Invoice Transaction Rules
    self.assertEqual(len(sub_applied_rule_list), 1)

    sub_applied_rule = sub_applied_rule_list[0]
    self.assertEqual(sub_applied_rule.getId(), 'default_invoice_transaction_rule')
    self.assertEqual(sub_applied_rule.getPortalType(), 'Applied Rule')
    self.assertEqual(sub_applied_rule.getSpecialise(), 'portal_rules/default_invoice_transaction_rule')

    sub_movement_list = sub_applied_rule.contentValues() # list of Sale Invoice Transaction Lines
    self.assertEqual(len(sub_movement_list), 3) # there should be 'income', 'receivable', 'collected_vat'

    for sub_movement in sub_movement_list :
      if sub_movement.getId() not in ('income', 'receivable', 'collected_vat',) :
        self.fail(msg='%s is not a normal Sale Invoice Transaction Line name' % sub_movement)
      self.assertEqual(movement.getPortalType(), 'Simulation Movement')
      if sub_movement.getId() == 'income' :
        self.assertEqual(sub_movement.getSource(), 'account/account1')
        self.assertEqual(sub_movement.getDestination(), 'account/account2')
        self.assertEqual(sub_movement.getQuantity(), (7.0 * 11.0) * 19.0)

    # check if invoice transaction lines are added and correct (outside simulation too)
    invoice_transaction_line = getattr(self.invoice, 'income', None)
    self.failIf(invoice_transaction_line is None)
    self.assertEqual(invoice_transaction_line.getPortalType(), 'Sale Invoice Transaction Line')
    self.assertEqual(invoice_transaction_line.getSource(), 'account/account1')
    self.assertEqual(invoice_transaction_line.getDestination(), 'account/account2')
    self.assertEqual(invoice_transaction_line.getQuantity(), (7.0 * 11.0) * 19.0)

    ####
    # TEST NO 2 : one Invoice Line (quantity * price) * tax == (7 * 11) * 19
    # expand once again and check that everithing is still the same
    ####
    # the invoice is expanded by the invoice_edit_workflow when it is edited.
    self.invoice.edit(title='Invoice1')

    # check every level of the simulation
    applied_rule_list = self.simulation_tool.contentValues() # list of Invoice Rules
    self.assertEqual(len(applied_rule_list), 1)

    applied_rule = applied_rule_list[0]
    self.assertEqual(applied_rule.getPortalType(), 'Applied Rule')
    self.assertEqual(applied_rule.getSpecialise(), 'portal_rules/default_invoice_rule')
    self.assertEqual(applied_rule.getCausality(), 'accounting/invoice1')

    movement_list = applied_rule.contentValues() # list of Invoice Lines
    self.assertEqual(len(movement_list), 1)

    movement = movement_list[0]
    self.assertEqual(movement.getId(), '1')
    self.assertEqual(movement.getPortalType(), 'Simulation Movement')
    self.assertEqual(movement.getDelivery(), 'accounting/invoice1/1')

    sub_applied_rule_list = movement.contentValues() # list of Invoice Transaction Rules
    self.assertEqual(len(sub_applied_rule_list), 1)

    sub_applied_rule = sub_applied_rule_list[0]
    self.assertEqual(sub_applied_rule.getId(), 'default_invoice_transaction_rule')
    self.assertEqual(sub_applied_rule.getPortalType(), 'Applied Rule')
    self.assertEqual(sub_applied_rule.getSpecialise(), 'portal_rules/default_invoice_transaction_rule')

    sub_movement_list = sub_applied_rule.contentValues() # list of Sale Invoice Transaction Lines
    self.assertEqual(len(sub_movement_list), 3) # there should be 'income', 'receivable', 'collected_vat'

    for sub_movement in sub_movement_list :
      if sub_movement.getId() not in ('income', 'receivable', 'collected_vat',) :
        self.fail(msg='%s is not a normal Sale Invoice Transaction Line name' % sub_movement)
      self.assertEqual(movement.getPortalType(), 'Simulation Movement')
      if sub_movement.getId() == 'income' :
        self.assertEqual(sub_movement.getSource(), 'account/account1')
        self.assertEqual(sub_movement.getDestination(), 'account/account2')
        self.assertEqual(sub_movement.getQuantity(), (7.0 * 11.0) * 19.0)

    # check if invoice transaction lines are added and correct (outside simulation too)
    invoice_transaction_line = getattr(self.invoice, 'income', None)
    self.failIf(invoice_transaction_line is None)
    self.assertEqual(invoice_transaction_line.getPortalType(), 'Sale Invoice Transaction Line')
    self.assertEqual(invoice_transaction_line.getSource(), 'account/account1')
    self.assertEqual(invoice_transaction_line.getDestination(), 'account/account2')
    self.assertEqual(invoice_transaction_line.getQuantity(), (7.0 * 11.0) * 19.0)

    ####
    # TEST NO 3 : two Invoice Lines (quantity * price) * tax == (7 * 11) * 19 + (13 * 17) * 19
    # add a line with same product_line and test again
    ####
    invoice_line2 = self.invoice.newContent(id='2', portal_type='Invoice Line', resource='product/product1', quantity=13.0, price=17.0)
    # the invoice is expanded by the invoice_edit_workflow when it is edited.
    self.invoice.edit(title='Invoice1')

    # check every level of the simulation
    applied_rule_list = self.simulation_tool.contentValues() # list of Invoice Rules
    self.assertEqual(len(applied_rule_list), 1)

    applied_rule = applied_rule_list[0]
    self.assertEqual(applied_rule.getPortalType(), 'Applied Rule')
    self.assertEqual(applied_rule.getSpecialise(), 'portal_rules/default_invoice_rule')
    self.assertEqual(applied_rule.getCausality(), 'accounting/invoice1')

    movement_list = applied_rule.contentValues() # list of Invoice Lines
    self.assertEqual(len(movement_list), 2)

    for movement in movement_list :
      movement_id = movement.getId()
      if movement_id not in ('1', '2',) :
        self.fail(msg='%s is not a normal Invoice Line name' % sub_movement)
      self.assertEqual(movement.getPortalType(), 'Simulation Movement')
      self.assertEqual(movement.getDelivery(), 'accounting/invoice1/%s' % movement_id)

      sub_applied_rule_list = movement.contentValues() # list of Invoice Transaction Rules
      self.assertEqual(len(sub_applied_rule_list), 1)

      sub_applied_rule = sub_applied_rule_list[0]
      self.assertEqual(sub_applied_rule.getId(), 'default_invoice_transaction_rule')
      self.assertEqual(sub_applied_rule.getPortalType(), 'Applied Rule')
      self.assertEqual(sub_applied_rule.getSpecialise(), 'portal_rules/default_invoice_transaction_rule')

      sub_movement_list = sub_applied_rule.contentValues() # list of Sale Invoice Transaction Lines
      self.assertEqual(len(sub_movement_list), 3) # there should be 'income', 'receivable', 'collected_vat'

      for sub_movement in sub_movement_list :
        if sub_movement.getId() not in ('income', 'receivable', 'collected_vat',) :
          self.fail(msg='%s is not a normal Sale Invoice Transaction Line name' % sub_movement)
        self.assertEqual(movement.getPortalType(), 'Simulation Movement')
        if sub_movement.getId() == 'income' :
          self.assertEqual(sub_movement.getSource(), 'account/account1')
          self.assertEqual(sub_movement.getDestination(), 'account/account2')
          if movement_id == '1' :
            self.assertEqual(sub_movement.getQuantity(), (7.0 * 11.0) * 19.0)

          elif movement_id == '2' :
            self.assertEqual(sub_movement.getQuantity(), (13.0 * 17.0) * 19.0)

    # check if invoice transaction lines are added and correct (outside simulation too)
    invoice_transaction_line = getattr(self.invoice, 'income', None)
    self.failIf(invoice_transaction_line is None)
    self.assertEqual(invoice_transaction_line.getPortalType(), 'Sale Invoice Transaction Line')
    self.assertEqual(invoice_transaction_line.getSource(), 'account/account1')
    self.assertEqual(invoice_transaction_line.getDestination(), 'account/account2')
    self.assertEqual(invoice_transaction_line.getQuantity(), (7.0 * 11.0 + 13.0 * 17.0) * 19.0)

    ####
    # TEST NO 4 : three Invoice Lines (quantity * price) * tax == (7 * 11) * 19 + (13 * 17) * 19 + (23 * 29) * 31
    ####
    # add a line with different product_line and test again (we first need a line for this one)
    self.product2_region1_line1 = getattr(self.product2_region1_cell, 'income', None)
    self.failUnless(self.product2_region1_line1 != None)
    self.product2_region1_line1.edit(title='income', source='account/account3', destination='account/account4', quantity=31.0)

    invoice_line3 = self.invoice.newContent(id='3', portal_type='Invoice Line', resource='product/product2', quantity=23.0, price=29.0)
    # the invoice is expanded by the invoice_edit_workflow when it is edited.
    self.invoice.edit(title='Invoice1')

    # check every level of the simulation
    applied_rule_list = self.simulation_tool.contentValues() # list of Invoice Rules
    self.assertEqual(len(applied_rule_list), 1)

    applied_rule = applied_rule_list[0]
    self.assertEqual(applied_rule.getPortalType(), 'Applied Rule')
    self.assertEqual(applied_rule.getSpecialise(), 'portal_rules/default_invoice_rule')
    self.assertEqual(applied_rule.getCausality(), 'accounting/invoice1')

    movement_list = applied_rule.contentValues() # list of Invoice Lines
    self.assertEqual(len(movement_list), 3)

    for movement in movement_list :
      movement_id = movement.getId()
      if movement_id not in ('1', '2', '3',) :
        self.fail(msg='%s is not a normal Invoice Line name' % sub_movement)
      self.assertEqual(movement.getPortalType(), 'Simulation Movement')
      self.assertEqual(movement.getDelivery(), 'accounting/invoice1/%s' % movement_id)

      sub_applied_rule_list = movement.contentValues() # list of Invoice Transaction Rules
      self.assertEqual(len(sub_applied_rule_list), 1)

      sub_applied_rule = sub_applied_rule_list[0]
      self.assertEqual(sub_applied_rule.getId(), 'default_invoice_transaction_rule')
      self.assertEqual(sub_applied_rule.getPortalType(), 'Applied Rule')
      self.assertEqual(sub_applied_rule.getSpecialise(), 'portal_rules/default_invoice_transaction_rule')

      sub_movement_list = sub_applied_rule.contentValues() # list of Sale Invoice Transaction Lines
      self.assertEqual(len(sub_movement_list), 3) # there should be 'income', 'receivable', 'collected_vat'

      for sub_movement in sub_movement_list :
        if sub_movement.getId() not in ('income', 'receivable', 'collected_vat',) :
          self.fail(msg='%s is not a normal Sale Invoice Transaction Line name' % sub_movement)
        self.assertEqual(movement.getPortalType(), 'Simulation Movement')
        if sub_movement.getId() == 'income' :
          if movement_id == '1' :
            self.assertEqual(sub_movement.getSource(), 'account/account1')
            self.assertEqual(sub_movement.getDestination(), 'account/account2')
            self.assertEqual(sub_movement.getQuantity(), (7.0 * 11.0) * 19.0)
          elif movement_id == '2' :
            self.assertEqual(sub_movement.getSource(), 'account/account1')
            self.assertEqual(sub_movement.getDestination(), 'account/account2')
            self.assertEqual(sub_movement.getQuantity(), (13.0 * 17.0) * 19.0)
          elif movement_id == '3' :
            self.assertEqual(sub_movement.getSource(), 'account/account3')
            self.assertEqual(sub_movement.getDestination(), 'account/account4')
            self.assertEqual(sub_movement.getQuantity(), (23.0 * 29.0) * 31.0)

    # check if invoice transaction lines are added and correct (outside simulation too)
    invoice_transaction_line = getattr(self.invoice, 'income', None)
    self.failIf(invoice_transaction_line is None)
    self.assertEqual(invoice_transaction_line.getPortalType(), 'Sale Invoice Transaction Line')
    self.assertEqual(invoice_transaction_line.getSource(), 'account/account1')
    self.assertEqual(invoice_transaction_line.getDestination(), 'account/account2')
    self.assertEqual(invoice_transaction_line.getQuantity(), (7.0 * 11.0 + 13.0 * 17.0) * 19.0)

    invoice_transaction_line = getattr(self.invoice, 'income_1', None)
    self.failIf(invoice_transaction_line is None)
    self.assertEqual(invoice_transaction_line.getPortalType(), 'Sale Invoice Transaction Line')
    self.assertEqual(invoice_transaction_line.getSource(), 'account/account3')
    self.assertEqual(invoice_transaction_line.getDestination(), 'account/account4')
    self.assertEqual(invoice_transaction_line.getQuantity(), (23.0 * 29.0) * 31.0)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestAccountingRules))
        return suite
