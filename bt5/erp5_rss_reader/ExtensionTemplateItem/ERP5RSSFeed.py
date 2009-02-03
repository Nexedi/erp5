##############################################################################
#
# Copyright (c) 2006-2007 Nexedi SA and Contributors. All Rights Reserved.
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
from DateTime import DateTime
import urllib2
import libxml2
import re
from zLOG import LOG


def getObjectStringList(xml_string, element_to_find = 'object'):
  """
    this function splits an ERP5 XML string into object
    string list, each object string is converted
    into utf-8 encoding and html entities are 
    translated into corresponding unicode code
  """
  rss_doc = libxml2.parseDoc(xml_string)
  return ['%s' % node for node in rss_doc.xpathEval('//%s' % element_to_find)]

def setTextContent(self):
  """
    Edit text_content
  """
  try:
    text_content = urllib2.urlopen(self.asURL()).read()
    try:
      text_content = unicode(text_content, "utf-8").encode("utf-8")
    except UnicodeDecodeError:
      text_content = unicode(text_content, "iso-8859-1").encode("utf-8")
  except IOError:
    text_content = None
  if text_content is not None:
    self.edit(text_content=text_content)

def setRSSItemProperties(self, rss_item):
  pass