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

class DCWorkflowWorklistDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a workflow worklist
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, uri):
    self.uri = uri

  security.declareProtected(Permissions.AccessContentsInformation, 'getDescription')
  def getDescription(self):
    return getattr(self.getDocumentedObject(), "description", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Workflow Worklist"

  security.declareProtected(Permissions.AccessContentsInformation, 'getId' )
  def getId(self):
    """
    Returns the id of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "__name__", '')

  security.declareProtected( Permissions.AccessContentsInformation, 'getSectionList' )
  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    return []


  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    if self.getDocumentedObject().title == "":
      return self.getDocumentedObject().actbox_name
    else: 
      return self.getDocumentedObject().title  

  security.declareProtected(Permissions.AccessContentsInformation, 'getGuardRoles' )
  def getGuardRoles(self):
    """
    Returns roles to pass this worklist
    """
    role_list = ()
    if hasattr(self.getDocumentedObject(),'guard'):
      dir(self.getDocumentedObject().guard)
      if hasattr(self.getDocumentedObject().guard, '__dict__'):
        if 'roles' in self.getDocumentedObject().guard.__dict__.keys():
          role_list = self.getDocumentedObject().guard.__dict__['roles']
    return ', '.join(role for role in role_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getVarMatches' )
  def getVarMatches(self):
    """
    Returns variables and values to match worklist
    """
    var_matches = {}
    if hasattr(self.getDocumentedObject(),'var_matches'):
      var_matches = self.getDocumentedObject().var_matches
    var_matches_list = []
    for key in var_matches.keys():
      var_matches_list.append('%s: %s' % (key, ', '.join(x for x in var_matches[key])))
      #var_matches_list.append((key, '%s' % ', '.join(x for x in var_matches[key])))
    return var_matches_list 
     
InitializeClass(DCWorkflowWorklistDocumentationHelper)
