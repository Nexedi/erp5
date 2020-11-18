##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from zLOG import LOG, ERROR, DEBUG, WARNING

class StateError(Exception):
  """
  Must call only an available transition
  """
  pass

class ConfigurationState(XMLObject):
  """
  A Busniess Configuration State.
  """
  meta_type = 'ERP5 State'
  portal_type = 'Configuration State'
  add_permission = Permissions.AddPortalContent
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

  def getAvailableTransitionList(self, document):
    """
    Return available transitions only if they are accessible for document.
    """
    transition_list = self.getDestinationValueList(portal_type = 'Configuration Transition')
    result_list = []
    for transition in transition_list:
      value = transition._checkPermission(document)
      if value:
        result_list.append(transition)
    return result_list

  def executeTransition(self, transition, document, form_kw=None):
    """
    Execute transition on the object.
    """
    if transition not in self.getAvailableTransitionList(document):
      raise StateError
    else:
      transition.execute(document, form_kw=form_kw)

  def undoTransition(self, document):
    """
    Reverse previous transition
    """
    wh = self.getWorkflowHistory(document, remove_undo=1)
    status_dict = wh[-2]
    # Update workflow state
    state_bc_id = self.getParentValue().getStateBaseCategory()
    document.setCategoryMembership(state_bc_id, status_dict[state_bc_id])
    # Update workflow history
    status_dict['undo'] = 1
    self.getParentValue()._updateWorkflowHistory(document, status_dict)
    # XXX
    LOG("State, undo", ERROR, "Variable (like DateTime) need to be updated!")

  def getWorkflowHistory(self, document, remove_undo=0, remove_not_displayed=0):
    """
    Return history tuple
    """
    wh = document.workflow_history[self.getParentValue()._generateHistoryKey()]
    result = []
    # Remove undo
    if not remove_undo:
      result = [x.copy() for x in wh]
    else:
      result = []
      for x in wh:
        if x.has_key('undo') and x['undo'] == 1:
          result.pop()
        else:
          result.append(x.copy())
    return result

  def getVariableValue(self, document, variable_name):
    """
    Get current value of the variable from the object
    """
    status_dict = self.getParentValue().getCurrentStatusDict(document)
    return status_dict[variable_name]

  def getDestinationReferenceList(self):
    return self.getDestinationIdList()
