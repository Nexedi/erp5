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

from zLOG import LOG
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from testPackingList import TestPackingList, TestPackingListMixin

class TestERP5SimulationMixin(TestPackingListMixin):
  def getBusinessTemplateList(self):
    return list(TestPackingListMixin.getBusinessTemplateList(self)) + \
           ['erp5_simulation',]

  def afterSetUp(self, quiet=1, run=1):
    TestPackingListMixin.afterSetUp(self, quiet, run)
    portal_rules = self.portal.portal_rules
    for rule in portal_rules.objectValues(portal_type='Order Rule'):
      if rule.getValidationState() == 'validated':
        rule.invalidate()
    self.validateNewRules()

class TestERP5Simulation(TestERP5SimulationMixin, ERP5TypeTestCase):
  run_all_test = 1
  quiet = 0

  def validateNewRules(self):
    # create an Order Rule document.
    portal_rules = self.portal.portal_rules
    new_order_rule = filter(
      lambda x:x.title == 'New Simple Order Rule',
      portal_rules.objectValues(portal_type='Order Rule'))[0]
    if new_order_rule.getValidationState() != 'validated':
      new_order_rule.validate()

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
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    sequence.edit(solver_process=solver_process)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_types['Quantity Split Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO',
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
      self.assertEquals(state, solver.getSolverState())

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
  def validateNewRules(self):
    # create an Order Rule document.
    portal_rules = self.portal.portal_rules
    new_order_rule = filter(
      lambda x:x.title == 'New Default Order Rule',
      portal_rules.objectValues(portal_type='Order Rule'))[0]
    if new_order_rule.getValidationState() != 'validated':
      new_order_rule.validate()

  def stepAcceptDecisionQuantity(self,sequence=None, sequence_list=None, **kw):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Accept Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_types['Quantity Accept Solver'])
    solver_process.buildTargetSolverList()
    solver_process.solve()
    # XXX-JPS We do not need the divergence message anymore.
    # since the divergence message == the divergence tester itself
    # with its title, description, tested property, etc.

  def stepAcceptDecisionResource(self,sequence=None, sequence_list=None, **kw):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    resource_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='resource',
      solver_process.contentValues())[0]
    # use Resource Replacement Solver.
    resource_solver_decision.setSolverValue(self.portal.portal_types['Resource Replacement Solver'])
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepSplitAndDeferPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and defer action
    """
    packing_list = sequence.get('packing_list')
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Split Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_types['Quantity Split Solver'])
    # configure for Quantity Split Solver.
    kw = {'delivery_solver':'FIFO',
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
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    quantity_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues())[0]
    # use Quantity Adoption Solver.
    quantity_solver_decision.setSolverValue(self.portal.portal_types['Quantity Adoption Solver'])
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepAdoptPrevisionQuantity(self,sequence=None, sequence_list=None, **kw):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    self._adoptPrevisionQuantity(packing_list)

  def stepNewPackingListAdoptPrevisionQuantity(self, sequence=None,
                                               sequence_list=None, **kw):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('new_packing_list')
    self._adoptPrevisionQuantity(packing_list)

  def stepAdoptPrevisionResource(self,sequence=None, sequence_list=None, **kw):
    """
    Solve resource divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    resource_solver_decision = filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='resource',
      solver_process.contentValues())[0]
    # use Resource Adopt Solver.
    resource_solver_decision.setSolverValue(self.portal.portal_types['Resource Adoption Solver'])
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepCheckPackingListLineWithSameResource(self,sequence=None, sequence_list=None, **kw):
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
                        [x.getOrder() for x in \
                         line.getDeliveryRelatedValueList()])

  def stepUnifyDestinationWithDecision(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    for destination_solver_decision in filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='destination',
      solver_process.contentValues()):
      # use Destination Replacement Solver.
      destination_solver_decision.setSolverValue(self.portal.portal_types['Destination Replacement Solver'])
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepUnifyStartDateWithDecision(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    for start_date_solver_decision in filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='start_date',
      solver_process.contentValues()):
      # use StartDate Replacement Solver.
      start_date_solver_decision.setSolverValue(self.portal.portal_types['Start Date Replacement Solver'])
      # configure for Quantity Split Solver.
      kw = {'value':packing_list.getStartDate()}
      start_date_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepUnifyStartDateWithPrevision(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    packing_list = sequence.get('packing_list')
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    start_date = simulation_line_list[-1].getStartDate()
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(packing_list)
    for start_date_solver_decision in filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='start_date',
      solver_process.contentValues()):
      # use StartDate Replacement Solver.
      start_date_solver_decision.setSolverValue(self.portal.portal_types['Start Date Replacement Solver'])
      # configure for Quantity Split Solver.
      kw = {'value':start_date}
      start_date_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def checkOrderRuleSimulation(self, rule_reference, sequence=None, sequence_list=None, **kw):
    """
      Test if simulation is matching order, be sure that rule_reference is used
      to expand simulation for order
    """
    order = sequence.get('order')
    related_applied_rule_list = order.getCausalityRelatedValueList( \
                                   portal_type=self.applied_rule_portal_type)
    no_applied_rule_state = ('draft', 'auto_planned')
    order_state = order.getSimulationState()

    if order_state in no_applied_rule_state:
      self.assertEquals(0, len(related_applied_rule_list))
    else:
      LOG('stepCheckOrderRuleSimulation', 0, 'related_applied_rule_list: %s' %
                   str([x.getObject() for x in related_applied_rule_list]))
      self.assertEquals(1, len(related_applied_rule_list))
      applied_rule = related_applied_rule_list[0].getObject()
      sequence.edit(applied_rule=applied_rule)
      self.failUnless(applied_rule is not None)
      self.failUnless(order_state, \
                      applied_rule.getLastExpandSimulationState())

      # Test if applied rule has a specialise value with passed rule_reference
      portal_rules = getToolByName(order, 'portal_rules')
      self.assertEquals(rule_reference,
                        applied_rule.getSpecialiseReference())

      simulation_movement_list = applied_rule.objectValues()
      sequence.edit(simulation_movement_list=simulation_movement_list)

      # Count the number of movement in order
      movement_list = order.getMovementList()
      # Check if number of unique movement is equal to number of
      # simulation movement
      unique_movement_list = dict(
        [('%r,%r,%r' % (x.getResource(), x.getVariationCategoryList(),
          x.getVariationPropertyDict())), x] for x in movement_list).values()
      self.assertEquals(len(unique_movement_list),
                        len(simulation_movement_list))
      # Check if all movements are related to simulation movements
      order_movement_list = sum([x.getOrderValueList() for x in \
                                 simulation_movement_list], [])
      self.failIfDifferentSet(movement_list, order_movement_list)

      # Check each simulation movement
      for simulation_movement in simulation_movement_list:
        order_movement_list = simulation_movement.getOrderValueList()
        # Test quantity
        self.assertEquals(sum([x.getQuantity() for x in order_movement_list]),
                          simulation_movement.getQuantity())
        for order_movement in order_movement_list:
          # Test price
          self.assertEquals(order_movement.getPrice(), \
                            simulation_movement.getPrice())
          # Test resource
          self.assertEquals(order_movement.getResource(), \
                            simulation_movement.getResource())
          # Test resource variation
          self.assertEquals(order_movement.getVariationText(), \
                            simulation_movement.getVariationText())
          self.assertEquals(order_movement.getVariationCategoryList(), \
                            simulation_movement.getVariationCategoryList())
          # XXX Test acquisition
          self.checkAcquisition(simulation_movement, order_movement)

  def stepModifySimulationLineQuantityForMergedLine(self,sequence=None, sequence_list=None, **kw):
    """
      Check if simulation movement are disconnected
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list), 1)
    for simulation_line in simulation_line_list:
      simulation_line.edit(quantity=self.default_quantity-2)
      simulation_line.getOrderValue().edit(quantity=self.default_quantity-2)

  def stepCheckSimulationQuantityUpdatedForMergedLine(self,sequence=None, sequence_list=None, **kw):
    """
      Test if the quantity of the simulation movement was changed
    """
    applied_rule = sequence.get('applied_rule')
    simulation_line_list = applied_rule.objectValues()
    self.assertEquals(len(simulation_line_list), 1)
    for simulation_line in simulation_line_list:
      self.assertEquals(simulation_line.getQuantity() + \
                        simulation_line.getDeliveryError(),
                        self.default_quantity * 2)

  def stepCheckPackingListLineWithDifferentResource(self,sequence=None, sequence_list=None, **kw):
    """
      Look if the packing list has new previsions
    """
    packing_list_line = sequence.get('packing_list_line')
    new_resource = sequence.get('resource')
    self.assertEquals(packing_list_line.getQuantity(), self.default_quantity*2)
    self.assertEquals(packing_list_line.getResourceValue(), new_resource)
    simulation_line_list = packing_list_line.getDeliveryRelatedValueList()
    order_line_list = sum([x.getOrderList() for x in simulation_line_list], [])
    self.assertEquals(sorted(packing_list_line.getCausalityList()),
                      sorted(order_line_list))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Simulation))
  suite.addTest(unittest.makeSuite(TestERP5SimulationPackingList))
  return suite
