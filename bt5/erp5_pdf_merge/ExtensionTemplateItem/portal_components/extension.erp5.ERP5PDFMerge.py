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


def mergePDFList(self, pdf_data_list, start_on_recto=False):
  """Merge multiple PDFs in a new PDF.

  Both input and output are raw PDF data as string, so pdf_data_list must be
  a list of strings, and the output is the merged pdf as a string.
  If "start_on_recto" is set to true, some blank pages will be added in order
  to have each PDF as the recto page. This is useful if you have to print the
  merged pdf in recto/verso mode.
  """
  from six.moves import cStringIO as StringIO
  from PyPDF2 import PdfFileWriter, PdfFileReader

  output = PdfFileWriter()

  for pdf_data in pdf_data_list:
    if pdf_data:
      pdf_reader = PdfFileReader(StringIO(pdf_data))
      page_count = pdf_reader.getNumPages()
      for page in range(page_count):
        output.addPage(pdf_reader.getPage(page))
      if start_on_recto and page_count % 2:
        output.addBlankPage()

  outputStream = StringIO()
  output.write(outputStream)
  return outputStream.getvalue()
