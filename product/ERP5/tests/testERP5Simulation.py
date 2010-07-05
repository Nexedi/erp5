# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
"""
This test is experimental for new simulation implementation.
"""

import unittest
import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from testPackingList import TestPackingList, TestPackingListMixin
from testInvoice import TestSaleInvoice, TestInvoiceMixin
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from Products.ERP5Type.Document.BusinessTemplate import getChainByType

class TestERP5SimulationMixin(TestInvoiceMixin):
  def getBusinessTemplateList(self):
    return list(TestInvoiceMixin.getBusinessTemplateList(self)) + \
           ['erp5_administration', 'erp5_simulation',]

  def afterSetUp(self, quiet=1, run=1):
    TestInvoiceMixin.afterSetUp(self)
    portal_rules = self.portal.portal_rules
    for rule in portal_rules.objectValues(portal_type='Order Root Simulation Rule'):
      if rule.getValidationState() == 'validated':
        rule.invalidate()
    self.validateNewRules()
    self.setUpBusinessProcess()

  def setUpBusinessProcess(self):
    business_process = self.portal.business_process_module.erp5_default_business_process
    pay_business_path = business_process['pay']
    pay_business_path.setSource('account_module/bank')
    pay_business_path.setDestination('account_module/bank')

  @UnrestrictedMethod
  def createInvoiceTransactionRule(self, resource=None):
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
    invoice_rule = portal.portal_rules.new_invoice_transaction_simulation_rule
    if invoice_rule.getValidationState() == 'validated':
      invoice_rule.invalidate()
    invoice_rule.deleteContent(list(invoice_rule.contentIds(filter={'portal_type':['Predicate', 'Accounting Rule Cell']})))
    transaction.commit()
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
    transaction.commit()
    self.tic()

  def validateNewRules(self):
    # create an Order Rule document.
    portal_rules = self.portal.portal_rules
    new_order_rule = filter(
      lambda x:x.title == 'New Default Order Root Simulation Rule',
      portal_rules.objectValues(portal_type='Order Root Simulation Rule'))[0]
    if new_order_rule.getValidationState() != 'validated':
      new_order_rule.validate()

  def _acceptDecisionQuantity(self, document):
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(document)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Accept Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Accept Solver'])
    # configure for Accept Solver.
    kw = {'tested_property_list':['quantity',]}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def _acceptDivergenceOnInvoice(self, invoice, divergence_list):
    print invoice, divergence_list
    return self._acceptDecisionQuantity(invoice)

  def stepAcceptDecisionQuantity(self,sequence=None, sequence_list=None):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    self._acceptDecisionQuantity(packing_list)

  def stepAcceptDecisionQuantityInvoice(self, sequence=None,
                                        sequence_list=None):
    """
    Solve quantity divergence by using solver tool.
    """
    invoice = sequence.get('invoice')
    self._acceptDecisionQuantity(invoice)

  def stepAcceptDecisionResource(self,sequence=None, sequence_list=None):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    resource_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='resource',
      solver_process.contentValues())[0]
    # use Resource Replacement Solver.
    resource_solver_decision.setSolverValue(self.portal.portal_solvers['Accept Solver'])
    # configure for Accept Solver.
    kw = {'tested_property_list':['resource',]}
    resource_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepSplitAndDeferPackingList(self, sequence=None, sequence_list=None):
    """
      Do the split and defer action
    """
    packing_list = sequence.get('packing_list')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO Delivery Solver',
          'start_date':self.datetime + 15,
          'stop_date':self.datetime + 25}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()
    # build split deliveries manually. XXX ad-hoc
    previous_tag = None
    for delivery_builder in packing_list.getBuilderList():
      this_builder_tag = '%s_split_%s' % (packing_list.getPath(),
                                          delivery_builder.getId())
      after_tag = []
      if previous_tag:
        after_tag.append(previous_tag)
      delivery_builder.activate(
        after_method_id=('solve',
                         'immediateReindexObject',
                         'recursiveImmediateReindexObject',), # XXX too brutal.
        after_tag=after_tag,
        ).build(explanation_uid=packing_list.getCausalityValue().getUid())

  def _adoptPrevisionQuantity(self, packing_list):
    """
    Solve quantity divergence by using solver tool.
    """
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Adoption Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Adopt Solver'])
    # configure for Adopt Solver.
    kw = {'tested_property_list':['quantity',]}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def _adoptDivergenceOnInvoice(self, invoice, divergence_list):
    print invoice, divergence_list
    return self._adoptPrevisionQuantity(invoice)

  def _adoptDivergenceOnPackingList(self, packing_list, divergence_list):
    print packing_list, divergence_list
    return self._adoptPrevisionQuantity(packing_list)

  def stepAdoptPrevisionQuantity(self,sequence=None, sequence_list=None):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    self._adoptPrevisionQuantity(packing_list)

  def stepNewPackingListAdoptPrevisionQuantity(self, sequence=None,
                                               sequence_list=None):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('new_packing_list')
    self._adoptPrevisionQuantity(packing_list)

  def stepAdoptPrevisionResource(self,sequence=None, sequence_list=None):
    """
    Solve resource divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    resource_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='resource',
      solver_process.contentValues())[0]
    # use Resource Adopt Solver.
    resource_solver_decision.setSolverValue(self.portal.portal_solvers['Adopt Solver'])
    # configure for Adopt Solver.
    kw = {'tested_property_list':['resource',]}
    resource_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckPackingListLineWithSameResource(self,sequence=None, sequence_list=None):
    """
      Look if the packing list has new previsions
    """
    old_packing_list_line = sequence.get('packing_list_line')
    packing_list_line = old_packing_list_line.aq_parent[str(int(old_packing_list_line.getId())-1)]
    resource = sequence.get('resource')
    for line in sequence.get('packing_list').getMovementList():
      self.assertEquals(line.getResourceValue(), resource)
      self.assertEquals(line.getQuantity(), self.default_quantity)
      self.assertEquals(line.getCausalityList(),
                        [x.getParentValue().getParentValue().getDelivery() for x in \
                         line.getDeliveryRelatedValueList()])

  def stepUnifyDestinationWithDecision(self,sequence=None, sequence_list=None):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    for destination_solver_decision in filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='destination',
      solver_process.contentValues()):
      # use Destination Replacement Solver.
      destination_solver_decision.setSolverValue(self.portal.portal_solvers['Accept Solver'])
      # configure for Accept Solver.
      kw = {'tested_property_list':['destination',]}
      destination_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def _unifyStartDateWithDecision(self, document):
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(document)
    for start_date_solver_decision in filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='start_date',
      solver_process.contentValues()):
      # use StartDate Replacement Solver.
      start_date_solver_decision.setSolverValue(self.portal.portal_solvers['Unify Solver'])
      # configure for Unify Solver.
      kw = {'tested_property_list':['start_date',],
            'value':document.getStartDate()}
      start_date_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepUnifyStartDateWithDecision(self,sequence=None, sequence_list=None):
    packing_list = sequence.get('packing_list')
    self._unifyStartDateWithDecision(packing_list)

  def stepUnifyStartDateWithDecisionInvoice(self,sequence=None, sequence_list=None):
    invoice = sequence.get('invoice')
    self._unifyStartDateWithDecision(invoice)

  def stepUnifyStartDateWithPrevision(self,sequence=None, sequence_list=None):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    start_date = simulation_line_list[-1].getStartDate()
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    for start_date_solver_decision in filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='start_date',
      solver_process.contentValues()):
      # use StartDate Replacement Solver.
      start_date_solver_decision.setSolverValue(self.portal.portal_solvers['Unify Solver'])
      # configure for Unify Solver.
      kw = {'tested_property_list':['start_date',],
            'value':start_date}
      start_date_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckPackingListLineWithDifferentResource(self,sequence=None, sequence_list=None):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    new_resource = sequence.get('resource')
    self.assertEquals(packing_list_line.getQuantity(), self.default_quantity*2)
    self.assertEquals(packing_list_line.getResourceValue(), new_resource)
    simulation_line_list = packing_list_line.getDeliveryRelatedValueList()
    order_line_list = sum([x.getParentValue().getParentValue().getDeliveryList() for x in simulation_line_list], [])
    self.assertEquals(sorted(packing_list_line.getCausalityList()),
                      sorted(order_line_list))

class TestERP5Simulation(TestERP5SimulationMixin, ERP5TypeTestCase):
  run_all_test = 1
  quiet = 0

  def afterSetUp(self):
    TestERP5SimulationMixin.afterSetUp(self)
    new_delivery_rule = self.portal.portal_rules.new_delivery_simulation_rule
    new_delivery_rule['quantity_tester'].edit(quantity=None,
                                           quantity_range_max=2,
                                           quantity_range_min=-1)

  def beforeTearDown(self):
    new_delivery_rule = self.portal.portal_rules.new_delivery_simulation_rule
    new_delivery_rule['quantity_tester'].edit(quantity=0,
                                           quantity_range_max=None,
                                           quantity_range_min=None)
    transaction.commit()
    TestERP5SimulationMixin.beforeTearDown(self)

  def _modifyPackingListLineQuantity(self, sequence=None,
      sequence_list=None, delta=0.0):
    """
    Set a increased quantity on packing list lines
    """
    packing_list = sequence.get('packing_list')
    quantity = self.default_quantity + delta
    sequence.edit(line_quantity=quantity)
    for packing_list_line in packing_list.objectValues(
        portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(quantity=quantity)
    sequence.edit(last_delta=delta)

  def stepIncreasePackingListLineQuantity2(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, 2.0)

  def stepDecreasePackingListLineQuantity1(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, -1.0)

  def stepDecreasePackingListLineQuantity10(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, -10.0)

  def stepSplitAndDeferPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and defer action
    """
    packing_list = sequence.get('packing_list')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    sequence.edit(solver_process=solver_process)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(
        self.portal.portal_solvers['Quantity Split Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO Delivery Solver',
          'start_date':packing_list.getStartDate() + 10}
    quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()

    solver_process.solve()
    # build split deliveries manually. XXX ad-hoc
    previous_tag = None
    for delivery_builder in packing_list.getBuilderList():
      this_builder_tag = '%s_split_%s' % (packing_list.getPath(),
                                          delivery_builder.getId())
      after_tag = []
      if previous_tag:
        after_tag.append(previous_tag)
      delivery_builder.activate(
        after_method_id=('solve',
                         'immediateReindexObject',
                         'recursiveImmediateReindexObject',), # XXX too brutal.
        after_tag=after_tag,
        ).build(explanation_uid=packing_list.getCausalityValue().getUid())

  def stepCheckPackingListSplitted(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list was splitted
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEquals(2,len(packing_list_list))
    packing_list1 = None
    packing_list2 = None
    for packing_list in packing_list_list:
      if packing_list.getUid() == sequence.get('packing_list').getUid():
        packing_list1 = packing_list
      else:
        packing_list2 = packing_list
    sequence.edit(new_packing_list=packing_list2)
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(self.default_quantity-10,line.getQuantity())
    for line in packing_list2.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEquals(10,line.getQuantity())

  def _checkSolverState(self, sequence=None, sequence_list=None,
                        state='solved'):
    """
      Check if target solvers' state.
    """
    solver_process = sequence.get('solver_process')
    for solver in solver_process.objectValues(
      portal_type=self.portal.getPortalTargetSolverTypeList()):
      self.assertEquals(state, solver.getValidationState())

  def stepCheckSolverIsSolving(self, sequence=None, sequence_list=None, **kw):
    """
      Check if all target solvers have 'solving' state.
    """
    self._checkSolverState(sequence, sequence_list, 'solving')

  def stepCheckSolverIsSolved(self, sequence=None, sequence_list=None, **kw):
    """
      Check if all target solvers have 'solved' state.
    """
    self._checkSolverState(sequence, sequence_list, 'solved')

  def test_01_splitAndDefer(self, quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      split and defer the packing list
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepIncreasePackingListLineQuantity2 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepDecreasePackingListLineQuantity1 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepDecreasePackingListLineQuantity10 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepSplitAndDeferPackingList \
                      stepCheckSolverIsSolving \
                      stepTic \
                      stepCheckPackingListSplitted \
                      stepCheckPackingListIsSolved \
                      stepCheckSolverIsSolved \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

class TestERP5SimulationPackingList(TestERP5SimulationMixin, TestPackingList):
  pass

for failing_method in [
  # This test does not work as it is because of the different behaviour of
  # Adopt Solver.
  'test_05d_SimulationChangeResourceOnOneSimulationMovementForMergedLine',

  # Those tests currently fail because they are making assertions on an applied
  # rule which with the new simulation structure is not the same as in the
  # original test packing list
  'test_03_PackingListChangeStartDate',
  'test_06_SimulationChangeStartDate',
  'test_07_SimulationChangeStartDateWithTwoOrderLine',
  'test_07a_SimulationChangeStartDateWithTwoOrderLine',
  
  ]:
  setattr(TestERP5SimulationPackingList, failing_method,
          expectedFailure(getattr(TestERP5SimulationPackingList, failing_method)))
        
class TestERP5SimulationInvoice(TestERP5SimulationMixin, TestSaleInvoice):
  quiet = TestSaleInvoice.quiet

  def test_09_InvoiceChangeStartDateFail(self, quiet=quiet):
    """
    Change the start_date of a Invoice Line,
    check that the invoice is divergent,
    then accept decision, and check Packing list is *not* divergent,
    because Unify Solver does not propagage the change to the upper
    simulation movement.
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

class TestAutomaticSolvingPackingList(TestERP5SimulationMixin, TestPackingListMixin,
                                      ERP5TypeTestCase):
  quiet = 0

  def afterSetUp(self, quiet=1, run=1):
    TestERP5SimulationMixin.afterSetUp(self)
    solver_process_type_info = self.portal.portal_types['Solver Process']
    self.original_allowed_content_types = solver_process_type_info.getTypeAllowedContentTypeList()
    self.added_target_solver_list = []

  def beforeTearDown(self, quiet=1, run=1):
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=())
    solver_process_type_info = self.portal.portal_types['Solver Process']
    solver_process_type_info.setTypeAllowedContentTypeList(self.original_allowed_content_types)
    self.portal.portal_solvers.manage_delObjects(self.added_target_solver_list)
    transaction.commit()
    self.tic()
    TestERP5SimulationMixin.beforeTearDown(self)

  @UnrestrictedMethod
  def _setUpTargetSolver(self, solver_id, solver_class, tested_property_list):
    solver_tool = self.portal.portal_solvers
    solver = solver_tool.newContent(
      portal_type='Solver Type',
      id=solver_id,
      tested_property_list=tested_property_list,
      automatic_solver=1,
      type_factory_method_id='add%s' % solver_class,
      type_group_list=('target_solver',),
    )
    solver.setCriterion(property='portal_type',
                        identity=['Simulation Movement',])
    solver.setCriterionProperty('portal_type')
    solver_process_type_info = self.portal.portal_types['Solver Process']
    solver_process_type_info.setTypeAllowedContentTypeList(
      solver_process_type_info.getTypeAllowedContentTypeList() + \
      [solver_id]
    )
    (default_chain, chain_dict) = getChainByType(self.portal)
    chain_dict['chain_%s' % solver_id] = 'solver_workflow'
    self.portal.portal_workflow.manage_changeWorkflows(default_chain,
                                                       props=chain_dict)
    self.portal.portal_caches.clearAllCache()
    self.added_target_solver_list.append(solver_id)

  def stepSetUpAutomaticQuantityAcceptSolver(self, sequence=None, sequence_list=None):
    self._setUpTargetSolver('Automatic Quantity Accept Solver',
                            'AcceptSolver', ('quantity',))
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=('portal_solvers/Automatic Quantity Accept Solver',))

  def stepSetUpAutomaticQuantityAdoptSolver(self, sequence=None, sequence_list=None):
    self._setUpTargetSolver('Automatic Quantity Adopt Solver',
                            'AdoptSolver', ('quantity',))
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      solver=('portal_solvers/Automatic Quantity Adopt Solver',))

  def test_01_PackingListDecreaseQuantity(self, quiet=quiet):
    """
      Change the quantity on an delivery line, then
      see if the packing list is solved automatically
      with accept solver.
    """
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = '\
                      stepSetUpAutomaticQuantityAcceptSolver \
                      ' + self.default_sequence + '\
                      stepDecreasePackingListLineQuantity \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def test_02_PackingListDecreaseQuantity(self, quiet=quiet):
    """
      Change the quantity on an delivery line, then
      see if the packing list is solved automatically
      with adopt solver.
    """
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = '\
                      stepSetUpAutomaticQuantityAdoptSolver \
                      ' + self.default_sequence + '\
                      stepDecreasePackingListLineQuantity \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsSolved \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Simulation))
  suite.addTest(unittest.makeSuite(TestERP5SimulationPackingList))
  suite.addTest(unittest.makeSuite(TestERP5SimulationInvoice))
  suite.addTest(unittest.makeSuite(TestAutomaticSolvingPackingList))
  return suite
