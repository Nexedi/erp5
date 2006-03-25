#!/usr/bin/python

##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kevin DELDYCKE    <kevin@nexedi.com>
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
from xml.dom import Node
from xml.dom.ext import PrettyPrint
from xml.dom.ext.reader import PyExpat




def usage():
  print """   Usage : xml_beautifier file_to_beautify.xml
   Description : this script indent a messy xml file.
"""



def getFileContent(file_path):
  # Verify that the file exist
  if not os.path.isfile(file_path):
    print "ERROR: " + file_path + " doesn't exist."
    return None

  # Get file content
  file_path = os.path.abspath(file_path)
  file_object = open(file_path, 'r')

  return file_object.read()



def getXmlDom(xml_string):
  # Create the PyExpat reader
  reader = PyExpat.Reader()

  # Create DOM tree from the xml string
  dom_tree = reader.fromString(xml_string)

  return dom_tree.documentElement



def writePrettyXml(dom_tree, file_path):
  # Save the file in the current folder
  out_path = os.path.abspath(file_path)
  out = open(out_path, 'w')

  # Print out the result
  PrettyPrint(dom_tree, out)



if __name__ == "__main__":

  # Get all parameters
  if len(sys.argv) == 2:
    xml_file = sys.argv[1]
  else:
    usage()
    sys.exit()

  # Normalize path
  xml_file = os.path.abspath(xml_file)

  xml_string = getFileContent(xml_file)
  if xml_string == None:
    sys.exit()

  dom_tree = getXmlDom(xml_string)

  writePrettyXml(dom_tree, xml_file)