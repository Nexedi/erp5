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

import warnings
from erp5.component.test.testDms import DocumentUploadTestCase


original_warnings_showwarnings = warnings.showwarning


class TestERP5PDFMerge(DocumentUploadTestCase):

  def test_showwarning_issue(self):
    """
    We should not let PdfFileReader overwrite warnings.showwarning method because we already do it in ERP5
    https://github.com/mstamy2/PyPDF2/blob/18a2627adac13124d4122c8b92aaa863ccfb8c29/PyPDF2/pdf.py#L1129
    """
    self.assertEqual(warnings.showwarning, original_warnings_showwarnings)
    document = self.portal.portal_contributions.newContent(
      file=self.makeFileUpload('REF-en-001.pdf'))
    merged_pdf_data = self.portal.ERP5Site_mergePDFList(
      [document.getData(), document.getData()])
    self.portal.document_module.newContent(
      portal_type='PDF',
      data=merged_pdf_data)
    self.tic()
    self.assertEqual(warnings.showwarning, original_warnings_showwarnings)

  def test_erp5_merge_pdf(self):
    document = self.portal.portal_contributions.newContent(
      file=self.makeFileUpload('REF-en-001.pdf'))
    merged_pdf_data = self.portal.ERP5Site_mergePDFList(
      [document.getData(), document.getData()])
    merged_document = self.portal.document_module.newContent(
      portal_type='PDF',
      data=merged_pdf_data)
    self.assertEqual('2', merged_document.getContentInformation()['Pages'])

  def test_erp5_merge_pdf_start_on_recto(self):
    document = self.portal.portal_contributions.newContent(
      file=self.makeFileUpload('REF-en-001.pdf'))
    merged_pdf_data = self.portal.ERP5Site_mergePDFList(
      [document.getData(), document.getData()], start_on_recto=True)
    merged_document = self.portal.document_module.newContent(
      portal_type='PDF',
      data=merged_pdf_data)
    # there are four pages, because blank pages has been added so that the
    # second time, our document starts on a recto page.
    self.assertEqual('4', merged_document.getContentInformation()['Pages'])

