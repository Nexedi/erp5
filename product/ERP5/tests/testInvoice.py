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
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from zLOG import LOG
from testPackingList import TestPackingListMixin
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
from testAccountingRules import TestAccountingRulesMixin

class TestInvoice(TestAccountingRulesMixin,TestPackingListMixin, ERP5TypeTestCase):
  """Test invoice are created from orders then packing lists. """
  
 
  RUN_ALL_TESTS = 1

  default_region = "europe/west/france"
  vat_gap = 'fr/pcg/4/44/445/4457/44571'
  sale_gap = 'fr/pcg/7/70/707/7071/70712'
  customer_gap = 'fr/pcg/4/41/411'

  def getTitle(self):
    return "Invoices"
  
  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    # FIXME: unittest user should not have the Manager role
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
            portal_type = 'Category',
            id = cat,
            immediate_reindex = 1 )
        else:
          path=path[cat]
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
    sequence.edit(client = sequence.get('organisation'))
    self.stepCreateOrganisation2(sequence, **kw)
    vendor = sequence.get('organisation')
    vendor.setRegion(self.default_region)
    self.assertNotEquals(vendor.getRegionValue(), None)
    sequence.edit(vendor = vendor)
  
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
    if not 'receivable_vat' in account_module.objectIds():
      vat_account = account_module.newContent(id='receivable_vat')
      vat_account.setGap(self.vat_gap)
      portal.portal_workflow.doActionFor(vat_account,
          'validate_action',wf_id='account_workflow')
    vat_account=account_module['receivable_vat']
    if not 'sale' in account_module.objectIds():
      sale_account = account_module.newContent(id='sale')
      sale_account.setGap(self.sale_gap)
      portal.portal_workflow.doActionFor(sale_account,
          'validate_action',wf_id='account_workflow')
    sale_account=account_module['sale']
    if not 'customer' in account_module.objectIds():
      customer_account = account_module.newContent(id='customer')
      customer_account.setGap(self.customer_gap)
      portal.portal_workflow.doActionFor(customer_account,
          'validate_action',wf_id='account_workflow')
    customer_account=account_module['customer']
    
    invoice_rule = self.getPortal().portal_rules.default_invoice_transaction_rule
    invoice_rule.deleteContent([x.getId() for x in invoice_rule.objectValues()])
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
    income = cell.newContent(id='income',
            portal_type=self.sale_invoice_transaction_portal_type)
    income.setQuantity(1.0)
    income.setSourceValue(sale_account)
    receivable = cell.newContent(id='receivable',
            portal_type=self.sale_invoice_transaction_portal_type)
    receivable.setQuantity(-1.196)
    receivable.setSourceValue(customer_account)
    collected_vat = cell.newContent(id='collected_vat',
            portal_type=self.sale_invoice_transaction_portal_type)
    collected_vat.setQuantity(0.196)
    collected_vat.setSourceValue(vat_account)
    
  def modifyPackingListState(self, transition_name, sequence,packing_list=None):
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

  def stepSetReadyNewPackingList(self, sequence=None, sequence_list=None, **kw):
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
    
  def stepCancelPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('cancel_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEquals(packing_list.getSimulationState(), 'cancelled')

  def stepPackingListSimulation(self, sequence=None, sequence_list=None, **kw):
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
    """ checks that the invoice is built with the default_invoice_builder """
    packing_list = sequence.get('packing_list')
    related_applied_rule_list = packing_list.getCausalityRelatedValueList(
                                   portal_type=self.applied_rule_portal_type)
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
      # Simulation Movemen
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
    order = order_module.newContent(portal_type='Sale Order')
    order.setStartDate(DateTime('2004-11-20'))
    order.setStopDate(DateTime('2004-11-24'))
    order.setDestinationValue(destination)
    order.setDestinationSectionValue(destination_section)
    order.setSourceValue(source)
    order.setSourceSectionValue(source_section)
    order_line = order.newContent(portal_type = 'Sale Order Line', id = '1')
    order_line.setResourceValue(product)
    order_line.setQuantity(10)
    order_line.setPrice(100)
    sequence.edit(
      order = order,
      order_line = order_line,
      order_line_list = [order_line])
    self.assertEquals(order_line.getTotalPrice(), 10*100)

  def stepCheckOrderRule(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    simulation_tool = self.getSimulationTool()
    # Check that there is an applied rule for our packing list
    rule_list = [x for x in simulation_tool.objectValues()
                            if x.getCausalityValue()==order]
    self.assertNotEquals(len(rule_list), 0)
    sequence.edit(order_rule_list = rule_list)
    # TODO
    return 
    """
    rule_line_list = order_rule.objectValues()
    order_line_list = order.objectValues()
    self.assertEquals(len(order_line_list), len(rule_line_list))
    self.assertEquals(1, len(rule_line_list))
    rule_line = rule_line_list[0]
    sequence.edit(order_rule_line=rule_line)
    order_line = order_line_list[0]
    self.assertEquals(rule_line.getQuantity(), 10)
    self.assertEquals(rule_line.getPrice(), 100)
    self.assertEquals(rule_line.getOrderValue(), order_line)
    self.assertEquals(rule_line.getStartDate(), order_line.getStartDate())
    self.assertEquals(rule_line.getStopDate(), order_line.getStopDate())
    self.assertEquals(rule_line.getPortalType(), 'Simulation Movement')
    self.assertEquals(rule_line.getResourceValue(),
                      order_line.getResourceValue())
    """
    
  def stepCheckInvoicingRule(self, sequence=None, sequence_list=None, **kw):
    """ Checks that the invoicing rule is applied and its values are
        correct. """
    order_rule_list = sequence.get('order_rule_list')
    for order_rule in order_rule_list :
      for order_simulation_movement in order_rule.objectValues() :
        invoicing_rule_list = order_simulation_movement.objectValues()
        self.assertEquals(len(invoicing_rule_list), 1)
        invoicing_rule = invoicing_rule_list[0]
        sequence.edit(invoicing_rule = invoicing_rule)
        self.assertEquals(invoicing_rule.getSpecialiseId(),
                         'default_invoicing_rule')
        self.assertEquals(invoicing_rule.getPortalType(),
                         'Applied Rule')
    
        simulation_movement_list = invoicing_rule.objectValues()
        self.assertNotEquals(len(simulation_movement_list), 0)
        for simulation_movement in simulation_movement_list :
          resource = sequence.get('resource')
          self.assertEquals(simulation_movement.getPortalType(),
                            'Simulation Movement')
          self.assertEquals(simulation_movement.getResourceValue(),
                            resource)
          # TODO: What is the invoice dates supposed to be ?
          # is this done through profiles ?
          self.assertEquals(simulation_movement.getStartDate(),
                     sequence.get('order').getStartDate())
          self.assertEquals(simulation_movement.getStopDate(),
                      sequence.get('order').getStopDate())
          
  def stepCheckDeliveryRuleForDeferred(
                      self, sequence=None, sequence_list=None, **kw):
    """ Checks that a delivery rule has been created when we took 'split
        and defer' decision on the divergeant Packing List. """
  
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

  def stepCheckInvoice(self,sequence=None, sequence_list=None, **kw):
    """ checks invoice properties are well set. """
    # XXX need to clear the accounting module.
    accounting_module = self.getAccountingModule()
    sale_invoice_transaction_list = accounting_module.objectValues()
    self.assertEquals(len(sale_invoice_transaction_list),1)
    packing_list = sequence.get("packing_list")
    
    sale_invoice = sale_invoice_transaction_list[0]
    sequence.edit(invoice=sale_invoice)
    sale_invoice_line_list = sale_invoice.contentValues(
                filter={'portal_type':'Invoice Line'})
    self.assertEquals(len(sale_invoice_line_list),1)
    sale_invoice_line = sale_invoice_line_list[0]
    sequence.edit(invoice_line=sale_invoice_line)
    product = sequence.get('resource')
    self.assertEquals(sale_invoice_line.getResourceValue(), product)
    self.assertEquals(sale_invoice_line.getPrice(), self.price1)
    self.assertEquals(sale_invoice_line.getQuantity(), self.quantity1)
    self.assertEquals(sale_invoice_line.getTotalPrice(), self.total_price1)
    self.assertEquals(sale_invoice.getCausalityValue(), packing_list)
    
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

  def stepCheckTwoInvoicesTransactionLines(self,sequence=None, sequence_list=None, **kw):
    """ checks invoice properties are well set. """
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    import pdb;pdb.set_trace()
    self.assertEquals(3,len(invoice.objectValues(
        portal_type=self.sale_invoice_transaction_line_portal_type)))
    self.assertEquals(3,len(new_invoice.objectValues(
        portal_type=self.sale_invoice_transaction_line_portal_type)))

  def stepRebuildAndCheckNothingIsCreated(self, sequence=None,
                                           sequence_list=None, **kw):
    """Rebuilds with sale_invoice_builder and checks nothing more is
    created. """
    return 'TODO' #XXX
    accounting_module = self.getAccountingModule()
    sale_invoice_transaction_list = accounting_module.objectValues()
    self.assertEquals(len(sale_invoice_transaction_list), 1)

  def stepModifyInvoicesDate(self, sequence=None,
                                           sequence_list=None, **kw):
    """Rebuilds with sale_invoice_builder and checks nothing more is
    created. """
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    invoice.edit(start_date=self.datetime,
                 stop_date=self.datetime+1)
    new_invoice.edit(start_date=self.datetime,
                 stop_date=self.datetime+1)

  def stepRemoveDateMovementGroupForTransactionBuilder(self, sequence=None,
            sequence_list=None,**kw):
    """
    Remove DateMovementGroup
    """
    portal = self.getPortal()
    builder = portal.portal_deliveries.sale_invoice_transaction_builder
    previous_list = builder.getDeliveryCollectOrderList()
    new_list = [x for x in previous_list if x != 'DateMovementGroup']
    new_list.append('ParentExplanationMovementGroup')
    builder.setDeliveryCollectOrderList(new_list)
    
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
      DecreasePackingListLineQuantity 
      CheckPackingListIsCalculating 
      SplitAndDeferPackingList 
      Tic 
      CheckPackingListIsSolved 
      CheckPackingListSplitted
      stepAddPackingListContainer
      stepAddPackingListContainerLine
      stepSetContainerLineFullQuantity
      stepTic
      stepCheckPackingListIsPacked
      stepDefineNewPackingListContainer
      stepTic
      stepCheckNewPackingListIsPacked
    """

  def test_SimpleInvoice(self, quiet=0, run=RUN_ALL_TESTS):
    """Checks that a Simple Invoice is created from a Packing List"""
    for base_sequence in (TestInvoice.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      self.playSequence(
        base_sequence +
      """
        stepSetReadyPackingList
        stepTic
        stepStartPackingList
        stepCheckInvoicingRule
        stepTic
        stepCheckInvoiceBuilding
        stepRebuildAndCheckNothingIsCreated
      """)

  def test_TwoInvoicesFromTwoPackingList(self, quiet=0, run=1):
    """ This test was created for the following bug:
        - an order is created and confirmed
        - the packing list is split
        - the 2 packing list are delivered (at different date)
        - 2 invoices are built, then we set the same date on both of them
        - the accounting rules are generated and put in only one invoice !!,
          so we have an invoice with twice the number of accounting rules
          and an invoice with no accounting rules. both invoices are wrong
    """
    for base_sequence in (TestInvoice.TWO_PACKING_LIST_DEFAULT_SEQUENCE, ) :
      self.playSequence(
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
      """)

  def DISABLEDtest_InvoiceEditPackingListLine(self, quiet=0, run=RUN_ALL_TESTS):
    """Checks that editing a Packing List Line still creates a correct
      Invoice"""
    for base_sequence in (TestInvoice.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      self.playSequence(
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
    """)

  def DISABLEDtest_InvoiceDeletePackingListLine(self, quiet=0, run=RUN_ALL_TESTS):
    """Checks that deleting a Packing List Line still creates a correct
    Invoice"""
    for base_sequence in (TestInvoice.PACKING_LIST_DEFAULT_SEQUENCE, ) :
                # XXX use another sequence that creates 2 lines
      self.playSequence(
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
    """)

  def DISABLEDtest_InvoiceAddPackingListLine(self, quiet=0, run=RUN_ALL_TESTS):
    """Checks that adding a Packing List Line still creates a correct
    Invoice"""
    for base_sequence in (TestInvoice.PACKING_LIST_DEFAULT_SEQUENCE, ) :
                # XXX use another sequence that creates 2 lines
      self.playSequence(
        base_sequence +
    """
      stepAddPackingListLine
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
    """)
    
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestInvoice))
    return suite

