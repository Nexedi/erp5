##############################################################################
#
# Copyright (c) 2002-2008 Nexedi SA and Contributors. All Rights Reserved.
#               Nicolas Delaby <nicolas@nexedi.com>
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

import os
from urllib import urlencode
import tempfile
from DateTime import DateTime
from zLOG import LOG
barcode = 'barcode'
ps2pdf = 'ps2pdf -sPAPERSIZE=a4'
lp =  'lp'

def escapeString(string):
  #Barcode can accept only ASCII
  string = str(unicode(str(string), 'utf-8'))
  #Escape
  string = string.replace('"', '\\"')
  return string

def printBarcodeSheet(self, sheet_number=1, input_list=[], test=False):
  unit = 'mm'
  code = self.getCodingType() or 'code128'
  row_number = self.getRowNumber() or 0
  column_number = self.getColumnNumber() or 0
  page_left_margin = self.getPageLeftMargin() or 10
  page_bottom_margin = self.getPageBottomMargin() or 10
  page_right_margin = self.getPageRightMargin() or 10
  page_top_margin = self.getPageTopMargin() or 10
  page_height = self.getPageHeight() or 210
  page_width = self.getPageWidth() or 297
  horizontal_padding = self.getHorizontalPadding() or 0
  vertical_padding = self.getVerticalPadding() or 0

  def getPdfOutput(self, ps_file_path, file_name='ReferenceSheet_%s' % DateTime().strftime('%d-%m-%Y_%Hh%M.pdf')):
    #Return PS as PDF
    suffix= '.pdf'
    tempdir = tempfile.tempdir
    tempfile.tempdir = '/tmp'
    new_pdf_file_path = tempfile.mktemp(suffix)
    tempfile.tempdir = tempdir
    ps2pdf_command = '%s %s %s' % (ps2pdf, ps_file_path, new_pdf_file_path)
    ret = os.system(ps2pdf_command)
    if ret != 0:
      raise RuntimeError('PS Conversion Failed')
    file = open(new_pdf_file_path, 'rb')
    result = file.read()
    file_size = len(result)
    file.close()
    self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/pdf')
    self.REQUEST.RESPONSE.setHeader('Content-Length', file_size)
    self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename="%s"' % (file_name))
    return result
  suffix= '.txt'
  tempdir = tempfile.tempdir
  tempfile.tempdir = '/tmp'
  new_txt_file_path = tempfile.mktemp(suffix)
  tempfile.tempdir = tempdir
  if test:
    #Fake list
    input_list = os.linesep.join(['TEST%s' % str(b).zfill(8) for b in range(1111111,  1111111 + ( row_number * column_number * sheet_number ))])
  elif input_list not in ('', None):
   if not isinstance(input_list, list):
     input_list = os.linesep.join(map(escapeString, input_list.split(os.linesep)))
   else:
     input_list = os.linesep.join(input_list)
  else:
    input_list = os.linesep.join(['%s' % str(self.portal_ids.generateNewId(id_group='barcode')).zfill(12) for b in range( row_number * column_number * sheet_number )])
  text_command = 'echo "%s" > %s' % (input_list, new_txt_file_path)
  ret = os.system(text_command)
  if ret != 0:
    raise RuntimeError('File Creation Failed')

  if horizontal_padding not in ('', None) and vertical_padding not in ('', None):
    margin = '%sx%s' % (horizontal_padding, vertical_padding)
  else:
    margin = ''
  if page_height not in ('', None) and page_width not in ('', None):
    pagesize = '%sx%smm' % (page_width, page_height)
  table_margin = []
  if page_left_margin not in ('', None):
    table_margin.append('+%s' % (page_left_margin))
  if page_bottom_margin not in ('', None):
    table_margin.append('+%s' % (page_bottom_margin))
  else:
    table_margin.append('+%s' % (page_left_margin))
  if page_right_margin not in ('', None):
    table_margin.append('-%s' % (page_right_margin))
  if page_top_margin not in ('', None):
    table_margin.append('-%s' % (page_top_margin))

  argument_list = []
  encoding = '-e %s' % (code)
  argument_list.append(encoding)
  for option, argument in (('-m', margin),
                          ('-p', pagesize),
                          ('-u', unit)):
    if argument not in ('', None):
      argument_list.append('%s %s'% (option, argument))
  if row_number not in (0, None) and column_number not in (0, None):
          argument_list.append('-t %sx%s%s' % (column_number, row_number,
                                               ''.join(table_margin)))

  argument_list.append('-i %s' % (new_txt_file_path))

  barcode_command = '%s %s' % (barcode, ' '.join(argument_list))

  #Creation of ps file
  suffix= '.ps'
  tempdir = tempfile.tempdir
  tempfile.tempdir = '/tmp'
  new_ps_file_path = tempfile.mktemp(suffix)
  tempfile.tempdir = tempdir

  barcode_command += ' -o %s ' %(new_ps_file_path)
  ret = os.system(barcode_command)
  if ret != 0:
    raise RuntimeError('Barcode PS File Creation Failed')
  if test:
    return getPdfOutput(self, new_ps_file_path, file_name='TestReferenceSheet.pdf')

  return getPdfOutput(self, new_ps_file_path)

