##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
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

from lxml import etree
from zLOG import LOG
from Products.ERP5SyncML.XMLSyncUtils import getConduitByName
from difflib import unified_diff
from Products.ERP5Type.DiffUtils import DiffFile


def callAddNodeOnConduit(self, conduit_id, uid):
  obj = self.getPortalObject().portal_catalog.getObject(uid)
  conduit = getConduitByName(conduit_id)
  if obj.getPortalType() in ('Person', 'Organisation'):
    xml = obj.Node_asTioSafeXML()
  elif obj.getPortalType() in ('Product', 'Service'):
    xml = obj.Resource_asTioSafeXML()
  conduit.addNode(xml=etree.fromstring(xml), object=self)


def diffXML(xml_plugin="", xml_erp5="", html=True):
  diff_list = list(unified_diff(xml_plugin.split('\n'), xml_erp5.split('\n'), tofile="erp5 xml", fromfile="plugin xml", lineterm=''))
  if len(diff_list) != 0:
    diff_msg = '\n\nTioSafe XML Diff :\n'
    diff_msg += '\n'.join(diff_list)
    if html:
      return DiffFile(diff_msg).toHTML()
    return diff_msg
  else:
    return 'No diff'

