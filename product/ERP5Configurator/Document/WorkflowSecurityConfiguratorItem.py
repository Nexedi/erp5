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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Configurator.mixin.configurator_item import ConfiguratorItemMixin

class WorkflowSecurityConfiguratorItem(ConfiguratorItemMixin, XMLObject):
  """ Setup workflow for different roles. Use passed OO file. """

  meta_type = 'ERP5 Workflow Security Configurator Item'
  portal_type = 'Workflow Security Configurator Item'
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
                    , PropertySheet.DublinCore )

  def _checkConsistency(self, fixit=False, filter=None, **kw):
    return []
    if fixit:
      ## NOT TESTED
      business_configuration = self.getBusinessConfigurationValue()
      table_dict = business_configuration.ConfigurationTemplate_readOOCalcFile(self.filename)
      portal = self.getPortalObject()
      suffix = '_security'
      suffix_len = len(suffix)
      if self.filename[-suffix_len:] == suffix:
        workflow_id = self.filename[:-suffix_len]
      else:
        raise "NoValidName"

      # Configure state permission
      view_permission_list = ['View']
      access_permission_list = ['Access contents information']
      modify_permission_list = ['Modify portal content']
      add_content_permission_list = ['Add portal content']
      # Configure list of variable on the workflow
      permission_list = view_permission_list + \
                        access_permission_list + \
                        modify_permission_list + \
                        add_content_permission_list
      # Remove permission list
      workflow = portal.portal_workflow[workflow_id]
      workflow.delManagedPermissions(workflow.permissions)
      # Add new permission list
      for permission in permission_list:
        workflow.addManagedPermission(permission)
      # Configure state permission matrix
      state_list = table_dict['state']
      for state_config in state_list:
        state_id = state_config.pop('state')
        state = workflow.states[state_id]
        # Clean the state matrix
        for permission in permission_list:
          state.setPermission(permission, 0, [])
        # Update state matrix
        permission_dict = {x: [] for x in permission_list}
        for role, perm_symbol in state_config.items():
          managed_permission_list = []
          if 'A' in perm_symbol:
            managed_permission_list.extend(access_permission_list)
          if 'V' in perm_symbol:
            managed_permission_list.extend(view_permission_list)
          if 'C' in perm_symbol:
            managed_permission_list.extend(add_content_permission_list)
          if 'M' in perm_symbol:
            managed_permission_list.extend(modify_permission_list)
          for permission in managed_permission_list:
            permission_dict[permission].append(role.capitalize())
        for permission, roles in permission_dict.items():
          state.setPermission(permission, 0, roles)
        # XXX To be deleted
        #       for permission in permission_list:
        #         module.manage_permission(permission, ['Manager'], 0)

      # Configure transition guard
      transition_list = table_dict['transition']
      for transition_conf in transition_list:
        transition_id = transition_conf.pop('transition')
        transition = workflow.transitions[transition_id]
        guard = transition.getGuard()
        role_list = [x.capitalize() for x in transition_conf.keys()]
        role_string = ';'.join(role_list)
        guard.changeFromProperties({'guard_roles': role_string})
      # Update business template
      bt5_obj = business_configuration.getSpecialiseValue()
      template_workflow_id_list = list(bt5_obj.getTemplateWorkflowIdList())
      if workflow_id not in template_workflow_id_list:
        template_workflow_id_list.append(workflow_id)
      bt5_obj.edit(template_workflow_id_list=template_workflow_id_list,)
