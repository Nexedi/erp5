# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SA and Contributors. All Rights Reserved.
#                Aurélien Calonne <aurel@nexedi.com>
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

from App.Extensions import getBrain
from lxml import etree
from zLOG import LOG, ERROR

SEPARATOR = '\n'

NodeBrain = getBrain('TioSafeBrain', 'Node', reload=1)
TransactionBrain = getBrain('TioSafeBrain', 'Transaction', reload=1)

class OscommerceNode(NodeBrain):

  def __init__(self, *args, **kw):
    NodeBrain.__init__(self, *args, **kw)
    # country property is used in gid computation of organisation
    # transform it to category as soon as possible
    if getattr(self, 'country', None) is not None:
      try:
        self.country = self.getIntegrationSite().getCategoryFromMapping(
          category = 'Country/%s' % self.country, create_mapping=True,
          create_mapping_line=True,
          ).split('/', 1)[-1]
      except ValueError, msg:
        LOG("OscommerceBrain.OscommerceNode.__init__", ERROR, "Getting category for %s raise with msg = %s" %(value, msg))
        self.country = ""


class Organisation(OscommerceNode):

  def _asXML(self):
    if getattr(self, 'country', None) is not None and not len(self.country):
      # Mapping is not done
      return ""

    xml = ""
    node = etree.Element('node', type="Organisation")

    self._setTagList(self, node, ['title',])
    self._generateCoordinatesXML(node)

    xml += etree.tostring(node, pretty_print=True, encoding='utf-8')
    #LOG('Node asXML returns : %s' %(xml,), 300, "")
    return xml