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
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.ConfiguratorItemMixin import ConfiguratorItemMixin
from erp5.component.interface.IConfiguratorItem import IConfiguratorItem
from zLOG import LOG, INFO


@zope.interface.implementer(IConfiguratorItem)
class RoleConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup role per module basis. """

  meta_type = 'ERP5 Role Configurator Item'
  portal_type = 'Role Configurator Item'
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
    error_list = [self._createConstraintMessage('Roles should imported and created')]
    if fixit:
      business_configuration = self.getBusinessConfigurationValue()
      object_list = business_configuration.ConfigurationTemplate_readOOCalcFile(self.filename)
      portal = self.getPortalObject()

      portal_type_dict = {}
      # we may pass some override dynamic values from outside
      # Example:we post 'group_id' and in column we have it then
      # it will be replaced with value if not configuration file matters
      dynamic_values = dict(group_id = getattr(aq_base(self), 'group_id', None),
                            function_id = getattr(aq_base(self), 'function_id', None),
                            site_id = getattr(aq_base(self), 'site_id', None),)
      for oo_module_dict in object_list:
        mod_conf_list = []
        portal_type = oo_module_dict.pop('portal_type')
        for category, role_list_string in oo_module_dict.items():
          # passed from outside (it has higher priority than configuration file)
          category = dynamic_values.get(category, category)
          title = category.replace('/', '_')
          role_name_list = [x.strip() for x in role_list_string.split(';')]
          role_category_list = [category]
          conf_dict =  {'title': title,
                        'description': 'Configured by ERP5 Configurator',
                        'role_name_list': role_name_list,
                        'role_category_list': role_category_list}

          mod_conf_list.append(conf_dict)
        portal_type_dict[portal_type] = mod_conf_list
      ## Update fake site
      # XXX rafael: improve this, the ignore list is quite ugly.
      ignore_list = []
      portal_type_id_list = portal.portal_types.objectIds()
      for portal_type, role_list in portal_type_dict.items():
        for role_dict in role_list:
          if portal_type in portal_type_id_list:
            portal.portal_types[portal_type].newContent(portal_type='Role Information', \
                                                        **role_dict)
          else:
            ignore_list.append(portal_type)
            LOG("CONFIGURATOR", INFO, "Fail to define Roles for %s" % portal_type)

      ## Update BT5

      bt5_obj = business_configuration.getSpecialiseValue()
      # keep existing roles definition (from previous configuration saves)
      for existing_type in bt5_obj.getTemplatePortalTypeRoleList():
        portal_type_dict[existing_type] = 1
      bt5_obj.edit(template_portal_type_role_list=[i for i in portal_type_dict.keys() if i not in ignore_list])

    return error_list
