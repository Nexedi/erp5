##############################################################################
#
# Copyright (c) 2002-2026 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestDeliveryLineEdit(ERP5TypeTestCase):

  def testDeliveryLineEdit(self):
    """Make sure that unordered properties are updated after resource properties."""
    resource_value_1 = self.portal.erp5_core_test_module.newContent(portal_type='Delivery Line Edit Test')
    resource_value_2 = self.portal.erp5_core_test_module.newContent(portal_type='Delivery Line Edit Test')

    delivery_line_value = self.portal.erp5_core_test_module.newContent(portal_type='Delivery Line Edit Test')
    self.assertEqual(delivery_line_value.getPrice(), None)
    self.assertEqual(delivery_line_value.getCustomX(), None)

    delivery_line_value.edit(resource_value=resource_value_1)
    self.assertEqual(delivery_line_value.getResourceValue(), resource_value_1)
    self.assertEqual(delivery_line_value.getPrice(), 10)
    self.assertEqual(delivery_line_value.getCustomX(), 'Hello')

    delivery_line_value.edit(resource_value=resource_value_2,
                             price=123,
                             custom_x='World')
    self.assertEqual(delivery_line_value.getResourceValue(), resource_value_2)
    self.assertEqual(delivery_line_value.getPrice(), 123)
    self.assertEqual(delivery_line_value.getCustomX(), 'World')

    delivery_line_value.edit(resource=resource_value_1.getRelativeUrl())
    self.assertEqual(delivery_line_value.getResourceValue(), resource_value_1)
    self.assertEqual(delivery_line_value.getPrice(), 10)
    self.assertEqual(delivery_line_value.getCustomX(), 'Hello')

    delivery_line_value.edit(resource=resource_value_2.getRelativeUrl(),
                             price=123,
                             custom_x='World')
    self.assertEqual(delivery_line_value.getResourceValue(), resource_value_2)
    self.assertEqual(delivery_line_value.getPrice(), 123)
    self.assertEqual(delivery_line_value.getCustomX(), 'World')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestDeliveryLineEdit))
  return suite
