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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem


@zope.interface.implementer(IConfiguratorItem)
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

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore )

  def _checkConsistency(self, fixit=False, **kw):
    portal = self.getPortalObject()

    # Support adding new property sheet to portal type information.
    # arguments:
    #  * target_portal_type
    #  * add_propertysheet_list
    portal_type_value = portal.portal_types[self.target_portal_type]
    property_sheet_list = portal_type_value.getTypePropertySheetList()
    extra_property_sheet_list = []
    for name in self.add_propertysheet_list:
      if name not in property_sheet_list:
        extra_property_sheet_list.append(name)
    # TODO: This class must support many other portal types features.
    business_template_value = self.getBusinessConfigurationValue().getSpecialiseValue()
    if extra_property_sheet_list:
      if fixit:
        portal_type_value.setTypePropertySheetList(
          property_sheet_list + extra_property_sheet_list,
        )
        business_template_value.edit(
          template_portal_type_property_sheet_list=list(
            business_template_value.getTemplatePortalTypePropertySheetList()
          ) + [
            '%s | %s' % (self.target_portal_type, name)
            for name in extra_property_sheet_list
          ],
        )
      return [
        self._createConstraintMessage(
          'Associate Property Sheets %r to %r in %r' % (
            extra_property_sheet_list,
            self.target_portal_type,
            business_template_value.getTitle(),
          )
        )
      ]
    return []
