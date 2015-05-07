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

  is_selected = 0 # for checkerbox (True 1 /False 0)

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

  def getPermissionRole(self):
    permission = 'None'
    role = 'None'
    if self.is_selected == 1:
      permission_id = int(self.id.split('_')[1])
      role_id = int(self.id.split('_')[2])
      # zwj: make sure here gets the right coordinates
      workflow = self.getParent().getParent()
      permission_list = sorted(workflow.getManagedPermissionList())
      role_list = workflow.getRoleList()
      permission = permission_list[permission_id]
      role = role_list[role_id]
      # zwj: check the name of the role and permission is the one we want
    if role == 'None':
      role = ['Manager']
    return permission, role
