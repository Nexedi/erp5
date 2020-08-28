##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#          Nicolas Dumazet <nicolas.dumazet@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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

from erp5.component.test.testPurchaseOrder import TestPurchaseOrder

class TestInternalOrder(TestPurchaseOrder):
  """
    Test business template erp5_trade
  """
  run_all_test = 1
  order_portal_type = 'Internal Order'
  order_line_portal_type = 'Internal Order Line'
  order_cell_portal_type = 'Internal Order Cell'
  packing_list_portal_type = 'Internal Packing List'
  packing_list_line_portal_type = 'Internal Packing List Line'
  packing_list_cell_portal_type = 'Internal Packing List Cell'
  delivery_builder_id = 'internal_packing_list_builder'

  def getTitle(self):
    return "Internal Order"

  def test_order_payment_condition_copied(self):
    """
    No Payment conditions for Internal Orders
    """

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInternalOrder))
  return suite

