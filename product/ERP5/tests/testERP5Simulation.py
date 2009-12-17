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
    script.write(script.read().replace("'Order Rule'", "'New Order Rule'")) # XXX-JPS Hacky

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
          portal_type='Category Membership Divergence Tester',
          tested_property=i) # XXX-JPS put a title
      # create category divergence testers that is also used for matching
      for i in ('resource',
                'variation_category',):
        new_order_rule.newContent(
          portal_type='Category Membership Divergence Tester',
          tested_property=i,
          matching_provider=1)
      # create category divergence testers that is only used for matching
      for i in ('order',):
        new_order_rule.newContent(
          portal_type='Category Membership Divergence Tester',
          tested_property=i,
          divergence_provider=0,
          matching_provider=1)
      # create dict divergence testers that is also used for matching
      for i in ('variation_property_dict',):
        new_order_rule.newContent(
          portal_type='Dict Divergence Tester', # XXX-JPS - better to create Variation Divergence Tester and develop the concept of abstract variation
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
          portal_type='Float Divergence Tester', # XXX-JPS Quantity Divergence Tester ? (ie. quantity unit)
          tested_property=i,
          use_delivery_ratio=1,
          quantity=0)
      new_order_rule.validate()

class TestERP5Simulation(TestERP5SimulationMixin, TestPackingList):
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
    # create a target solver
    solver = solver_process.newContent(
      portal_type='Quantity Accept Solver',
      delivery_list=quantity_solver_decision.getDeliveryList())
    quantity_solver_decision.setSolverValue(solver)
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
    # create a target solver
    solver = solver_process.newContent(
      portal_type='Resource Accept Solver',
      delivery_list=resource_solver_decision.getDeliveryList())
    resource_solver_decision.setSolverValue(solver)
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
    # create a target solver
    kw = {'delivery_solver':'FIFO',
          'start_date':self.datetime + 15,
          'stop_date':self.datetime + 25}
    solver = solver_process.newContent(
      portal_type='Quantity Accept Solver',
      delivery_list=quantity_solver_decision.getDeliveryList(),
      **kw)
    quantity_solver_decision.setSolverValue(solver)
    solver_process.solve()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Simulation))
  return suite
