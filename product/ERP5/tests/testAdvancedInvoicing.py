##############################################################################
#
# Copyright (c) 2009 Nexedi KK and Contributors. All Rights Reserved.
#          Tatuya Kamada <tatuya@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301,
# USA.
#
##############################################################################
"""
  Tests invoice and invoice transaction creation from simulation.
  Most test-cases are based on the testInvoice.py.
"""

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5.tests.testInvoice import TestSaleInvoiceMixin
from Products.ERP5.tests.utils import newSimulationExpectedFailure

class TestAdvancedInvoice(TestSaleInvoiceMixin, ERP5TypeTestCase):
  """Test methods for sale and purchase invoice.
  Subclasses must defines portal types to use.
  """
  quiet = 1
  RUN_ALL_TESTS = 1
  PACKING_LIST_DEFAULT_SEQUENCE = \
  """
  stepCreateEntities
  stepCreateCurrency
  stepCreateSaleInvoiceTransactionRule
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

  INVOICE_DEFAULT_SEQUENCE = PACKING_LIST_DEFAULT_SEQUENCE + \
  """
  stepStartPackingList
  stepTic
  stepInvoiceBuilderAlarm
  stepTic
  stepStartRelatedInvoice
  stepTic
  """

  TWO_PACKING_LIST_DEFAULT_SEQUENCE = \
  """
  stepCreateEntities
  stepCreateCurrency
  stepCreateSaleInvoiceTransactionRule
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

  invoice_portal_type = 'Sale Invoice'
  invoice_line_portal_type = 'Invoice Line'
  invoice_cell_portal_type = 'Invoice Cell'
  invoice_module_name = 'sale_invoice_module'
  invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy', 'erp5_base', 'erp5_pdm',
        'erp5_simulation', 'erp5_trade', 'erp5_accounting', 'erp5_invoicing',
        'erp5_advanced_invoicing', 'erp5_apparel', 'erp5_project',
        'erp5_configurator_standard_trade_template',
        'erp5_configurator_standard_invoicing_template',
        'erp5_configurator_standard_accounting_template',
        'erp5_configurator_standard_solver', 'erp5_simulation_test')

  def stepStartRelatedInvoice(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue(
      portal_type=self.invoice_portal_type)
    self.assertNotEquals(invoice, None)
    invoice.start()
    self.assertEqual('started', invoice.getSimulationState())

  def stepAddInvoiceTransactionLines(self, sequence=None, sequence_list=[]):
    """
    add some invoice and accounting lines to the invoice
    """
    invoice = sequence.get('invoice')
    invoice.newContent(portal_type=self.invoice_line_portal_type,
        resource_value=sequence.get('resource'), quantity=3, price=555)
    invoice_transaction = invoice.getCausalityRelatedValue()
    invoice_transaction.newContent(portal_type=self.invoice_transaction_line_portal_type,
                                   id ='receivable', source='account_module/customer',
                                   destination='account_module/supplier', quantity=-1665)
    invoice_transaction.newContent(portal_type='Sale Invoice Transaction Line',
                                   id='income', source='account_module/sale',
                                   destination='account_module/purchase', quantity=1665)

  def stepAddInvoiceLinesManyTransactions(self, sequence=None, sequence_list=[]):
    """
    add some invoice and accounting lines to the invoice
    """
    invoice = sequence.get('invoice')
    invoice_line = invoice.newContent(portal_type='Invoice Line')
    invoice_line.edit(resource_value=sequence.get('resource'), quantity=3,
        price=555)

    invoice_transaction = invoice.getCausalityRelatedValue()
    transaction_line_1 = invoice_transaction.newContent(portal_type=self.invoice_transaction_line_portal_type)
    transaction_line_2 = invoice_transaction.newContent(portal_type=self.invoice_transaction_line_portal_type)
    self.tic()
    transaction_line_1.edit(id ='receivable', source='account_module/customer',
        destination='account_module/supplier', quantity=-1665)
    transaction_line_2.edit(
        id='income', source='account_module/sale',
        destination='account_module/purchase', quantity=1665)

  def stepChangeQuantityDoubledOnInvoice(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue(portal_type=self.invoice_portal_type)
    self.assertNotEquals(invoice, None)
    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]
    new_quantity = invoice_line.getQuantity() * 2
    invoice_line.setQuantity(new_quantity)
    sequence.edit(invoice_line_doubled_quantity=new_quantity)


  def stepAcceptDecisionOnInvoice(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue(portal_type=self.invoice_portal_type)
    builder_list = invoice.getBuilderList()
    self.assertEqual(1, len(builder_list))
    divergence_list = invoice.getDivergenceList()
    for builder in builder_list:
      builder.solveDivergence(invoice.getRelativeUrl(),
                              divergence_to_accept_list=divergence_list)

  def stepCheckDivergenceOnInvoice(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue(portal_type=self.invoice_portal_type)
    self.assertEqual('solved', invoice.getCausalityState())
    new_quantity = sequence.get('invoice_line_doubled_quantity')
    self.assertEqual([], invoice.getDivergenceList())

    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]
    self.assertEqual(new_quantity, invoice_line.getQuantity())
    self.assertEqual(new_quantity,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())

  def stepCheckDivergedOnPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    self.assertEqual('diverged', packing_list.getCausalityState())

  def stepCheckSolvedOnPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    self.assertEqual('solved', packing_list.getCausalityState())

  def stepCheckDivergedQuantityOnInvoice(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue(portal_type=self.invoice_portal_type)
    self.assertTrue(invoice.isDivergent())
    divergence_list = invoice.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

  def stepCheckDivergedQuantityOnPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    divergence_list = packing_list.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

  def stepAdoptPrevisionOnPackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    divergence_list = packing_list.getDivergenceList()
    for builder in packing_list.getBuilderList():
      builder.solveDivergence(packing_list.getRelativeUrl(),
                              divergence_to_adopt_list=divergence_list)

  def stepAdoptPrevisionOnInvoice(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue()

    divergence_list = invoice.getDivergenceList()
    builder_list = invoice.getBuilderList()
    self.assertEqual(1, len(builder_list))
    for builder in builder_list:
      builder.solveDivergence(invoice.getRelativeUrl(),
                              divergence_to_adopt_list=divergence_list)

  def test_CreatingAccountingTransactionThroughInvoice(self, quiet=quiet, run=RUN_ALL_TESTS):
    """test creating simple invoice and accounting transaction"""
    if not run: return
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.INVOICE_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    self.assertEqual('solved', packing_list.getCausalityState())
    invoice = packing_list.getCausalityRelatedValue()
    self.assertEqual(self.invoice_portal_type, invoice.getPortalType())
    self.assertEqual('solved', invoice.getCausalityState())
    self.assertEqual([], invoice.getDivergenceList())

    invoice_transaction  = invoice.getCausalityRelatedValue()
    self.assertNotEquals(invoice_transaction, None)
    self.assertEqual('solved', invoice_transaction.getCausalityState())

  def test_AcceptQuantityDivergenceOnInvoiceWithStoppedPackingList(self, quiet=quiet, run=RUN_ALL_TESTS):
    """Accept divergence with stopped packing list"""
    if not run: return
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(
      self.PACKING_LIST_DEFAULT_SEQUENCE +
      """
      stepTic
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepStopPackingList
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepChangeQuantityDoubledOnInvoice
      stepTic
      stepCheckDivergedQuantityOnInvoice
      stepAcceptDecisionOnInvoice
      stepTic
      stepCheckDivergenceOnInvoice
      stepCheckSolvedOnPackingList
      """)

    sequence_list.play(self, quiet=quiet)
    packing_list = sequence.get('packing_list')
    self.assertEqual([], packing_list.getDivergenceList())
    self.assertEqual('solved', packing_list.getCausalityState())

  def test_AdoptQuantityDivergenceOnInvoiceLineWithStoppedPackingList(self, quiet=quiet,
                                                                      run=RUN_ALL_TESTS):
    """Adopt quantity with stopped packing list"""
    if not run: return
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(
      self.PACKING_LIST_DEFAULT_SEQUENCE + \
      """
      stepStartPackingList
      stepStopPackingList
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepChangeQuantityDoubledOnInvoice
      stepTic
      stepCheckDivergedQuantityOnInvoice
      stepAdoptPrevisionOnInvoice
      stepTic
      """)
    sequence_list.play(self, quiet=quiet)
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue()
    self.assertEqual([], invoice.getDivergenceList())
    self.assertEqual('solved', invoice.getCausalityState())

    self.assertEqual(1,
        len(invoice.getMovementList(portal_type=self.invoice_line_portal_type)))
    invoice_line = invoice.getMovementList(portal_type=self.invoice_line_portal_type)[0]
    self.assertEqual(99.0, invoice_line.getQuantity())
    self.assertEqual(555.0, invoice_line.getPrice())
    self.assertEqual(99.0,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())
    self.assertEqual([], packing_list.getDivergenceList())
    self.assertEqual('solved', packing_list.getCausalityState())

  def test_PackingListEditAndInvoiceRule(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    Delivery Rule should not be applied on packing list lines created\
    from Order.
    """
    if not run: return
    if not quiet:
      self.logMessage('Packing List Edit')
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
      self.PACKING_LIST_DEFAULT_SEQUENCE +
      """
      stepEditPackingList
      stepCheckDeliveryRuleNotAppliedOnPackingListEdit
      stepCheckInvoicesConsistency
      """)
    sequence_list.play(self, quiet=quiet)

  def test_InvoiceViewAsODT(self):
    """Create ODT printout """
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    invoice = self.portal.getDefaultModule(self.invoice_portal_type).newContent(
                              portal_type=self.invoice_portal_type,
                              specialise=self.business_process,
                              start_date=DateTime(2008, 12, 31),
                              title='Invoice',
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


class TestAdvancedSaleInvoice(TestAdvancedInvoice):
  quiet = 1
  RUN_ALL_TESTS = 1
  login = TestAdvancedInvoice.login

  def afterSetUp(self):
    super(TestAdvancedSaleInvoice, self).afterSetUp()
    # register builders for advanced invoicing.
    business_process = self.portal.unrestrictedTraverse(
      'business_process_module/erp5_default_business_process', None)
    if business_process is not None:
      business_process.invoice.setDeliveryBuilderList([
          'portal_deliveries/advanced_purchase_invoice_builder',
          'portal_deliveries/advanced_sale_invoice_builder',
          ])
      business_process.account.setDeliveryBuilderList([
          'portal_deliveries/advanced_purchase_invoice_transaction_builder',
          'portal_deliveries/advanced_sale_invoice_transaction_builder',
          ])
    # This is quite ugly, we should use late import/export functions of generators
    self.portal.erp5_sql_transactionless_connection.manage_test(
     "delete from portal_ids where \
       id_group='Accounting_Transaction_Module-Sale_Invoice_Transaction'")
    self.commit()

  def stepCheckInvoicesAndTransactionsConsistency(self, sequence=None, sequence_list=None,
                                                  **kw):
    """
    - to check transaction lines match invoice lines
    """
    invoice_list = self.getPortal()[self.invoice_module_name].objectValues()
    for invoice in invoice_list:
      state_list = \
          list(self.getPortal().getPortalCurrentInventoryStateList())
      state_list.append('cancelled')
      if invoice.getSimulationState() in state_list:
        invoice_line_list = invoice.contentValues(
            portal_type=self.invoice_line_portal_type)
        expected_price = 0.0
        for line in invoice_line_list:
          expected_price += line.getTotalPrice()
        invoice_transaction  = invoice.getCausalityRelatedValue()
        if invoice_transaction.getSimulationState() in state_list:
          invoice_transaction_line_list = invoice_transaction.contentValues(
            portal_type=self.invoice_transaction_line_portal_type)
          self.assertEqual(3, len(invoice_transaction_line_list))

          for line_id, line_source, line_dest, line_ratio in \
                  self.transaction_line_definition_list:
            for line in invoice_transaction.contentValues(
                portal_type=self.invoice_transaction_line_portal_type):
              if line.getSource() == 'account_module/%s' % line_source and \
                     line.getDestination() == 'account_module/%s' % line_dest:
                break
              else:
                self.fail('No line found that matches %s' % line_id)
              resource_precision = line.getResourceValue().getQuantityPrecision()
              self.assertEqual(round(line.getQuantity(), resource_precision),
                                round(expected_price * line_ratio, resource_precision))

  def stepRemoveDateMovementGroupForAdvancedTransactionBuilder(self, sequence=None, sequence_list=None, **kw):
    """
    Remove DateMovementGroup
    """
    portal = self.getPortal()
    builder = portal.portal_deliveries.advanced_sale_invoice_transaction_builder
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
        user = uf.getUserById('test_user').__of__(uf)
        newSecurityManager(None, user)

  def test_01_TwoInvoicesFromTwoPackingList(self, quiet=quiet, run=RUN_ALL_TESTS):
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
    if not quiet:
      self.logMessage('Two Invoices from Two Packing List')
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
      self.TWO_PACKING_LIST_DEFAULT_SEQUENCE +
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
      stepRemoveDateMovementGroupForAdvancedTransactionBuilder
      stepStartTwoInvoices
      stepTic
      stepCheckInvoicesAndTransactionsConsistency
      """)
    sequence_list.play(self, quiet=quiet)

  def test_02_InvoiceDeletePackingListLine(self, quiet=quiet,
      run=RUN_ALL_TESTS):
    """
    Checks that deleting a Packing List Line still creates a correct
    Invoice
    """
    if not run: return
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
    """)
    sequence_list.play(self, quiet=quiet)

  def test_03_InvoiceDecreaseQuantity(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    Change the quantity of a Invoice Line,
    check that the invoice is divergent,
    then split and defer, and check everything is solved
    """
    if not run: return
    if not quiet:
      self.logMessage('Invoice Decrease Qantity')
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
  def test_04_InvoiceChangeStartDateFail(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    Change the start_date of a Invoice Line,
    check that the invoice is divergent,
    then accept decision, and check Packing list is divergent
    """
    if not run: return
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

    stepCheckPackingListIsDivergent
    """
    self.playSequence(sequence, quiet=quiet)

  def test_05_AcceptDecisionOnPackingList(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    - Increase or Decrease the quantity of a Packing List line
    - Accept Decision on Packing List
    - Packing List must not be divergent and use new quantity
    - Invoice must not be divergent and use new quantity
    """
    if not run: return
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

  def test_06_AcceptDecisionOnPackingListAndInvoice(self, quiet=quiet,
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

  def test_07_SplitAndDeferInvoice(self, quiet=quiet, run=RUN_ALL_TESTS):
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

  def test_08_AcceptDecisionOnInvoice(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    - Accept Order, Accept Packing List
    - Increase or Decrease quantity on Invoice
    - Accept Decision on Invoice
    - Accept Invoice
    - Packing List must not be divergent and use old quantity
    - Invoice must not be divergent and use new quantity
    """
    if not run: return
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

  def test_09_Reference(self, quiet=quiet, run=RUN_ALL_TESTS):
    if not run: return
    if not quiet:
      self.logMessage('test Reference')

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

    # We could generate a better reference here.
    self.assertEqual('1', invoice.getReference())

  def test_10_ManuallyAddedMovements(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation
    """
    if not run: return
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements')
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
      self.PACKING_LIST_DEFAULT_SEQUENCE +
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
          stepStartInvoice
          stepTic
          stepAddInvoiceTransactionLines
          stepTic
          stepCheckSimulationTrees
          """)
    sequence_list.play(self, quiet=quiet)


  def test_11_ManuallyAddedMovementsManyTransactions(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    Checks that adding invoice lines and accounting lines
    generates correct simulation

    In this case checks what is happening, where movements are added in
    one transaction and edited in another
    """
    if not run: return
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements in separate transactions')
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
      self.PACKING_LIST_DEFAULT_SEQUENCE +
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
      stepTic
      stepCheckInvoiceIsSolved
      stepStartInvoice
      stepTic
      stepAddInvoiceLinesManyTransactions
      stepTic
      stepCheckSimulationTrees
      """)
    sequence_list.play(self, quiet=quiet)

  def test_12_compareInvoiceAndPackingList(self, quiet=quiet, run=RUN_ALL_TESTS):
    """
    Checks that a Simple Invoice is created from a Packing List
    """
    if not run: return
    if not quiet:
      self.logMessage('Compare Simple Invoice and Packing List')
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
      self.PACKING_LIST_DEFAULT_SEQUENCE +
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

  def test_13_acceptQuantityDivergenceOnInvoiceWithStartedPackingList(
    self, quiet=quiet, run=RUN_ALL_TESTS):
    if not run: return
    if not quiet:
      self.logMessage('Accept Quantity Divergence on Invoice')

    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(
      self.PACKING_LIST_DEFAULT_SEQUENCE +
      """
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepChangeQuantityDoubledOnInvoice
      stepTic
      stepCheckDivergedQuantityOnInvoice
      stepAcceptDecisionOnInvoice
      stepTic
      stepCheckDivergenceOnInvoice
      stepCheckDivergedOnPackingList
      stepCheckDivergedQuantityOnPackingList
      stepAdoptPrevisionOnPackingList
      stepTic
      """)

    sequence_list.play(self, quiet=quiet)
    packing_list = sequence.get('packing_list')
    invoice = packing_list.getCausalityRelatedValue(portal_type=self.invoice_portal_type)
    self.assertEqual('solved', packing_list.getCausalityState())
    self.assertEqual('solved', invoice.getCausalityState())

class TestAdvancedPurchaseInvoice(TestAdvancedInvoice):
  """Tests for purchase invoice.
  """
  resource_portal_type = 'Product'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  order_cell_portal_type = 'Purchase Order Cell'
  packing_list_portal_type = 'Purchase Packing List'
  packing_list_line_portal_type = 'Purchase Packing List Line'
  packing_list_cell_portal_type = 'Purchase Packing List Cell'
  invoice_portal_type = 'Purchase Invoice'
  invoice_transaction_line_portal_type = 'Purchase Invoice Transaction Line'
  invoice_line_portal_type = 'Invoice Line'
  invoice_cell_portal_type = 'Invoice Cell'
  invoice_module_name = 'sale_invoice_module'

  login = TestAdvancedInvoice.login

  PACKING_LIST_DEFAULT_SEQUENCE = \
  """
  stepCreateEntities
  stepCreateCurrency
  stepCreateSaleInvoiceTransactionRule
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

  INVOICE_DEFAULT_SEQUENCE = PACKING_LIST_DEFAULT_SEQUENCE + \
  """
  stepReceivePackingList
  stepTic
  stepInvoiceBuilderAlarm
  stepTic
  stepStartRelatedInvoice
  stepTic
  """

  def stepReceivePackingList(self, sequence=None, sequence_list=None, **kw):
    packing_list = sequence.get('packing_list')
    packing_list.setReady()
    packing_list.start()
    packing_list.stop()
    self.assertEqual('stopped', packing_list.getSimulationState())
    self.commit()


class TestWorkflow(SecurityTestCase):
  def getBusinessTemplateList(self):
    return ('erp5_core', 'erp5_base', 'erp5_pdm',
            'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_advanced_invoicing')

  def afterSetUp(self):
    skin_folder = self.portal.portal_skins.custom
    security_mapping_script_id = 'ERP5Type_getSecurityMapping'
    if getattr(skin_folder, security_mapping_script_id, None) is None:
      skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id=security_mapping_script_id)
      skin_folder[security_mapping_script_id].ZPythonScript_edit('', 'return (("ERP5Type_getSecurityCategoryFromAssignment", ["function"]),)')

    role_list = [
        {'role_name_list': ('Assignee',), 'role_category_list': ('function/assignee',)},
        {'role_name_list': ('Assignor',), 'role_category_list': ('function/assignor',)},
        {'role_name_list': ('Auditor',), 'role_category_list': ('function/auditor',)},
        {'role_name_list': ('Author',), 'role_category_list': ('function/author',)},
        {'role_name_list': ('Associate',), 'role_category_list': ('function/associate',)},
        {'role_name_list': ('Manager',), 'role_category_list': ('function/manager',)},
        ]

    sale_invoice_type = self.portal.portal_types['Sale Invoice']
    if len(sale_invoice_type.contentIds(filter={'portal_type': 'Role Infomation'})) == 0:
      for role in role_list:
        type_document = sale_invoice_type.newContent(portal_type='Role Information')
        type_document.edit(**role)
      self.tic()

    for role in role_list:
      for role_category in role['role_category_list']:
        category_id_list = role_category.split('/')[1:]
        node = self.portal.portal_categories.function
        while category_id_list:
          category_id = category_id_list.pop(0)
          if node.get(category_id, None) is None:
            node = node.newContent(id=category_id, portal_type='Category')
          else:
            node = node.get(category_id)
    self.tic()

    person_list = [
        {'id': 'other'},
        {'id': 'assignee', 'assignment_list': ({'function': 'assignee'},)},
        {'id': 'assignor', 'assignment_list': ({'function': 'assignor'},)},
        {'id': 'associate', 'assignment_list': ({'function': 'associate'},)},
        {'id': 'auditor', 'assignment_list': ({'function': 'auditor'},)},
        {'id': 'author', 'assignment_list': ({'function': 'author'},)},
        {'id': 'manager', 'assignment_list': ({'function': 'manager'},)},
        ]

    person_module = self.portal.person_module
    for person in person_list:
      if person_module.get(person['id'], None) is None:
        person_document = person_module.newContent(id=person['id'], portal_type='Person')
        person_document.edit(reference=person['id'])
        for assignment in person.get('assignment_list', []):
          assignment_document = person_document.newContent(portal_type='Assignment')
          assignment_document.edit(function=assignment['function'])
          self.portal.portal_workflow.doActionFor(assignment_document, 'open_action')
        self.tic()
        setattr(self, person['id'], person_document)

  def test_autoplanned(self):
    sale_invoice = self.portal.getDefaultModule('Sale Invoice').newContent(portal_type='Sale Invoice')
    self.assertEqual(sale_invoice.getSimulationState(), 'draft')
    sale_invoice.autoPlan()
    self.assertEqual(sale_invoice.getSimulationState(), 'auto_planned')

    # other as anonymous
    username = self.other.Person_getUserId()
    self.failIfUserCanAccessDocument(username, sale_invoice)
    self.failIfUserCanAddDocument(username, sale_invoice)
    self.failIfUserCanDeleteDocument(username, sale_invoice)
    self.failIfUserCanModifyDocument(username, sale_invoice)
    self.failIfUserCanViewDocument(username, sale_invoice)

    # assignee
    username = self.assignee.Person_getUserId()
    self.assertUserCanAccessDocument(username, sale_invoice)
    self.assertUserCanAddDocument(username, sale_invoice)
    self.assertUserCanDeleteDocument(username, sale_invoice)
    self.assertUserCanModifyDocument(username, sale_invoice)
    self.assertUserCanViewDocument(username, sale_invoice)

    # assignor
    username = self.assignor.Person_getUserId()
    self.assertUserCanAccessDocument(username, sale_invoice)
    self.assertUserCanAddDocument(username, sale_invoice)
    self.assertUserCanDeleteDocument(username, sale_invoice)
    self.assertUserCanModifyDocument(username, sale_invoice)
    self.assertUserCanViewDocument(username, sale_invoice)

    # associate
    username = self.associate.Person_getUserId()
    self.assertUserCanAccessDocument(username, sale_invoice)
    self.assertUserCanAddDocument(username, sale_invoice)
    self.assertUserCanDeleteDocument(username, sale_invoice)
    self.assertUserCanModifyDocument(username, sale_invoice)
    self.assertUserCanViewDocument(username, sale_invoice)

    # auditor
    username = self.auditor.Person_getUserId()
    self.assertUserCanAccessDocument(username, sale_invoice)
    self.failIfUserCanAddDocument(username, sale_invoice)
    self.failIfUserCanDeleteDocument(username, sale_invoice)
    self.failIfUserCanModifyDocument(username, sale_invoice)
    self.assertUserCanViewDocument(username, sale_invoice)

    # author
    username = self.author.Person_getUserId()
    self.failIfUserCanAccessDocument(username, sale_invoice)
    self.failIfUserCanAddDocument(username, sale_invoice)
    self.failIfUserCanDeleteDocument(username, sale_invoice)
    self.failIfUserCanModifyDocument(username, sale_invoice)
    self.failIfUserCanViewDocument(username, sale_invoice)

    # manager
    username = self.manager.Person_getUserId()
    self.assertUserCanAccessDocument(username, sale_invoice)
    self.assertUserCanAddDocument(username, sale_invoice)
    self.assertUserCanDeleteDocument(username, sale_invoice)
    self.assertUserCanModifyDocument(username, sale_invoice)
    self.assertUserCanViewDocument(username, sale_invoice)

    portal_workflow = self.portal.portal_workflow
    action_ids = [action['id'] for action in
                  portal_workflow.listActionInfos(object=sale_invoice)
                  if action['category'] == 'workflow']
    self.assertSameSet(('confirm_action', 'plan_action',), action_ids)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAdvancedSaleInvoice))
  suite.addTest(unittest.makeSuite(TestAdvancedPurchaseInvoice))
  suite.addTest(unittest.makeSuite(TestWorkflow))
  return suite
