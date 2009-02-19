##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Globals import InitializeClass
from Products.ERP5Type import Permissions
from DocumentationHelper import DocumentationHelper
from DCWorkflowDocumentationHelper import getRoleList

class DCWorkflowStateDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a workflow state
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Workflow State"

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionItemList')
  def getTransitionItemList(self, **kw):
    """
    """
    state = self.getDocumentedObject()
    base_uri = '/'.join(state.getPhysicalPath()[:-2] + ('transitions', ''))
    return [self.getDocumentationHelper('DCWorkflowTransitionDocumentationHelper',
                                        base_uri + id)
            for id in state.transitions]

  security.declareProtected(Permissions.AccessContentsInformation, 'getRoleList')
  def getRoleList(self):
    """
    """
    return getRoleList(self.getDocumentedObject().getWorkflow())

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionsList')
  def getPermissionsList(self):
    """
    """
    return map(self.getPermissionsOfRole, self.getRoleList())

  def getPermissionsOfRole(self, role):
    """
    Returns list of permissions for a given role with AVMC format above
      A = Access contents information
      V = View
      M = Modify Portal Content
      C = Add Portal Content
    """
    permissions = ""
    permission_roles = self.getDocumentedObject().permission_roles
    if permission_roles:
      if role in permission_roles.get('Access contents information', ()):
        permissions += "A"
      if role in permission_roles.get('View', ()):
        permissions += "V"
      if role in permission_roles.get('Modify portal content', ()):
        permissions += "M"
      if role in permission_roles.get('Add portal content', ()):
        permissions += "C"
    return permissions


InitializeClass(DCWorkflowStateDocumentationHelper)
