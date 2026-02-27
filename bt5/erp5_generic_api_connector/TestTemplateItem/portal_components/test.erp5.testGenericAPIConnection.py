##############################################################################
#
# Copyright (c) 2002-2025 Nexedi SA and Contributors. All Rights Reserved.
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

class Test(ERP5TypeTestCase):
  def create_web_service(self):
    api_connector = self.portal.portal_web_services.newContent(
      portal_type='Generic API Connector',
      reference='test_reference',
      api_token='test_token',
      url_string='test_url',
    )
    api_connector.validate()
    self.tic()
    return api_connector

  def afterSetUp(self):
    pass

  def test_connectionParameters(self):
    """Simple test to check creation of api connector"""
    api_connector = self.create_web_service()
    token = api_connector.getApiToken()
    url = api_connector.getUrlString()
    reference = api_connector.getReference()

    self.assertEqual(token, "test_token")
    self.assertEqual(url, "test_url")
    self.assertEqual(reference, "test_reference")