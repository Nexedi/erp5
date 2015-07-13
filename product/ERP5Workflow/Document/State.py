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

  def getAvailableTransitionList(self, document):
    transition_list = self.getDestinationValueList(portal_type = 'Transition')
    result_list = []
    for transition in transition_list:
      value = transition._checkPermission(document)
      if value:
        result_list.append(transition)
    return result_list

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

  def setPermission(self, permission, acquired, roles, REQUEST=None):
      """Set a permission for this State."""
      pr = self.erp5_permission_roles
      if pr is None:
          self.erp5_permission_roles = pr = PersistentMapping()
      if acquired:
          roles = list(roles)
      else:
          roles = tuple(roles)
      pr[permission] = roles

  def getPermissionRoleList(self):
    return self.erp5_permission_roles

  def getWorkflow(self):
    return aq_parent(aq_inner(aq_parent(aq_inner(self))))

  def getDestinationReferenceList(self):
    ref_list = []
    for tr in self.getDestinationValueList():
      ref_list.append(tr.getReference())
    return ref_list

  def setGroups(self, REQUEST, RESPONSE=None):
    """Set the group to role mappings in REQUEST for this State.
    """
    map = self.group_roles
    if map is None:
      self.group_roles = map = PersistentMapping()
    map.clear()
    all_roles = self.getWorkflow().getRoles()
    for group in self.getWorkflow().getGroups():
      roles = []
      for role in all_roles:
        if REQUEST.get('%s|%s' % (group, role), 0):
          roles.append(role)
      roles.sort()
      roles = tuple(roles)
      map[group] = roles
    if RESPONSE is not None:
      RESPONSE.redirect(
            "%s/manage_groups?manage_tabs_message=Groups+changed."
            % self.absolute_url())
