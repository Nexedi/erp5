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

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions
from zLOG import LOG, INFO

def getPermissionsOfRole(state=None, role=''):
  """
  Returns list of permissions for a given role with AVMC format above
    A = Access contents information
    V = View
    M = Modify Portal Content
    C = Add Portal Content
  """
  #LOG('yoooo', INFO, 'state=%s role=%s ' % (state, role))
  permissions = ""
  if state != None:
    if hasattr(state, '__dict__'):
      if 'permission_roles' in state.__dict__.keys():
        if 'View' in state.__dict__['permission_roles'].keys():
          if role in state.__dict__['permission_roles']['View']:
            permissions += "V"
        if 'Access contents information' in state.__dict__['permission_roles'].keys():
          if role in state.__dict__['permission_roles']['Access contents information']:
            permissions += "A"
        if 'Modify portal content' in state.__dict__['permission_roles'].keys():
          if role in state.__dict__['permission_roles']['Modify portal content']:
            permissions += "M"
        if 'Add portal content' in state.__dict__['permission_roles'].keys():
          if role in state.__dict__['permission_roles']['Add portal content']:
            permissions += "C"
  return permissions


class DCWorkflowStateDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a workflow state
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, uri):
    self.uri = uri

  security.declareProtected(Permissions.AccessContentsInformation, 'getDescription')
  def getDescription(self):
    return self.getDocumentedObject().__dict__["description"]

  security.declareProtected(Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Workflow State"

  security.declareProtected(Permissions.AccessContentsInformation, 'getId' )
  def getId(self):
    """
    Returns the id of the documentation helper
    """
    return self.getDocumentedObject().__name__


  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return self.getDocumentedObject().__dict__["title"]

  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    return []

  security.declareProtected( Permissions.AccessContentsInformation, 'getTransitionList' )
  def getTransitionList(self):
    """
    Returns list of possible transitions from this state
    """
    return self.getDocumentedObject().transitions

  security.declareProtected( Permissions.AccessContentsInformation, 'getPermissionsOfRoleOwner' )
  def getPermissionsOfRoleOwner(self):
    """
    """
    return getPermissionsOfRole(self.getDocumentedObject(),'Owner')

  security.declareProtected( Permissions.AccessContentsInformation, 'getPermissionsOfRoleAssignor' )
  def getPermissionsOfRoleAssignor(self):
    """
    """
    return getPermissionsOfRole(self.getDocumentedObject(),'Assignor')

  security.declareProtected( Permissions.AccessContentsInformation, 'getPermissionsOfRoleAssignee' )
  def getPermissionsOfRoleAssignee(self):
    """
    """
    return getPermissionsOfRole(self.getDocumentedObject(),'Assignee')

  security.declareProtected( Permissions.AccessContentsInformation, 'getPermissionsOfRoleAssociate' )
  def getPermissionsOfRoleAssociate(self):
    """
    """
    return getPermissionsOfRole(self.getDocumentedObject(),'Associate')

  security.declareProtected( Permissions.AccessContentsInformation, 'getPermissionsOfRoleAuthor' )
  def getPermissionsOfRoleAuthor(self):
    """
    """
    return getPermissionsOfRole(self.getDocumentedObject(),'Author')

  security.declareProtected( Permissions.AccessContentsInformation, 'getPermissionsOfRoleAuditor' )
  def getPermissionsOfRoleAuditor(self):
    """
    """
    return getPermissionsOfRole(self.getDocumentedObject(),'Auditor')

InitializeClass(DCWorkflowStateDocumentationHelper)
