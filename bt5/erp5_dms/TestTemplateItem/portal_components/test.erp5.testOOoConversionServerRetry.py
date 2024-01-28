##############################################################################
#
# Copyright (c) 2002-2018 Nexedi SA and Contributors. All Rights Reserved.
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

from erp5.component.test.testDms import DocumentUploadTestCase
from Products.ERP5Form.PreferenceTool import Priority


class TestOOoConversionServerRetry(DocumentUploadTestCase):
  def getBusinessTemplateList(self):
    business_template_list = ['erp5_core_proxy_field_legacy',
                            'erp5_jquery',
                            'erp5_full_text_mroonga_catalog',
                            'erp5_base',
                            'erp5_ingestion_mysql_innodb_catalog',
                            'erp5_ingestion',
                            'erp5_web',
                            'erp5_dms']
    return business_template_list

  def clearDocumentModule(self):
    self.abort()
    doc_module = self.portal.document_module
    doc_module.manage_delObjects(list(doc_module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.abort()
    activity_tool = self.portal.portal_activities
    activity_status = {m.processing_node < -1
                       for m in activity_tool.getMessageList()}
    if True in activity_status:
      activity_tool.manageClearActivities()

    self.clearDocumentModule()

  def afterSetUp(self):
    self.portal.portal_caches.clearAllCache()
    self.retry_count = 2

  def getDefaultSystemPreference(self):
    id_ = 'default_system_preference'
    tool = self.getPreferenceTool()
    try:
      pref = tool[id_]
    except KeyError:
      pref = tool.newContent(id_, 'System Preference')
      pref.setPriority(Priority.SITE)
      pref.enable()
    return pref


  def test_01_no_retry_for_no_network_issue(self):
    system_pref = self.getDefaultSystemPreference()
    system_pref.setPreferredDocumentConversionServerRetry(self.retry_count)
    self.tic()

    filename = 'monochrome_sample.tiff'
    file_ = self.makeFileUpload(filename)
    document = self.portal.document_module.newContent(portal_type='Text')
    document.edit(file = file_)
    message = document.Document_tryToConvertToBaseFormat()
    self.assertEqual(message.count('Error converting document to base format'), 1)



  def test_02_retry_for_network_issue(self):
    system_pref = self.getDefaultSystemPreference()
    saved_server_list = system_pref.getPreferredDocumentConversionServerUrlList()
    system_pref.setPreferredDocumentConversionServerRetry(self.retry_count)
    system_pref.setPreferredDocumentConversionServerUrlList(['https://broken.url'])
    self.tic()
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_)

    message = document.Document_tryToConvertToBaseFormat()
    self.assertEqual(message.count('broken.url: Connection refused'), self.retry_count + 1)
    system_pref.setPreferredDocumentConversionServerUrlList(saved_server_list)
    self.commit()

  def test_03_retry_for_socket_issue(self):
    system_pref = self.getDefaultSystemPreference()
    server_list = system_pref.getPreferredDocumentConversionServerUrlList()
    system_pref.setPreferredDocumentConversionServerRetry(self.retry_count)
    system_pref.setPreferredOoodocServerTimeout(1)
    self.tic()
    filename = 'TEST-en-002.doc'
    file_ = self.makeFileUpload(filename)
    document = self.portal.portal_contributions.newContent(file=file_)

    message = document.Document_tryToConvertToBaseFormat()
    if 'Socket Error: SSLError' in message:
      self.assertEqual(message.count('Socket Error: SSLError'), (self.retry_count + 1) * len(server_list))
