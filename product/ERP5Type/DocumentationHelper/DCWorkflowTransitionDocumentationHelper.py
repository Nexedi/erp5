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
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions

class DCWorkflowTransitionDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a workflow transition
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Workflow Transition"

  security.declareProtected(Permissions.AccessContentsInformation, 'getNewStateId')
  def getNewStateId(self):
    """
    Returns the id of the new state for de workflow transition
    """
    return getattr(self.getDocumentedObject(), "new_state_id", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getTriggerType')
  def getTriggerType(self):
    """
    Returns the trigger type for de workflow transition
    """
    trigger_type_list = ['Automatic','Initiated by user action','Initiated by WorkflowMethod']
    trigger_type_id = getattr(self.getDocumentedObject(), "trigger_type", '')
    return trigger_type_list[trigger_type_id]

  security.declareProtected(Permissions.AccessContentsInformation, 'getScriptName')
  def getScriptName(self):
    """
    Returns the name of the script for de workflow transition
    """
    return getattr(self.getDocumentedObject(), "script_name", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getAfterScriptName')
  def getAfterScriptName(self):
    """
    Returns the name of the script for de workflow transition
    """
    return getattr(self.getDocumentedObject(), "after_script_name", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableStateIds')
  def getAvailableStateIds(self):
    """
    Returns available states in the workflow
    """
    return self.getDocumentedObject().getAvailableStateIds()

  security.declareProtected(Permissions.AccessContentsInformation, 'getGuardRoles')
  def getGuardRoles(self):
    """
    Returns roles to pass this transition
    """
    role_list = ()
    if hasattr(self.getDocumentedObject(),'guard'):
      dir(self.getDocumentedObject().guard)
      if hasattr(self.getDocumentedObject().guard, '__dict__'):
        if 'roles' in self.getDocumentedObject().guard.__dict__.keys():
          role_list = self.getDocumentedObject().guard.__dict__['roles']
    return ', '.join(role for role in role_list)

InitializeClass(DCWorkflowTransitionDocumentationHelper)
