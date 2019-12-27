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

  # XXX do we need to protect this method?
  def getMappingDict(self, reverse=False):
    # Use volatile attributes for caching.
    try:
      if reverse:
        return self._v_reverse_mapping_dict
      else:
        return self._v_mapping_dict
    except AttributeError:
      mapping_dict = {}
      for line in self.getMappingPropertyList():
        f, t = [x.strip() for x in line.split('|', 1)]
        if reverse:
          if t[:1] == '-':
            f, t = t[1:], '-' + f
          else:
            f, t = t, f
          mapping_dict[f] = t
        else:
          mapping_dict[f] = t
      if reverse:
        self._v_reverse_mapping_dict = mapping_dict
      else:
        self._v_mapping_dict = mapping_dict
      return mapping_dict

  # XXX do we need to protect this method?
  def getMappedPropertyId(self, property, reverse=False):
    return self.getMappingDict(reverse=reverse).get(property, property)

  # Security should be handled by the target document not by the mapped
  # property document.
  security.declarePublic('getMappedProperty')
  def getMappedProperty(self, document, property):
    if property.endswith('_list'):
      property = property[:-5]
      getProperty = document.getPropertyList
    else:
      getProperty = document.getProperty
    mapping_dict = self.getMappingDict()
    mapped_property = mapping_dict.get(property, property)
    if mapped_property.startswith('-'):
      return -1 * getProperty(mapped_property[1:])
    else:
      return getProperty(mapped_property)

  # Security should be handled by the target document not by the mapped
  # property document.
  security.declarePublic('setMappedProperty')
  def setMappedProperty(self, document, property, value):
    if property.endswith('_list'):
      property = property[:-5]
      setProperty = document.setPropertyList
    else:
      setProperty = document.setProperty
    mapping_dict = self.getMappingDict(reverse=True)
    mapped_property = mapping_dict.get(property, property)
    if mapped_property.startswith('-'):
      return setProperty(mapped_property[1:], -1 * value)
    else:
      return setProperty(mapped_property, value)
