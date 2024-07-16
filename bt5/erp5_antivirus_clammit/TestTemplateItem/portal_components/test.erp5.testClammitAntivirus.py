##############################################################################
#
# Copyright (c) 2002-2024 Nexedi SA and Contributors. All Rights Reserved.
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

import mock

from erp5.component.document.ClammitConnector import ClammitConnector
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestClammitAntivirus(ERP5TypeTestCase):
  """
  When the bt5 erp5_antivirus_clammit is installed, documents
  that are marked suspect (workflow state, provided by erp5_antivirus)
  will be automatically submited to an antivirus scan, and then marked
  safe or infected.
  """

  _SANE_HTTP_STATUS_CODE = ClammitConnector._SANE_HTTP_STATUS_CODE
  _INFECTED_HTTP_STATUS_CODE = ClammitConnector._INFECTED_HTTP_STATUS_CODE

  def getResponseMock(self, expected_status_code):
    def _responseMock(*args, **kw):
      class Response:
        status_code = expected_status_code
      return Response()
    return _responseMock

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    portal = self.portal
    portal_web_services = portal.portal_web_services
    self.clammit_connector = portal_web_services.get("clammit_test_connector")
    if self.clammit_connector is None:
      self.clammit_connector = portal_web_services.newContent(
        id="clammit_test_connector",
        portal_type="Clammit Connector",
        reference="clammit_test_connector",
        url_string="https://localhost:3000/clammit",
        timeout=5,
      )

  @mock.patch("requests.request")
  def test_analyse_safe_document(self, requests_request_mock):
    requests_request_mock.side_effect = self.getResponseMock(self._SANE_HTTP_STATUS_CODE)

    # Create a file as user
    uf = self.getPortal().acl_users
    user = "someuser"
    uf._doAddUser(user, "", ["Author"], [])
    self.loginByUserName(user)
    document_value = self.portal.document_module.newContent(
      portal_type="File",
      data=b"hello_world",
    )
    document_value.setSuspect()

    self.login()
    self.tic()
    self.assertEqual(document_value.getScanState(), "safe")

  @mock.patch("requests.request")
  def test_analysed_infected_document(self, requests_request_mock):
    requests_request_mock.side_effect = self.getResponseMock(self._INFECTED_HTTP_STATUS_CODE)

    # Create a file as user
    uf = self.getPortal().acl_users
    user = "someuser"
    uf._doAddUser(user, "", ["Author"], [])
    self.loginByUserName(user)
    document_value = self.portal.document_module.newContent(
      portal_type="File",
      data=b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',
    )
    document_value.setSuspect()

    self.login()
    self.tic()
    self.assertEqual(document_value.getScanState(), "infected")