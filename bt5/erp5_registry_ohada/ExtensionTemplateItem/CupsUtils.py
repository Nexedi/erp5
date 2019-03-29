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

import sys, os
import commands
from tempfile import NamedTemporaryFile
from zLOG import LOG, TRACE, WARNING, ERROR, INFO

def printFile(printer_name, file_path_to_print, use_ps_file=True, nb_copy=1):
  '''
    print a pdf on the printer defined in cups by printer name
  '''
  if not printer_name:
    LOG('printPDF :', ERROR, 'no printers defined in user preferences')
    return
  if use_ps_file:
    file_path_to_print = convertPdfIntoPs(file_path_to_print)

  if not os.path.exists('/usr/bin/lp'):
      raise ValueError("lp command is not installed")
  cmd = '/usr/bin/lp -d %s -n %s %s' % (printer_name, nb_copy,
      file_path_to_print)
  result = commands.getstatusoutput(cmd)
  if result[0] != 0:
      LOG('printPDF :', ERROR, 'lp command'\
          'failed with the following error message : \n%s' % result[1])

      # if we raise an error, test couln't be launch
      #raise ValueError, 'Error: lp command failed with the following'\
      #                  'error message : \n%s' % result[1]

  # XXX here, the tmp file can't be removed until printer have not finished to
  # print the pdf document. So currently, the temp file (a signed pdf) rest on
  # the server, this is a security and disk space problem.
  #os.remove(file_path_to_print)
  return "executed"

def convertPdfIntoPs(file_path_to_print):
  '''
    some printers can't handle direcly pdf but are able to handle ps format
    this method convert a pdf into a ps file
  '''
  ps_file = NamedTemporaryFile()
  ps_file_name = ps_file.name
  ps_file.close()


  if not os.path.exists('/usr/bin/pdf2ps'):
      raise ValueError("pdf2ps command is not installed")
  cmd = '/usr/bin/pdf2ps %s %s'%(file_path_to_print, ps_file_name)
  result = commands.getstatusoutput(cmd)
  if result[0] != 0:
      LOG('printPDF :', ERROR, 'pdf2ps (from ghostscript package) command'\
          'failed with the following error message : \n%s' % result[1])

  # delete the pdf file because it's not usefull to keep it
  if os.path.exists(file_path_to_print):
    os.remove(file_path_to_print)
  return ps_file_name

def getPrinterList(self):
  '''
    return the list of installed printers
  '''
  if not os.path.exists('/usr/bin/lpstat'):
      raise ValueError("lpstat command is not installed")
  cmd = '/usr/bin/lpstat -a'
  result = commands.getstatusoutput(cmd)
  if result[0] != 0:
      LOG('printPDF :', ERROR, 'lpstat command'\
          'failed with the following error message : \n%s' % result[1])

      # if we raise an error, test couln't be launch
      #raise ValueError, 'Error: lpstat command failed with the following'\
      #                  'error message : \n%s' % result[1]
  result_line_list = result[1].split('\n')
  printer_list = [x.split()[0] for x in result_line_list]
  return printer_list

def getPrinterItemList(self):
  '''
    return item list of printers
  '''
  printer_list = self.getPrinterList()
  if printer_list:
    printer_item_list = [[x, x] for x in printer_list]
    printer_item_list = [('',''),] + printer_item_list
    return printer_item_list
  return (('',''),)
