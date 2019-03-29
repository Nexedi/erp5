##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from zLOG import LOG, TRACE, WARNING, ERROR, INFO
import commands
from tempfile import NamedTemporaryFile
from Products.ERP5.Document.File import _unpackData


def addBackgroundOnPdfFile(orginal_pdf, background_pdf):
  '''This method apply the background on all pages of the original pdf file
     Pdftk uses only the first page from the background_pdf_file and
     applies it to every page of the orginal_pdf_file. This page is
     scaled and rotated as needed to fit the input page.'''
  tmp_pdf_file_name = NamedTemporaryFile().name
  
  # create two temporary files to give to pdftk command
  orginal_pdf_file = NamedTemporaryFile() 
  background_pdf_file = NamedTemporaryFile()

  # saving content
  orginal_pdf_file.write(orginal_pdf)
  orginal_pdf_file.seek(0) 

  # saving content
  background_pdf_file.write(_unpackData(background_pdf.data))
  background_pdf_file.seek(0) 

  try:
    result = commands.getstatusoutput('pdftk %s background %s output %s' % \
          (orginal_pdf_file.name, background_pdf_file.name, tmp_pdf_file_name))

    # check that the command has been done succeful
    if result[0] != 0:
      LOG('addBackgroundOnPdfFile :', ERROR, 'pdftk command'\
          'failed with the following error message : \n%s' % result[1])

      # delete created pdf before raise an error
      #os.remove(tmp_pdf_file_name)
      orginal_pdf_file.close()
      background_pdf_file.close()

      raise ValueError('Error: pdftk command failed with the following'\
                        'error message : \n%s' % result[1])

  finally:
    background_pdf_file.close()
    orginal_pdf_file.close()
  
  return tmp_pdf_file_name 


def mergePDF(pdf_document_list):
  '''Merge all pdf in the pdf_document_list in one using pdftk and return it'''

  from warnings import warn
  warn("mergePDF is deprecated, use erp5_pdf_merge business template instead")
  tmp_pdf_list = []
  # create as tmp file as there is pdf_documents
  for pdf_document in pdf_document_list:
    tmp_pdf_file = NamedTemporaryFile()
    # saving content
    tmp_pdf_file.write(_unpackData(pdf_document.data))
    tmp_pdf_file.seek(0)
    tmp_pdf_list.append(tmp_pdf_file)

  # create a tmp file to put the resulting pdf file
  result_file = NamedTemporaryFile()
  result = None

  try:
    name_list = [x.name for x in tmp_pdf_list]
    cmd = 'pdftk %s cat output %s' % (' '.join(name_list), result_file.name)
    result = commands.getstatusoutput(cmd)

    # check that the command has been done succeful
    if result[0] != 0:
      LOG('mergePDF :', ERROR, 'pdftk command'\
          'failed with the following error message : \n%s' % result[1])

      # delete created pdf before raise an error
      for tmp_file in tmp_pdf_list:
        tmp_file.close()

      raise ValueError('Error: pdftk command failed with the following'\
                        'error message : \n%s' % result[1])

    else:
      # going to the begining of the input file
      result_file.seek(0)
      # put content in variable
      result=result_file.read()

  finally:
    for tmp_file in tmp_pdf_list:
      tmp_file.close()
    # close result file
    result_file.close()

  return result
