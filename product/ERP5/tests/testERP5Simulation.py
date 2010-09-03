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
from testPackingList import TestPackingListMixin
from testInvoice import TestInvoiceMixin
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from Products.ERP5Type.Document.BusinessTemplate import getChainByType

class TestERP5SimulationMixin(TestInvoiceMixin):

  def afterSetUp(self, quiet=1, run=1):
    TestInvoiceMixin.afterSetUp(self)
    business_process = self.portal.business_process_module.erp5_default_business_process
    pay_business_link = business_process['pay']
    pay_business_link.setSource('account_module/bank')
    pay_business_link.setDestination('account_module/bank')

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

class TestAutomaticSolvingPackingList(TestPackingListMixin, ERP5TypeTestCase):
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
  suite.addTest(unittest.makeSuite(TestAutomaticSolvingPackingList))
  return suite
