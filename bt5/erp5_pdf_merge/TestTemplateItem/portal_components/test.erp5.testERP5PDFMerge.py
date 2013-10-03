##############################################################################
#
# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5OOo.tests.testDms import makeFileUpload

class TestERP5PDFMerge(ERP5TypeTestCase):
  def test_erp5_merge_pdf(self):
    document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('REF-en-001.pdf'))
    merged_pdf_data = self.portal.ERP5Site_mergePDFList(
      [document.getData(), document.getData()])
    merged_document = self.portal.document_module.newContent(
      portal_type='PDF',
      data=merged_pdf_data)
    self.assertEqual('2', merged_document.getContentInformation()['Pages'])

  def test_erp5_merge_pdf_start_on_recto(self):
    document = self.portal.portal_contributions.newContent(
      file=makeFileUpload('REF-en-001.pdf'))
    merged_pdf_data = self.portal.ERP5Site_mergePDFList(
      [document.getData(), document.getData()], start_on_recto=True)
    merged_document = self.portal.document_module.newContent(
      portal_type='PDF',
      data=merged_pdf_data)
    # there are four pages, because blank pages has been added so that the
    # second time, our document starts on a recto page.
    self.assertEqual('4', merged_document.getContentInformation()['Pages'])

