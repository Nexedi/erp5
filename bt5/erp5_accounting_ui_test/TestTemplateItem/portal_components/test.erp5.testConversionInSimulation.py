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

from DateTime import DateTime
from zLOG import LOG
from Testing import ZopeTestCase
from erp5.component.test.testAccounting import AccountingTestCase
from AccessControl.SecurityManagement import newSecurityManager
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

class TestConversionInSimulation(AccountingTestCase):

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

  def createCategoriesInCategory(self, category, category_id_list):
    for category_id in category_id_list:
      child = category
      for id_ in category_id.split('/'):
        try:
          child = child[id_]
        except KeyError:
          child = child.newContent(id_)

  def createCategories(self):
    """Create the categories for our test. """
    category_tool = self.getCategoryTool()
    _ = self.createCategoriesInCategory
    _(category_tool.region, [self.default_region])
    _(category_tool.gap, [self.vat_gap, self.sale_gap, self.customer_gap])
    _(category_tool.delivery_mode, [self.mail_delivery_mode])
    _(category_tool.incoterm, [self.cpt_incoterm])
    _(category_tool.quantity_unit,
      [self.unit_piece_quantity_unit, self.mass_quantity_unit])
    _(category_tool.product_line, ['apparel'])

  def _solveDivergence(self, obj, prop, decision, group='line'):
    """
      Check if simulation movement are disconnected
    """
    kw = {'%s_group_listbox' % group:{}}
    for divergence in obj.getDivergenceList():
      if divergence.getProperty('tested_property') != prop:
        continue
      sm_url = divergence.getProperty('simulation_movement').getRelativeUrl()
      kw['line_group_listbox']['%s&%s' % (sm_url, prop)] = {
        'choice':decision}
    self.portal.portal_workflow.doActionFor(
      obj,
      'solve_divergence_action',
      **kw)

  def afterSetUp(self):
    super(TestConversionInSimulation, self).afterSetUp()
    super(TestConversionInSimulation, self).login()
    self.createCategories()
    self.createAndValidateAccounts()
    self.login()

  def beforeTearDown(self):
    self.abort()
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
    if getattr(self, 'business_process', None) is not None:
      self.business_process.getParentValue()._delObject(
        self.business_process.getId()
      )
    self.tic()
    super(TestConversionInSimulation, self).beforeTearDown()

  def login(self, *args, **kw):
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
            # XXX erp5_core is still not clean. Remove when not needed
            'erp5_core_proxy_field_legacy',
            'erp5_pdm',
            'erp5_simulation',
            'erp5_trade',
            'erp5_accounting',
            'erp5_accounting_ui_test',
            'erp5_invoicing',
            'erp5_simplified_invoicing',
            'erp5_configurator_standard_solver',
            'erp5_configurator_standard_trade_template',
            'erp5_configurator_standard_accounting_template',
            'erp5_configurator_standard_invoicing_template',
            'erp5_simulation_test',
            )

  def createAndValidateAccounts(self):
    account_module = self.portal.account_module
    for account_id, account_gap, account_type \
               in self.account_definition_list:
      if not account_id in account_module.objectIds():
        account = account_module.newContent(account_id,
           gap=account_gap, account_type=account_type)
        self.portal.portal_workflow.doActionFor(account, 'validate_action')

  def createBusinessProcess(self, resource=None):
    module = self.portal.business_process_module
    name = self.__class__.__name__ + '_' + self._testMethodName
    self.business_process = business_process = module.newContent(
      name,
      reference=name,
    )
    # copy business links from the default erp5 Business Process
    source = module['erp5_default_business_process']
    business_link_id_list = [obj.getId()
                             for obj in source.objectValues()
                             if obj.getPortalType() == 'Business Link']
    business_process.manage_pasteObjects(
      source.manage_copyObjects(business_link_id_list)
    )
    trade_phase = self.getCategoryTool().trade_phase
    kw = dict(portal_type='Trade Model Path',
              trade_date='trade_phase/trade/order')
    business_process.newContent(
      reference='default_path',
      trade_phase_value_list=[x for x in trade_phase.trade.objectValues()
                              if x.getId() != 'accounting'],
      **kw)
    kw.update(trade_phase='trade/accounting',
              resource_value=resource,
              membership_criterion_base_category_list=(
                'destination_region',
                'product_line'),
              membership_criterion_category_list=(
                'destination_region/region/' + self.default_region,
                'product_line/apparel'))
    for line_id, line_source_id, line_destination_id, line_ratio in \
        self.transaction_line_definition_list:
      trade_model_path = business_process.newContent(
        reference='acounting_' + line_id,
        efficiency=line_ratio,
        source='account_module/' + line_source_id,
        destination='account_module/' + line_destination_id,
        **kw)
      # A trade model path already exist for root simulation movements
      # (Accounting Transaction Root Simulation Rule).
      # The ones we are creating are for Invoice Transaction Simulation Rule.
      trade_model_path._setCriterionPropertyList(('portal_type',))
      trade_model_path.setCriterion('portal_type', 'Simulation Movement')
    business_process.validate()
    self.tic()

  def buildPackingLists(self):
    self.portal.portal_alarms.packing_list_builder_alarm.activeSense()
    self.tic()

  def buildInvoices(self):
    self.portal.portal_alarms.invoice_builder_alarm.activeSense()
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
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
                                  portal_type='Currency Exchange Line',
                        price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createBusinessProcess(currency)
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
                              specialise_value=self.business_process,
                              title='Order')
    order.newContent(portal_type='Sale Order Line',
                     resource_value=resource,
                     quantity=1,
                     price=2)

    order.confirm()
    self.tic()
    self.buildPackingLists()

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    order_movement = related_applied_rule.contentValues()[0]
    delivery_applied_rule = order_movement.contentValues()[0]
    delivery_movement = delivery_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    invoice_transaction_movement_1 =\
         invoice_transaction_applied_rule.contentValues()[0]
    self.assertEqual(currency,
          invoice_transaction_movement_1.getResourceValue())
    self.assertEqual(currency,
          delivery_movement.getPriceCurrencyValue())
    self.assertEquals\
     (invoice_transaction_movement_1.getDestinationTotalAssetPrice(),
        655.957*invoice_transaction_movement_1.getTotalPrice())
    self.assertEquals\
        (invoice_transaction_movement_1.getSourceTotalAssetPrice(),
        None)
    invoice_transaction_movement_2 =\
         invoice_transaction_applied_rule.contentValues()[1]
    self.assertEqual(currency,
          invoice_transaction_movement_2.getResourceValue())
    self.assertEqual(currency,
          delivery_movement.getPriceCurrencyValue())
    self.assertEquals\
        (invoice_transaction_movement_2.getDestinationTotalAssetPrice(),
        655.957*invoice_transaction_movement_2.getTotalPrice())

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
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
                              portal_type='Currency Exchange Line',
                price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createBusinessProcess(currency)
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
                              specialise_value=self.business_process,
                              title='Order')
    order.newContent(portal_type='Sale Order Line',
                     resource_value=resource,
                     quantity=1,
                     price=2)

    order.confirm()
    self.tic()
    self.buildPackingLists()

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    order_movement = related_applied_rule.contentValues()[0]
    delivery_applied_rule = order_movement.contentValues()[0]
    delivery_movement = delivery_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    invoice_transaction_movement =\
         invoice_transaction_applied_rule.contentValues()[0]
    self.assertEqual(currency,
          invoice_transaction_movement.getResourceValue())
    self.assertEqual(currency,
          delivery_movement.getPriceCurrencyValue())
    self.assertEquals\
        (invoice_transaction_movement.getSourceTotalAssetPrice(),
         -655.957*invoice_transaction_movement.getTotalPrice())
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
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
                                  portal_type='Currency Exchange Line',
                        price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createBusinessProcess(currency)
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
                              specialise_value=self.business_process,
                              title='Order')
    order.newContent(portal_type='Sale Order Line',
                     resource_value=resource,
                     quantity=1,
                     price=2)
    order.confirm()
    self.tic()
    self.buildPackingLists()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.buildInvoices()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                            portal_type='Sale Invoice Transaction')
    self.assertNotEquals(related_invoice, None)
    related_invoice.start()
    self.tic()
    line_list= related_invoice.contentValues(
      portal_type=self.portal.getPortalAccountingMovementTypeList())
    self.assertNotEquals(line_list, None)
    result_list = []
    for line in line_list:
      result_list.append((line.getSource(), line.getDestinationTotalAssetPrice()))
      self.assertEqual(line.getSourceTotalAssetPrice(), None)

    self.assertEquals(
      sorted(result_list),
      sorted([
        ('account_module/customer', round(-2*(1+0.196)*655.957)),
        ('account_module/receivable_vat', round(2*0.196*655.957)),
        ('account_module/sale', round(2*655.957 ))
      ])
    )

    self.assertEqual(len(related_invoice.checkConsistency()), 0)

  def test_01_source_total_asset_price_on_accounting_lines(self,quiet=0,
          run=run_all_test):
    """
    tests that the delivery builder of the invoice transaction lines
    copies the source asset price on the accounting_lines of the invoice
    """
    if not run: return
    if not quiet:
      printAndLog(
       'test_01_source_total_asset_price_on_accounting_lines')

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
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
                                  portal_type='Currency Exchange Line',
                        price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createBusinessProcess(currency)
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
    order = self.portal.sale_order_module.newContent(
                              portal_type='Sale Order',
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              specialise_value=self.business_process,
                              title='Order')
    order.newContent(portal_type='Sale Order Line',
                     resource_value=resource,
                     quantity=1,
                     price=2)
    order.confirm()
    self.tic()
    self.buildPackingLists()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.buildInvoices()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                            portal_type='Sale Invoice Transaction')
    self.assertNotEquals(related_invoice, None)
    related_invoice.start()
    self.tic()
    line_list= related_invoice.contentValues(
      portal_type=self.portal.getPortalAccountingMovementTypeList())
    self.assertNotEquals(line_list, None)
    result_list = []
    for line in line_list:
      result_list.append((line.getSource(), line.getSourceTotalAssetPrice()))
      self.assertEqual(line.getDestinationTotalAssetPrice(), None)

    self.assertEquals(
      sorted(result_list),
      sorted([
        ('account_module/customer', round(2*(1+0.196)*655.957)),
        ('account_module/receivable_vat', round(-2*0.196*655.957)),
        ('account_module/sale', round(-2*655.957 ))
      ])
    )

    self.assertEqual(len(related_invoice.checkConsistency()), 0)

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
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
                              portal_type='Currency Exchange Line',
               price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createBusinessProcess(currency)
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
                              specialise_value=self.business_process,
                              title='Order')
    order.newContent(portal_type='Sale Order Line',
                     resource_value=resource,
                     quantity=5,
                     price=2)
    order.confirm()
    self.tic()
    self.buildPackingLists()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    related_packing_list_line_list=related_packing_list.getMovementList()
    related_packing_list_line= related_packing_list_line_list[0]
    self.assertEqual(related_packing_list_line.getQuantity(),5.0)

    related_packing_list_line.edit(quantity=3.0)
    self.tic()
    self.assertEqual(related_packing_list.getCausalityState(),
                             'diverged')
    self._solveDivergence(related_packing_list, 'quantity', 'accept')
    self.tic()
    related_packing_list.updateCausalityState()
    related_packing_list.start()
    related_packing_list.stop()
    self.tic()

    related_applied_rule = order.getCausalityRelatedValue(
                            portal_type='Applied Rule')
    order_movement = related_applied_rule.contentValues()[0]
    delivery_applied_rule = order_movement.contentValues()[0]
    delivery_movement = delivery_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    result_list = []
    for invoice_transaction_movement in invoice_transaction_applied_rule.contentValues():
      result_list.append((invoice_transaction_movement.getSource(), invoice_transaction_movement.getDestinationTotalAssetPrice()))
    self.assertEquals(
      sorted(result_list),
      sorted([
        ('account_module/customer', -2*3*(1+0.196)*655.957),
        ('account_module/receivable_vat', 2*3*0.196*655.957),
        ('account_module/sale', 2*3*655.957 )
      ])
    )


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
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
                               portal_type='Currency Exchange Line',
                price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createBusinessProcess(currency)
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
                              specialise_value=self.business_process,
                              title='Order')
    order.newContent(portal_type='Purchase Order Line',
                     resource_value=resource,
                     quantity=5,
                     price=2)
    order.confirm()
    self.tic()
    self.buildPackingLists()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Purchase Packing List')
    self.assertNotEquals(related_packing_list, None)
    related_packing_list_line_list=related_packing_list.getMovementList()
    related_packing_list_line= related_packing_list_line_list[0]
    self.assertEqual(related_packing_list_line.getQuantity(),5.0)

    related_packing_list_line.edit(quantity=3.0)
    self.tic()
    self.assertEqual(related_packing_list.getCausalityState(),
                             'diverged')

    self._solveDivergence(related_packing_list, 'quantity','accept')
    self.tic()
    related_packing_list.updateCausalityState()
    related_packing_list.start()
    related_packing_list.stop()
    self.tic()

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    order_movement = related_applied_rule.contentValues()[0]
    delivery_applied_rule = order_movement.contentValues()[0]
    delivery_movement = delivery_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]
    result_list = []
    for invoice_transaction_movement in invoice_transaction_applied_rule.contentValues():
      result_list.append((invoice_transaction_movement.getSource(), invoice_transaction_movement.getSourceTotalAssetPrice()))
    self.assertEquals(
      sorted(result_list),
      sorted([
        ('account_module/customer', 2*3*(1+0.196)*655.957),
        ('account_module/receivable_vat', -2*3*0.196*655.957),
        ('account_module/sale', -2*3*655.957 )
      ])
    )

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
    self.tic()#execute transaction
    x_curr_ex_line = currency.newContent(
                                  portal_type='Currency Exchange Line',
                        price_currency=new_currency.getRelativeUrl())
    x_curr_ex_line.setTitle('Euro to Francs CFA')
    x_curr_ex_line.setBasePrice(655.957)
    x_curr_ex_line.setStartDate(DateTime(2008,10,21))
    x_curr_ex_line.setStopDate(DateTime(2008,10,22))
    x_curr_ex_line.validate()
    self.createBusinessProcess(currency)
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
                              specialise_value=self.business_process,
                              title='Order')
    order.newContent(portal_type='Sale Order Line',
                     resource_value=resource,
                     quantity=5,
                     price=2)
    order.confirm()
    self.tic()
    self.buildPackingLists()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    self.assertEqual(related_packing_list.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEqual(related_packing_list.getIncoterm(),
                         order.getIncoterm())
    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.buildInvoices()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                             portal_type='Sale Invoice Transaction')
    self.assertNotEquals(related_invoice, None)
    self.assertEqual(related_invoice.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEqual(related_invoice.getIncoterm(),
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
    self.createBusinessProcess(currency)
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
                              specialise_value=self.business_process,
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
    self.tic()
    self.buildPackingLists()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type='Sale Packing List')
    self.assertNotEquals(related_packing_list, None)
    movement_list = related_packing_list.getMovementList()
    movement_list.sort(key=lambda x:x.getCausalityId())
    self.assertEqual(len(movement_list),2)
    self.assertEqual(movement_list[0].getQuantityUnit(),
                         first_order_line.getQuantityUnit())
    self.assertEqual(movement_list[1].getQuantityUnit(),
                         second_order_line.getQuantityUnit())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestConversionInSimulation))
  return suite
