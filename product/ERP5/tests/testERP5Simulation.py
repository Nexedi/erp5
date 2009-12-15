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

from testPackingList import TestPackingList, TestPackingListMixin

class TestERP5SimulationMixin(TestPackingListMixin):
  def getBusinessTemplateList(self):
    return list(TestPackingListMixin.getBusinessTemplateList(self)) + \
           ['erp5_simulation',]

  def afterSetUp(self, quiet=1, run=1):
    TestPackingListMixin.afterSetUp(self, quiet, run)
    self.validateNewRules()

  def validateNewRules(self):
    portal_types = self.portal.portal_types

    # add New Order Rule in Rule Tool's allowed content types.
    rule_tool_type = portal_types._getOb('Rule Tool')
    if not 'New Order Rule' in rule_tool_type.getTypeAllowedContentTypeList():
      rule_tool_type.edit(
        type_allowed_content_type_list=rule_tool_type.getTypeAllowedContentTypeList() + ['New Order Rule'])

    # select New Order Rule in 'SaleOrder_selectMovement' script.
    script = self.portal.SaleOrder_selectMovement
    script.write(script.read().replace("'Order Rule'", "'New Order Rule'"))

    # create a New Order Rule document.
    portal_rules = self.portal.portal_rules
    if portal_rules._getOb('new_order_rule', None) is None:
      new_order_rule = portal_rules.newContent(
        portal_type='New Order Rule',
        reference='default_order_rule',
        version=2,
        )
      # create category divergence testers
      for i in ('aggregate',
                'base_application',
                'base_contribution',
                'destination',
                'destination_account',
                'destination_function',
                'destination_project',
                'destination_section',
                'price_currency',
                'source',
                'source_account',
                'source_function',
                'source_project',
                'source_section',):
        new_order_rule.newContent(
          portal_type='Category Membership Divergence Tester',
          tested_property=i)
      # create category divergence testers that is also used for matching
      for i in ('resource',
                'variation_category',):
        new_order_rule.newContent(
          portal_type='Category Membership Divergence Tester',
          tested_property=i,
          matching_provider=1)
      # create dict divergence testers that is also used for matching
      for i in ('variation_property_dict',):
        new_order_rule.newContent(
          portal_type='Dict Divergence Tester',
          tested_property=i,
          matching_provider=1)
      # create datetime divergence testers
      for i in ('start_date',
                'stop_date',):
        new_order_rule.newContent(
          portal_type='DateTime Divergence Tester',
          tested_property=i,
          quantity=0)
      # create float divergence testers
      for i in ('quantity',):
        new_order_rule.newContent(
          portal_type='Float Divergence Tester',
          tested_property=i,
          use_delivery_ratio=1,
          quantity=0)
      new_order_rule.validate()

class TestERP5Simulation(TestERP5SimulationMixin, TestPackingList):
  def _addSolverProcess(self, divergence, solver_portal_type, **kw):
    solver_tool = self.portal.portal_solvers
    # create a solver process
    solver_process = solver_tool.newContent(portal_type='Solver Process')
    # create a target solver
    solver = solver_process.newContent(
      portal_type=solver_portal_type,
      delivery=divergence.getProperty('object_relative_url'),
      **kw)
    # create a solver decision
    solver_decision = solver_process.newContent(
      portal_type='Solver Decision',
      causality=divergence.getProperty('tester_relative_url'),
      delivery=divergence.getProperty('object_relative_url'),
      solver_value=solver,
      )
    return solver_process

  def stepAcceptDecisionQuantity(self,sequence=None, sequence_list=None, **kw):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    quantity_divergence = [x for x in packing_list.getDivergenceList() \
                           if x.getProperty('tested_property') == 'quantity'][0]
    solver_process = self._addSolverProcess(quantity_divergence,
                                            'Quantity Accept Solver')
    # then call solve() on solver process
    solver_process.solve()

  def stepAcceptDecisionResource(self,sequence=None, sequence_list=None, **kw):
    """
    Solve quantity divergence by using solver tool.
    """
    packing_list = sequence.get('packing_list')
    resource_divergence = [x for x in packing_list.getDivergenceList() \
                           if x.getProperty('tested_property') == 'resource'][0]
    solver_process = self._addSolverProcess(resource_divergence,
                                            'Resource Accept Solver')
    # then call solve() on solver process
    solver_process.solve()

  def stepSplitAndDeferPackingList(self, sequence=None, sequence_list=None, **kw):
    """
      Do the split and defer action
    """
    packing_list = sequence.get('packing_list')
    quantity_divergence = [x for x in packing_list.getDivergenceList() \
                           if x.getProperty('tested_property') == 'quantity'][0]
    kw = {'delivery_solver':'FIFO',
          'start_date':self.datetime + 15,
          'stop_date':self.datetime + 25}
    solver_process = self._addSolverProcess(quantity_divergence,
                                            'Quantity Split Solver', **kw)
    solver_process.solve()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Simulation))
  return suite
