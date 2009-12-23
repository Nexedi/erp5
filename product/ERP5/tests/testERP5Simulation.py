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
from testPackingList import TestPackingList, TestPackingListMixin

class TestERP5SimulationMixin(TestPackingListMixin):
  def getBusinessTemplateList(self):
    return list(TestPackingListMixin.getBusinessTemplateList(self)) + \
           ['erp5_simulation',]

  def afterSetUp(self, quiet=1, run=1):
    TestPackingListMixin.afterSetUp(self, quiet, run)
    self.validateNewRules()

  def beforeTearDown(self):
    portal_rules = self.portal.portal_rules
    for rule in portal_rules.objectValues(portal_type='New Order Rule'):
      if rule.getValidationState() == 'validated':
        rule.invalidate()

class TestERP5Simulation(TestERP5SimulationMixin, ERP5TypeTestCase):
  run_all_test = 1
  quiet = 0

  def validateNewRules(self):
    # create a New Order Rule document.
    portal_rules = self.portal.portal_rules
    try:
      new_order_rule = filter(
        lambda x:x.title == 'New Simple Order Rule',
        portal_rules.objectValues(portal_type='New Order Rule'))[0]
    except IndexError:
      new_order_rule = portal_rules.newContent(
        title='New Simple Order Rule',
        portal_type='New Order Rule',
        reference='default_order_rule',
        version=2,
        )
      # create category divergence testers that is only used for matching
      for i in ('resource',):
        new_order_rule.newContent(
          title='%s divergence tester' % i,
          portal_type='Category Membership Divergence Tester',
          tested_property=i,
          divergence_provider=0,
          matching_provider=1)
      # create float divergence testers
      for i in ('converted_quantity',):
        new_order_rule.newContent(
          title='%s divergence tester' % i,
          portal_type='Float Divergence Tester',
          tested_property=i,
          use_delivery_ratio=1,
          quantity_range_min=-1,
          quantity_range_max=2)
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
      lambda x:x.getCausalityValue().getTestedProperty()=='converted_quantity',
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
    # create a New Order Rule document.
    portal_rules = self.portal.portal_rules
    try:
      new_order_rule = filter(
        lambda x:x.title == 'New Default Order Rule',
        portal_rules.objectValues(portal_type='New Order Rule'))[0]
    except IndexError:
      new_order_rule = portal_rules.newContent(
        title='New Default Order Rule',
        portal_type='New Order Rule',
        reference='default_order_rule',
        version=2,
        )
      # create category divergence testers
      for i in ('aggregate',
                'base_application',
                'base_contribution',
                'destination',
                'destination_account', # XXX-JPS - Needed ?
                'destination_function', # XXX-JPS - Needed ?
                'destination_project', # XXX-JPS - Needed ?
                'destination_section', 
                'price_currency', # XXX-JPS - Needed ?
                'source', 
                'source_account', # XXX-JPS - Needed ?
                'source_function', # XXX-JPS - Needed ?
                'source_project', # XXX-JPS - Needed ?
                'source_section',): 
        new_order_rule.newContent(
          title='%s divergence tester' % i,
          portal_type='Category Membership Divergence Tester',
          tested_property=i)
      # create category divergence testers that is also used for matching
      for i in ('resource',):
        new_order_rule.newContent(
          title='%s divergence tester' % i,
          portal_type='Category Membership Divergence Tester',
          tested_property=i,
          matching_provider=1)
      # create variation divergence testers that is also used for matching
      for i in ('variation_property_dict',):
        # tested_property has no meaning for this tester.
        new_order_rule.newContent(
          title='%s divergence tester' % i,
          portal_type='Variation Divergence Tester',
          tested_property=i,
          matching_provider=1)
      # create datetime divergence testers
      for i in ('start_date',
                'stop_date',):
        new_order_rule.newContent(
          title='%s divergence tester' % i,
          portal_type='DateTime Divergence Tester',
          tested_property=i,
          quantity=0)
      # create float divergence testers
      for i in ('quantity',):
        new_order_rule.newContent(
          title='%s divergence tester' % i,
          portal_type='Float Divergence Tester', # XXX-JPS Quantity Divergence Tester ? (ie. quantity unit)
          tested_property=i,
          use_delivery_ratio=1,
          quantity=0)
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Simulation))
  suite.addTest(unittest.makeSuite(TestERP5SimulationPackingList))
  return suite
