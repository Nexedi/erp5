# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
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

import sys
from Products.ERP5Legacy.tests import testLegacyBPMCore
sys.modules['Products.ERP5.tests.testBPMCore'] = testLegacyBPMCore
from Products.ERP5.tests.testTradeModelLine import *
from Products.ERP5.tests.testTradeModelLinePurchase import *
from Products.ERP5.tests.testComplexTradeModelLineUseCase import *

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTradeModelLineSale))
  suite.addTest(unittest.makeSuite(TestTradeModelLinePurchase))
  suite.addTest(unittest.makeSuite(TestComplexTradeModelLineUseCaseSale))
  suite.addTest(unittest.makeSuite(TestComplexTradeModelLineUseCasePurchase))
  return suite

###
##  TestTradeModelLine
##

TestTradeModelLine.trade_model_path_portal_type = None
TestTradeModelLine.business_link_portal_type = None

for name in list(TestTradeModelLine.__dict__):
  if '_NewSimulation_' in name:
    delattr(TestTradeModelLine, name)

def createBusinessProcess(self, *args, **kw):
  business_process = super(TestTradeModelLine, self) \
    .createBusinessProcess(*args, **kw)
  taxed = self.createBusinessState(business_process, reference='taxed')
  invoiced = self.createBusinessState(business_process, reference='invoiced')
  self.createBusinessPath(business_process, trade_phase='default/discount',
    predecessor_value=invoiced, successor_value=taxed)
  self.createBusinessPath(business_process, trade_phase='default/tax',
    predecessor_value=invoiced, successor_value=taxed)
  return business_process
TestTradeModelLine.createBusinessProcess = createBusinessProcess

def checkWithoutBPM(self, order):
  transaction.commit() # clear transactional cache
  order.getSpecialiseValue()._setSpecialise(None)
  self.checkAggregatedAmountList(order)
  applied_rule_id = order.getCausalityRelatedId(portal_type='Applied Rule')
  order.expand(applied_rule_id=applied_rule_id)
  for line in order.getMovementList():
    simulation_movement_list, = self.getTradeModelSimulationMovementList(line)
    self.assertFalse(simulation_movement_list)
  transaction.abort()
TestTradeModelLine.checkWithoutBPM = checkWithoutBPM

def checkModelLineOnDelivery(self, delivery):
  transaction.commit() # clear transactional cache
  delivery.newContent(portal_type='Trade Model Line',
                      price=0.5,
                      base_application='base_amount/discount',
                      base_contribution='base_amount/total_discount',
                      trade_phase='default/discount',
                      resource_value=self['service/discount'],
                      reference='total_dicount_2',
                      int_index=10)
  discount_price = (3*4) * 0.5
  tax_price = (1*2) * 0.2
  total_tax_price = tax_price * 2 * 0.12
  self.getAggregatedAmountDict(delivery,
      service_tax=dict(total_price=tax_price),
      total_dicount_2=dict(total_price=discount_price),
      service_tax_2=dict(total_price=tax_price),
      tax_3=dict(total_price=total_tax_price),
      total_discount=dict(total_price=(total_tax_price+discount_price) * 0.8))
  transaction.abort()
TestTradeModelLine.checkModelLineOnDelivery = checkModelLineOnDelivery

def checkComposition(self, movement, specialise_value_list, type_count_dict):
  composed = movement.asComposedDocument()
  self.assertTrue(movement in composed._effective_model_list)
  self.assertSameSet(composed.getSpecialiseValueList(),
                     specialise_value_list)
  count = 0
  for portal_type, n in type_count_dict.iteritems():
    if portal_type:
      count += n
      self.assertEqual(n, len(composed.objectValues(portal_type=portal_type)))
  self.assertTrue(count, len(composed.objectValues()))
TestTradeModelLine.checkComposition = checkComposition

def checkTradeModelRuleSimulationExpand(self, delivery):
  expected_result_dict = self[delivery.getPath()]
  price_currency = self['price_currency']

  # There is no 'specialise' on the packing list, deleting entire branches
  # of the simulation tree. See also SimulationMovement.asComposedDocument
  no_expand = 'packing_list' in self and 'invoice' not in self

  for line in delivery.getMovementList():
    simulation_movement_list, = \
      self.getTradeModelSimulationMovementList(line)
    if no_expand:
      self.assertFalse(simulation_movement_list)
      continue
    result_dict = dict((sm.getResourceValue().getUse(), sm)
                       for sm in simulation_movement_list)
    self.assertEqual(len(simulation_movement_list),
                     len(result_dict))
    for use in 'discount', 'tax':
      total_price = expected_result_dict[use].get(line.getId())
      if total_price:
        sm = result_dict.pop(use)
        self.assertEqual(str(sm.getTotalPrice()), str(total_price))
        self.assertEqual(1, len(sm.getCausalityValueList()))
        self.assertEqual(1, len(sm.getCausalityValueList(
          portal_type='Business Path')))
        self.assertEqual(0, len(sm.getCausalityValueList(
          portal_type='Trade Model Line')))
        self.assertEqual(sm.getBaseApplicationList(),
                          ['base_amount/' + use])
        self.assertEqual(sm.getBaseContributionList(),
                          dict(discount=['base_amount/tax'], tax=[])[use])
    self.assertEqual({}, result_dict)
TestTradeModelLine.checkTradeModelRuleSimulationExpand = \
  checkTradeModelRuleSimulationExpand
