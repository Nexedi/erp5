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
"""
  Tests invoice creation from simulation.

"""
import sys, zipfile, xml.dom.minidom
import StringIO

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload, DummyMailHost
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5OOo.OOoUtils import OOoParser
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from Acquisition import aq_parent
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from testPackingList import TestPackingListMixin
from Products.ERP5.tests.utils import newSimulationExpectedFailure

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
      self.assertNotEquals(None,
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
    self.createCategories()
    self.validateRules()
    self.createBusinessProcess()
    self.login()

  def beforeTearDown(self):
    self.abort()
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

  def login(self):
    """login, without manager role"""
    uf = self.getPortal().acl_users
    uf._doAddUser('test_invoice_user', '', ['Assignee', 'Assignor', 'Member',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('test_invoice_user').__of__(uf)
    newSecurityManager(None, user)

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
                trade_phase='default/accounting',
                trade_date='trade_phase/default/invoicing',
                membership_criterion_base_category_list=('destination_region',
                                                         'product_line'),
                membership_criterion_category=(
                  'destination_region/region/' + self.default_region,
                  'product_line/apparel'))
      account_module = portal.account_module
      for account_id, account_gap, account_type in self.account_definition_list:
        if not account_module.has_key(account_id):
          account = account_module.newContent(account_id, gap=account_gap,
                                              account_type=account_type)
          portal.portal_workflow.doActionFor(account, 'validate_action')
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
    self.assertNotEquals(client1.getRegionValue(), None)
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
    self.assertNotEquals(len(rule_list), 0)
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
      self.assertNotEquals(len(simulation_movement_list), 0)
      for simulation_movement in simulation_movement_list :
        invoice_transaction_rule_list.extend([applied_rule for applied_rule
          in simulation_movement.objectValues() if applied_rule \
              .getSpecialiseValue().getPortalType()
              == 'Invoice Transaction Simulation Rule'])
        resource_list = sequence.get('resource_list')
        self.assertEqual(simulation_movement.getPortalType(),
                          'Simulation Movement')
        self.assertTrue(simulation_movement.getResourceValue() in
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
      invoice_transaction_rule = \
        applied_invoice_transaction_rule.getSpecialiseValue()
      self.assertEqual(3, len(applied_invoice_transaction_rule.objectValues()))
      for line_id, line_source_id, line_destination_id, line_ratio in \
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
      self.assertNotEquals(len(simulation_movement_list), 0)
      total_quantity = 0
      for simulation_movement in simulation_movement_list :
        total_quantity += simulation_movement.getQuantity()
        # check that those movements come from the same root applied
        # rule than the order.
        self.assertEqual( simulation_movement.getRootAppliedRule(),
                           order_root_applied_rule)
      self.assertEqual(total_quantity, movement.getQuantity())

  def checkMirrorAcquisition(self, object, acquired_object):
    """
      Check if properties are well acquired for mirrored case
    """
    # packing_list_movement, simulation_movement

    self.assertEqual(acquired_object.getStartDate(), object.getStopDate())
    self.assertEqual(acquired_object.getStopDate(), object.getStartDate())
    self.assertEqual(acquired_object.getSourceValue(), \
                      object.getDestinationValue())
    self.assertEqual(acquired_object.getDestinationValue(), \
                      object.getSourceValue())

    self.assertEqual(acquired_object.getSourceSectionValue(), \
                      object.getDestinationSectionValue())
    self.assertEqual(acquired_object.getDestinationSectionValue(), \
                      object.getSourceSectionValue())

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
        self.assert_(invoice_movement.getRelativeUrl().\
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
    order_rule = sequence.get('order_rule')
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
    account_module = self.portal.account_module
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
      self.assertAlmostEquals(expected_dict[key],found_dict[key],places=2)
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
      self.assertAlmostEquals(expected_dict[key], found_dict[key], places=2)

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

  def stepRemoveDateMovementGroupForTransactionBuilder(self, sequence=None,
            sequence_list=None, **kw):
    """
    Remove DateMovementGroup
    """
    portal = self.getPortal()
    builder = portal.portal_deliveries.sale_invoice_transaction_builder
    delivery_movement_group_list = builder.getDeliveryMovementGroupList()
    uf = self.getPortal().acl_users
    uf._doAddUser('admin', '', ['Manager'], [])
    user = uf.getUserById('admin').__of__(uf)
    newSecurityManager(None, user)
    for movement_group in delivery_movement_group_list:
      if movement_group.getPortalType() == 'Property Movement Group':
        # it contains 'start_date' and 'stop_date' only, so we remove
        # movement group itself.
        builder.deleteContent(movement_group.getId())
    builder.newContent(
      portal_type = 'Parent Explanation Movement Group',
      collect_order_group='delivery',
      int_index=len(delivery_movement_group_list)+1
      )
    user = uf.getUserById('test_invoice_user').__of__(uf)
    newSecurityManager(None, user)

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
    """
    split and defer at the invoice level
    """
    invoice = sequence.get('invoice')
    kw = {'listbox':[
      {'listbox_key':line.getRelativeUrl(),
       'choice':'SplitAndDefer'} for line in invoice.getMovementList()]}
    self.portal.portal_workflow.doActionFor(
      invoice,
      'split_and_defer_action',
      start_date=self.datetime + 15,
      stop_date=self.datetime + 25,
      **kw)
    pass

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

  def stepAddInvoiceLines(self, sequence=None, sequence_list=[]):
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

  def stepAddWrongInvoiceLines(self, sequence=None, sequence_list=[]):
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

  def stepCheckStartInvoiceFail(self, sequence=None, sequence_list=[]):
    """
    checks that it's not possible to start an invoice with really wrong
    lines
    """
    try:
      self.tic()
    except RuntimeError, exc:
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

  def stepCheckSimulationTrees(self, sequence=None, sequence_list=[]):
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
        'Invoice Simulation Rule': {
          'movement_type_list': invoice.getPortalInvoiceMovementTypeList(),
          'next_rule_list': ['Invoice Transaction Simulation Rule', 'Trade Model Simulation Rule'],
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
      for k, v in rule_def.iteritems():
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
              self.assertEqual(set(found_rule_dict.itervalues()), {1})
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

  def stepAddInvoiceLinesManyTransactions(self, sequence=None, sequence_list=[]):
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

class TestInvoice(TestInvoiceMixin):
  """Test methods for sale and purchase invoice.
  Subclasses must defines portal types to use.
  """
  quiet = 1
  def test_invoice_transaction_line_resource(self):
    """
    tests that simulation movements corresponding to accounting line have a
    good resource in the simulation
    """
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency',
                                base_unit_quantity=0.01)
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            price_currency= currency.getRelativeUrl(),
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            price_currency= currency.getRelativeUrl(),
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)

    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

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

  @newSimulationExpectedFailure
  def test_modify_planned_order_invoicing_rule(self):
    """
    tests that modifying a planned order affects movements from invoicing
    rule
    """
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency',
                                base_unit_quantity=0.01)

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            price_currency= currency.getRelativeUrl())
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            price_currency= currency.getRelativeUrl())
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)

    other_entity = self.portal.organisation_module.newContent(
                                    portal_type='Organisation',
                                    title='Other Entity',
                                    price_currency=currency.getRelativeUrl())
    other_project = self.portal.project_module.newContent(
                                    portal_type='Project',
                                    title='Other Project')
    order.plan()
    self.tic()
    self.assertEqual('planned', order.getSimulationState())

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    delivery_movement = related_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]

    order_line.setSourceValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                      invoice_movement.getSourceValue())

    order_line.setDestinationValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                      invoice_movement.getDestinationValue())

    order_line.setSourceSectionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                      invoice_movement.getSourceSectionValue())

    # make sure destination_section != source_section, this might be needed by
    # some rules
    order_line.setSourceSectionValue(order_line.getDestinationSectionValue())

    order_line.setDestinationSectionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getDestinationSectionValue())

    order_line.setSourceAdministrationValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourceAdministrationValue())

    order_line.setDestinationAdministrationValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationAdministrationValue())

    order_line.setSourceDecisionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourceDecisionValue())

    order_line.setDestinationDecisionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationDecisionValue())

    order_line.setSourceProjectValue(other_project)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_project,
                 invoice_movement.getSourceProjectValue())

    order_line.setDestinationProjectValue(other_project)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_project,
            invoice_movement.getDestinationProjectValue())

    order_line.setSourcePaymentValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourcePaymentValue())

    order_line.setDestinationPaymentValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationPaymentValue())

    order_line.setSourceFunctionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourceFunctionValue())

    order_line.setDestinationFunctionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationFunctionValue())

    self.assertNotEquals(123, order_line.getPrice())
    order_line.setPrice(123)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(123,
            invoice_movement.getPrice())

    self.assertNotEquals(456, order_line.getQuantity())
    order_line.setQuantity(456)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(456,
            invoice_movement.getQuantity())

    other_resource = self.portal.product_module.newContent(
                                        portal_type='Product',
                                        title='Other Resource')
    order_line.setResourceValue(other_resource)
    self.tic()
    # after changing 'resource', related simulation movement will be
    # replaced with another id, and we need to find the appropriate one
    # here.
    delivery_movement = related_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_resource,
            invoice_movement.getResourceValue())

    order_line.setStartDate(DateTime(2001, 02, 03))
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(DateTime(2001, 02, 03),
                 invoice_movement.getStartDate())

    order_line.setStopDate(DateTime(2002, 03, 04))
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(DateTime(2002, 03, 04),
                 invoice_movement.getStopDate())

  @newSimulationExpectedFailure
  def test_modify_planned_order_invoice_transaction_rule(self):
    """
    tests that modifying a planned order affects movements from invoice
    transaction rule
    """
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency',
                                base_unit_quantity=0.01)
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)
    other_entity = self.portal.organisation_module.newContent(
                                      portal_type='Organisation',
                                      title='Other Entity',
                                      default_address_region=self.default_region)
    other_project = self.portal.project_module.newContent(
                                      portal_type='Project',
                                      title='Other Project')
    order.plan()
    self.tic()
    self.assertEqual('planned', order.getSimulationState())

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    order_movement = related_applied_rule.contentValues()[0]
    delivery_applied_rule = order_movement.contentValues()[0]
    delivery_movement = delivery_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = invoice_movement.contentValues()[0]

    # utility function to return the simulation movement that should be used
    # for "income" line
    def getIncomeSimulationMovement(applied_rule):
      for movement in applied_rule.contentValues():
        if movement.getDestination() == 'account_module/purchase'\
            and movement.getSource() == 'account_module/sale':
          return movement
      self.fail('Income movement not found')

    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)

    order_line.setSourceSectionValue(other_entity)
    self.tic()
    self.assertEqual(other_entity,
                      invoice_transaction_movement.getSourceSectionValue())

    # make sure destination_section != source_section, this might be needed by
    # some rules
    order_line.setSourceSectionValue(order_line.getDestinationSectionValue())

    order_line.setDestinationSectionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getDestinationSectionValue())

    order_line.setSourceAdministrationValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourceAdministrationValue())

    order_line.setDestinationAdministrationValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationAdministrationValue())

    order_line.setSourceDecisionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourceDecisionValue())

    order_line.setDestinationDecisionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationDecisionValue())

    order_line.setSourceProjectValue(other_project)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_project,
                 invoice_transaction_movement.getSourceProjectValue())

    order_line.setDestinationProjectValue(other_project)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_project,
            invoice_transaction_movement.getDestinationProjectValue())

    order_line.setSourceFunctionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourceFunctionValue())

    order_line.setDestinationFunctionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationFunctionValue())

    order_line.setSourcePaymentValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourcePaymentValue())

    order_line.setDestinationPaymentValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationPaymentValue())

    order_line.setQuantity(1)
    order_line.setPrice(123)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(123,
            invoice_transaction_movement.getQuantity())

    order_line.setQuantity(456)
    order_line.setPrice(1)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(456,
            invoice_transaction_movement.getQuantity())

    order_line.setStartDate(DateTime(2001, 02, 03))
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(DateTime(2001, 02, 03),
                 invoice_transaction_movement.getStartDate())

    order_line.setStopDate(DateTime(2002, 03, 04))
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(DateTime(2002, 03, 04),
                 invoice_transaction_movement.getStopDate())

  def test_Invoice_viewAsODT(self):
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    resource_tax = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource Tax',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    invoice = self.portal.getDefaultModule(self.invoice_portal_type).newContent(
                              portal_type=self.invoice_portal_type,
                              start_date=DateTime(2008, 12, 31),
                              title='Invoice',
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    product_line1 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            base_contribution='base_amount/tax1',
                            price=3)
    product_line2 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=20,
                            base_contribution='base_amount/tax1',
                            price=5)
    product_line3 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=60,
                            base_contribution='base_amount/tax2',
                            price=5)
    product_line4 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=60,
                            price=3)
    product_line5 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=7,
                            price=20)
    tax_line1 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource_tax,
                            use='trade/tax',
                            base_contribution='base_amount/tax1',
                            quantity=130,
                            price=0.2)
    tax_line2 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource_tax,
                            use='trade/tax',
                            base_contribution='base_amount/tax2',
                            quantity=300,
                            price=0.05)
    tax_line3 = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource_tax,
                            use='trade/tax',
                            base_contribution='base_amount/tax3',
                            quantity=20,
                            price=0.1)
    invoice.confirm()
    self.tic()
    odt = invoice.Invoice_viewAsODT()
    import cStringIO
    output = cStringIO.StringIO()
    output.write(odt)
    m = OpenDocumentTextFile(output)
    text_content=m.toString().encode('ascii','replace')
    if text_content.find('Resource Tax') != -1 :
      self.fail('fail to delete the tax line in product line')
    if text_content.find('Tax Code') == -1 :
      self.fail('fail to add the tax code')
    if text_content.find('Amount') == -1 :
      self.fail('fail to add the amount for each tax')
    if text_content.find('Rate') == -1 :
      self.fail('fail to add the Rate for each tax')
    tax1_product_total_price=str(10*3+20*5)
    if text_content.find(tax1_product_total_price) == -1 :
      self.fail('fail to get the total price of products which tax1')
    tax2_product_total_price=str(60*5)
    if text_content.find(tax2_product_total_price) == -1 :
      self.fail('fail to get the total price of products which tax2')
    no_tax_product_total_price=str(60*3+7*20)
    if text_content.find(no_tax_product_total_price) == -1 :
      self.fail('fail to get the total price of products which have no tax')
    product_total_price_no_tax=str(10*3+20*5+60*5+60*3+7*20)
    if text_content.find(product_total_price_no_tax) == -1 :
      self.fail('fail to get the total price of the products without tax')
    product_total_price=str(10*3+20*5+60*5+60*3+7*20+130*0.2+300*0.05+20*0.1)
    if text_content.find(product_total_price) == -1 :
      self.fail('fail to get the total price of the products with tax')
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_Invoice_viewAsODT_empty_image(self):
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    client_logo = client.newContent(portal_type='Embedded File',
                                    id='default_image')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    vendor_logo = vendor.newContent(portal_type='Embedded File',
                                    id='default_image')
    self.assertEqual(0, vendor_logo.getSize())
    self.assertEqual(0, vendor.getDefaultImageWidth())
    self.assertEqual(0, vendor.getDefaultImageHeight())
    invoice = self.portal.getDefaultModule(self.invoice_portal_type).newContent(
                              portal_type=self.invoice_portal_type,
                              start_date=DateTime(2008, 12, 31),
                              title='Invoice',
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    invoice.confirm()
    self.tic()

    odt = invoice.Invoice_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

    # the <draw:image> should not be present, because there's no logo
    parser = OOoParser()
    parser.openFromString(odt)
    style_xml = parser.oo_files['styles.xml']
    self.assert_('<draw:image' not in style_xml)

  def test_Invoice_viewAsODT_invalid_image(self):
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    file_data = FileUpload(__file__, 'rb')
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    client_logo = client.newContent(portal_type='Embedded File',
                                    id='default_image',
                                    file=file_data)
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    vendor_logo = vendor.newContent(portal_type='Embedded File',
                                    id='default_image',
                                    file=file_data)

    # width and height of an invalid image are -1 according to
    # OFS.Image.getImageInfo maybe this is not what we want here ?
    self.assertEqual(-1, vendor.getDefaultImageWidth())
    self.assertEqual(-1, vendor.getDefaultImageHeight())

    invoice = self.portal.getDefaultModule(self.invoice_portal_type).newContent(
                              portal_type=self.invoice_portal_type,
                              start_date=DateTime(2008, 12, 31),
                              title='Invoice',
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    line = invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    invoice.confirm()
    self.tic()

    odt = invoice.Invoice_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_invoice_building_with_cells(self):
    # if the order has cells, the invoice built from that order must have
    # cells too
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    variation_base_category_list=['size'])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,)
    order_line.setVariationBaseCategoryList(('size', ))
    order_line.setVariationCategoryList(['size/Baby', 'size/Child/32'])
    order_line.updateCellRange()

    cell_baby = order_line.newCell('size/Baby', base_id='movement',
                             portal_type=self.order_cell_portal_type)
    cell_baby.edit(quantity=10,
                   price=4,
                   variation_category_list=['size/Baby'],
                   mapped_value_property_list=['quantity', 'price'],)

    cell_child_32 = order_line.newCell('size/Child/32', base_id='movement',
                                 portal_type=self.order_cell_portal_type)
    cell_child_32.edit(quantity=20,
                       price=5,
                       variation_category_list=['size/Child/32'],
                       mapped_value_property_list=['quantity', 'price'],)
    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

    related_packing_list = order.getCausalityRelatedValue(
                                  portal_type=self.packing_list_portal_type)
    self.assertNotEquals(related_packing_list, None)

    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(related_invoice, None)

    line_list = related_invoice.contentValues(
                     portal_type=self.invoice_line_portal_type)
    self.assertEqual(1, len(line_list))
    invoice_line = line_list[0]

    self.assertEqual(resource, invoice_line.getResourceValue())
    self.assertEqual(['size'], invoice_line.getVariationBaseCategoryList())
    self.assertEqual(2,
          len(invoice_line.getCellValueList(base_id='movement')))

    cell_baby = invoice_line.getCell('size/Baby', base_id='movement')
    self.assertNotEquals(cell_baby, None)
    self.assertEqual(resource, cell_baby.getResourceValue())
    self.assertEqual(10, cell_baby.getQuantity())
    self.assertEqual(4, cell_baby.getPrice())
    self.assertTrue('size/Baby' in
                    cell_baby.getVariationCategoryList())
    self.assertTrue(cell_baby.isMemberOf('size/Baby'))

    cell_child_32 = invoice_line.getCell('size/Child/32', base_id='movement')
    self.assertNotEquals(cell_child_32, None)
    self.assertEqual(resource, cell_child_32.getResourceValue())
    self.assertEqual(20, cell_child_32.getQuantity())
    self.assertEqual(5, cell_child_32.getPrice())
    self.assertTrue('size/Child/32' in
                    cell_child_32.getVariationCategoryList())
    self.assertTrue(cell_child_32.isMemberOf('size/Child/32'))



  def test_invoice_created_from_packing_list_with_no_order(self):
    # if the order has cells and an aggregate, the invoice built
    #from that order must have
    # cells too
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    variation_base_category_list=['size'])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    no_order_packing_list = \
self.portal.getDefaultModule(self.packing_list_portal_type).newContent(
                              portal_type=self.packing_list_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    packing_list_line = no_order_packing_list.newContent(
                        portal_type=self.packing_list_line_portal_type,
                                  resource_value=resource,)
    packing_list_line.setVariationBaseCategoryList(('size', ))
    packing_list_line.setVariationCategoryList(['size/Baby', 'size/Child/32'])
    packing_list_line.updateCellRange()

    cell_baby = packing_list_line.newCell('size/Baby', base_id='movement',
                             portal_type=self.packing_list_cell_portal_type)
    cell_baby.edit(quantity=10,
                   price=4,
                   variation_category_list=['size/Baby'],
                   mapped_value_property_list=['quantity', 'price'],)

    cell_child_32 = packing_list_line.newCell(
                                'size/Child/32',base_id='movement',
                                 portal_type=self.packing_list_cell_portal_type)
    cell_child_32.edit(quantity=20,
                       price=5,
                       variation_category_list=['size/Child/32'],
                       mapped_value_property_list=['quantity', 'price'],)
    no_order_packing_list.confirm()
    self.tic()
    self.assertNotEquals(no_order_packing_list, None)

    no_order_packing_list.start()
    no_order_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = no_order_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(related_invoice, None)

    line_list = related_invoice.contentValues(
                     portal_type=self.invoice_line_portal_type)
    self.assertEqual(1, len(line_list))
    invoice_line = line_list[0]

    self.assertEqual(resource, invoice_line.getResourceValue())
    self.assertEqual(['size'], invoice_line.getVariationBaseCategoryList())
    self.assertEqual(2,
          len(invoice_line.getCellValueList(base_id='movement')))

    cell_baby = invoice_line.getCell('size/Baby', base_id='movement')
    self.assertNotEquals(cell_baby, None)
    self.assertEqual(resource, cell_baby.getResourceValue())
    self.assertEqual(10, cell_baby.getQuantity())
    self.assertEqual(4, cell_baby.getPrice())
    self.assertTrue('size/Baby' in
                    cell_baby.getVariationCategoryList())
    self.assertTrue(cell_baby.isMemberOf('size/Baby'))

    cell_child_32 = invoice_line.getCell('size/Child/32', base_id='movement')
    self.assertNotEquals(cell_child_32, None)
    self.assertEqual(resource, cell_child_32.getResourceValue())
    self.assertEqual(20, cell_child_32.getQuantity())
    self.assertEqual(5, cell_child_32.getPrice())
    self.assertTrue('size/Child/32' in
                    cell_child_32.getVariationCategoryList())
    self.assertTrue(cell_child_32.isMemberOf('size/Child/32'))

  def test_invoice_building_with_cells_and_aggregate(self):
    # if the order has cells and an aggregate, the invoice built
    #from that order must have
    # cells too
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    variation_base_category_list=['size'])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,)
    order_line.setVariationBaseCategoryList(('size', ))
    order_line.setVariationCategoryList(['size/Baby', 'size/Child/32'])
    order_line.updateCellRange()

    cell_baby = order_line.newCell('size/Baby', base_id='movement',
                             portal_type=self.order_cell_portal_type)
    cell_baby.edit(quantity=10,
                   price=4,
                   variation_category_list=['size/Baby'],
                   mapped_value_property_list=['quantity', 'price'],)

    cell_child_32 = order_line.newCell('size/Child/32', base_id='movement',
                                 portal_type=self.order_cell_portal_type)
    cell_child_32.edit(quantity=20,
                       price=5,
                       variation_category_list=['size/Child/32'],
                       mapped_value_property_list=['quantity', 'price'],)
    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

    related_packing_list = order.getCausalityRelatedValue(
                                  portal_type=self.packing_list_portal_type)
    self.assertNotEquals(related_packing_list, None)

    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(related_invoice, None)

    line_list = related_invoice.contentValues(
                     portal_type=self.invoice_line_portal_type)
    self.assertEqual(1, len(line_list))
    invoice_line = line_list[0]

    self.assertEqual(resource, invoice_line.getResourceValue())
    self.assertEqual(['size'], invoice_line.getVariationBaseCategoryList())
    self.assertEqual(2,
          len(invoice_line.getCellValueList(base_id='movement')))

    cell_baby = invoice_line.getCell('size/Baby', base_id='movement')
    self.assertNotEquals(cell_baby, None)
    self.assertEqual(resource, cell_baby.getResourceValue())
    self.assertEqual(10, cell_baby.getQuantity())
    self.assertEqual(4, cell_baby.getPrice())
    self.assertTrue('size/Baby' in
                    cell_baby.getVariationCategoryList())
    self.assertTrue(cell_baby.isMemberOf('size/Baby'))

    cell_child_32 = invoice_line.getCell('size/Child/32', base_id='movement')
    self.assertNotEquals(cell_child_32, None)
    self.assertEqual(resource, cell_child_32.getResourceValue())
    self.assertEqual(20, cell_child_32.getQuantity())
    self.assertEqual(5, cell_child_32.getPrice())
    self.assertTrue('size/Child/32' in
                    cell_child_32.getVariationCategoryList())
    self.assertTrue(cell_child_32.isMemberOf('size/Child/32'))


  def test_description_copied_on_lines(self):
    # if the order lines have different descriptions, description must be
    # copied in the simulation and on created movements
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    resource2 = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource2',)
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    order.newContent(portal_type=self.order_line_portal_type,
                                  quantity=3,
                                  price=10,
                                  description='The first line',
                                  resource_value=resource,)
    order.newContent(portal_type=self.order_line_portal_type,
                                  quantity=5,
                                  price=10,
                                  description='The second line',
                                  resource_value=resource2,)

    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

    related_packing_list = order.getCausalityRelatedValue(
                                  portal_type=self.packing_list_portal_type)
    self.assertNotEquals(related_packing_list, None)

    movement_list = related_packing_list.getMovementList()
    self.assertEqual(2, len(movement_list))
    self.assertEqual(['The first line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 3])
    self.assertEqual(['The second line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 5])

    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(related_invoice, None)

    movement_list = related_invoice.getMovementList(
                              portal_type=self.invoice_line_portal_type)
    self.assertEqual(2, len(movement_list))
    self.assertEqual(['The first line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 3])
    self.assertEqual(['The second line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 5])


  def test_CopyAndPaste(self):
    """Test copy on paste on Invoice.
    When an invoice is copy/pasted, references should be resetted.
    """
    accounting_module = self.portal.accounting_module
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

  def test_delivery_mode_and_incoterm_on_invoice(self):
    """
    test that categories delivery_mode and incoterm are copied on
    the invoice by the delivery builder
    """
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              delivery_mode=self.mail_delivery_mode,
                              incoterm=self.cpt_incoterm,
                              title='Order')
    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=5,
                                  price=2)
    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type=self.packing_list_portal_type)
    self.assertNotEquals(related_packing_list, None)
    self.assertEqual(related_packing_list.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEqual(related_packing_list.getIncoterm(),
                         order.getIncoterm())
    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(related_invoice, None)
    self.assertEqual(related_invoice.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEqual(related_invoice.getIncoterm(),
                         order.getIncoterm())


  def test_01_quantity_unit_copied(self):
    """
    tests that when a resource uses different quantity unit that the
    quantity units are copied on the packing list line and then the invoice
    line using the delivery builers
    """
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
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
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
                          portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                             quantity_unit = self.unit_piece_quantity_unit,
                                  quantity=5,
                                  price=3)
    second_order_line = order.newContent(
                          portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                             quantity_unit=self.mass_quantity_unit,
                                  quantity=1.5,
                                  price=2)
    self.assertEqual(first_order_line.getQuantityUnit(),
                      self.unit_piece_quantity_unit)
    self.assertEqual(second_order_line.getQuantityUnit(),
                      self.mass_quantity_unit)

    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type=self.packing_list_portal_type)
    self.assertNotEquals(related_packing_list, None)
    movement_list = related_packing_list.getMovementList()
    self.assertEqual(len(movement_list),2)
    movement_list = sorted(movement_list, key=lambda x: x.getQuantity())
    self.assertEqual(movement_list[0].getQuantityUnit(),
                      self.mass_quantity_unit)
    self.assertEqual(movement_list[0].getQuantity(), 1.5)
    self.assertEqual(movement_list[1].getQuantityUnit(),
                      self.unit_piece_quantity_unit)
    self.assertEqual(movement_list[1].getQuantity(), 5)

    related_packing_list.start()
    related_packing_list.stop()
    related_packing_list.deliver()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                                portal_type=self.invoice_portal_type)
    self.assertNotEquals(related_invoice, None)
    movement_list = related_invoice.getMovementList()
    self.assertEqual(len(movement_list),2)
    movement_list = sorted(movement_list, key=lambda x: x.getQuantity())
    self.assertEqual(movement_list[0].getQuantityUnit(),
                      self.mass_quantity_unit)
    self.assertEqual(movement_list[0].getQuantity(), 1.5)
    self.assertEqual(movement_list[1].getQuantityUnit(),
                      self.unit_piece_quantity_unit)
    self.assertEqual(movement_list[1].getQuantity(), 5)



  def _acceptDivergenceOnInvoice(self, invoice, divergence_list):
    print invoice, divergence_list
    self._solveDivergence(invoice, 'quantity', 'Accept Solver')

  def test_accept_quantity_divergence_on_invoice_with_stopped_packing_list(
                self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.PACKING_LIST_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.getMovementList()[0]
    previous_quantity = packing_list_line.getQuantity()

    packing_list.setReady()
    packing_list.start()
    packing_list.stop()
    self.assertEqual('stopped', packing_list.getSimulationState())
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(invoice, None)
    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]

    new_quantity = invoice_line.getQuantity() * 2
    invoice_line.setQuantity(new_quantity)

    self.tic()

    self.assertTrue(invoice.isDivergent())
    divergence_list = invoice.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

    # accept decision
    self._acceptDivergenceOnInvoice(invoice, divergence_list)

    self.tic()
    self.assertEqual('solved', invoice.getCausalityState())

    self.assertEqual([], invoice.getDivergenceList())
    self.assertEqual(new_quantity, invoice_line.getQuantity())
    self.assertEqual(new_quantity,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())

    self.assertEqual([], packing_list.getDivergenceList())
    self.assertEqual('solved', packing_list.getCausalityState())

  def _adoptDivergenceOnInvoice(self, invoice, divergence_list):
    print invoice, divergence_list
    self._solveDivergence(invoice, 'quantity', 'Adopt Solver')

  def test_adopt_quantity_divergence_on_invoice_line_with_stopped_packing_list(
                self, quiet=quiet):
    # #1053
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.PACKING_LIST_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.getMovementList()[0]
    previous_quantity = packing_list_line.getQuantity()
    previous_resource = packing_list_line.getResource()
    previous_price = packing_list_line.getPrice()

    packing_list.setReady()
    packing_list.start()
    packing_list.stop()
    self.assertEqual('stopped', packing_list.getSimulationState())
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(invoice, None)
    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]

    new_quantity = invoice_line.getQuantity() * 2
    invoice_line.setQuantity(new_quantity)

    self.tic()

    self.assertTrue(invoice.isDivergent())
    divergence_list = invoice.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

    # adopt prevision
    self._adoptDivergenceOnInvoice(invoice, divergence_list)

    self.tic()
    self.assertEqual([], invoice.getDivergenceList())
    self.assertEqual('solved', invoice.getCausalityState())

    self.assertEqual(1,
        len(invoice.getMovementList(portal_type=self.invoice_line_portal_type)))
    self.assertEqual(0,
        len(invoice.getMovementList(portal_type=self.invoice_transaction_line_portal_type)))

    self.assertEqual(previous_resource, invoice_line.getResource())
    self.assertEqual(previous_quantity, invoice_line.getQuantity())
    self.assertEqual(previous_price, invoice_line.getPrice())
    self.assertEqual(previous_quantity,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())

    self.assertEqual([], packing_list.getDivergenceList())
    self.assertEqual('solved', packing_list.getCausalityState())

  def test_subcontent_reindexing(self):
    """Tests, that modification on Order are propagated to lines and cells
    during reindxation"""
    invoice = self.portal.getDefaultModule(self.invoice_portal_type
        ).newContent(portal_type=self.invoice_portal_type,
            created_by_builder=1)
    self.tic()
    invoice_line = invoice.newContent(
        portal_type=self.invoice_line_portal_type)
    invoice_cell = invoice_line.newContent(
        portal_type=self.invoice_cell_portal_type)
    transaction_line = invoice.newContent(
        portal_type=self.invoice_transaction_line_portal_type)
    self._testSubContentReindexing(invoice, [invoice_line, transaction_line,
      invoice_cell])

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

class TestSaleInvoice(TestSaleInvoiceMixin, TestInvoice, ERP5TypeTestCase):
  """Tests for sale invoice.
  """
  quiet = 0

  # fix inheritance
  login = TestInvoiceMixin.login

  @UnrestrictedMethod
  def createCategories(self):
    TestPackingListMixin.createCategories(self)
    TestInvoiceMixin.createCategories(self)

  getNeededCategoryList = TestInvoiceMixin.getNeededCategoryList

  def test_01_SimpleInvoice(self, quiet=quiet):
    """
    Checks that a Simple Invoice is created from a Packing List
    """
    if not quiet:
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
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckInvoiceBuilding
        stepRebuildAndCheckNothingIsCreated
        stepCheckInvoicesConsistency
        stepCheckInvoiceLineHasReferenceAndIntIndex
      """)
    sequence_list.play(self, quiet=quiet)

  def stepCreateCurrency(self, sequence):
    currency = self.portal.currency_module.newContent(
      portal_type="Currency", title="Currency",
      base_unit_quantity=0.01)
    sequence.edit(currency=currency)

  def stepCheckInvoiceWithBadPrecision(self, sequence):
    portal = self.portal
    vendor = sequence.get('vendor')
    invoice = portal.accounting_module.newContent(
      portal_type="Sale Invoice Transaction",
      specialise=self.business_process,
      source_section_value=vendor,
      start_date=self.datetime,
      price_currency_value=sequence.get('currency'),
      destination_section_value=sequence.get('client1'),
      source_value=vendor)
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    sale_supply_line_source_account="account_module/sale",
                    product_line='apparel')
    product_line = invoice.newContent(portal_type="Invoice Line",
      resource_value=resource, quantity=1, price=0.014)
    product_line = invoice.newContent(portal_type="Invoice Line",
      resource_value=resource, quantity=1, price=0.014)
    self.tic()
    invoice.plan()
    invoice.confirm()
    self.tic()
    invoice.start()
    self.tic()
    movement_list = invoice.getMovementList(
        portal_type=invoice.getPortalAccountingMovementTypeList())
    receivable_line = [m for m in movement_list \
      if m.getSourceValue().getAccountType() == \
        "asset/receivable"][0]
    self.assertEquals(0.03, receivable_line.getSourceDebit())
    data = invoice.Invoice_getODTDataDict()
    precision = invoice.getQuantityPrecisionFromResource(
      invoice.getResource())
    self.assertEquals(round(data['total_price'], precision),
      receivable_line.getSourceDebit())
    vat_line = [m for m in movement_list \
      if m.getSourceValue().getAccountType() == \
        "liability/payable/collected_vat"][0]
    self.assertEquals(0.0, vat_line.getSourceDebit())
    income_line = [m for m in movement_list \
      if m.getSourceValue().getAccountType() == \
        "income"][0]
    self.assertEquals(0.03, income_line.getSourceCredit())

  def test_AccountingTransaction_roundDebitCredit(self):
    """
      Check that with two invoice lines with total price equal 0.14,
      the receivable line will be 0.03 and vat line 0
    """
    sequence_list = SequenceList()
    sequence_list.addSequenceString("""
      stepCreateCurrency
      stepCreateEntities
      stepCheckInvoiceWithBadPrecision
    """)
    sequence_list.play(self)

  def test_02_TwoInvoicesFromTwoPackingList(self, quiet=quiet):
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
    if not quiet: self.logMessage('Two Invoices from Two Packing List')
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
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckTwoInvoices
        stepRemoveDateMovementGroupForTransactionBuilder
        stepStartTwoInvoices
        stepTic
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckTwoInvoicesTransactionLines
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self, quiet=quiet)

  def test_03_InvoiceEditAndInvoiceRule(self, quiet=quiet):
    """
    Invoice Rule should not be applied on invoice lines created from\
    Packing List.

    We want to prevent this from happening:
      - Create a packing list
      - An invoice is created from packing list
      - Invoice is edited, updateSimulation is called
      - A new Invoice Rule is created for this invoice, and accounting
        movements for this invoice are present twice in the simulation.
    """
    if not quiet:
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
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckInvoiceBuilding
        stepEditInvoice
        stepTic
        stepCheckInvoiceRuleNotAppliedOnInvoiceEdit
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self, quiet=quiet)

  def test_04_PackingListEditAndInvoiceRule(self, quiet=quiet):
    """
    Delivery Rule should not be applied on packing list lines created\
    from Order.
    """
    if not quiet:
      self.logMessage('Packing List Edit')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepEditPackingList
        stepTic
        stepCheckDeliveryRuleNotAppliedOnPackingListEdit
      """)
    sequence_list.play(self, quiet=quiet)

  def test_05_InvoiceEditPackingListLine(self, quiet=quiet):
    """
    Checks that editing a Packing List Line still creates a correct
    Invoice
    """
    if not quiet:
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
      stepInvoiceBuilderAlarm
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
    """)
    sequence_list.play(self, quiet=quiet)

  def test_06_InvoiceDeletePackingListLine(self, quiet=quiet):
    """
    Checks that deleting a Packing List Line still creates a correct
    Invoice
    """
    if not quiet:
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
      stepInvoiceBuilderAlarm
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
      stepTic
    """)
    sequence_list.play(self, quiet=quiet)

  def test_07_InvoiceAddPackingListLine(self, quiet=quiet):
    """
    Checks that adding a Packing List Line still creates a correct
    Invoice
    """
    if not quiet:
      self.logMessage('Packing List Line Add')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE,
        self.PACKING_LIST_TWO_LINES_DEFAULT_SEQUENCE) :
      sequence_list.addSequenceString(
        base_sequence +
    """
      stepAddPackingListLine
      stepTic
      stepSetContainerFullQuantity
      stepTic
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
    """)
    sequence_list.play(self, quiet=quiet)

  def test_08_InvoiceDecreaseQuantity(self, quiet=quiet):
    """
    Change the quantity of a Invoice Line,
    check that the invoice is divergent,
    then split and defer, and check everything is solved
    """
    if not quiet:
      self.logMessage('Invoice Decrease Quantity')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding

    stepDecreaseInvoiceLineQuantity
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
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
    self.playSequence(sequence, quiet=quiet)

  @newSimulationExpectedFailure
  def test_09_InvoiceChangeStartDateFail(self, quiet=quiet):
    """
    Change the start_date of a Invoice Line,
    check that the invoice is divergent,
    then accept decision, and check Packing list is *not* divergent,
    because Unify Solver does not propagage the change to the upper
    simulation movement.
    """
    if not quiet:
      self.logMessage('Invoice Change Start Date')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding

    stepChangeInvoiceStartDate
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepUnifyStartDateWithDecisionInvoice
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
    self.playSequence(sequence, quiet=quiet)

  @newSimulationExpectedFailure
  def test_09b_InvoiceChangeStartDateSucceed(self, quiet=quiet):
    """
    Change the start_date of a Invoice Line,
    check that the invoice is divergent,
    deliver the Packing List to make sure it's frozen,
    then accept decision, and check everything is solved
    """
    if not quiet:
      self.logMessage('Invoice Change Sart Date')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic

    stepChangeInvoiceStartDate
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepUnifyStartDateWithDecisionInvoice
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
    self.playSequence(sequence, quiet=quiet)

  def test_10_AcceptDecisionOnPackingList(self, quiet=quiet):
    """
    - Increase or Decrease the quantity of a Packing List line
    - Accept Decision on Packing List
    - Packing List must not be divergent and use new quantity
    - Invoice must not be divergent and use new quantity
    """
    if not quiet:
      self.logMessage('InvoiceAcceptDecisionOnPackingList')
    end_sequence = \
    """
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepTic
    stepCheckPackingListIsDiverged
    stepAcceptDecisionQuantity
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding

    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepStartInvoice
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
    sequence_list.play(self, quiet=quiet)

  def test_16a_ManuallyAddedMovementsManyTransactions(self, quiet=quiet):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation

    In this case checks what is happening, where movements are added in
    one transaction and edited in another
    """
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements in separate transactions')
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
          stepInvoiceBuilderAlarm
          stepTic
          stepCheckInvoiceBuilding
          stepRebuildAndCheckNothingIsCreated
          stepCheckInvoicesConsistency
          stepAddInvoiceLinesManyTransactions
          stepTic
          stepCheckInvoiceIsSolved
          stepStartInvoice
          stepTic
          stepCheckSimulationTrees
          """)
    sequence_list.play(self, quiet=quiet)


  def test_11_AcceptDecisionOnPackingListAndInvoice(self, quiet=quiet):
    """
    - Increase or Decrease the quantity of a Packing List line
    - Accept Decision on Packing List
    - Packing List must not be divergent and use new quantity
    - Put old quantity on Invoice
    - Accept Decision on Invoice
    - Packing List must not be divergent and use new quantity
    - Invoice must not be divergent and use old quantity
    """
    if not quiet:
      self.logMessage('InvoiceAcceptDecisionOnPackingListAndInvoice')
    mid_sequence = \
    """
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepTic
    stepCheckPackingListIsDiverged
    stepAcceptDecisionQuantity
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
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
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved
    stepStartInvoice
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
    sequence_list.play(self, quiet=quiet)

  def test_12_SplitPackingListAndAcceptInvoice(self, quiet=quiet):
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
    if not quiet:
      self.logMessage('InvoiceSplitPackingListAndAcceptInvoice')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepCheckInvoicingRule
    stepDecreasePackingListLineQuantity
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepTic
    stepCheckPackingListIsDiverged
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
    stepInvoiceBuilderAlarm
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
    stepTic
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepStartInvoice
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
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved

    stepSetInvoiceLineQuantityToZero
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepStartInvoice
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
    self.playSequence(sequence, quiet=quiet)

  def test_13_SplitAndDeferInvoice(self, quiet=quiet):
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
    if not quiet:
      self.logMessage('InvoiceSplitAndDeferInvoice')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
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
    stepTic
    stepCheckInvoiceIsDiverged
    stepSplitAndDeferInvoice
    stepTic
    stepStartInvoice
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

    stepStartInvoice
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
    self.playSequence(sequence, quiet=quiet)

  def test_14_AcceptDecisionOnInvoice(self, quiet=quiet):
    """
    - Accept Order, Accept Packing List
    - Increase or Decrease quantity on Invoice
    - Accept Decision on Invoice
    - Accept Invoice
    - Packing List must not be divergent and use old quantity
    - Invoice must not be divergent and use new quantity
    """
    if not quiet:
      self.logMessage('InvoiceAcceptDecisionOnInvoice')
    mid_sequence = \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
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
    stepTic
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepStartInvoice
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
    sequence_list.play(self, quiet=quiet)


  def test_Reference(self):
    # A reference is set automatically on Sale Invoice Transaction
    supplier = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Supplier')
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    currency = self.portal.currency_module.newContent(
                            portal_type='Currency')
    invoice = self.portal.accounting_module.newContent(
                    portal_type='Sale Invoice Transaction',
                    start_date=DateTime(),
                    price_currency_value=currency,
                    resource_value=currency,
                    source_section_value=supplier,
                    destination_section_value=client)
    self.portal.portal_workflow.doActionFor(invoice, 'confirm_action')

    self.assertEqual('1', invoice.getReference())

  def test_16_ManuallyAddedMovements(self, quiet=quiet):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation
    """
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements')
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
          stepInvoiceBuilderAlarm
          stepTic
          stepCheckInvoiceBuilding
          stepRebuildAndCheckNothingIsCreated
          stepCheckInvoicesConsistency
          stepAddInvoiceLines
          stepTic
          stepStartInvoice
          stepTic
          stepCheckSimulationTrees
          """)
    sequence_list.play(self, quiet=quiet)

  def test_17_ManuallyAddedWrongMovements(self, quiet=quiet):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation, even when adding very wrong movements
    """
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements')
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
          stepInvoiceBuilderAlarm
          stepTic
          stepCheckInvoiceBuilding
          stepAddWrongInvoiceLines
          stepTic
          stepStartInvoice
          stepCheckStartInvoiceFail
          stepCheckSimulationTrees
          """)
    sequence_list.play(self, quiet=quiet)

  def test_18_compareInvoiceAndPackingList(self, quiet=quiet):
    """
    Checks that a Simple Invoice is created from a Packing List
    """
    if not quiet:
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
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckInvoiceBuilding
        stepCheckInvoicesConsistency
        stepCheckPackingListInvoice
      """)
    sequence_list.play(self, quiet=quiet)

  def _adoptDivergenceOnPackingList(self, packing_list, divergence_list):
    builder_list = packing_list.getBuilderList()
    for builder in builder_list:
      builder.solveDivergence(packing_list.getRelativeUrl(),
                              divergence_to_adopt_list=divergence_list)

  def test_accept_quantity_divergence_on_invoice_with_started_packing_list(
                        self, quiet=quiet):
    # only applies to sale invoice, because purchase invoices are not built yet
    # when the packing list is in started state
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.PACKING_LIST_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.getMovementList()[0]
    previous_quantity = packing_list_line.getQuantity()

    packing_list.setReady()
    packing_list.start()
    self.assertEqual('started', packing_list.getSimulationState())
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEquals(invoice, None)
    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]

    new_quantity = invoice_line.getQuantity() * 2
    invoice_line.setQuantity(new_quantity)

    self.tic()

    self.assertTrue(invoice.isDivergent())
    divergence_list = invoice.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

    # accept decision
    self._acceptDivergenceOnInvoice(invoice, divergence_list)

    self.tic()
    self.assertEqual('solved', invoice.getCausalityState())

    self.assertEqual([], invoice.getDivergenceList())
    self.assertEqual(new_quantity, invoice_line.getQuantity())
    self.assertEqual(new_quantity,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())

    if invoice_line.getDeliveryRelatedValue().getParentValue().getSpecialiseId() == \
        'new_invoice_simulation_rule':
      # With new simulation solvers, changes on simulation movements will
      # not backtrack.
      pass
    else:
      # With legacy simulation solvers, changes on simulation movements
      # will backtrack if simulation movements are not frozen.
      # the packing list is divergent, because it is not frozen
      self.assertEqual('diverged', packing_list.getCausalityState())
      divergence_list = packing_list.getDivergenceList()
      self.assertEqual(1, len(divergence_list))
      divergence = divergence_list[0]
      self.assertEqual('quantity', divergence.tested_property)
      # if we adopt prevision on this packing list, both invoice and
      # packing list will be solved
      self._adoptDivergenceOnPackingList(packing_list, divergence_list)
      self.tic()
    self.assertEqual('solved', packing_list.getCausalityState())
    self.assertEqual('solved', invoice.getCausalityState())

class TestPurchaseInvoice(TestInvoice, ERP5TypeTestCase):
  """Tests for purchase invoice.
  """
  resource_portal_type = 'Product'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  order_cell_portal_type = 'Purchase Order Cell'
  packing_list_portal_type = 'Purchase Packing List'
  packing_list_line_portal_type = 'Purchase Packing List Line'
  packing_list_cell_portal_type = 'Purchase Packing List Cell'
  invoice_portal_type = 'Purchase Invoice Transaction'
  invoice_transaction_line_portal_type = 'Purchase Invoice Transaction Line'
  invoice_line_portal_type = 'Invoice Line'
  invoice_cell_portal_type = 'Invoice Cell'

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
      stepTic
    """

class OpenDocumentTextFile :
  def __init__ (self, filelikeobj) :
    zip = zipfile.ZipFile(filelikeobj)
    self.content = xml.dom.minidom.parseString(zip.read("content.xml"))

  def toString (self) :
    """ Converts the document to a string. """
    buffer = u""
    for val in ["text:p", "text:h", "text:list"]:
      for paragraph in self.content.getElementsByTagName(val) :
        buffer += self.textToString(paragraph) + "\n"
    return buffer

  def textToString(self, element) :
    buffer = u""
    for node in element.childNodes :
      if node.nodeType == xml.dom.Node.TEXT_NODE :
        buffer += node.nodeValue
      elif node.nodeType == xml.dom.Node.ELEMENT_NODE :
        buffer += self.textToString(node)
    return buffer

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSaleInvoice))
  suite.addTest(unittest.makeSuite(TestPurchaseInvoice))
  return suite
