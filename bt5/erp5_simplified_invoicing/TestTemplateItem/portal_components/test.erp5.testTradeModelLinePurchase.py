# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#          Fabien Morin <fabien@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest
from erp5.component.test.testTradeModelLine import TestTradeModelLine

class TestTradeModelLinePurchase(TestTradeModelLine):
  invoice_portal_type = 'Purchase Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  invoice_transaction_line_portal_type = 'Purchase Invoice Transaction Line'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  packing_list_portal_type = 'Purchase Packing List'
  trade_condition_portal_type = 'Purchase Trade Condition'

  def packPackingList(self, packing_list):
    self.assertEqual(getattr(packing_list, 'getContainerState', None), None)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTradeModelLinePurchase))
  return suite
