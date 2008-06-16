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
from AccessorMethodDocumentationHelper import getDefinitionString

class WorkflowMethodDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a workflow method
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, uri):
    self.uri = uri

  security.declareProtected(Permissions.AccessContentsInformation, 'getDescription')
  def getDescription(self):
    return getattr(self.getDocumentedObject(), "__doc__", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Workflow Method"

  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "__name__", '')

  security.declareProtected( Permissions.AccessContentsInformation, 'getSectionList' )
  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    return []


  #security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationState' )
  #def getDestinationState(self):
  #  """
  #  Returns the destination_state of the transition workflow method
  #  """
  #  return self.getDocumentedObject().__dict__['new_state_id']

  #security.declareProtected(Permissions.AccessContentsInformation, 'getTriggerType' )
  #def getTriggerType(self):
  #  """
  #  Returns the trigger type of the workflow method
  #  """
  #  TT = ['Automatic','Initiated by user action','Initiated by WorkflowMethod']
  #  TT_id = self.getDocumentedObject().__dict__['trigger_type']
  #  return TT[TT_id]

  #security.declareProtected(Permissions.AccessContentsInformation, 'getLocalRoles' )
  #def getLocalRoles(self):
  #  """
  #  Returns the local roles of the workflow method
  #  """
  #  return self.getDocumentedObject().__ac_local_roles__

  #security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableStateIds' )
  #def getAvailableStateIds(self):
  #  """
  #  Returns available states in the workflow
  #  """
  #  return self.getDocumentedObject().getAvailableStateIds()

  security.declareProtected( Permissions.AccessContentsInformation, 'getDefinition' )
  def getDefinition(self):
    """
    Returns the definition of the workflow_method with the name and arguments
    """
    return getDefinitionString(self.getDocumentedObject())

InitializeClass(WorkflowMethodDocumentationHelper)
