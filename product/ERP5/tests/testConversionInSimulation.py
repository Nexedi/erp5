#############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
import unittest
import os
from DateTime import DateTime
from zLOG import LOG
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from Testing import ZopeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from Products.ERP5.tests.testAccounting import AccountingTestCase
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from Products.ERP5Form.Document.Preference import Priority
from testPackingList import TestPackingListMixin
from testAccountingRules import TestAccountingRulesMixin
from Acquisition import aq_parent
QUIET = False
run_all_test = True



def printAndLog(msg):
  """
  A utility function to print a message
  to the standard output and to the LOG
  at the same time
  """
  msg = str(msg)
  ZopeTestCase._print('\n ' + msg)
  LOG('Testing... ', 0, msg)

class TestConversionInSimulation(AccountingTestCase,ERP5TypeTestCase):
  
  username = 'username'
  default_region = "europe/west/france"
  vat_gap = 'fr/pcg/4/44/445/4457/44571'
  vat_rate = 0.196
  sale_gap = 'fr/pcg/7/70/707/7071/70712'
  customer_gap = 'fr/pcg/4/41/411'
  mail_delivery_mode = 'by_mail'
  cpt_incoterm = 'cpt'
  unit_piece_quantity_unit = 'unit/piece'
  mass_quantity_unit = 'mass/kg'

  # (account_id, account_gap, account_type)
  account_definition_list = (
      ('receivable_vat', vat_gap, 'liability/payable/collected_vat',),
      ('sale', sale_gap, 'income'),
      ('customer', customer_gap, 'asset/receivable'),
      ('refundable_vat', vat_gap, 'asset/receivable/refundable_vat'),
      ('purchase', sale_gap, 'expense'),
      ('supplier', customer_gap, 'liability/payable'),
      )
  # (line_id, source_account_id, destination_account_id, line_quantity)
  transaction_line_definition_list = (
      ('income', 'sale', 'purchase', 1.0),
      ('receivable', 'customer', 'supplier', -1.0 - vat_rate),
      ('collected_vat', 'receivable_vat', 'refundable_vat', vat_rate),
      )
   
		 
  def createCategories(self):
    """Create the categories for our test. """
    return UnrestrictedMethod(self._createCategories)()
  def _createCategories(self):
    # create categories
    for cat_string in self.getNeededCategoryList() :
      base_cat = cat_string.split("/")[0]
      path = self.getPortal().portal_categories[base_cat]
      for cat in cat_string.split("/")[1:] :
        if not cat in path.objectIds() :
          path = path.newContent(
                    portal_type='Category',
                    id=cat,)
        else:
          path = path[cat]
    # check categories have been created
    for cat_string in self.getNeededCategoryList() :
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('region/%s' % self.default_region,
            'gap/%s' % self.vat_gap,
            'gap/%s' % self.sale_gap,
            'gap/%s' % self.customer_gap,
	    'delivery_mode/%s' % self.mail_delivery_mode,
	    'incoterm/%s' % self.cpt_incoterm,
            'quantity_unit/%s' % self.unit_piece_quantity_unit,
            'quantity_unit/%s' % self.mass_quantity_unit,
        )

  def _solveDivergence(self, obj, property, decision, group='line'):
    """
      Check if simulation movement are disconnected
    """
    kw = {'%s_group_listbox' % group:{}}
    for divergence in obj.getDivergenceList():
      if divergence.getProperty('tested_property') != property:
        continue
      sm_url = divergence.getProperty('simulation_movement').getRelativeUrl()
      kw['line_group_listbox']['%s&%s' % (sm_url, property)] = {
        'choice':decision}
    self.portal.portal_workflow.doActionFor(
      obj,
      'solve_divergence_action',
      **kw)
      
  def afterSetUp(self):
    self.createCategories()
    self.validateRules()
    self.login()

  def beforeTearDown(self):
    get_transaction().abort()
    # clear modules if necessary
    currency_list = ('euro', 'yen', 'usd')
    module = self.portal.currency_module
    module.manage_delObjects([x for x in module.objectIds()
                        if x not in currency_list])
    for currency_id in currency_list:
      currency = self.currency_module._getOb(currency_id, None)
      if currency is not None:
        currency.manage_delObjects([x.getId() for x in
                currency.objectValues(
                  portal_type='Currency Exchange Line')])
    get_transaction().commit()
    self.tic()
 
  def login(self,name=username, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Assignee', 'Assignor',
            'Author'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)
   
  def getBusinessTemplateList(self):
    """
      Return the list of business templates we need to run the test.
      This method is called during the initialization of the unit test by
      the unit test framework in order to know which business templates
      need to be installed to run the test on.
    """
    return ('erp5_base',
             'erp5_pdm',
	     'erp5_trade',
            'erp5_accounting',
	    'erp5_accounting_ui_test',
	    'erp5_invoicing'
            )
  def createInvoiceTransactionRule(self, resource=None):
    return UnrestrictedMethod(
        self._createSaleInvoiceTransactionRule)(resource=resource)

  def _createSaleInvoiceTransactionRule(self, resource=None):
    """Create a sale invoice transaction rule with only one cell for
    product_line/apparel and default_region
    The accounting rule cell will have the provided resource, but this his more
    or less optional (as long as price currency is set correctly on order)
    """
    portal = self.portal
    account_module = portal.account_module
    for account_id, account_gap, account_type \
               in self.account_definition_list:
      if not account_id in account_module.objectIds():
        account = account_module.newContent(id=account_id)
        account.setGap(account_gap)
        account.setAccountType(account_type)
        portal.portal_workflow.doActionFor(account, 'validate_action')

    invoice_rule = portal.portal_rules.default_invoice_transaction_rule
    invoice_rule.deleteContent([x.getId()
                          for x in invoice_rule.objectValues()])
    get_transaction().commit()
    self.tic()
    region_predicate = invoice_rule.newContent(portal_type = 'Predicate')
    product_line_predicate = invoice_rule.newContent(portal_type = 'Predicate')
    region_predicate.edit(
      membership_criterion_base_category_list = ['destination_region'],
      membership_criterion_category_list =
                  ['destination_region/region/%s' % self.default_region ],
      int_index = 1,
      string_index = 'region'
    )
    product_line_predicate.edit(
      membership_criterion_base_category_list = ['product_line'],
      membership_criterion_category_list =
                            ['product_line/apparel'],
      int_index = 1,
      string_index = 'product'
    )
    product_line_predicate.immediateReindexObject()
    region_predicate.immediateReindexObject()

    invoice_rule.updateMatrix()
    cell_list = invoice_rule.getCellValueList(base_id='movement')
    self.assertEquals(len(cell_list),1)
    cell = cell_list[0]

    for line_id, line_source_id, line_destination_id, line_ratio in \
        self.transaction_line_definition_list:
      line = cell.newContent(id=line_id,
          portal_type='Accounting Transaction Line', quantity=line_ratio,
          resource_value=resource,
          source_value=account_module[line_source_id],
          destination_value=account_module[line_destination_id])

    invoice_rule.validate()
    get_transaction().commit()
    self.tic()

  def test_01_simulation_movement_destination_asset_price(self,quiet=0,
          run=run_all_test):
    """
    tests that when resource on simulation movements is different
     from the price currency of the destination section, that
      destination_asset_price is set on the movement
      """
    if not run: return
    if not quiet:
       printAndLog('test_01_simulation_movement_destination_asset_price')
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
		    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    new_currency = \
           self.portal.currency_module.newContent(portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    get_transaction().commit()
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
	                          portal_type='Currency Exchange Line',
			price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createInvoiceTransactionRule(currency)
    get_transaction().commit()
    self.tic()#execute transactio
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
		price_currency=new_currency.getRelativeUrl(),
                        default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                         default_address_region=self.default_region)
    order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type='Sale Order Line',
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)
    
    order.confirm()
    get_transaction().commit()
    self.tic()
    
    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    delivery_movement = related_applied_rule.contentValues()[0]
    
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    invoice_transaction_movement_1 =\
         invoice_transaction_applied_rule.contentValues()[0]
    self.assertEquals(currency,
          invoice_transaction_movement_1.getResourceValue())
    self.assertEquals(currency,
          delivery_movement.getPriceCurrencyValue())
    self.assertEquals\
     (invoice_transaction_movement_1.getDestinationTotalAssetPrice(),
	round(655.957*delivery_movement.getTotalPrice()))
    self.assertEquals\
        (invoice_transaction_movement_1.getSourceTotalAssetPrice(),
	None)
    invoice_transaction_movement_2 =\
         invoice_transaction_applied_rule.contentValues()[1]
    self.assertEquals(currency,
          invoice_transaction_movement_2.getResourceValue())
    self.assertEquals(currency,
          delivery_movement.getPriceCurrencyValue())
    self.assertEquals\
        (invoice_transaction_movement_2.getDestinationTotalAssetPrice(),
	round(655.957*delivery_movement.getTotalPrice()))
	
  def test_01_simulation_movement_source_asset_price(self,quiet=0,
          run=run_all_test):
    """
    tests that when resource on simulation movements is different
     from the price currency of the source section, that
      source_asset_price is set on the movement
    """
    if not run: return
    if not quiet:
       printAndLog('test_01_simulation_movement_source_asset_price')
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
		    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    new_currency = \
           self.portal.currency_module.newContent(portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    get_transaction().commit()
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
	                      portal_type='Currency Exchange Line',
		price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createInvoiceTransactionRule(currency)
    get_transaction().commit()
    self.tic()#execute transactio
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client', 
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
			    price_currency=new_currency.getRelativeUrl(),
                            default_address_region=self.default_region)
    order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type='Sale Order Line',
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)
    
    order.confirm()
    get_transaction().commit()
    self.tic()
    
    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    delivery_movement = related_applied_rule.contentValues()[0]
    
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    invoice_transaction_movement =\
         invoice_transaction_applied_rule.contentValues()[0]
    self.assertEquals(currency,
          invoice_transaction_movement.getResourceValue())
    self.assertEquals(currency,
          delivery_movement.getPriceCurrencyValue())
    self.assertEquals\
        (invoice_transaction_movement.getSourceTotalAssetPrice(),
	round(655.957*delivery_movement.getTotalPrice()))
    self.assertEquals\
        (invoice_transaction_movement.getDestinationTotalAssetPrice(),
	None)
	
	
  def test_01_destination_total_asset_price_on_accounting_lines(self,quiet=0,
          run=run_all_test):
    """
    tests that the delivery builder of the invoice transaction lines  
    copies the destination asset price on the accounting_lines of the invoice
    """
    if not run: return
    if not quiet:
       printAndLog(
       'test_01_destination_total_asset_price_on_accounting_lines')
    		  
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
		    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    new_currency = \
           self.portal.currency_module.newContent(portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    get_transaction().commit()
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
	                          portal_type='Currency Exchange Line',
			price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createInvoiceTransactionRule(currency)
    get_transaction().commit()
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client', 
		price_currency=new_currency.getRelativeUrl(),
                       default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                         default_address_region=self.default_region)
    order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type='Sale Order Line',
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)
    order.confirm()
    get_transaction().commit()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    related_packing_list.start()
    related_packing_list.stop()
    get_transaction().commit()
    self.tic()
    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    delivery_movement = related_applied_rule.contentValues()[0]
    related_invoice = related_packing_list.getCausalityRelatedValue(
                            portal_type='Sale Invoice Transaction')
    self.assertNotEquals(related_invoice, None)
    related_invoice.start()
    get_transaction().commit()
    self.tic()
    line_list= related_invoice.contentValues(
      portal_type=self.portal.getPortalAccountingMovementTypeList())
    self.assertNotEquals(line_list, None)
    for line in line_list:
       self.assertEquals(line.getDestinationTotalAssetPrice(),
              round(655.957*delivery_movement.getTotalPrice()))
  
		 
		 
  def test_01_diverged_sale_packing_list_destination_total_asset_price(
	  self,quiet=0,run=run_all_test):
    """
    tests that when the sale packing list is divergent on the quantity and
    that the resource on simulation movements is different
     from the price currency of the source section,
     source_asset_price is updated as we solve the divergence and
     accept the decision
    """
    if not run: return
    if not quiet:
     printAndLog(
        'test_01_diverged_sale_packing_list_destination_total_asset_price')
    		  
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
		    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    new_currency = \
           self.portal.currency_module.newContent(portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    get_transaction().commit()
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
	                      portal_type='Currency Exchange Line',
	       price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createInvoiceTransactionRule(currency)
    get_transaction().commit()
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client', 
		price_currency=new_currency.getRelativeUrl(),
                        default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                         default_address_region=self.default_region)
    order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type='Sale Order Line',
                                  resource_value=resource,
                                  quantity=5,
                                  price=2)
    order.confirm()
    get_transaction().commit()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    related_packing_list_line_list=related_packing_list.getMovementList()
    related_packing_list_line= related_packing_list_line_list[0]
    self.assertEquals(related_packing_list_line.getQuantity(),5.0)
    old_destination_asset_price = \
          round(655.957*related_packing_list_line.getTotalPrice())
   
    related_packing_list_line.edit(quantity=3.0)
    get_transaction().commit()
    self.tic()
    self.assertEquals(related_packing_list.getCausalityState(),
                             'diverged')  
    self._solveDivergence(related_packing_list, 'quantity', 'accept')
    get_transaction().commit()
    self.tic()
    related_packing_list.start()
    related_packing_list.stop()
    get_transaction().commit()
    self.tic()

    related_applied_rule = order.getCausalityRelatedValue(
                            portal_type='Applied Rule')		
    delivery_movement = related_applied_rule.contentValues()[0]  
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    invoice_transaction_movement =\
         invoice_transaction_applied_rule.contentValues()[0]
    self.assertEquals(
       invoice_transaction_movement.getDestinationTotalAssetPrice(),
                old_destination_asset_price *(3.0/5.0))
   
   
  def test_01_diverged_purchase_packing_list_source_total_asset_price(
	   self,quiet=0,run=run_all_test):
    """
    tests that when the purchase packing list is divergent on the quantity
      and that the resource on simulation movements is different
     from the price currency of the destination section,
     destination_asset_price is updated as we solve the divergence and
     accept the decision
    """
    if not run: return
    if not quiet:
     printAndLog(
      'test_01_diverged_purchase_packing_list_source_total_asset_price')
    		  
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
		    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    new_currency = \
      self.portal.currency_module.newContent(portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    get_transaction().commit()
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
	                       portal_type='Currency Exchange Line',
		price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createInvoiceTransactionRule(currency)
    get_transaction().commit()
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                         default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
		price_currency=new_currency.getRelativeUrl(),
                        default_address_region=self.default_region)
    order = self.portal.purchase_order_module.newContent(
                              portal_type='Purchase Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type='Purchase Order Line',
                                  resource_value=resource,
                                  quantity=5,
                                  price=2)
    order.confirm()
    get_transaction().commit()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Purchase Packing List')
    self.assertNotEquals(related_packing_list, None)
    related_packing_list_line_list=related_packing_list.getMovementList()
    related_packing_list_line= related_packing_list_line_list[0]
    self.assertEquals(related_packing_list_line.getQuantity(),5.0)
    old_source_asset_price = \
          round(655.957*related_packing_list_line.getTotalPrice())
   
    related_packing_list_line.edit(quantity=3.0)
    get_transaction().commit()
    self.tic()
    self.assertEquals(related_packing_list.getCausalityState(),
                             'diverged')
    
    self._solveDivergence(related_packing_list, 'quantity','accept')
    get_transaction().commit()
    self.tic()
    related_packing_list.start()
    related_packing_list.stop()
    get_transaction().commit()
    self.tic()

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    delivery_movement = related_applied_rule.contentValues()[0]  
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    invoice_transaction_movement =\
         invoice_transaction_applied_rule.contentValues()[0]
    self.assertEquals(invoice_transaction_movement.\
        getSourceTotalAssetPrice(),
        old_source_asset_price *(3.0/5.0))
	
  def test_01_delivery_mode_on_sale_packing_list_and_invoice(
	  self,quiet=0,run=run_all_test):
    """
    tests that when the sale packing list is divergent on the quantity and
    that the resource on simulation movements is different
     from the price currency of the source section,
     source_asset_price is updated as we solve the divergence and
     accept the decision
    """
    if not run: return
    if not quiet:
     printAndLog(
        'test_01_delivery_mode_on_sale_packing_list_and_invoice')
    		  
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
		    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    new_currency = \
           self.portal.currency_module.newContent(portal_type='Currency')
    new_currency.setReference('XOF')
    new_currency.setTitle('Francs CFA')
    new_currency.setBaseUnitQuantity(1.00)
    get_transaction().commit()
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
	                          portal_type='Currency Exchange Line',
			price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createInvoiceTransactionRule(currency)
    get_transaction().commit()
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client', 
		price_currency=new_currency.getRelativeUrl(),
                       default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                         default_address_region=self.default_region)
    order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
			      delivery_mode=self.mail_delivery_mode,
			      incoterm=self.cpt_incoterm,
                              title='Order')
    order_line = order.newContent(portal_type='Sale Order Line',
                                  resource_value=resource,
                                  quantity=5,
                                  price=2)
    order.confirm()
    get_transaction().commit()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    self.assertEquals(related_packing_list.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEquals(related_packing_list.getIncoterm(),
                         order.getIncoterm())
    related_packing_list.start()
    related_packing_list.stop()
    get_transaction().commit()
    self.tic()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                             portal_type='Sale Invoice Transaction')
    self.assertNotEquals(related_invoice, None)
    self.assertEquals(related_invoice.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEquals(related_invoice.getIncoterm(),
                         order.getIncoterm())
    
  def test_01_quantity_unit_on_sale_packing_list(
      self,quiet=0,run=run_all_test):
    """
    tests that when a resource uses different quantity unit that the
    """
    if not run: return
    if not quiet:
     printAndLog(
        'test_01_quantity_unit_on_sale_packing_list')
                  
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
                    product_line='apparel')
    resource.setQuantityUnitList([self.unit_piece_quantity_unit,
                                 self.mass_quantity_unit])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    get_transaction().commit()
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                         default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                         default_address_region=self.default_region)
    order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              delivery_mode=self.mail_delivery_mode,
                              incoterm=self.cpt_incoterm,
                              title='Order')
    first_order_line = order.newContent(
                        portal_type='Sale Order Line',
                                  resource_value=resource,
                      quantity_unit = self.unit_piece_quantity_unit,
                                  quantity=5,
                                  price=3)
    second_order_line = order.newContent(
                      portal_type='Sale Order Line',
                                  resource_value=resource,
                             quantity_unit=self.mass_quantity_unit,
                                  quantity=1.5,
                                  price=2)
    order.confirm()
    get_transaction().commit()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    movement_list = related_packing_list.getMovementList()
    self.assertEquals(len(movement_list),2)
    self.assertEquals(movement_list[0].getQuantityUnit(),
                         first_order_line.getQuantityUnit())
    self.assertEquals(movement_list[1].getQuantityUnit(),
                         second_order_line.getQuantityUnit())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestConversionInSimulation))
  return suite
