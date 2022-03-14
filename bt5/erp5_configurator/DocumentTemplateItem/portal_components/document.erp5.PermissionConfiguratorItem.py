##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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
class PermissionConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Set permission matrix on module."""

  meta_type = 'ERP5 Permission Configurator Item'
  portal_type = 'Permission Configurator Item'
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
    template_module_id_list = []
    error_list = []
    module_permissions_map = {}
    business_configuration = self.getBusinessConfigurationValue()
    sheets_dict = business_configuration.ConfigurationTemplate_readOOCalcFile(\
                           self.filename)
    for module_id, permissions in sheets_dict.items():
      module_permissions = {}
      for permission in permissions:
        roles = []
        permission_name = permission.pop('permission')
        for role, checked in permission.items():
          if checked == '1':  roles.append(role)
        module_permissions[permission_name] = roles
      # add to module map
      module_permissions_map[module_id] = module_permissions

    # set permissions in fake site
    portal = self.getPortalObject()
    for module_id, permissions_map in module_permissions_map.items():
      if permissions_map != {}:
        template_module_id_list.append(module_id)
        module = portal[module_id]
        for permission_name, roles in permissions_map.items():
          # we must alway include additionally 'Manager' and 'Owner'
          roles.extend(['Manager', 'Owner'])
          if fixit:
            module.manage_permission(permission_name, tuple(roles), 0)
          error_list.append(self._createConstraintMessage(
            '%s should be set to %s' % (','.join(roles), module.getId())))

    # add customized module to customer's bt5
    if len(template_module_id_list) and fixit:
      bt5_obj = business_configuration.getSpecialiseValue()
      bt5_obj.setTemplateModuleIdList(template_module_id_list)

    return error_list
