##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    TAHARA Yusei <yusei@nexedi.com>
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

from warnings import warn
import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Message import translateString
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class ValueConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """Create documents of given portal type in given path."""

  meta_type = 'ERP5 Value Configurator Item'
  portal_type = 'Value Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.ConfiguratorItem )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    portal = self.getPortalObject()
    error_list = []
    for  configuration_dict in iter(self.getConfigurationListList()):
      search_dict, relative_path, property_value_dict = map(
       configuration_dict.get,('search_dict', 'relative_path',
                               'property_value_dict'))
      if search_dict is not None:
        document = self.portal_catalog.getResultValue(**search_dict)
      else:
        document = portal
      if relative_path is not None and document is not None:
        document = document.unrestrictedTraverse(relative_path, None)
      if document is not None:
        for property_id, value in property_value_dict.items():
          if document.getProperty(property_id) != value:
            error_list.append(self._createConstraintMessage(
              '%s: property "%s" should be changed to value "%s"' %(
                                     document.getPath(), property_id, value)))
          if fixit:
            document.setProperty(property_id, value)

    return error_list
