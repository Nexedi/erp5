##############################################################################
#
# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
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
import base64
import six
from lxml import etree
from difflib import unified_diff
from erp5.component.module.DiffUtils import DiffFile

def diffXML(xml_plugin="", xml_erp5="", gid="", html=True):
  if isinstance(xml_erp5, six.text_type):
    xml_erp5 = xml_erp5.encode('utf-8')
  if xml_plugin == "":
    xml_plugin="<object>Not found</object>"
  if xml_erp5 == "":
    xml_erp5="<object>Not found</object>"
  try:
    xml = etree.fromstring(xml_erp5)
    xml_erp5 = etree.tostring(xml, pretty_print=True, encoding="utf-8")
  except etree.XMLSyntaxError:  # pylint:disable=catching-non-exception
    pass

  if isinstance(xml_plugin, six.text_type):
    xml_plugin = xml_plugin.encode('utf-8')
  try:
    xml = etree.fromstring(xml_plugin)
    xml_plugin = etree.tostring(xml, pretty_print=True, encoding="utf-8")
  except etree.XMLSyntaxError:  # pylint:disable=catching-non-exception
    pass

  diff_list = list(unified_diff(xml_plugin.split('\n'), xml_erp5.split('\n'), tofile="erp5 xml", fromfile="plugin xml", lineterm=''))
  if diff_list:
    diff_msg = '\n\nXML Diff :\n'
    if gid:
      diff_msg = '\n\nXML Diff for %s:\n' % base64.b16decode(gid)
    diff_msg += '\n'.join(diff_list)
    if html:
      return DiffFile(diff_msg).toHTML()
    return diff_msg
  return 'No diff'
