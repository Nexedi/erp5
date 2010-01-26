# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
This is BPM Evaluation Test class using erp5_bpm development Business Template

Generally it tries to use two Business Processes - one with sequence very
similar to normal ERP5 - TestBPMEvaluationDefaultProcessMixin, second one
inverted - TestBPMEvaluationDifferentProcessMixin.

It uses only Sale path to demonstrate BPM.

It is advised to *NOT* remove erp5_administration.
"""
import transaction

from Products.ERP5.tests.testBPMCore import TestBPMMixin
from Products.ERP5.tests.testBPMEvaluation import \
     TestBPMEvaluationMixin, \
     test_suite

if True:
  def getBusinessTemplateList(self):
    return TestBPMMixin.getBusinessTemplateList(self) + ('erp5_bpm',
        'erp5_administration', 'erp5_simulation',)

  TestBPMEvaluationMixin.getBusinessTemplateList = getBusinessTemplateList

  def _createRootTradeRule(self, **kw):
    edit_dict = {}
    edit_dict.update(
      trade_phase = 'default/delivery',
    )
    edit_dict.update(**kw)
    rule = self.rule_tool.newContent(**edit_dict)

    # matching providers
    for category in ('resource', 'order'):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)
    rule.newContent(
      portal_type='Variation Divergence Tester',
      title='variation divergence tester',
      tested_property='variation_property_dict',
      divergence_provider=False,
      matching_provider=True)

    # divergence providers
    for category in ('source_section',
                     'resource',
                     'destination_section',
                     'source',
                     'aggregate'):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    for property_id in ('start_date', 'stop_date'):
      rule.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)

    return rule

  TestBPMEvaluationMixin._createRootTradeRule = _createRootTradeRule

  def _createTradeModelRule(self):
    rule = self.rule_tool.newContent(portal_type='Trade Model Rule',
      reference='default_trade_model_rule',
      test_method_id = ('SimulationMovement_testTradeModelRule',)
      )
    # matching providers
    for category in ('resource',):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)
    rule.newContent(
      portal_type='Variation Divergence Tester',
      title='variation divergence tester',
      tested_property='variation_property_dict',
      divergence_provider=False,
      matching_provider=True)

    # divergence providers
    for category in ('resource',
                     'source_section',
                     'destination_section',
                     'source',
                     'source_function',
                     'destination_function',
                     'source_project',
                     'destination_project',
                     'aggregate',
                     'price_currency',
                     'base_contribution',
                     'base_application',
                     'source_account',
                     'destination_account',
                     ):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    for property_id in ('start_date', 'stop_date'):
      rule.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)

    rule.validate()
    transaction.commit()

  TestBPMEvaluationMixin._createTradeModelRule = _createTradeModelRule

  def _createInvoicingRule(self):
    edit_dict = {}
    edit_dict.update(
    )
    rule = self.rule_tool.newContent(portal_type='Invoicing Rule',
      reference='default_invoicing_rule',
      trade_phase = 'default/invoicing',
      test_method_id = ('SimulationMovement_testInvoicingRule',)
      )
    # matching providers
    for category in ('resource',):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)
    rule.newContent(
      portal_type='Variation Divergence Tester',
      title='variation divergence tester',
      tested_property='variation_property_dict',
      divergence_provider=False,
      matching_provider=True)

    # divergence providers
    for category in ('resource',
                     'source_section',
                     'destination_section',
                     'source',
                     'source_function',
                     'destination_function',
                     'source_project',
                     'destination_project',
                     'aggregate',
                     'price_currency',
                     'base_contribution',
                     'base_application',
                     'source_account',
                     'destination_account',
                     ):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    for property_id in ('start_date', 'stop_date'):
      rule.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)

    rule.validate()
    transaction.commit()

  TestBPMEvaluationMixin._createInvoicingRule = _createInvoicingRule
