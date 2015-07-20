##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2015 Wenjie ZHENG <wenjie.zheng@tiolive.com>
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
from Persistence import PersistentMapping
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.XMLObject import XMLObject
from zLOG import LOG, ERROR, DEBUG, WARNING

class StateError(Exception):
  """
  Must call only an available transition
  """
  pass

class State(IdAsReferenceMixin("state_", "prefix"), XMLObject, XMLMatrix):
  """
  A ERP5 State.
  """
  meta_type = 'ERP5 State'
  portal_type = 'State'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  erp5_permission_roles = {} # { permission: [role] or (role,) }
  default_reference = ''
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
             PropertySheet.Base,
             PropertySheet.XMLObject,
             PropertySheet.CategoryCore,
             PropertySheet.DublinCore,
             PropertySheet.Reference,
             PropertySheet.State,)

  def setPermission(self, permission, acquired, roles, REQUEST=None):
      """Set a permission for this State."""
      permission_role = self.erp5_permission_roles
      if permission_role is None:
          self.erp5_permission_roles = permission_role = PersistentMapping()
      if acquired:
          roles = list(roles)
      else:
          roles = tuple(roles)
      permission_role[permission] = roles

  def getPermissionRoleList(self):
    return self.erp5_permission_roles

  def getDestinationReferenceList(self):
    ref_list = []
    for tr in self.getDestinationValueList():
      ref_list.append(tr.getReference())
    return ref_list
