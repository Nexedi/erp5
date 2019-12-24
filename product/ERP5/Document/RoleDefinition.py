##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.ERP5Type \
  import ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT

class RoleDefinition(XMLObject):
  # CMF Type Definition
  meta_type = 'ERP5 Role Definition'
  portal_type = 'Role Definition'
  add_permission = Permissions.ChangeLocalRoles

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  zope.interface.implements(interfaces.ILocalRoleGenerator)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.RoleDefinition
                    )

  def _setRoleName(self, value):
    if value and value not in \
       zip(*self.RoleDefinition_getRoleNameItemList())[1]:
      raise Unauthorized("You are not allowed to give %s role" % value)
    self._baseSetRoleName(value)

  security.declarePrivate("getLocalRolesFor")
  def getLocalRolesFor(self, ob, user_name=None):
    group_id_generator = getattr(ob,
      ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT)
    role_list = self.getRoleName(),
    return {group_id: role_list
      for group_id in group_id_generator(category_order=('agent',),
                                         agent=self.getAgentList())}
