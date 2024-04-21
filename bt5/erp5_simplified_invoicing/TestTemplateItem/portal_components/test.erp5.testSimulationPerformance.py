# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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

from __future__ import print_function
import subprocess
import unittest
from time import time
from Products.ERP5Type.tests.runUnitTest import ERP5TypeTestLoader
from erp5.component.test.testTradeModelLine import TestTradeModelLineSale

if ERP5TypeTestLoader._testMethodPrefix == 'test':
  ERP5TypeTestLoader._testMethodPrefix = 'perf'

class TestSimulationPerformance(TestTradeModelLineSale):

  def getTitle(self):
    return "Simulation Performance"

  def afterSetUp(self):
    super(TestSimulationPerformance, self).afterSetUp()
    subprocess.call('sync')

  def runAlarms(self):
    for alarm in self.portal.portal_alarms.objectValues():
      if alarm.isEnabled():
        endswith = alarm.getId().endswith
        if endswith('_builder_alarm'):
          alarm.activeSense()
    self.tic()

  def perf_00_setupAndFillCache(self):
    self.test_01_OrderWithSimpleTaxedAndDiscountedLines()
    self.__class__._order = self['order'].getRelativeUrl()
    self.runAlarms()

  def perf_01_invoiceSimpleOrder(self, order_count=1):
    start = time()
    order = self.portal.unrestrictedTraverse(self._order)
    order_list = [self.clone(order) for _ in xrange(order_count)]
    for order in order_list:
      for line in list(order.getMovementList()):
        self.clone(line)
    self.tic()
    for order in order_list:
      order.order()
      self.commit()
    self.tic()
    for order in order_list:
      order.confirm()
      self.commit()
    self.tic()

    self.runAlarms()
    packing_list_list = sum((order.getCausalityRelatedValueList(
        portal_type=self.packing_list_portal_type)
      for order in order_list), [])

    for packing_list in packing_list_list:
      self.packPackingList(packing_list)
      self.commit()
    self.tic()
    for packing_list in packing_list_list:
      packing_list.start()
      self.commit()
    self.tic()
    for packing_list in packing_list_list:
      packing_list.stop()
      self.commit()
    self.tic()

    self.runAlarms()
    invoice_list = sum((packing_list.getCausalityRelatedValueList(
        portal_type=self.invoice_portal_type)
      for packing_list in packing_list_list), [])

    for packing_list in packing_list_list:
      packing_list.deliver()
      self.commit()
    self.tic()
    for invoice in invoice_list:
      invoice.start()
      self.commit()
    self.tic()
    for invoice in invoice_list:
      invoice.stop()
      self.commit()
    self.tic()
    for invoice in invoice_list:
      invoice.deliver()
      self.commit()
    self.tic()

    self.runAlarms()
    end = time()
    print("\n%s took %.4gs (%s order(s))" % (self._testMethodName,
                                             end - start, order_count))

  def perf_02_invoiceManySimpleOrders(self):
    self.perf_01_invoiceSimpleOrder(10)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSimulationPerformance))
  return suite
