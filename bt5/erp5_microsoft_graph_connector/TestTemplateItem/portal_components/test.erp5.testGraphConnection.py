##############################################################################
#
# Copyright (c) 2002-2023 Nexedi SA and Contributors. All Rights Reserved.
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
    graph_connector = self.portal.portal_web_services.newContent(
        portal_type='Graph Connector',
        reference='test_reference',
        client_id='test_id',
        client_secret='test_secret',
        tenant_id='test_tenant_id',
        graph_url='https://graph.microsoft.com/v1.0')
    graph_connector.validate()
    self.tic()
    return graph_connector


  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    pass

  def test_connectionParameters(self):
    """
     Simple test to check creation of graph connector
    """
    graph_connector = self.create_web_service()
    client_id = graph_connector.getClientId()
    client_secret = graph_connector.getClientSecret()
    tenant_id = graph_connector.getTenantId()
    graph_url = graph_connector.getGraphUrl()
    self.assertEqual(client_id, "test_id")
    self.assertEqual(client_secret, "test_secret")
    self.assertEqual(tenant_id, "test_tenant_id")
    self.assertEqual(graph_url, 'https://graph.microsoft.com/v1.0')
