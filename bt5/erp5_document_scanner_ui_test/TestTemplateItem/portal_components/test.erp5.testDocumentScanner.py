##############################################################################
#
# Copyright (c) 2002-2020 Nexedi SA and Contributors. All Rights Reserved.
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

import json
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class DocumentScanner(ERP5TypeTestCase):
  """
  Document Scanner Test Case
  """

  def getTitle(self):
    return "Test Document Scanner"

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """

    id_list = [o.getId() for o in self.portal.portal_catalog(
      reference="document_scanner_js",
      portal_type="Active Process")]
    if id_list:
      self.portal.portal_activities.manage_delObjects(ids=id_list)
    self.tic()

  def test_remove_outdated_active_process(self):
    data_dict = json.loads(
      self.portal.Base_getDocumentScannerDefaultBackendDataAsJSON())
    self.assertEqual(data_dict["image_list"], [])
    active_process_url = data_dict["active_process"]
    active_process = self.portal.restrictedTraverse(str(active_process_url))
    self.assertEqual(active_process.getResultList(), [])
    data_png = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA"
      "AEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAAWgm"
       "WQ0AAAAASUVORK5CYII=")
    response = self.portal.Base_storeNewImageCropped(data_png,
                                                     active_process.getRelativeUrl())
    first_uuid = json.loads(response)["uuid"]
    self.assertIn(first_uuid, [r.reference for r in active_process.getResultList()])
    response = self.portal.Base_storeNewImageCropped(data_png,
                                                     active_process.getRelativeUrl())
    second_uuid = json.loads(response)["uuid"]
    self.assertIn(second_uuid, [r.reference for r in active_process.getResultList()])
    self.assertIn(first_uuid, [r.reference for r in active_process.getResultList()])
    self.tic()
    req = self.portal.erp5_sql_connection.manage_test
    req("update catalog set modification_date='{date}' where uid={uid}".format(
      date=(DateTime()-6).toZone('UTC'),
      uid=active_process.getUid()))
    self.portal.portal_alarms.remove_outdated_document_scanner_active_process.activeSense()
    self.tic()
    self.assertNotIn(active_process.getId(), list(self.portal.portal_activities.objectIds()))
