##############################################################################
#
# Copyright (c) 2004-2008 Nexedi SA and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#          Jerome Perrin <jerome@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Acquisition import aq_parent
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testPackingList import TestPackingListMixin
import six

class TestInvoiceMixin(TestPackingListMixin):
  """Test methods for invoices
  """
  default_region = "europe/west/france"
  vat_gap = 'fr/pcg/4/44/445/4457/44571'
  vat_rate = 0.196
  sale_gap = 'fr/pcg/7/70/707/7071/70712'
  customer_gap = 'fr/pcg/4/41/411'
  bank_gap = 'fr/pcg/5/51/512'
  mail_delivery_mode = 'by_mail'
  cpt_incoterm = 'cpt'
  unit_piece_quantity_unit = 'unit/piece'
  mass_quantity_unit = 'mass/kg'
  oldMailhost = None

  # (account_id, account_gap, account_type)
  account_definition_list = (
      ('receivable_vat', vat_gap, 'liability/payable/collected_vat',),
      ('sale', sale_gap, 'income'),
      ('customer', customer_gap, 'asset/receivable'),
      ('refundable_vat', vat_gap, 'asset/receivable/refundable_vat'),
      ('purchase', sale_gap, 'expense'),
      ('supplier', customer_gap, 'liability/payable'),
      ('bank', bank_gap, 'asset/cash/bank'),
      )
  # (line_id, source_account_id, destination_account_id, line_quantity)
  transaction_line_definition_list = (
      ('income', 'sale', 'purchase', 1.0),
      ('receivable', 'customer', 'supplier', -1.0 - vat_rate),
      ('collected_vat', 'receivable_vat', 'refundable_vat', vat_rate),
      )

  def getTitle(self):
    return "Invoices"

  def getBusinessTemplateList(self):
    return super(TestInvoiceMixin, self).getBusinessTemplateList() + (
      'erp5_accounting', 'erp5_invoicing', 'erp5_simplified_invoicing',
      'erp5_configurator_standard_accounting_template',
      'erp5_configurator_standard_invoicing_template')

  @UnrestrictedMethod
  def createCategories(self):
    """Create the categories for our test. """
    # pull in the TestOrderMixin categories first
    super(TestInvoiceMixin, self).createCategories()
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
      self.assertNotEqual(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('region/%s' % self.default_region,
            'gap/%s' % self.vat_gap,
            'gap/%s' % self.sale_gap,
            'gap/%s' % self.customer_gap,
            'gap/%s' % self.bank_gap,
            'delivery_mode/%s' % self.mail_delivery_mode,
            'incoterm/%s' % self.cpt_incoterm,
            'quantity_unit/%s' % self.unit_piece_quantity_unit,
            'quantity_unit/%s' % self.mass_quantity_unit,
            'base_amount/tax1',
            'base_amount/tax2',
            'base_amount/tax3',
            'use/trade/tax',
        )

  def afterSetUp(self):
    self.createUser('test_user',
                    ['Assignee', 'Assignor', 'Member',
                     'Associate', 'Auditor', 'Author'])
    self.createUser('manager', ['Manager'])
    self.loginByUserName('manager')
    self.createCategories()
    self.validateRules()
    self.createBusinessProcess()
    self.loginByUserName('test_user')

  def beforeTearDown(self):
    self.abort()
    self.loginByUserName('manager')
    super(TestInvoiceMixin, self).beforeTearDown()
    for folder in (self.portal.accounting_module,
                   self.portal.organisation_module,
                   self.portal.sale_order_module,
                   self.portal.purchase_order_module,
                   self.portal.sale_packing_list_module,
                   self.portal.purchase_packing_list_module,
                   self.portal.portal_simulation,):
      folder.manage_delObjects([x for x in folder.objectIds() if x not in ('organisation_1','organisation_2','ppl_1','ppl_2')])
    self.tic()

  def stepCreateSaleInvoiceTransactionRule(self, sequence, **kw) :
    pass # see createBusinessProcess

  ## XXX move this to "Sequence class"
  def playSequence(self, sequence_string, quiet=0) :
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def createBusinessProcess(self):
    portal = self.portal
    business_process_id = self.__class__.__name__
    try:
      business_process = portal.business_process_module[business_process_id]
    except KeyError:
      business_process = portal.business_process_module.newContent(
        business_process_id, 'Business Process',
        specialise=self.__class__.business_process)
      kw = dict(portal_type='Trade Model Path',
                trade_phase='trade/accounting',
                trade_date='trade_phase/trade/invoicing',
                membership_criterion_base_category_list=('destination_region',
                                                         'product_line'),
                membership_criterion_category=(
                  'destination_region/region/' + self.default_region,
                  'product_line/apparel'))
      account_module = portal.account_module
      for account_id, account_gap, account_type in self.account_definition_list:
        if account_id not in account_module:
          account = account_module.newContent(account_id, gap=account_gap,
                                              account_type=account_type)
          account.validate()
      for line_id, line_source_id, line_destination_id, line_ratio in \
          self.transaction_line_definition_list:
        trade_model_path = business_process.newContent(
          reference='accounting_' + line_id,
          efficiency=line_ratio,
          source_value=account_module[line_source_id],
          destination_value=account_module[line_destination_id],
          **kw)
        # A trade model path already exist for root simulation movements
        # (Accounting Transaction Root Simulation Rule).
        # The ones we are creating are for Invoice Transaction Simulation Rule.
        trade_model_path._setCriterionPropertyList(('portal_type',))
        trade_model_path.setCriterion('portal_type', 'Simulation Movement')
    self.business_process = business_process.getRelativeUrl()

  def stepCreateEntities(self, sequence, **kw) :
    """Create a vendor and two clients. """
    self.stepCreateOrganisation1(sequence, **kw)
    self.stepCreateOrganisation2(sequence, **kw)
    self.stepCreateOrganisation3(sequence, **kw)
    self.stepCreateProject1(sequence, **kw)
    self.stepCreateProject2(sequence, **kw)
    vendor = sequence.get('organisation1')
    vendor.setRegion(self.default_region)
    vendor.validate()
    sequence.edit(vendor=vendor)
    client1 = sequence.get('organisation2')
    client1.setRegion(self.default_region)
    self.assertNotEqual(client1.getRegionValue(), None)
    client1.validate()
    sequence.edit(client1=client1)
    client2 = sequence.get('organisation3')
    self.assertEqual(client2.getRegionValue(), None)
    client2.validate()
    sequence.edit(client2=client2)

  def stepCheckOrderRule(self, sequence=None, sequence_list=None, **kw):
    """Check we have a related Order Rule"""
    order = sequence.get('order')
    simulation_tool = self.getSimulationTool()
    # Check that there is an applied rule for our packing list
    rule_list = [x for x in simulation_tool.objectValues()
                            if x.getCausalityValue()==order]
    self.assertNotEqual(len(rule_list), 0)
    sequence.edit(order_rule_list = rule_list)

    self.assertEqual(len(order.getMovementList()),
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
        temp_invoicing_rule_list = [ar for ar in order_simulation_movement.objectValues()[0].objectValues()[0].objectValues()
          if ar.getSpecialiseValue().getPortalType() == 'Invoice Simulation Rule']
        self.assertEqual(len(temp_invoicing_rule_list), 1)
        invoicing_rule_list.extend(temp_invoicing_rule_list)
    sequence.edit(invoicing_rule_list=invoicing_rule_list)
    invoicing_rule = invoicing_rule_list[0]
    sequence.edit(invoicing_rule = invoicing_rule)
    for invoicing_rule in invoicing_rule_list:
      self.assertEqual(invoicing_rule.getSpecialiseReference(),
          'default_invoicing_rule')
      self.assertEqual(invoicing_rule.getPortalType(),
          'Applied Rule')
      simulation_movement_list = invoicing_rule.objectValues()
      self.assertNotEqual(len(simulation_movement_list), 0)
      for simulation_movement in simulation_movement_list :
        invoice_transaction_rule_list.extend([applied_rule for applied_rule
          in simulation_movement.objectValues() if applied_rule \
              .getSpecialiseValue().getPortalType()
              == 'Invoice Transaction Simulation Rule'])
        resource_list = sequence.get('resource_list')
        self.assertEqual(simulation_movement.getPortalType(),
                          'Simulation Movement')
        self.assertIn(simulation_movement.getResourceValue(),
            resource_list)
        self.assertTrue(simulation_movement.isConvergent())
        # TODO: What is the invoice dates supposed to be ?
        # is this done through profiles ?
        #self.assertEqual(simulation_movement.getStartDate(),
        #           sequence.get('order').getStartDate())
        #self.assertEqual(simulation_movement.getStopDate(),
        #            sequence.get('order').getStopDate())
    sequence.edit(invoice_transaction_rule_list=invoice_transaction_rule_list)

  def stepCheckInvoiceTransactionRule(self, sequence=None, sequence_list=None,
      **kw):
    """
    Checks that the applied invoice_transaction_rule is expanded and its movements are
    consistent with its parent movement
    """
    invoice_transaction_rule_list = \
        sequence.get('invoice_transaction_rule_list')
    for applied_invoice_transaction_rule in invoice_transaction_rule_list:
      parent_movement = aq_parent(applied_invoice_transaction_rule)
      self.assertEqual(3, len(applied_invoice_transaction_rule.objectValues()))
      for _, line_source_id, line_destination_id, line_ratio in \
                                            self.transaction_line_definition_list:
        movement = None
        for simulation_movement in \
                applied_invoice_transaction_rule.objectValues():
          if simulation_movement.getSourceId() == line_source_id and\
              simulation_movement.getDestinationId() == line_destination_id:
            movement = simulation_movement
            break

        self.assertTrue(movement is not None)
        self.assertEqual(movement.getCorrectedQuantity(), parent_movement.getPrice() *
            parent_movement.getCorrectedQuantity() * line_ratio)
        self.assertEqual(movement.getStartDate(),
            parent_movement.getStartDate())
        self.assertEqual(movement.getStopDate(),
            parent_movement.getStopDate())

  def modifyPackingListState(self, transition_name,
                             sequence,packing_list=None):
    """ calls the workflow for the packing list """
    if packing_list is None:
      packing_list = sequence.get('packing_list')
    packing_list.portal_workflow.doActionFor(packing_list, transition_name)

  def stepSetReadyPackingList(self, sequence=None, sequence_list=None, **kw):
    """ set the Packing List as Ready. This must build the invoice. """
    self.modifyPackingListState('set_ready_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEqual(packing_list.getSimulationState(), 'ready')

  def stepSetReadyNewPackingList(self, sequence=None,
                                 sequence_list=None, **kw):
    """ set the Packing List as Ready. This must build the invoice. """
    packing_list = sequence.get('new_packing_list')
    self.modifyPackingListState('set_ready_action', sequence=sequence,
                                packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'ready')

  def stepStartPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('start_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEqual(packing_list.getSimulationState(), 'started')

  def stepStartNewPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('new_packing_list')
    self.modifyPackingListState('start_action', sequence=sequence,
                                packing_list=packing_list)
    self.assertEqual(packing_list.getSimulationState(), 'started')

  def stepStopPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('stop_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEqual(packing_list.getSimulationState(), 'stopped')

  def stepDeliverPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('deliver_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEqual(packing_list.getSimulationState(), 'delivered')

  def stepCancelPackingList(self, sequence=None, sequence_list=None, **kw):
    self.modifyPackingListState('cancel_action', sequence=sequence)
    packing_list = sequence.get('packing_list')
    self.assertEqual(packing_list.getSimulationState(), 'cancelled')

  def modifyInvoiceState(self, transition_name,
                             sequence,invoice=None):
    """ calls the workflow for the invoice """
    if invoice is None:
      invoice = sequence.get('invoice')
    invoice.portal_workflow.doActionFor(invoice, transition_name)

  def stepStartInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('start_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEqual(invoice.getSimulationState(), 'started')

  def stepStartNewInvoice(self, sequence=None, sequence_list=None, **kw):
    invoice = sequence.get('new_invoice')
    self.modifyInvoiceState('start_action', sequence=sequence,
                                invoice=invoice)
    self.assertEqual(invoice.getSimulationState(), 'started')

  def stepStopInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('stop_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEqual(invoice.getSimulationState(), 'stopped')

  def stepDeliverInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('deliver_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEqual(invoice.getSimulationState(), 'delivered')

  def stepCancelInvoice(self, sequence=None, sequence_list=None, **kw):
    self.modifyInvoiceState('cancel_action', sequence=sequence)
    invoice = sequence.get('invoice')
    self.assertEqual(invoice.getSimulationState(), 'cancelled')


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
      self.assertNotEqual(len(simulation_movement_list), 0)
      total_quantity = 0
      for simulation_movement in simulation_movement_list :
        total_quantity += simulation_movement.getQuantity()
        # check that those movements come from the same root applied
        # rule than the order.
        self.assertEqual( simulation_movement.getRootAppliedRule(),
                           order_root_applied_rule)
      self.assertEqual(total_quantity, movement.getQuantity())

  def checkMirrorAcquisition(self, obj, acquired_object):
    """
      Check if properties are well acquired for mirrored case
    """
    # packing_list_movement, simulation_movement

    self.assertEqual(acquired_object.getStartDate(), obj.getStopDate())
    self.assertEqual(acquired_object.getStopDate(), obj.getStartDate())
    self.assertEqual(acquired_object.getSourceValue(), \
                      obj.getDestinationValue())
    self.assertEqual(acquired_object.getDestinationValue(), \
                      obj.getSourceValue())

    self.assertEqual(acquired_object.getSourceSectionValue(), \
                      obj.getDestinationSectionValue())
    self.assertEqual(acquired_object.getDestinationSectionValue(), \
                      obj.getSourceSectionValue())

  def stepCheckInvoiceBuilding(self, sequence=None, sequence_list=None, **kw):
    """
    checks that the invoice is built with the default_invoice_builder
    """
    packing_list = sequence.get('packing_list')
    related_invoice_list = packing_list.getCausalityRelatedValueList(
                     portal_type=self.invoice_portal_type)

    if packing_list.getPortalType() == 'Purchase Packing List':
      packing_list_building_state = 'stopped'
    else:
      packing_list_building_state = 'started'
    packing_list_state = packing_list.getSimulationState()
    if packing_list_state != packing_list_building_state :
      self.assertEqual(0, len(related_invoice_list))
    else:
      self.assertEqual(1, len(related_invoice_list))

      invoice = related_invoice_list[0].getObject()
      self.assertTrue(invoice is not None)
      # Invoices created by Delivery Builder are in confirmed state
      self.assertEqual(invoice.getSimulationState(), 'confirmed')

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
        self.assertEqual(len(invoice_movement_list), 1)
        invoice_movement = invoice_movement_list[0]
        self.assertTrue(invoice_movement is not None)
        self.assertTrue(invoice_movement.getRelativeUrl().\
                              startswith(invoice_relative_url))

      # Then, test if each Invoice movement is equals to the sum of somes
      # Simulation Movements
      for invoice_movement in invoice.getMovementList(portal_type = [
                          self.invoice_cell_portal_type,
                          self.invoice_line_portal_type]) :
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
          self.assertEqual(invoice_movement.getResource(), \
                            related_simulation_movement.getResource())
          # Test resource variation
          self.assertEqual(invoice_movement.getVariationText(), \
                            related_simulation_movement.getVariationText())
          self.assertEqual(invoice_movement.getVariationCategoryList(), \
                        related_simulation_movement.getVariationCategoryList())
          # Test acquisition
          self.checkAcquisition(invoice_movement,
                                related_simulation_movement)
          # Test delivery ratio
          self.assertEqual(related_simulation_movement.getQuantity() /\
                            invoice_movement_quantity, \
                            related_simulation_movement.getDeliveryRatio())

        self.assertEqual(quantity, invoice_movement.getQuantity())
        # Test price
        self.assertEqual(total_price / quantity, invoice_movement.getPrice())

      sequence.edit(invoice = invoice)

      # Test causality
      self.assertEqual(len(invoice.getCausalityValueList(
                      portal_type = self.packing_list_portal_type)), 1)
      self.assertEqual(invoice.getCausalityValue(), packing_list)

      # Finally, test getTotalQuantity and getTotalPrice on Invoice
      self.assertEqual(packing_list.getTotalQuantity(),
                        invoice.getTotalQuantity())
      self.assertEqual(packing_list.getTotalPrice(),
                        invoice.getTotalPrice())

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
        self.assertEqual(3, len(invoice_transaction_line_list))
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
          resource_precision = line.getResourceValue().getQuantityPrecision()
          self.assertEqual(round(line.getQuantity(), resource_precision),
              round(expected_price * line_ratio, resource_precision))

  def stepCheckInvoiceLineHasReferenceAndIntIndex(self, sequence=None, **kw):
    """Check that the unique invoice line in the invoice has reference and int
    index.
    """
    invoice = sequence.get('invoice')
    invoice_line_list = invoice.contentValues(
                            portal_type=self.invoice_line_portal_type)
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]
    self.assertEqual(1, invoice_line.getIntIndex())
    self.assertEqual('1', invoice_line.getReference())

  def stepCheckPackingListInvoice(
                      self, sequence=None, sequence_list=None, **kw):
    """ Checks if the delivery builder is working as expected,
        coping the atributes from packing list to invoice."""
    packing_list = sequence.get('packing_list')
    related_invoice_list = packing_list.getCausalityRelatedValueList(
                     portal_type=self.invoice_portal_type)
    self.assertEqual(len(related_invoice_list), 1)
    invoice = related_invoice_list[0]
    self.assertEqual(packing_list.getSource(), invoice.getSource())
    self.assertEqual(packing_list.getDestination(), invoice.getDestination())
    self.assertEqual(packing_list.getDestinationSection(), \
                                       invoice.getDestinationSection())
    self.assertEqual(packing_list.getSourceSection(), \
                                       invoice.getSourceSection())
    self.assertEqual(packing_list.getDestinationDecision(), \
                                       invoice.getDestinationDecision())
    self.assertEqual(packing_list.getSourceDecision(), \
                                       invoice.getSourceDecision())
    self.assertEqual(packing_list.getDestinationAdministration(), \
                                       invoice.getDestinationAdministration())
    self.assertEqual(packing_list.getSourceAdministration(), \
                                       invoice.getSourceAdministration())
    self.assertEqual(packing_list.getDestinationProject(), \
                                       invoice.getDestinationProject())
    self.assertEqual(packing_list.getSourceProject(), \
                                       invoice.getSourceProject())
    self.assertEqual(packing_list.getPriceCurrency(), \
                                       invoice.getPriceCurrency())



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
    self.assertTrue(packing_list is not None)
    simulation_tool = self.getSimulationTool()
    # Check that there is an applied rule for our packing list
    rule_list = [x for x in simulation_tool.objectValues()
                          if x.getCausalityValue()==packing_list]
    self.assertEqual(len(rule_list),1)
    packing_list_rule = rule_list[0]
    sequence.edit(packing_list_rule=packing_list_rule)
    rule_line_list = packing_list_rule.objectValues()
    packing_list_line_list = packing_list.objectValues()
    self.assertEqual(len(packing_list_line_list),
                      len(rule_line_list))
    self.assertEqual(1, len(rule_line_list))
    rule_line = rule_line_list[0]
    packing_list_line = packing_list_line_list[0]
    self.assertEqual(rule_line.getQuantity(), 10)
    self.assertEqual(rule_line.getPrice(), 100)
    self.assertEqual(rule_line.getDeliveryValue(),
                      packing_list_line)
    self.assertEqual(rule_line.getStartDate(),
                      packing_list_line.getStartDate())
    self.assertEqual(rule_line.getStopDate(),
                      packing_list_line.getStopDate())
    self.assertEqual(rule_line.getPortalType(),
                      'Simulation Movement')


  def stepCheckPackingList(self,sequence=None, sequence_list=None,**kw):
    """  """
    packing_list_module = self.getSalePackingListModule()
    order = sequence.get('order')
    sale_packing_list_list = []
    for o in packing_list_module.objectValues():
      if o.getCausalityValue() == order:
        sale_packing_list_list.append(o)
    self.assertEqual(len(sale_packing_list_list), 1)
    sale_packing_list = sale_packing_list_list[0]
    sale_packing_list_line_list = sale_packing_list.objectValues()
    self.assertEqual(len(sale_packing_list_line_list),1)
    sale_packing_list_line = sale_packing_list_line_list[0]
    product = sequence.get('resource')
    self.assertEqual(sale_packing_list_line.getResourceValue(),
                      product)
    self.assertEqual(sale_packing_list_line.getPrice(),
                      self.price1)
    LOG('sale_packing_list_line.showDict()',0,
          sale_packing_list_line.showDict())
    self.assertEqual(sale_packing_list_line.getQuantity(),
                      self.quantity1)
    self.assertEqual(sale_packing_list_line.getTotalPrice(),
                      self.total_price1)
    sequence.edit(packing_list = sale_packing_list)

  def stepCheckTwoInvoices(self,sequence=None, sequence_list=None, **kw):
    """ checks invoice properties are well set. """
    # Now we will check that we have two invoices created
    for x in '', 'new_':
      packing_list = sequence.get(x + 'packing_list')
      invoice, = packing_list.getCausalityRelatedValueList(
          portal_type=self.invoice_portal_type)
      self.assertEqual(invoice.getSimulationState(), 'confirmed')
      sequence.set(x + 'invoice', invoice)

  def stepStartTwoInvoices(self,sequence=None, sequence_list=None, **kw):
    """ start both invoices. """
    portal = self.getPortal()
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    portal.portal_workflow.doActionFor(invoice, 'start_action')
    portal.portal_workflow.doActionFor(new_invoice, 'start_action')

  def stepCheckTwoInvoicesTransactionLines(self,sequence=None,
                                           sequence_list=None, **kw):
    """ checks invoice properties are well set. """
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    self.assertEqual(3,len(invoice.objectValues(
        portal_type=self.invoice_transaction_line_portal_type)))
    self.assertEqual(3,len(new_invoice.objectValues(
        portal_type=self.invoice_transaction_line_portal_type)))
    found_dict = {}
    for line in invoice.objectValues(
        portal_type=self.invoice_transaction_line_portal_type):
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
      self.assertAlmostEqual(expected_dict[key],found_dict[key],places=2)
    found_dict = {}
    for line in new_invoice.objectValues(
        portal_type=self.invoice_transaction_line_portal_type):
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
      self.assertAlmostEqual(expected_dict[key], found_dict[key], places=2)

  def stepRebuildAndCheckNothingIsCreated(self, sequence=None,
                                           sequence_list=None, **kw):
    """Rebuilds with sale_invoice_builder and checks nothing more is
    created. """
    accounting_module = self.portal.accounting_module
    portal_type_list = ('Sale Invoice Transaction', 'Purchase Invoice Transaction')
    sale_invoice_transaction_count = len(accounting_module.objectValues(
      portal_type=portal_type_list))
    for builder in self.getPortal().portal_deliveries.objectValues():
      builder.build()
    self.assertEqual(sale_invoice_transaction_count,
                      len(accounting_module.objectValues(
      portal_type=portal_type_list)))

  def stepModifyInvoicesDate(self, sequence=None,
                                           sequence_list=None, **kw):
    """Change invoice date"""
    invoice = sequence.get('invoice')
    new_invoice = sequence.get('new_invoice')
    invoice.edit(start_date=self.datetime,
                 stop_date=self.datetime+1)
    new_invoice.edit(start_date=self.datetime,
                 stop_date=self.datetime+1)

  def stepEditInvoice(self, sequence=None, sequence_list=None, **kw):
    """Edit the current invoice, to trigger updateSimulation."""
    invoice = sequence.get('invoice')
    invoice.edit(description='This invoice was edited!')

  def stepCheckInvoiceRuleNotAppliedOnInvoiceEdit(self,
                    sequence=None, sequence_list=None, **kw):
    """If we call edit on the invoice, invoice rule should not be
    applied on lines created by delivery builder."""
    invoice = sequence.get('invoice')
    self.assertEqual([], invoice.getCausalityRelatedValueList())

  def stepEditPackingList(self, sequence=None, sequence_list=None, **kw):
    """Edit the current packing list, to trigger updateSimulation."""
    packing_list = sequence.get('packing_list')
    packing_list.edit(description='This packing list was edited!')

  def stepAcceptDecisionDescriptionPackingList(self,sequence=None, sequence_list=None):
    packing_list = sequence.get('packing_list')
    self._solveDivergence(packing_list, 'description', 'Accept Solver')

  def stepAssertCausalityStateIsNotSolvedInConsistencyMessage(self,
                    sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    self.assertEqual(
      ['Causality State is not "Solved". Please wait or take action'
        + ' for causality state to reach "Solved".'],
      [str(message.message) for message in packing_list.checkConsistency()])

  def stepSetReadyWorkflowTransitionIsBlockByConsistency(self,
                    sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    with self.assertRaisesRegex(ValidationFailed,
        '.*Causality State is not "Solved"*'):
      self.getPortal().portal_workflow.doActionFor(
        packing_list, 'set_ready_action')

  def stepCheckDeliveryRuleNotAppliedOnPackingListEdit(self,
                    sequence=None, sequence_list=None, **kw):
    """If we call edit on the packing list, delivery rule should not be
    applied on lines created by delivery builder."""
    packing_list = sequence.get('packing_list')
    self.assertEqual([], packing_list.getCausalityRelatedValueList())

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
    self.assertEqual('calculating',invoice.getCausalityState())

  def stepCheckInvoiceIsDiverged(self, sequence=None, sequence_list=None,
      **kw):
    """
    Test if invoice is diverged
    """
    invoice = sequence.get('invoice')
    self.assertEqual('diverged',invoice.getCausalityState())

  def stepCheckInvoiceIsSolved(self, sequence=None, sequence_list=None,
      **kw):
    """
    Test if invoice is solved
    """
    invoice = sequence.get('invoice')
    self.assertEqual('solved', invoice.getCausalityState(),
                      invoice.getDivergenceList())

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
    if invoice.isDivergent():
      self.fail(invoice.getDivergenceList())

  def stepSplitAndDeferInvoice(self, sequence=None, sequence_list=None,
      **kw):
    invoice = sequence.get('invoice')
    solver_process = self.portal.portal_solver_processes.newSolverProcess(invoice)
    quantity_solver_decision, = [x for x in solver_process.contentValues()
      if x.getCausalityValue().getTestedProperty() == 'quantity']
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO Delivery Solver',
          'start_date':self.datetime + 15,
          'stop_date':self.datetime + 25}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepUnifyStartDateWithDecisionInvoice(self, sequence=None,
                                            sequence_list=None):
    invoice = sequence.get('invoice')
    self._solveDivergence(invoice, 'start_date', 'Unify Solver',
                          value=invoice.getStartDate())

  def stepAdoptPrevisionQuantityInvoice(self,sequence=None, sequence_list=None):
    invoice = sequence.get('invoice')
    self._solveDivergence(invoice, 'quantity', 'Adopt Solver')

  def stepAcceptDecisionQuantityInvoice(self,sequence=None, sequence_list=None):
    invoice = sequence.get('invoice')
    self._solveDivergence(invoice, 'quantity', 'Accept Solver')

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
    self.assertEqual(2,len(invoice_list))
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
      self.assertEqual(self.default_quantity-1,line.getQuantity())
    for line in invoice2.objectValues(
          portal_type=self.invoice_line_portal_type):
      self.assertEqual(1,line.getQuantity())

  def stepCheckInvoiceNotSplitted(self, sequence=None, sequence_list=None, **kw):
    """
    Test if invoice was not splitted
    """
    packing_list = sequence.get('packing_list')
    invoice_list = packing_list.getCausalityRelatedValueList(
        portal_type=self.invoice_portal_type)
    self.assertEqual(1,len(invoice_list))
    invoice1 = None
    for invoice in invoice_list:
      if invoice.getUid() == sequence.get('invoice').getUid():
        invoice1 = invoice
    last_delta = sequence.get('last_delta', 0.0)
    for line in invoice1.objectValues(
        portal_type=self.invoice_line_portal_type):
      self.assertEqual(self.default_quantity + last_delta,
          line.getQuantity())

  def stepAddInvoiceLines(self, sequence=None, sequence_list=None):
    """
    add some invoice and accounting lines to the invoice
    """
    invoice = sequence.get('invoice')
    invoice.newContent(portal_type='Invoice Line',
        resource_value=sequence.get('resource'), quantity=3, price=555)
    invoice.newContent(portal_type='Sale Invoice Transaction Line',
        id ='receivable', source='account_module/customer',
        destination='account_module/supplier', quantity=-1665)
    invoice.newContent(portal_type='Sale Invoice Transaction Line',
        id='income', source='account_module/sale',
        destination='account_module/purchase', quantity=1665)

  def stepAddWrongInvoiceLines(self, sequence=None, sequence_list=None):
    """
    add some wrong invoice and accounting lines to the invoice
    """
    invoice = sequence.get('invoice')
    invoice.newContent(portal_type='Sale Invoice Transaction Line',
        id='bad_movement', source='account_module/sale',
        destination='account_module/purchase', quantity=2, price=4)
    invoice.newContent(portal_type='Sale Invoice Transaction Line',
        id='counter_bad_movement', source='account_module/sale',
        destination='account_module/purchase', quantity=-2, price=4)
    for movement in invoice.getMovementList():
      movement.edit(resource_value=sequence.get('resource'))

  def stepCheckStartInvoiceFail(self, sequence=None, sequence_list=None):
    """
    checks that it's not possible to start an invoice with really wrong
    lines
    """
    try:
      self.tic()
    except RuntimeError as exc:
      invoice = sequence.get('invoice')
      # check which activities are failing
      self.assertTrue(str(exc).startswith('tic is looping forever.'),
          '%s does not start with "tic is looping forever."' % str(exc))
      msg_list = [('/'.join(x.object_path), x.method_id)
          for x in self.getActivityTool().getMessageList()]
      self.assertTrue((invoice.getPath(), '_localBuild') in msg_list, msg_list)
      # flush failing activities
      activity_tool = self.getActivityTool()
      activity_tool.manageClearActivities(keep=0)
    else:
      self.fail("Error: stepStartInvoice didn't fail, the builder script"
          + " InvoiceTransaction_postTransactionLineGeneration should have"
          + " complained that accounting movements use multiple resources")

  def stepCheckSimulationTrees(self, sequence=None, sequence_list=None):
    """
    check that rules are created in the order we expect them
    """
    applied_rule_set = set()
    invoice = sequence.get('invoice')
    for movement in invoice.getMovementList():
      for sm in movement.getDeliveryRelatedValueList():
        applied_rule_set.add(sm.getRootAppliedRule())

    rule_dict = {
        'Order Root Simulation Rule': {
          'movement_type_list': ['Sale Order Line', 'Sale Order Cell'],
          'next_rule_list': ['Delivery Simulation Rule', ],
          },
        'Delivery Simulation Rule': {
          'movement_type_list': ['Sale Packing List Line', 'Sale Packing List Cell'],
          'next_rule_list': ['Invoice Simulation Rule', ],
          },
        'Trade Model Simulation Rule': {
          'next_rule_list': ['Invoice Transaction Simulation Rule'],
          },
        'Invoice Simulation Rule': {
          'movement_type_list': invoice.getPortalInvoiceMovementTypeList() \
              + invoice.getPortalAccountingMovementTypeList(),
          'next_rule_list': ['Invoice Transaction Simulation Rule', 'Payment Simulation Rule',
            'Trade Model Simulation Rule'],
          },
        'Invoice Transaction Simulation Rule': {
          'parent_movement_type_list': invoice.getPortalInvoiceMovementTypeList(),
          'movement_type_list': invoice.getPortalAccountingMovementTypeList(),
          'next_rule_list': ['Payment Simulation Rule'],
          },
        'Payment Simulation Rule': {
          'parent_movement_type_list': invoice.getPortalAccountingMovementTypeList(),
          'next_rule_list': [],
          },
        }

    def checkTree(rule):
      """
      checks the tree recursively
      """
      rule_type = rule.getSpecialiseValue().getPortalType()
      rule_def = rule_dict.get(rule_type, {})
      for k, v in six.iteritems(rule_def):
        if k == 'movement_type_list':
          for movement in rule.objectValues():
            if movement.getDeliveryValue() is not None:
              self.assertTrue(movement.getDeliveryValue().getPortalType() in v,
                  'looking for %s in %s on %s' % (
                  movement.getDeliveryValue().getPortalType(), v,
                  movement.getPath()))
        elif k == 'next_rule_list':
          for movement in rule.objectValues():
            found_rule_dict = {}
            for next_rule in movement.objectValues():
              next_rule_type = next_rule.getSpecialiseValue().getPortalType()
              self.assertTrue(next_rule_type in v,
                  'looking for %s in %s on %s' % (
                  next_rule_type, v, next_rule.getPath()))
              n = found_rule_dict.get(next_rule_type, 0)
              found_rule_dict[next_rule_type] = n + 1
            # for each movement, we want to make sure that each rule is not
            # instanciated more than once
            if len(found_rule_dict):
              self.assertEqual(set(six.itervalues(found_rule_dict)), {1})
        elif k == 'parent_movement_type_list':
          if rule.getParentValue().getDeliveryValue() is not None:
            parent_type = rule.getParentValue().getDeliveryValue().getPortalType()
            self.assertTrue(parent_type in v, 'looking for %s in %s on %s' % (
                parent_type, v, rule.getParentValue().getPath()))
        elif k == 'parent_id_list':
          self.assertTrue(rule.getParentId() in v, 'looking for %s in %s on %s'
              % (rule.getParentId(), v, rule.getPath()))
      for movement in rule.objectValues():
        for next_rule in movement.objectValues():
          checkTree(next_rule)

    for applied_rule in applied_rule_set:
      checkTree(applied_rule)

  def stepAddInvoiceLinesManyTransactions(self, sequence=None, sequence_list=None):
    """
    add some invoice and accounting lines to the invoice
    """
    invoice = sequence.get('invoice')
    invoice_line = invoice.newContent(portal_type='Invoice Line')
    transaction_line_1 = invoice.newContent(portal_type='Sale Invoice Transaction Line')
    transaction_line_2 = invoice.newContent(portal_type='Sale Invoice Transaction Line')
    self.tic()
    invoice_line.edit(resource_value=sequence.get('resource'), quantity=3,
        price=555)
    transaction_line_1.edit(id ='receivable', source='account_module/customer',
        destination='account_module/supplier', quantity=-1665)
    transaction_line_2.edit(
        id='income', source='account_module/sale',
        destination='account_module/purchase', quantity=1665)

  def stepInvoiceBuilderAlarm(self, sequence=None,
                                  sequence_list=None, **kw):
    self.portal.portal_alarms.invoice_builder_alarm.activeSense()


class TestSaleInvoiceMixin(TestInvoiceMixin,
                           ERP5TypeTestCase):
  """Test sale invoice are created from orders then packing lists.

    Those tests methods only work for sale, because sale and purchase invoice
    are not built at the same time on packing list workflow.
  """
  quiet = 0
  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  invoice_cell_portal_type = 'Invoice Cell'
  invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'
  payment_portal_type = 'Payment Transaction'

  # default sequence for one line of not varianted resource.
  PACKING_LIST_DEFAULT_SEQUENCE = """
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
      stepPackingListBuilderAlarm
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
      stepPackingListBuilderAlarm
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
      stepPackingListBuilderAlarm
      stepTic
      stepCheckOrderRule
      stepCheckOrderSimulation
      stepCheckDeliveryBuilding
      stepDecreasePackingListLineQuantity
      stepCheckPackingListIsCalculating
      stepTic
      stepCheckPackingListIsDiverged
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
