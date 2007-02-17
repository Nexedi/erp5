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
  Tests invoice creation from simulation.

TODO:
  * check empty related Delivery Rule
  * check divergence

"""

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner, aq_parent
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
import os
from Products.ERP5Type import product_path
from Products.CMFCore.utils import getToolByName
from testPackingList import TestPackingListMixin
from testAccountingRules import TestAccountingRulesMixin

class TestInvoice(TestPackingListMixin,
                  TestAccountingRulesMixin,
                  ERP5TypeTestCase):
  """Test invoice are created from orders then packing lists. """

  RUN_ALL_TESTS = 1

  default_region = "europe/west/france"
  vat_gap = 'fr/pcg/4/44/445/4457/44571'
  vat_rate = 0.196
  sale_gap = 'fr/pcg/7/70/707/7071/70712'
  customer_gap = 'fr/pcg/4/41/411'

  # (account_id, account_gap)
  #XXX gap for the last 3 should be set to real values
  account_definition_list = (
      ('receivable_vat', vat_gap),
      ('sale', sale_gap),
      ('customer', customer_gap),
      ('refundable_vat', vat_gap),
      ('purchase', sale_gap),
      ('supplier', customer_gap),
      )
  # (line_id, source_account_id, destination_account_id, line_quantity)
  transaction_line_definition_list = (
      ('income', 'sale', 'purchase', 1.0),
      ('receivable', 'customer', 'supplier', -1.0 - vat_rate),
      ('collected_vat', 'receivable_vat', 'refundable_vat', vat_rate),
      )

  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  invoice_cell_portal_type = 'Invoice Cell'
  invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'

  def getTitle(self):
    return "Invoices"

  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
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
    return ('region/%s' % self.default_region,
            'gap/%s' % self.vat_gap,
            'gap/%s' % self.sale_gap,
            'gap/%s' % self.customer_gap,
        )

  def getBusinessTemplateList(self):
    """ """
    return TestPackingListMixin.getBusinessTemplateList(self) + (
              'erp5_accounting',)

  def stepTic(self, **kw):
    self.tic()

  def stepCreateEntities(self, sequence, **kw) :
    """Create a vendor and a client. """
    self.stepCreateOrganisation1(sequence, **kw)
    self.stepCreateOrganisation2(sequence, **kw)
    self.stepCreateOrganisation3(sequence, **kw)
    sequence.edit(vendor=sequence.get('organisation1'))
    client1 = sequence.get('organisation2')
    client1.setRegion(self.default_region)
    self.assertNotEquals(client1.getRegionValue(), None)
    sequence.edit(client1=client1)
    client2 = sequence.get('organisation3')
    self.assertEquals(client2.getRegionValue(), None)
    sequence.edit(client2=client2)

  def stepCreateCurrency(self, sequence, **kw) :
    """Create a default currency. """
    currency_module = self.getCurrencyModule()
    if len(currency_module.objectValues(id='EUR'))==0:
      currency = self.getCurrencyModule().newContent(
            portal_type = 'Currency',
            id = "EUR" )
    currency = currency_module.objectValues(id='EUR')[0]
    sequence.edit(currency = currency)

  def stepSetOrderPriceCurrency(self, sequence, **kw) :
    """Set the price currency of the order.

    This step is not necessary.
    TODO : - include a test without this step.
           - include a test with this step late.
    """
    currency = sequence.get('currency')
    order = sequence.get('order')
    order.setPriceCurrency(currency.getRelativeUrl())

  def stepCreateSaleInvoiceTransactionRule(self, sequence, **kw) :
    """Create the rule for accounting. """

    portal = self.getPortal()
    account_module = self.getAccountModule()
    for account_id, account_gap in self.account_definition_list:
      if not account_id in account_module.objectIds():
        account = account_module.newContent(id=account_id)
        account.setGap(account_gap)
        portal.portal_workflow.doActionFor(account,
            'validate_action', wf_id='account_workflow')
    invoice_rule = self.getPortal().portal_rules\
                          .default_invoice_transaction_rule
    invoice_rule.deleteContent([x.getId()
                          for x in invoice_rule.objectValues()])
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
                             portal_type='Accounting Transaction Line')
      line.setQuantity(line_ratio)
      line.setSourceValue(account_module[line_source_id])
      line.setDestinationValue(account_module[line_destination_id])

  def modifyPackingListState(self, transition_name,
                             sequence,packing_list=None):
    """ calls the workflow for the packing list """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list,
          transition_name, wf_id='packing_list_workflow')

  def stepSetReadyPackingList(self, sequence=None, sequence_list=None, **kw):
    """ set the Packing List as Ready. This must build the invoice. """
    self.modifyPackingListState('set_ready_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'ready')

  def stepSetReadyNewPackingList(self, sequence=None,
                                 sequence_list=None, **kw):
    """ set the Packing List as Ready. This must build the invoice. """
    packing_list = sequence.get('new_packing_list')
    self.modifyPackingListState('set_ready_action', sequence=sequence,
                                packing_list=packing_list)
    self.assertEquals(packing_list.getSimulationState(), 'ready')

  def stepStartPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('start_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'started')

  def stepStartNewPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('new_packing_list')
    self.modifyPackingListState('start_action', sequence=sequence,
                                packing_list=packing_list)
    self.assertEquals(packing_list.getSimulationState(), 'started')

  def stepStopPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('stop_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'stopped')

  def stepDeliverPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('deliver_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'delivered')

  def stepCancelPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('cancel_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'cancelled')


  def modifyInvoiceState(self, transition_name,
                             sequence,invoice=None):
    """ calls the workflow for the invoice """
    if invoice is None:
      invoice = sequence.get('invoice')
    invoice.portal_workflow.doActionFor(invoice,
          transition_name, wf_id='accounting_workflow')

  def stepConfirmInvoice(self, sequence=None, sequence_list=None, **kw):
    """ set the Packing List as Ready. This must build the invoice. """
    self.modifyInvoiceState('confirm_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEquals(invoice.getSimulationState(), 'confirmed')

  def stepSetReadyInvoice(self, sequence=None, sequence_list=None, **kw):
    """ set the Packing List as Ready. This must build the invoice. """
    self.modifyInvoiceState('set_ready_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEquals(invoice.getSimulationState(), 'ready')

  def stepSetReadyNewInvoice(self, sequence=None,
                                 sequence_list=None, **kw):
    """ set the Packing List as Ready. This must build the invoice. """
    invoice = sequence.get('new_invoice')
    self.modifyInvoiceState('set_ready_action', sequence=sequence,
                                invoice=invoice)
    self.assertEquals(invoice.getSimulationState(), 'ready')

  def stepStartInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('start_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEquals(invoice.getSimulationState(), 'started')

  def stepStartNewInvoice(self, sequence=None, sequence_list=None, **kw):
    invoice = sequence.get('new_invoice')
    self.modifyInvoiceState('start_action', sequence=sequence,
                                invoice=invoice)
    self.assertEquals(invoice.getSimulationState(), 'started')

  def stepStopInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('stop_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEquals(invoice.getSimulationState(), 'stopped')

  def stepDeliverInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('deliver_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEquals(invoice.getSimulationState(), 'delivered')

  def stepCancelInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('cancel_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEquals(invoice.getSimulationState(), 'cancelled')


  def stepSwitchPackingLists(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    new_packing_list = sequence.get('new_packing_list')
    #invoice = new_packing_list.getDefaultCausalityRelatedValue(
        #portal_type=self.invoice_portal_type)
    sequence.edit(packing_list=new_packing_list,
        new_packing_list=packing_list)#, invoice=invoice)

  def stepSwitchInvoices(self, sequence=None, sequence_list=None, **kw):
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    sequence.edit(invoice=new_invoice, new_invoice=invoice)

  def stepCheckPackingListSimulation(self, sequence=None, sequence_list=None, **kw):
    """ checks that simulation movements related to the packing list are OK """
    packing_list = sequence.get('packing_list')
    order = sequence.get('order')
    order_root_applied_rule = order.getCausalityRelatedValueList(
                                  portal_type = 'Applied Rule')[0]
    # check simulation movements from this packing list
    for movement in packing_list.getMovementList() :
      simulation_movement_list = movement.getOrderRelatedValueList()
      self.assertNotEquals(len(simulation_movement_list), 0)
      total_quantity = 0
      for simulation_movement in simulation_movement_list :
        total_quantity += simulation_movement.getQuantity()
        # check that those movements come from the same root applied
        # rule than the order.
        self.assertEquals( simulation_movement.getRootAppliedRule(),
                           order_root_applied_rule)
      self.assertEquals(total_quantity, movement.getQuantity())

  def stepCheckInvoiceBuilding(self, sequence=None, sequence_list=None, **kw):
    """
    checks that the invoice is built with the default_invoice_builder
    """
    packing_list = sequence.get('packing_list')
    related_invoice_list = packing_list.getCausalityRelatedValueList(
                     portal_type=self.sale_invoice_transaction_portal_type)

    packing_list_building_state = 'started'
    packing_list_state = packing_list.getSimulationState()
    if packing_list_state != packing_list_building_state :
      self.assertEquals(0, len(related_invoice_list))
    else:
      self.assertEquals(1, len(related_invoice_list))

      invoice = related_invoice_list[0].getObject()
      self.failUnless(invoice is not None)
      # Invoices created by Delivery Builder are in planned state
      self.assertEquals(invoice.getSimulationState(), 'planned')

      # Get the list of simulation movements of packing list ...
      packing_list_simulation_movement_list = []
      for packing_list_movement in packing_list.getMovementList():
           packing_list_simulation_movement_list.extend(
                packing_list_movement.getDeliveryRelatedValueList())
      # ... invoice simulation movement are their childrens.
      simulation_movement_list = []
      for p_l_simulation_movement in packing_list_simulation_movement_list :
        for applied_rule in p_l_simulation_movement.objectValues() :
          simulation_movement_list.extend(applied_rule.objectValues())

      # First, test if each Simulation Movement is related to an
      # Invoice Movement
      invoice_relative_url = invoice.getRelativeUrl()
      for simulation_movement in simulation_movement_list:
        invoice_movement_list = simulation_movement.getDeliveryValueList()
        self.assertEquals(len(invoice_movement_list), 1)
        invoice_movement = invoice_movement_list[0]
        self.failUnless(invoice_movement is not None)
        self.assert_(invoice_movement.getRelativeUrl().\
                              startswith(invoice_relative_url))

      # Then, test if each Invoice movement is equals to the sum of somes
      # Simulation Movements
      for invoice_movement in invoice.getMovementList(portal_type = [
                          self.sale_invoice_cell_portal_type,
                          self.sale_invoice_line_portal_type]) :
        related_simulation_movement_list = invoice_movement.\
                 getDeliveryRelatedValueList(portal_type='Simulation Movement')
        quantity = 0
        total_price = 0
        invoice_movement_quantity = invoice_movement.getQuantity()
        for related_simulation_movement in related_simulation_movement_list:
          quantity += related_simulation_movement.getQuantity()
          total_price += related_simulation_movement.getPrice() *\
                         related_simulation_movement.getQuantity()
          # Test resource
          self.assertEquals(invoice_movement.getResource(), \
                            related_simulation_movement.getResource())
          # Test resource variation
          self.assertEquals(invoice_movement.getVariationText(), \
                            related_simulation_movement.getVariationText())
          self.assertEquals(invoice_movement.getVariationCategoryList(), \
                        related_simulation_movement.getVariationCategoryList())
          # Test acquisition
          self.checkAcquisition(invoice_movement,
                                related_simulation_movement)
          # Test delivery ratio
          self.assertEquals(related_simulation_movement.getQuantity() /\
                            invoice_movement_quantity, \
                            related_simulation_movement.getDeliveryRatio())

        self.assertEquals(quantity, invoice_movement.getQuantity())
        # Test price
        self.assertEquals(total_price / quantity, invoice_movement.getPrice())

      sequence.edit(invoice = invoice)

      # Test causality
      self.assertEquals(len(invoice.getCausalityValueList(
                      portal_type = self.packing_list_portal_type)), 1)
      self.assertEquals(invoice.getCausalityValue(), packing_list)

      # Finally, test getTotalQuantity and getTotalPrice on Invoice
      self.assertEquals(packing_list.getTotalQuantity(),
                        invoice.getTotalQuantity())
      self.assertEquals(packing_list.getTotalPrice(),
                        invoice.getTotalPrice())


  def stepCreateSimpleSaleOrder(self, sequence, **kw):
    """ create the Order for our test.
      It contains one line :
        resource : product_module/notebook
        quantity : 10
        price : 100
    """
    source_section = sequence.get('source_section')
    source = sequence.get('source')
    destination_section = sequence.get('destination_section')
    destination = sequence.get('destination')
    product = sequence.get('product')

    order_module = self.getSaleOrderModule()
    order = order_module.newContent(portal_type=self.order_portal_type)
    order.setStartDate(DateTime('2004-11-20'))
    order.setStopDate(DateTime('2004-11-24'))
    order.setDestinationValue(destination)
    order.setDestinationSectionValue(destination_section)
    order.setSourceValue(source)
    order.setSourceSectionValue(source_section)
    order_line = order.newContent(portal_type=order_line_portal_type, id='1')
    order_line.setResourceValue(product)
    order_line.setQuantity(10)
    order_line.setPrice(100)
    self.assertEquals(len(order.checkConsistency()), 0)
    sequence.edit(
      order = order,
      order_line = order_line,
      order_line_list = [order_line])
    self.assertEquals(order_line.getTotalPrice(), 10*100)

  def stepCheckOrderRule(self, sequence=None, sequence_list=None, **kw):
    """Check we have a related Order Rule"""
    order = sequence.get('order')
    simulation_tool = self.getSimulationTool()
    # Check that there is an applied rule for our packing list
    rule_list = [x for x in simulation_tool.objectValues()
                            if x.getCausalityValue()==order]
    self.assertNotEquals(len(rule_list), 0)
    sequence.edit(order_rule_list = rule_list)

    self.assertEquals(len(order.getMovementList()),
                  sum([len(rule.objectIds()) for rule in rule_list]))

  def stepCheckInvoicingRule(self, sequence=None, sequence_list=None, **kw):
    """
    Checks that the invoicing rule is applied and its values are correct.
    """
    order_rule_list = sequence.get('order_rule_list')
    invoicing_rule_list = []
    invoice_transaction_rule_list = []
    for order_rule in order_rule_list :
      for order_simulation_movement in order_rule.objectValues() :
        temp_invoicing_rule_list = order_simulation_movement.objectValues()
        self.assertEquals(len(temp_invoicing_rule_list), 1)
        invoicing_rule_list.extend(order_simulation_movement.objectValues())
    sequence.edit(invoicing_rule_list=invoicing_rule_list)
    invoicing_rule = invoicing_rule_list[0]
    sequence.edit(invoicing_rule = invoicing_rule)
    for invoicing_rule in invoicing_rule_list:
      self.assertEquals(invoicing_rule.getSpecialiseId(),
          'default_invoicing_rule')
      self.assertEquals(invoicing_rule.getPortalType(),
          'Applied Rule')
      simulation_movement_list = invoicing_rule.objectValues()
      self.assertNotEquals(len(simulation_movement_list), 0)
      for simulation_movement in simulation_movement_list :
        invoice_transaction_rule_list.extend(simulation_movement.objectValues())
        resource_list = sequence.get('resource_list')
        self.assertEquals(simulation_movement.getPortalType(),
                          'Simulation Movement')
        self.assertTrue(simulation_movement.getResourceValue() in
            resource_list)
        self.assertTrue(simulation_movement.isConvergent())
        # TODO: What is the invoice dates supposed to be ?
        # is this done through profiles ?
        #self.assertEquals(simulation_movement.getStartDate(),
        #           sequence.get('order').getStartDate())
        #self.assertEquals(simulation_movement.getStopDate(),
        #            sequence.get('order').getStopDate())
    sequence.edit(invoice_transaction_rule_list=invoice_transaction_rule_list)

  def stepCheckInvoiceTransactionRule(self, sequence=None, sequence_list=None,
      **kw):
    """
    Checks that the invoice_transaction_rule is expanded and its movements are
    consistent with its parent movement
    """
    invoice_transaction_rule_list = \
        sequence.get('invoice_transaction_rule_list')
    for invoice_transaction_rule in invoice_transaction_rule_list:
      parent_movement = aq_parent(invoice_transaction_rule)
      self.assertEquals(3, len(invoice_transaction_rule.objectValues()))
      for line_id, line_source_id, line_destination_id, line_ratio in \
          self.transaction_line_definition_list:
        movement = getattr(invoice_transaction_rule, line_id, None)
        self.assertTrue(movement is not None)
        self.assertEquals(movement.getCorrectedQuantity(), parent_movement.getPrice() *
            parent_movement.getCorrectedQuantity() * line_ratio)
        self.assertEquals(movement.getSourceId(), line_source_id)
        self.assertEquals(movement.getDestinationId(), line_destination_id)
        self.assertEquals(movement.getStartDate(),
            parent_movement.getStartDate())
        self.assertEquals(movement.getStopDate(),
            parent_movement.getStopDate())

  def stepCheckInvoicesConsistency(self, sequence=None, sequence_list=None,
      **kw):
    """
    Checks that all invoices are consistent:
    - transaction lines match invoice lines
    - no movement is divergent
    """
    invoice_list = self.getPortal()['accounting_module'].objectValues()
    for invoice in invoice_list:
      accounting_state_list = \
          list(self.getPortal().getPortalCurrentInventoryStateList())
      accounting_state_list.append('cancelled')
      if invoice.getSimulationState() in accounting_state_list:
        invoice_line_list = invoice.contentValues(
            portal_type=self.invoice_line_portal_type)
        invoice_transaction_line_list = invoice.contentValues(
            portal_type=self.invoice_transaction_line_portal_type)
        self.assertEquals(3, len(invoice_transaction_line_list))
        expected_price = 0.0
        for line in invoice_line_list:
          expected_price += line.getTotalPrice()
        for line_id, line_source, line_dest, line_ratio in \
            self.transaction_line_definition_list:
          for line in invoice.contentValues(
              portal_type=self.invoice_transaction_line_portal_type):
            if line.getSource() == 'account_module/%s' % line_source and \
                line.getDestination() == 'account_module/%s' % line_dest:
              break
          else:
            self.fail('No line found that matches %s' % line_id)
          self.assertEquals(line.getQuantity(), expected_price * line_ratio)

  def stepCheckDeliveryRuleForDeferred(
                      self, sequence=None, sequence_list=None, **kw):
    """ Checks that a delivery rule has been created when we took 'split
        and defer' decision on the divergeant Packing List. """
    # TODO

  def stepCheckDeliveryRuleIsEmpty(
                      self, sequence=None, sequence_list=None, **kw):
    """ Checks that an empty delivery rule is created for the
        convergeant Packing List"""
    packing_list = sequence.get('packing_list')
    self.failUnless(packing_list is not None)
    simulation_tool = self.getSimulationTool()
    # Check that there is an applied rule for our packing list
    rule_list = [x for x in simulation_tool.objectValues()
                          if x.getCausalityValue()==packing_list]
    self.assertEquals(len(rule_list),1)
    packing_list_rule = rule_list[0]
    sequence.edit(packing_list_rule=packing_list_rule)
    rule_line_list = packing_list_rule.objectValues()
    packing_list_line_list = packing_list.objectValues()
    self.assertEquals(len(packing_list_line_list),
                      len(rule_line_list))
    self.assertEquals(1, len(rule_line_list))
    rule_line = rule_line_list[0]
    packing_list_line = packing_list_line_list[0]
    self.assertEquals(rule_line.getQuantity(), 10)
    self.assertEquals(rule_line.getPrice(), 100)
    self.assertEquals(rule_line.getDeliveryValue(),
                      packing_list_line)
    self.assertEquals(rule_line.getStartDate(),
                      packing_list_line.getStartDate())
    self.assertEquals(rule_line.getStopDate(),
                      packing_list_line.getStopDate())
    self.assertEquals(rule_line.getPortalType(),
                      'Simulation Movement')


  def stepCheckPackingList(self,sequence=None, sequence_list=None,**kw):
    """  """
    packing_list_module = self.getSalePackingListModule()
    order_rule = sequence.get('order_rule')
    order = sequence.get('order')
    sale_packing_list_list = []
    for o in packing_list_module.objectValues():
      if o.getCausalityValue() == order:
        sale_packing_list_list.append(o)
    self.assertEquals(len(sale_packing_list_list), 1)
    sale_packing_list = sale_packing_list_list[0]
    sale_packing_list_line_list = sale_packing_list.objectValues()
    self.assertEquals(len(sale_packing_list_line_list),1)
    sale_packing_list_line = sale_packing_list_line_list[0]
    product = sequence.get('resource')
    self.assertEquals(sale_packing_list_line.getResourceValue(),
                      product)
    self.assertEquals(sale_packing_list_line.getPrice(),
                      self.price1)
    LOG('sale_packing_list_line.showDict()',0,
          sale_packing_list_line.showDict())
    self.assertEquals(sale_packing_list_line.getQuantity(),
                      self.quantity1)
    self.assertEquals(sale_packing_list_line.getTotalPrice(),
                      self.total_price1)
    sequence.edit(packing_list = sale_packing_list)

  def stepCheckTwoInvoices(self,sequence=None, sequence_list=None, **kw):
    """ checks invoice properties are well set. """
    # New we will check that we have two invoices
    packing_list = sequence.get('packing_list')
    invoice_list = packing_list.getCausalityRelatedValueList(
         portal_type=self.sale_invoice_transaction_portal_type)
    self.assertEquals(len(invoice_list),1)
    invoice = invoice_list[0]
    sequence.edit(invoice=invoice)
    new_packing_list = sequence.get('new_packing_list')
    new_invoice_list = new_packing_list.getCausalityRelatedValueList(
        portal_type=self.sale_invoice_transaction_portal_type)
    self.assertEquals(len(new_invoice_list),1)
    new_invoice = new_invoice_list[0]
    sequence.edit(new_invoice=new_invoice)

  def stepConfirmTwoInvoices(self,sequence=None, sequence_list=None, **kw):
    """ confirme both invoices. """
    portal = self.getPortal()
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    portal.portal_workflow.doActionFor(invoice,
        'confirm_action',wf_id='accounting_workflow')
    portal.portal_workflow.doActionFor(new_invoice,
        'confirm_action',wf_id='accounting_workflow')

  def stepCheckTwoInvoicesTransactionLines(self,sequence=None,
                                           sequence_list=None, **kw):
    """ checks invoice properties are well set. """
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    self.assertEquals(3,len(invoice.objectValues(
        portal_type=self.sale_invoice_transaction_line_portal_type)))
    self.assertEquals(3,len(new_invoice.objectValues(
        portal_type=self.sale_invoice_transaction_line_portal_type)))
    account_module = self.getAccountModule()
    found_dict = {}
    for line in invoice.objectValues(
        portal_type=self.sale_invoice_transaction_line_portal_type):
      source_id = line.getSourceId()
      found_dict[source_id] = line.getQuantity()
    total_price = (self.default_quantity-1) * self.default_price
    expected_dict = {
      'sale' : total_price,
      'receivable_vat' : total_price * self.vat_rate,
      'customer' : - (total_price + total_price * self.vat_rate)
      }
    self.failIfDifferentSet(expected_dict.keys(),found_dict.keys())
    for key in found_dict.keys():
      self.assertAlmostEquals(expected_dict[key],found_dict[key],places=2)
    found_dict = {}
    for line in new_invoice.objectValues(
        portal_type=self.sale_invoice_transaction_line_portal_type):
      source_id = line.getSourceId()
      found_dict[source_id] = line.getQuantity()
    total_price = 1 * self.default_price
    expected_dict = {
      'sale' : total_price,
      'receivable_vat' : total_price * self.vat_rate,
      'customer' : - (total_price + total_price * self.vat_rate)
      }
    self.failIfDifferentSet(expected_dict.keys(), found_dict.keys())
    for key in found_dict.keys():
      self.assertAlmostEquals(expected_dict[key], found_dict[key], places=2)

  def stepRebuildAndCheckNothingIsCreated(self, sequence=None,
                                           sequence_list=None, **kw):
    """Rebuilds with sale_invoice_builder and checks nothing more is
    created. """
    accounting_module = self.getAccountingModule()
    sale_invoice_transaction_count = len(accounting_module.objectValues())
    for builder in self.getPortal().portal_deliveries.objectValues():
      builder.build()
    self.assertEquals(sale_invoice_transaction_count,
                      len(accounting_module.objectValues()))

  def stepModifyInvoicesDate(self, sequence=None,
                                           sequence_list=None, **kw):
    """Change invoice date"""
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    invoice.edit(start_date=self.datetime,
                 stop_date=self.datetime+1)
    new_invoice.edit(start_date=self.datetime,
                 stop_date=self.datetime+1)

  def stepRemoveDateMovementGroupForTransactionBuilder(self, sequence=None,
            sequence_list=None, **kw):
    """
    Remove DateMovementGroup
    """
    portal = self.getPortal()
    builder = portal.portal_deliveries.sale_invoice_transaction_builder
    previous_list = builder.getDeliveryCollectOrderList()
    new_list = [x for x in previous_list if x != 'DateMovementGroup']
    new_list.append('ParentExplanationMovementGroup')
    builder.setDeliveryCollectOrderList(new_list)

  def stepEditInvoice(self, sequence=None, sequence_list=None, **kw):
    """Edit the current invoice, to trigger updateAppliedRule."""
    invoice = sequence.get('invoice')
    invoice.edit()

    # call updateAppliedRule directly, don't rely on edit interactions
    rule_id = 'default_invoice_rule'
    self.failUnless(rule_id in
                    self.getPortal().portal_rules.objectIds())
    invoice.updateAppliedRule(rule_id=rule_id)

  def stepCheckInvoiceRuleNotAppliedOnInvoiceEdit(self,
                    sequence=None, sequence_list=None, **kw):
    """If we call edit on the invoice, invoice rule should not be
    applied on lines created by delivery builder."""
    invoice = sequence.get('invoice')
    # FIXME: empty applied rule should not be created
    #self.assertEquals(len(invoice.getCausalityRelatedValueList(
    #         portal_type=self.applied_rule_portal_type)), 0)
    for invoice_mvt in invoice.getMovementList():
      self.assertEquals(len(invoice_mvt.getOrderRelatedValueList(
            portal_type=self.simulation_movement_portal_type)), 0)

  def stepEditPackingList(self, sequence=None, sequence_list=None, **kw):
    """Edit the current packing list, to trigger updateAppliedRule."""
    packing_list = sequence.get('packing_list')
    packing_list.edit()

    # call updateAppliedRule directly, don't rely on edit interactions
    rule_id = 'default_delivery_rule'
    self.failUnless(rule_id in
                    self.getPortal().portal_rules.objectIds())
    packing_list.updateAppliedRule(rule_id=rule_id)

  def stepCheckDeliveryRuleNotAppliedOnPackingListEdit(self,
                    sequence=None, sequence_list=None, **kw):
    """If we call edit on the packing list, delivery rule should not be
    applied on lines created by delivery builder."""
    packing_list = sequence.get('packing_list')
    # FIXME: empty applied rule should not be created
    #self.assertEquals(len(packing_list.getCausalityRelatedValueList(
    #         portal_type=self.applied_rule_portal_type)), 0)
    for delivery_mvt in packing_list.getMovementList():
      self.assertEquals(len(delivery_mvt.getOrderRelatedValueList(
            portal_type=self.simulation_movement_portal_type)), 0)

  def stepDecreaseInvoiceLineQuantity(self, sequence=None, sequence_list=None,
      **kw):
    """
    Set a decreased quantity on invoice lines
    """
    invoice = sequence.get('invoice')
    quantity = sequence.get('line_quantity',default=self.default_quantity)
    quantity = quantity - 1
    sequence.edit(line_quantity=quantity)
    for invoice_line in invoice.objectValues(
        portal_type=self.invoice_line_portal_type):
      invoice_line.edit(quantity=quantity)
    sequence.edit(last_delta = sequence.get('last_delta', 0.0) - 1.0)

  def stepIncreaseInvoiceLineQuantity(self, sequence=None, sequence_list=None,
      **kw):
    """
    Set a Increased quantity on invoice lines
    """
    invoice = sequence.get('invoice')
    quantity = sequence.get('line_quantity',default=self.default_quantity)
    quantity = quantity + 1
    sequence.edit(line_quantity=quantity)
    for invoice_line in invoice.objectValues(
        portal_type=self.invoice_line_portal_type):
      invoice_line.edit(quantity=quantity)
    sequence.edit(last_delta = sequence.get('last_delta', 0.0) + 1.0)

  def stepSetInvoiceLineQuantityToZero(self, sequence=None, sequence_list=None,
      **kw):
    """
    Set the quantity on invoice lines to zero
    """
    invoice = sequence.get('invoice')
    #default_quantity = sequence.get('line_quantity',default_quantity)
    quantity = 0.0
    sequence.edit(line_quantity=quantity)
    for invoice_line in invoice.objectValues(
        portal_type=self.invoice_line_portal_type):
      invoice_line.edit(quantity=quantity)
    sequence.edit(last_delta = - self.default_quantity)

  def stepChangeInvoiceStartDate(self, sequence=None, sequence_list=None, **kw):
    """
      Change the start_date of the invoice.
    """
    invoice = sequence.get('invoice')
    invoice.edit(start_date=self.datetime + 15)

  def stepCheckInvoiceIsCalculating(self, sequence=None, sequence_list=None,
      **kw):
    """
    Test if invoice is calculating
    """
    invoice = sequence.get('invoice')
    self.assertEquals('calculating',invoice.getCausalityState())

  def stepCheckInvoiceIsDiverged(self, sequence=None, sequence_list=None,
      **kw):
    """
    Test if invoice is diverged
    """
    invoice = sequence.get('invoice')
    self.assertEquals('diverged',invoice.getCausalityState())

  def stepCheckInvoiceIsSolved(self, sequence=None, sequence_list=None,
      **kw):
    """
    Test if invoice is solved
    """
    invoice = sequence.get('invoice')
    self.assertEquals('solved',invoice.getCausalityState())

  def stepCheckInvoiceIsDivergent(self, sequence=None, sequence_list=None,
      **kw):
    """
    Test if invoice is divergent
    """
    invoice = sequence.get('invoice')
    self.assertTrue(invoice.isDivergent())

  def stepCheckInvoiceIsNotDivergent(self, sequence=None, sequence_list=None,
      **kw):
    """
    Test if invoice is not divergent
    """
    invoice = sequence.get('invoice')
    self.assertFalse(invoice.isDivergent())

  def stepSplitAndDeferInvoice(self, sequence=None, sequence_list=None,
      **kw):
    """
    split and defer at the invoice level
    """
    invoice = sequence.get('invoice')
    invoice.portal_workflow.doActionFor(invoice,'split_prevision_action',
        wf_id='invoice_causality_workflow', start_date=self.datetime +
        15, stop_date=self.datetime + 25)

  def stepAcceptDecisionInvoice(self, sequence=None, sequence_list=None,
      **kw):
    """
    accept decision at the invoice level
    """
    invoice = sequence.get('invoice')
    invoice.portal_workflow.doActionFor(invoice,'accept_decision_action')

  def stepCheckInvoiceSplitted(self, sequence=None, sequence_list=None, **kw):
    """
    Test if invoice was splitted
    """
    packing_list = sequence.get('packing_list')
    invoice_list = packing_list.getCausalityRelatedValueList(
        portal_type=self.invoice_portal_type)
    self.assertEquals(2,len(invoice_list))
    invoice1 = None
    invoice2 = None
    for invoice in invoice_list:
      if invoice.getUid() == sequence.get('invoice').getUid():
        invoice1 = invoice
      else:
        invoice2 = invoice
    sequence.edit(new_invoice=invoice2)
    for line in invoice1.objectValues(
          portal_type=self.invoice_line_portal_type):
      self.assertEquals(self.default_quantity-1,line.getQuantity())
    for line in invoice2.objectValues(
          portal_type=self.invoice_line_portal_type):
      self.assertEquals(1,line.getQuantity())

  def stepCheckInvoiceNotSplitted(self, sequence=None, sequence_list=None, **kw):
    """
    Test if invoice was not splitted
    """
    packing_list = sequence.get('packing_list')
    invoice_list = packing_list.getCausalityRelatedValueList(
        portal_type=self.invoice_portal_type)
    self.assertEquals(1,len(invoice_list))
    invoice1 = None
    for invoice in invoice_list:
      if invoice.getUid() == sequence.get('invoice').getUid():
        invoice1 = invoice
    last_delta = sequence.get('last_delta', 0.0)
    for line in invoice1.objectValues(
        portal_type=self.invoice_line_portal_type):
      self.assertEquals(self.default_quantity + last_delta,
          line.getQuantity())

  # default sequence for one line of not varianted resource.
  PACKING_LIST_DEFAULT_SEQUENCE = """
      stepCreateSaleInvoiceTransactionRule
      stepCreateEntities
      stepCreateCurrency
      stepCreateOrder
      stepSetOrderProfile
      stepSetOrderPriceCurrency
      stepCreateNotVariatedResource
      stepTic
      stepCreateOrderLine
      stepSetOrderLineResource
      stepSetOrderLineDefaultValues
      stepOrderOrder
      stepTic
      stepCheckDeliveryBuilding
      stepConfirmOrder
      stepTic
      stepCheckOrderRule
      stepCheckOrderSimulation
      stepCheckDeliveryBuilding
      stepAddPackingListContainer
      stepAddPackingListContainerLine
      stepSetContainerLineFullQuantity
      stepTic
      stepCheckPackingListIsPacked
    """

  # default sequence for two lines of not varianted resource.
  PACKING_LIST_TWO_LINES_DEFAULT_SEQUENCE = """
      stepCreateSaleInvoiceTransactionRule
      stepCreateEntities
      stepCreateCurrency
      stepCreateOrder
      stepSetOrderProfile
      stepSetOrderPriceCurrency
      stepCreateNotVariatedResource
      stepTic
      stepCreateOrderLine
      stepSetOrderLineResource
      stepSetOrderLineDefaultValues
      stepCreateNotVariatedResource
      stepTic
      stepCreateOrderLine
      stepSetOrderLineResource
      stepSetOrderLineDefaultValues
      stepOrderOrder
      stepTic
      stepCheckDeliveryBuilding
      stepConfirmOrder
      stepTic
      stepCheckOrderRule
      stepCheckOrderSimulation
      stepCheckDeliveryBuilding
      stepAddPackingListContainer
      stepAddPackingListContainerLine
      stepTic
      stepSetContainerFullQuantity
      stepTic
      stepCheckPackingListIsPacked
    """

  # default sequence for one line of not varianted resource.
  TWO_PACKING_LIST_DEFAULT_SEQUENCE = """
      stepCreateSaleInvoiceTransactionRule
      stepCreateEntities
      stepCreateCurrency
      stepCreateOrder
      stepSetOrderProfile
      stepSetOrderPriceCurrency
      stepCreateNotVariatedResource
      stepTic
      stepCreateOrderLine
      stepSetOrderLineResource
      stepSetOrderLineDefaultValues
      stepOrderOrder
      stepTic
      stepCheckDeliveryBuilding
      stepConfirmOrder
      stepTic
      stepCheckOrderRule
      stepCheckOrderSimulation
      stepCheckDeliveryBuilding
      stepDecreasePackingListLineQuantity
      stepCheckPackingListIsCalculating
      stepSplitAndDeferPackingList
      stepTic
      stepCheckPackingListIsSolved
      stepCheckPackingListSplitted
      stepAddPackingListContainer
      stepAddPackingListContainerLine
      stepSetContainerLineFullQuantity
      stepTic
      stepCheckPackingListIsPacked
      stepDefineNewPackingListContainer
      stepTic
      stepCheckNewPackingListIsPacked
    """

  def test_01_SimpleInvoice(self, quiet=0, run=RUN_ALL_TESTS):
    """
    Checks that a Simple Invoice is created from a Packing List
    """
    if not run: return
    self.logMessage('Simple Invoice')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepTic
        stepStartPackingList
        stepCheckInvoicingRule
        stepTic
        stepCheckInvoiceBuilding
        stepRebuildAndCheckNothingIsCreated
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self)

  def test_02_TwoInvoicesFromTwoPackingList(self, quiet=0, run=RUN_ALL_TESTS):
    """
    This test was created for the following bug:
        - an order is created and confirmed
        - the packing list is split
        - the 2 packing list are delivered (at different date)
        - 2 invoices are built, then we set the same date on both of them
        - the accounting rules are generated and put in only one invoice !!,
          so we have an invoice with twice the number of accounting rules
          and an invoice with no accounting rules. both invoices are wrong
    """
    if not run: return
    self.logMessage('Two Invoices from Two Packing List')
    sequence_list = SequenceList()
    for base_sequence in (self.TWO_PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepSetReadyNewPackingList
        stepTic
        stepStartPackingList
        stepStartNewPackingList
        stepTic
        stepCheckTwoInvoices
        stepRemoveDateMovementGroupForTransactionBuilder
        stepConfirmTwoInvoices
        stepTic
        stepCheckTwoInvoicesTransactionLines
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self)

  def test_03_InvoiceEditAndInvoiceRule(self, quiet=0, run=RUN_ALL_TESTS):
    """
    Invoice Rule should not be applied on invoice lines created from\
    Packing List.

    We want to prevent this from happening:
      - Create a packing list
      - An invoice is created from packing list
      - Invoice is edited, updateAppliedRule is called
      - A new Invoice Rule is created for this invoice, and accounting
        movements for this invoice are present twice in the simulation.
    """
    if not run: return
    self.logMessage('Invoice Edit')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepTic
        stepStartPackingList
        stepCheckInvoicingRule
        stepTic
        stepCheckInvoiceBuilding
        stepEditInvoice
        stepCheckInvoiceRuleNotAppliedOnInvoiceEdit
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self)

  def test_04_PackingListEditAndInvoiceRule(self, quiet=0, run=RUN_ALL_TESTS):
    """
    Delivery Rule should not be applied on packing list lines created\
    from Order.
    """
    if not run: return
    self.logMessage('Packing List Edit')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepEditPackingList
        stepCheckDeliveryRuleNotAppliedOnPackingListEdit
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self)

  def test_05_InvoiceEditPackingListLine(self, quiet=0, run=RUN_ALL_TESTS):
    """
    Checks that editing a Packing List Line still creates a correct
    Invoice
    """
    if not run: return
    self.logMessage('Packing List Line Edit')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
    """
      stepEditPackingListLine
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
    """)
    sequence_list.play(self)

  def test_06_InvoiceDeletePackingListLine(self, quiet=0,
      run=RUN_ALL_TESTS):
    """
    Checks that deleting a Packing List Line still creates a correct
    Invoice
    """
    if not run: return
    self.logMessage('Packing List Line Delete')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_TWO_LINES_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
    """
      stepDeletePackingListLine
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
    """)
    sequence_list.play(self)

  def test_07_InvoiceAddPackingListLine(self, quiet=0, run=RUN_ALL_TESTS):
    """
    Checks that adding a Packing List Line still creates a correct
    Invoice
    """
    if not run: return
    self.logMessage('Packing List Line Add')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE,
        self.PACKING_LIST_TWO_LINES_DEFAULT_SEQUENCE) :
      sequence_list.addSequenceString(
        base_sequence +
    """
      stepAddPackingListLine
      stepSetContainerFullQuantity
      stepTic
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
    """)
    sequence_list.play(self)

  def test_08_InvoiceDecreaseQuantity(self, quiet=0, run=RUN_ALL_TESTS):
    """
    Change the quantity of a Invoice Line,
    check that the invoice is divergent,
    then split and defer, and check everything is solved
    """
    if not run: return
    self.logMessage('Invoice Decrease Qantity')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding

    stepDecreaseInvoiceLineQuantity
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepSplitAndDeferInvoice
    stepTic

    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved
    stepCheckInvoiceSplitted

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence)

  def test_09_InvoiceChangeStartDate(self, quiet=0, run=RUN_ALL_TESTS):
    """
    Change the start_date of a Invoice Line,
    check that the invoice is divergent,
    then accept decision, and check everything is solved
    """
    if not run: return
    self.logMessage('Invoice Change Sart Date')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding

    stepChangeInvoiceStartDate
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepAcceptDecisionInvoice
    stepTic

    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence)

  def test_10_AcceptDecisionOnPackingList(self, quiet=0, run=RUN_ALL_TESTS):
    """
    - Increase or Decrease the quantity of a Packing List line
    - Accept Decision on Packing List
    - Packing List must not be divergent and use new quantity
    - Invoice must not be divergent and use new quantity
    """
    if not run: return
    self.logMessage('InvoiceAcceptDecisionOnPackingList')
    end_sequence = \
    """
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepAcceptDecisionPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding

    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepConfirmInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """

    mid_sequence_list = ["""
    stepCheckInvoicingRule
    stepDecreasePackingListLineQuantity
    """, """
    stepCheckInvoicingRule
    stepIncreasePackingListLineQuantity
    """]

    sequence_list = SequenceList()
    for seq in mid_sequence_list:
      sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
          seq + end_sequence
      sequence_list.addSequenceString(sequence)
    sequence_list.play(self)

  def test_11_AcceptDecisionOnPackingListAndInvoice(self, quiet=0,
      run=RUN_ALL_TESTS):
    """
    - Increase or Decrease the quantity of a Packing List line
    - Accept Decision on Packing List
    - Packing List must not be divergent and use new quantity
    - Put old quantity on Invoice
    - Accept Decision on Invoice
    - Packing List must not be divergent and use new quantity
    - Invoice must not be divergent and use old quantity
    """
    if not run: return
    self.logMessage('InvoiceAcceptDecisionOnPackingListAndInvoice')
    mid_sequence = \
    """
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepAcceptDecisionPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding

    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule
    """
    end_sequence = \
    """
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionInvoice
    stepTic
    stepConfirmInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule
    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """

    mid_sequence_list = [("""
    stepCheckInvoicingRule
    stepDecreasePackingListLineQuantity
    """, """
    stepIncreaseInvoiceLineQuantity
    stepTic
    """), ("""
    stepCheckInvoicingRule
    stepIncreasePackingListLineQuantity
    """, """
    stepDecreaseInvoiceLineQuantity
    stepTic
    """)]

    sequence_list = SequenceList()
    for seq1, seq2 in mid_sequence_list:
      sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
          seq1 + mid_sequence + seq2 + end_sequence
      sequence_list.addSequenceString(sequence)
    sequence_list.play(self)

  def test_12_SplitPackingListAndAcceptInvoice(self, quiet=0,
      run=RUN_ALL_TESTS):
    """
    - Decrease the quantity of a Packing List line
    - Split and Defer on Packing List
    - Packing List must not be divergent and use new quantity
    - splitted Packing List must not be divergent and use old - new quantity

    - Put old quantity on Invoice1
    - Accept Decision on Invoice1
    - Packing List must not be divergent and use new quantity
    - splitted Packing List must not be divergent and use old - new quantity
    - Invoice1 must not be divergent and use old quantity

    - set Invoice2 quantity to 0
    - Accept Decision on Invoice2
    - Packing List must not be divergent and use new quantity
    - splitted Packing List must not be divergent and use old - new quantity
    - Invoice1 must not be divergent and use old quantity
    - Invoice2 must not be divergent and use 0 as quantity
    """
    if not run: return
    self.logMessage('InvoiceSplitPackingListAndAcceptInvoice')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepCheckInvoicingRule
    stepDecreasePackingListLineQuantity
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepSplitAndDeferPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListSplitted

    stepIncreaseInvoiceLineQuantity
    stepCheckInvoiceIsCalculating
    stepAcceptDecisionInvoice
    stepTic
    stepConfirmInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsSolved
    stepCheckInvoiceNotSplitted
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency

    stepSwitchPackingLists

    stepAddPackingListContainer
    stepSetContainerFullQuantity
    stepTic
    stepCheckPackingListIsSolved
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved

    stepSetInvoiceLineQuantityToZero
    stepCheckInvoiceIsCalculating
    stepAcceptDecisionInvoice
    stepTic
    stepConfirmInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsSolved
    stepCheckInvoiceNotSplitted
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence)

  def test_13_SplitAndDeferInvoice(self, quiet=0, run=RUN_ALL_TESTS):
    """
    - Accept Order, Accept Packing List
    - Decrease quantity on Invoice
    - Split and defer Invoice
    - Accept Invoice
    - Accept splitted Invoice
    - Packing List must not be divergent and use old quantity
    - Invoice must not be divergent and use new quantity
    - splitted Invoice must not be divergent and use old - new quantity
    """
    if not run: return
    self.logMessage('InvoiceSplitAndDeferInvoice')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepDecreaseInvoiceLineQuantity
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepSplitAndDeferInvoice
    stepTic
    stepConfirmInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved
    stepCheckInvoiceSplitted

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepSwitchInvoices

    stepConfirmInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence)

  def test_14_AcceptDecisionOnInvoice(self, quiet=0, run=RUN_ALL_TESTS):
    """
    - Accept Order, Accept Packing List
    - Increase or Decrease quantity on Invoice
    - Accept Decision on Invoice
    - Accept Invoice
    - Packing List must not be divergent and use old quantity
    - Invoice must not be divergent and use new quantity
    """
    if not run: return
    self.logMessage('InvoiceAcceptDecisionOnInvoice')
    mid_sequence = \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted
    """
    end_sequence = \
    """
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepAcceptDecisionInvoice
    stepTic
    stepConfirmInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """

    mid_sequence_list = ["""
    stepDecreaseInvoiceLineQuantity
    """, """
    stepIncreaseInvoiceLineQuantity
    """]

    sequence_list = SequenceList()
    for seq in mid_sequence_list:
      sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
          mid_sequence + seq + end_sequence
      sequence_list.addSequenceString(sequence)
    sequence_list.play(self)

  def testCopyAndPaste(self, run=RUN_ALL_TESTS):
    """Test copy on paste on Invoice.
    When an invoice is copy/pasted, references should be resetted.
    """
    if not run:
      return
    accounting_module = self.getAccountingModule()
    invoice = accounting_module.newContent(
                    portal_type=self.invoice_portal_type)
    invoice.edit(reference='reference',
                 source_reference='source_reference',
                 destination_reference='destination_reference',)
    cb_data = accounting_module.manage_copyObjects([invoice.getId()])
    copied, = accounting_module.manage_pasteObjects(cb_data)
    new_invoice = accounting_module[copied['new_id']]
    self.assertNotEquals(invoice.getReference(),
                         new_invoice.getReference())
    self.assertNotEquals(invoice.getSourceReference(),
                         new_invoice.getSourceReference())
    self.assertNotEquals(invoice.getDestinationReference(),
                         new_invoice.getDestinationReference())

#class TestPurchaseInvoice(TestInvoice):
#  order_portal_type = 'Purchase Order'
#  order_line_portal_type = 'Purchase Order Line'
#  order_cell_portal_type = 'Purchase Order Cell'
#  packing_list_portal_type = 'Purchase Packing List'
#  packing_list_line_portal_type = 'Purchase Packing List Line'
#  packing_list_cell_portal_type = 'Purchase Packing List Cell'
#  delivery_builder_id = 'purchase_packing_list_builder'
#  invoice_portal_type = 'Purchase Invoice Transaction'
#  invoice_transaction_line_portal_type = 'Purchase Invoice Transaction Line'
#
#  def getTitle(self):
#    return "Purchase Invoices"

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInvoice))
    return suite

