##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
#                    Wenjie ZHENG <wenjie.zheng@tiolive.com>
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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from zLOG import LOG, ERROR, DEBUG, WARNING

class PermissionRoles(XMLObject):
  """
  Permission role matrix cell unit,
  Used to assign a role to a permission.
  """

  meta_type = 'ERP5 PermissionRoles'
  portal_type = 'PermissionRoles'
  add_permission = Permissions.AddPortalContent
  isIndexable = ConstantGetter('isIndexable', value=False)
  selected = 0 # checkerbox

  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
             PropertySheet.Base,
             PropertySheet.XMLObject,
             PropertySheet.CategoryCore,
             PropertySheet.DublinCore,
             PropertySheet.State,)

  security.declarePrivate('getPermissionRole')
  def getPermissionRole(self):
    permission = 'None'
    role = 'None'
    if self.selected == 1:
      permission_id = int(self.id.split('_')[1])
      role_id = int(self.id.split('_')[2])
      # zwj: make sure here gets the right coordinates
      workflow = self.getParentValue().getParentValue()
      permission_list = sorted(workflow.getWorkflowManagedPermissionList())
      role_list = workflow.getManagedRoleList()
      permission = permission_list[permission_id]
      role = role_list[role_id]
      # zwj: check the name of the role and permission is the one we want
    if role == 'None':
      role = ['Manager']
    return permission, role

  def _getPermissionIndex(self):
    return int(self.id[len(self.base_id+'_'):].split('_')[0])

  def _getRoleIndex(self):
    return int(self.id[len(self.base_id+'_'):].split('_')[1])

  def _getPermissionOrRole(self, is_role=False):
    # we want to get the permission or role from its index,
    # so we want the retrieve the key of the dict which is like:
    # self.index[cell_prefix][index] = {'Some Role Or Permission': 1,
    #                                   'Some Other One': 0, ...}
    if is_role:
      cell_permission_or_role_index = self._getRoleIndex()
    else:
      cell_permission_or_role_index = self._getPermissionIndex()
    index = int(is_role)
    for key, value in self.index[self.base_id][index].items():
      if cell_permission_or_role_index == value:
        return key
    raise ValueError('No key found for value %s.' % value)

  def _getPermission(self):
    return self._getPermissionOrRole(is_role=False)

  def _getRole(self):
    return self._getPermissionOrRole(is_role=True)

  def _setSelected(self, value):
    """
    edit the parent state's permission/role dict to reflect current cell selection (selected) status
    """

    state = self.getParentValue()
    cell_range = state.getCellRange()

    cell_permission = self._getPermission()
    cell_role = self._getRole()

    # update the state permission structure to take into account
    # the selection/non-selection of this cell
    roles = state.getStatePermissionRolesDict()[cell_permission]
    acquired = isinstance(roles, tuple)
    roles = list(set(roles))
    if value and (cell_role not in roles):
      roles.append(cell_role)
      state.setPermission(cell_permission, acquired, roles)
    if (not value) and (cell_role in roles):
      roles.remove(cell_role)
      state.setPermission(cell_permission, acquired, roles)
