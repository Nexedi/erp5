##############################################################################
#
# Copyright (c) 2002-2016 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestDeliveryNode(ERP5TypeTestCase):

  def getTitle(self):
    return "Test Delivery Node"

  def test_delivery_node(self):
    """
    """
    kw = {"title": "Test Delivery Node",
          "corporate_name": "Organisation SA",
          "default_email_coordinate_text": "g@g.com",
          "default_telephone_coordinate_text": "123",
          "default_fax_coordinate_text": "321",
          "default_address_street_address": "Street 123",
          "default_address_zip_code": "923",
          "default_address_city": "City",
          "default_address_region": "americas/south_america/brazil"
         }
    delivery_node = self.portal.delivery_node_module.newContent(
      portal_type="Delivery Node",
      **kw)
    self.assertNotEqual(None, delivery_node)
    self.assertEqual(kw["title"], delivery_node.getTitle())
    self.assertEqual(kw["corporate_name"],
                     delivery_node.getCorporateName())
    self.assertEqual(kw["default_telephone_coordinate_text"],
                    delivery_node["default_telephone"].getCoordinateText())
    self.assertEqual(kw["default_email_coordinate_text"],
                    delivery_node["default_email"].getCoordinateText())
    self.assertEqual(kw["default_fax_coordinate_text"],
                    delivery_node["default_fax"].getCoordinateText())
    self.assertEqual(kw["default_address_region"],
                    delivery_node.getDefaultAddressRegion())
    delivery_node.validate()
    self.assertEqual("validated", delivery_node.getValidationState())
    self.tic()