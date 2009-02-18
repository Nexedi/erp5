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
from DCWorkflowDocumentationHelper import getStatePermissionsOfRole

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

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionList')
  def getTransitionList(self):
    """
    Returns list of possible transitions from this state
    """
    return self.getDocumentedObject().transitions

  def getPermissionsOfRole(self, role):
    return getStatePermissionsOfRole(self.getDocumentedObject(), role)

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionsOfRoleOwner')
  def getPermissionsOfRoleOwner(self):
    """
    """
    return self.getPermissionsOfRole('Owner')

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionsOfRoleAssignor')
  def getPermissionsOfRoleAssignor(self):
    """
    """
    return self.getPermissionsOfRole('Assignor')

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionsOfRoleAssignee')
  def getPermissionsOfRoleAssignee(self):
    """
    """
    return self.getPermissionsOfRole('Assignee')

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionsOfRoleAssociate')
  def getPermissionsOfRoleAssociate(self):
    """
    """
    return self.getPermissionsOfRole('Associate')

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionsOfRoleAuthor')
  def getPermissionsOfRoleAuthor(self):
    """
    """
    return self.getPermissionsOfRole('Author')

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissionsOfRoleAuditor')
  def getPermissionsOfRoleAuditor(self):
    """
    """
    return self.getPermissionsOfRole('Auditor')

InitializeClass(DCWorkflowStateDocumentationHelper)
