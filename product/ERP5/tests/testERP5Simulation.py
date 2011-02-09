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
from testPackingList import TestPackingListMixin


class TestERP5Simulation(TestPackingListMixin, ERP5TypeTestCase):
  run_all_test = 1
  quiet = 0

  def afterSetUp(self):
    super(TestERP5Simulation, self).afterSetUp()
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      quantity_range_max=2,
      quantity_range_min=-1)

  def beforeTearDown(self):
    super(TestERP5Simulation, self).beforeTearDown()
    self.portal.portal_rules.new_delivery_simulation_rule.quantity_tester.edit(
      quantity_range_max=None,
      quantity_range_min=None)
    transaction.commit()
    self.tic()

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

  def test_00_simulationToolIsIndexed(self):
    """
    Parts of simulation (only legacy & "legacy legacy" simulation?)
    expect the simulation tool to be indexed in SQL queries, notably
    thanks to grand_parent related keys on Simulation Movements
    """
    portal_catalog = self.portal.portal_catalog

    portal_simulation_path = self.portal.portal_simulation.getPath()
    self.assertEquals(1,
        len(portal_catalog(path=portal_simulation_path)))

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
