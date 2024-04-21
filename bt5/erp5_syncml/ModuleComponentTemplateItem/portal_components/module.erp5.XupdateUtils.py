##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import six
from erp5.component.module.XMLSyncUtils import XMLSyncUtilsMixin
from xml.dom.ext.reader.Sax2 import FromXml  # pylint:disable=no-name-in-module,import-error

class XupdateUtils(XMLSyncUtilsMixin):
  """
  This class contains method specific to xupdate xml,
  this is the place where we should parse xupdate data.
  """

  def applyXupdate(self, object=None, xupdate=None, conduit=None, force=0, **kw): # pylint: disable=redefined-builtin
    """
    Parse the xupdate and then it will call the conduit
    """
    conflict_list = []
    if isinstance(xupdate, six.string_types):
      xupdate = FromXml(xupdate)

    for subnode in xupdate:
      if subnode.xpath('name()') in self.XUPDATE_INSERT_OR_ADD:
        conflict_list.extend(conduit.addNode(xml=subnode, object=object, \
                                         force=force, **kw))
      elif subnode.xpath('name()') in self.XUPDATE_DEL:
        conflict_list.extend(conduit.deleteNode(xml=subnode, object=object, \
                                         force=force, **kw))
      elif subnode.xpath('name()') in self.XUPDATE_UPDATE:
        conflict_list.extend(conduit.updateNode(xml=subnode, object=object, \
                                         force=force, **kw))
    return conflict_list


