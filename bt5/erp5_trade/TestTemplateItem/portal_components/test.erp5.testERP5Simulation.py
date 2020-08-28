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


from Products.ERP5Type.tests.SecurityTestCase import SecurityTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testPackingList import TestPackingListMixin

from Products.PythonScripts.Utility import allow_class
class DummySolverConfiguration(object):
  def as_dict(self):
    return {'tested_property_list': ['quantity']}
allow_class(DummySolverConfiguration)

class TestERP5Simulation(TestPackingListMixin, SecurityTestCase):
  run_all_test = 1
  quiet = 0

  def afterSetUp(self):
    super(TestERP5Simulation, self).afterSetUp()
    self.loginByUserName('manager')
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      quantity_range_max=2,
      quantity_range_min=-1)

  def beforeTearDown(self):
    super(TestERP5Simulation, self).beforeTearDown()
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      quantity_range_max=None,
      quantity_range_min=None)
    self.tic()

  def _modifyPackingListLineQuantity(self, sequence=None,
      sequence_list=None, delta=0.0):
    """
    Set a increased quantity on packing list lines
    """
    packing_list = sequence.get('packing_list')
    for packing_list_line in packing_list.objectValues(
        portal_type=self.packing_list_line_portal_type):
      packing_list_line.edit(quantity=packing_list_line.getQuantity() + delta)
    sequence.edit(last_delta=delta)

  def stepIncreasePackingListLineQuantity2(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, 2.0)

  def stepDecreasePackingListLineQuantity3(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, -3.0)

  def stepDecreasePackingListLineQuantity4(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, -4.0)

  def stepDecreasePackingListLineQuantity9(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, -9.0)

  def stepDecreasePackingListLineQuantity1010(self, sequence=None,
      sequence_list=None, **kw):
    return self._modifyPackingListLineQuantity(sequence, sequence_list, -1010.0)

  def stepSplitAndDeferPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and defer action
    """
    packing_list = sequence.get('packing_list')
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(packing_list)
    sequence.edit(solver_process=solver_process)
    quantity_solver_decision = [
      x for x in solver_process.contentValues()
      if x.getCausalityValue().getTestedProperty()=='quantity'][0]
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
      after_tag = []
      if previous_tag:
        after_tag.append(previous_tag)
      delivery_builder.activate(
        after_method_id=('solve',
                         'immediateReindexObject'), # XXX too brutal.
        after_tag=after_tag,
        ).build(explanation_uid=packing_list.getCausalityValue().getUid())

  def stepCheckPackingListSplitted(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list was splitted
    """
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    self.assertEqual(2,len(packing_list_list))
    packing_list1 = None
    packing_list2 = None
    for packing_list in packing_list_list:
      if packing_list.getUid() == sequence.get('packing_list').getUid():
        packing_list1 = packing_list
      else:
        packing_list2 = packing_list
    sequence.edit(new_packing_list=packing_list2)
    line, = packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type)
    self.assertEqual(self.default_quantity-10,line.getQuantity())
    line, = packing_list2.objectValues(
          portal_type= self.packing_list_line_portal_type)
    self.assertEqual(10,line.getQuantity())

  def _checkSolverState(self, sequence=None, sequence_list=None,
                        state='solved'):
    """
      Check if target solvers' state.
    """
    solver_process = sequence.get('solver_process')
    for solver in solver_process.objectValues(
      portal_type=self.portal.getPortalTargetSolverTypeList()):
      self.assertEqual(state, solver.getValidationState())

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

  def test_00_simulationToolIsIndexed(self):
    """
    Parts of simulation (only legacy & "legacy legacy" simulation?)
    expect the simulation tool to be indexed in SQL queries, notably
    thanks to grand_parent related keys on Simulation Movements
    """
    portal_catalog = self.portal.portal_catalog

    portal_simulation_path = self.portal.portal_simulation.getPath()
    self.assertEqual(1,
        len(portal_catalog(path=portal_simulation_path)))

  def stepCheckPackingListSplittedTwoTimes(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list was splitted two times
    """
    order = sequence.get('order')
    packing_list_list = self.getOrderedPackingListFromOrder(order)
    packing_list1, packing_list2, packing_list3 = packing_list_list

    sequence.edit(new_packing_list=packing_list2)
    line, = packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type)
    self.assertEqual(self.default_quantity-10,line.getQuantity())
    line, = packing_list2.objectValues(
          portal_type= self.packing_list_line_portal_type)
    self.assertEqual(6, line.getQuantity())
    line, = packing_list3.objectValues(
          portal_type= self.packing_list_line_portal_type)
    self.assertEqual(4, line.getQuantity())
    # Check the id in simulation is not too long after multiple splitting
    simulation_movement, = line.getDeliveryRelatedValueList()
    self.assertEqual('1_split_1', simulation_movement.getId())

  def stepSetNewPackingListAsPackingList(self, sequence=None, sequence_list=None, **kw):
    sequence.edit(packing_list=sequence.get('new_packing_list'))

  def test_01_splitAndDefer(self, quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then see if the packing list
      remains solved when we change a little bit the quantity (within the range
      accepted by the quantity tester).

      Then see if the packing list becomes divergent when the quantity is
      heavily changed (outside the range accepted by the quantity tester).
      Split and defer the packing list and check newly created packing list.

      Finally, split the new packing list to make sure we can split splitted
      packing list. In the same time, check if we do not create very long
      ids for simulation movements (this was the case before)
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
                      stepDecreasePackingListLineQuantity3 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepDecreasePackingListLineQuantity9 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepSplitAndDeferPackingList \
                      stepCheckSolverIsSolving \
                      stepTic \
                      stepCheckPackingListSplitted \
                      stepCheckPackingListIsSolved \
                      stepCheckSolverIsSolved \
                      stepSetNewPackingListAsPackingList \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepDecreasePackingListLineQuantity4 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepSplitAndDeferPackingList \
                      stepCheckSolverIsSolving \
                      stepTic \
                      stepCheckPackingListSplittedTwoTimes \
                      stepCheckPackingListIsSolved \
                      stepCheckSolverIsSolved \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def stepIncreasePackingListLineQuantity1000(self, sequence=None, sequence_list=None, **kw):
    self._modifyPackingListLineQuantity(sequence, sequence_list, 1000.0)

  def stepCheckPackingListSplittedForTest02(self, sequence=None, sequence_list=None, **kw):
    """
      Test if packing list was splitted
    """
    order = sequence.get('order')
    packing_list_list = self.getOrderedPackingListFromOrder(order)
    packing_list1, packing_list2 = packing_list_list

    destination_value = sequence.get('organisation3')
    self.assertEqual(packing_list1.getDestinationValue(), destination_value)
    self.assertEqual(packing_list2.getDestinationValue(), destination_value)

    sequence.edit(new_packing_list=packing_list2)
    for line in packing_list1.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEqual(self.default_quantity-10,line.getQuantity())
    self.assertEqual('solved', packing_list1.getCausalityState())
    for line in packing_list2.objectValues(
          portal_type= self.packing_list_line_portal_type):
      self.assertEqual(10+1000,line.getQuantity())
    self.assertEqual('solved', packing_list2.getCausalityState())

  def stepExpandOrder(self, sequence=None, sequence_list=None, **kw):
    order = sequence.get('order')
    order.updateSimulation(expand_root=1)

  def getOrderedPackingListFromOrder(self, order):
    packing_list_list = order.getCausalityRelatedValueList(
                               portal_type=self.packing_list_portal_type)
    packing_list_list.sort(key=lambda x: int(x.getId()))
    return packing_list_list


  def test_02_splitAndDeferAfterAcceptDecision(self, quiet=quiet, run=run_all_test):
    """
      Change the quantity on an delivery line, then
      see if the packing list is divergent and then
      accept decision, then change the quantity again
      and see if the packing list is divergent and then
      split and defer the packing list and then see
      if two packing lists has correct quantity and
      they are not diverged.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepIncreasePackingListLineQuantity1000 \
                      stepChangePackingListDestination \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepAcceptDecisionDestination \
                      stepAcceptDecisionQuantity \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsNotDivergent \
                      stepCheckPackingListIsSolved \
                      stepDecreasePackingListLineQuantity1010 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepSplitAndDeferPackingList \
                      stepCheckSolverIsSolving \
                      stepTic \
                      stepCheckPackingListSplittedForTest02 \
                      stepCheckSolverIsSolved \
                      stepExpandOrder \
                      stepTic \
                      stepCheckPackingListSplittedForTest02 \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)

  def _getPortalStatusMessage(self, url):
    return url.rsplit('=', 1)[-1].replace('%20', ' ')

  def stepSolveDivergenceThroughDialog(self,
                                       sequence=None,
                                       sequence_list=None):
    packing_list = sequence.get('packing_list')

    # 'Solve Divergences' Action (Delivery_viewSolveDivergenceDialog)
    self.assertUserCanPassWorkflowTransition('ERP5TypeTestCase',
                                             'solve_divergence_action',
                                             packing_list)
    solver_decision_list = packing_list.Delivery_getSolverDecisionList()
    self.assertEqual(len(solver_decision_list), 1)

    # Choose 'Divergence Resolution' (Adopt Prevision)
    solver_decision = solver_decision_list[0]
    listbox = [{
       'listbox_key':solver_decision.getPath(),
       'comment': '',
       'solver_configuration': DummySolverConfiguration(),
       'solver': 'portal_solvers/Adopt Solver'}]

    packing_list.Delivery_updateSolveDivergenceDialog(listbox=listbox)

    # Solve Divergences
    self.assertEqual(
      self._getPortalStatusMessage(packing_list.Delivery_submitSolveDivergenceDialog(listbox=listbox)),
      'Divergence solvers started in background.')

    # SolverProcess.solve() called
    # => SolverProcess.startSolving()
    #    => solve() activity created
    self.assertEqual(solver_decision.getValidationState(), 'solving')
    sequence.edit(solver_decision=solver_decision)

  def stepCheckOnlyOneSolverProcessCreated(self,
                                           sequence=None,
                                           sequence_list=None):
    packing_list = sequence.get('packing_list')
    solver_decision = sequence.get('solver_decision')

    # 'Solve Divergences' Action should not be available anymore
    self.failIfUserCanPassWorkflowTransition('ERP5TypeTestCase',
                                             'solve_divergence_action',
                                             packing_list)

    # Solver Process is in 'solving' state, so no new Solver Process should be
    # created and this should return nothing
    self.assertEqual(len(packing_list.getSolverValueList()), 1)
    self.assertEqual(len(packing_list.Delivery_getSolverDecisionList()), 0)

    listbox = [{
       'listbox_key':solver_decision.getPath(),
       'comment': '',
       'solver_configuration': DummySolverConfiguration(),
       'solver': 'portal_solvers/Adopt Solver'}]

    self.assertEqual(
      self._getPortalStatusMessage(packing_list.Delivery_updateSolveDivergenceDialog(listbox=listbox)),
      'Workflow state may have been updated by other user. Please try again.')

    self.assertEqual(
      self._getPortalStatusMessage(packing_list.Delivery_submitSolveDivergenceDialog(listbox=listbox)),
      'Workflow state may have been updated by other user. Please try again.')

    self.tic()
    self.assertEqual(packing_list.getCausalityState(), 'solved')

  def test_03_solverProcessCreatedOnlyOnce(self, quiet=quiet, run=run_all_test):
    """
    Solver Process used to be created after selecting 'Solve Divergences' Action:
      1. Select 'Solve Divergences' Action.
      2. Dialog is displayed and new 'draft' 'Solver Process' is created if it
         does not exist yet.
      3. Adopt Prevision/Accept Decision is selected: this creates a 'solve'
         Activity after changing Solver Process workflow state to 'solving'

    Until 'solve' Activity is processed:
      => 2. meant that there was no more 'Solver Process' in 'draft' state and
         thus a new one may be created.
      => The 'Solve Divergences' Action was still available.

    Now Solver Process is created when causality_state changed to diverged and
    'Solve Divergences' Action is not displayed unless its state is 'draft'.
    """
    if not run: return
    sequence_list = SequenceList()

    # Test with a simply order without cell
    sequence_string = self.default_sequence + '\
                      stepIncreasePackingListLineQuantity1000 \
                      stepCheckPackingListIsCalculating \
                      stepTic \
                      stepCheckPackingListIsDiverged \
                      stepSolveDivergenceThroughDialog \
                      stepCheckOnlyOneSolverProcessCreated \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self, quiet=quiet)
