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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem

class PortalTypeConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """Configure Portal Type."""

  meta_type = 'ERP5 Portal Type Configurator Item'
  portal_type = 'Portal Type Configurator Item'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(IConfiguratorItem)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    portal = self.getPortalObject()

    # Support adding new property sheet to portal type information.
    # arguments:
    #  * target_portal_type
    #  * add_propertysheet_list
    type_information = getattr(portal.portal_types, self.target_portal_type)
    for name in self.add_propertysheet_list:
      if not name in type_information.property_sheet_list:
        new_property_sheet_list = list(type_information.property_sheet_list)
        new_property_sheet_list.append(name)
        type_information.property_sheet_list = tuple(new_property_sheet_list)

    business_configuration = self.getBusinessConfigurationValue()
    bt5_obj = business_configuration.getSpecialiseValue()

    old_property_sheet_list = bt5_obj.getTemplatePortalTypePropertySheetList()
    new_property_sheet_list = (list(old_property_sheet_list) +
                              ['%s | %s' % (self.target_portal_type, name)
                                for name in self.add_propertysheet_list]
                              )
    if fixit:
      bt5_obj.edit(
        template_portal_type_property_sheet_list=new_property_sheet_list)
    #
    # TODO:This class must support many other features we can use in ZMI.
    #

    return ['Property Sheets configuration should be added in %s' % \
        bt5_obj.getTitle(),]
