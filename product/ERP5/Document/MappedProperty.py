##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject

class MappedProperty(XMLObject):
  """
  Mapped Property object describes how properties or categories are
  mapped, eg. use source as destination, use destination as source, use
  quantity as -quantity, etc.
  """
  meta_type = 'ERP5 Mapped Property'
  portal_type = 'Mapped Property'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (PropertySheet.Base,
                     PropertySheet.SimpleItem,
                     PropertySheet.CategoryCore,
                     PropertySheet.MappedProperty)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMappedProperty')
  def getMappedProperty(self, document, property):
    if property.endswith('_list'):
      property = property[:-5]
      getProperty = document.getPropertyList
    else:
      getProperty = document.getProperty
    mapping_dict = dict([[x.strip() for x in x.split('|')] \
                         for x in self.getMappingPropertyList()])
    mapped_property = mapping_dict.get(property, property)
    if mapped_property.startswith('-'):
      return -1 * getProperty(mapped_property[1:])
    else:
      return getProperty(mapped_property)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'setMappedProperty')
  def setMappedProperty(self, document, property, value):
    if property.endswith('_list'):
      property = property[:-5]
      setProperty = document.setPropertyList
    else:
      setProperty = document.setProperty
    mapping_dict = {}
    for x in self.getMappingPropertyList():
      from_property, to_property = [x.strip() for x in x.split('|')]
      if to_property.startswith('-'):
        mapping_dict[to_property[1:]] = '-%s' % from_property
      else:
        mapping_dict[to_property] = from_property
    mapped_property = mapping_dict.get(property, property)
    if mapped_property.startswith('-'):
      return setProperty(-1 * value)
    else:
      return setProperty(value)
