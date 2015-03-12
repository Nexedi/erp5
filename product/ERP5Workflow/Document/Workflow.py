##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2014 Wenjie Zheng <wenjie.zheng@tiolive.com>      
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
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.unauthorized import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.DCWorkflow.utils import modifyRolesForPermission
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition as DCWorkflow
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.Accessor import WorkflowState
from Products.ERP5Type import Permissions
from tempfile import mktemp
import os
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.ERP5Workflow.Document.Transition import TRIGGER_AUTOMATIC
from Products.ERP5Workflow.Document.Transition import TRIGGER_USER_ACTION
from Products.ERP5Workflow.Document.Transition import TRIGGER_WORKFLOW_METHOD
from Products.DCWorkflowGraph.config import DOT_EXE
from Products.DCWorkflowGraph.DCWorkflowGraph import bin_search, getGraph
from Products.DCWorkflow.States import StateDefinition as DCWorkflowState
from Products.CMFCore.WorkflowCore import ObjectDeleted
from Products.CMFCore.WorkflowCore import ObjectMoved
from Products.DCWorkflow.utils import Message as _
from Products.ERP5Type.Utils import UpperCase
from Acquisition import aq_base
from DateTime import DateTime
from zLOG import LOG, ERROR, DEBUG, WARNING

class Workflow(XMLObject):
  """
  A ERP5 Workflow.
  """

  meta_type = 'ERP5 Workflow'
  portal_type = 'Workflow'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  ### zwj: for security issue
  managed_permission_list = ()
  managed_role = ()
  erp5_permission_roles = {} # { permission: [role] or (role,) }
  manager_bypass = 0

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Workflow,
  )

  def initializeDocument(self, document):
    """
    Set initial state on the Document
    """
    state_bc_id = self.getStateBaseCategory()
    document.setCategoryMembership(state_bc_id, self.getSource())
    object = self.getStateChangeInformation(document, self.getSourceValue())

    # Initialize workflow history
    status_dict = {state_bc_id: document.unrestrictedTraverse(self.getSource()).getId()}
    status_dict['time'] = self.getDateTime()
    status_dict['action'] = None
    variable_list = self.contentValues(portal_type='Variable')
    for variable in variable_list:
      status_dict[variable.getTitle()] = variable.getInitialValue(object=object)
    self._updateWorkflowHistory(document, status_dict)
    ### zwj: initialize role mappings, also in State.py/executeTransition()
    self.updateRoleMappingsFor(document)

  def _generateHistoryKey(self):
    """
    Generate a key used in the workflow history.
    """
    history_key = self.unrestrictedTraverse(self.getRelativeUrl()).getId()
    return history_key

  def _updateWorkflowHistory(self, document, status_dict):
    """
    Change the state of the object.
    """
    # Create history attributes if needed
    if getattr(aq_base(document), 'workflow_history', None) is None:
      document.workflow_history = PersistentMapping()
      # XXX this _p_changed is apparently not necessary
      document._p_changed = 1

    # Add an entry for the workflow in the history
    workflow_key = self._generateHistoryKey()
    if not document.workflow_history.has_key(workflow_key):
      document.workflow_history[workflow_key] = ()

    # Update history
    status_dict['time'] = self.getDateTime()
    document.workflow_history[workflow_key] += (status_dict,)
    # XXX this _p_changed marks the document modified, but the
    # only the PersistentMapping is modified
    document._p_changed = 1
    # XXX this _p_changed is apparently not necessary
    document.workflow_history._p_changed = 1

  def getCurrentStatusDict(self, document):
    """
    Get the current status dict.
    """
    workflow_key = self._generateHistoryKey()

    # Copy is requested
    result = document.workflow_history[workflow_key][-1].copy()
    return result

  def getDateTime(self):
    """
    Return current date time.
    """
    return DateTime()

  def getManagedPermissionList(self):
    return self.managed_permission_list

  def getStateChangeInformation(self, document, state, transition=None):
    """
    Return an object used for variable tales expression.
    """
    if transition is None:
      transition_url = None
    else:
      transition_url = transition.getRelativeUrl()
    return self.asContext(document=document,
                          transition=transition,
                          transition_url=transition_url,
                          state=state)

  def isERP5WorkflowMethodSupported(self, document, transition):
    sdef = document._getDefaultAcquiredValue(self.getStateBaseCategory())
    ### zwj: upper line may meet problems when there are other Base categories.
    if sdef is None:
      return 0
    if (transition in sdef.getDestinationValueList() and
        self._checkTransitionGuard(transition, document) and
        transition.trigger_type == TRIGGER_WORKFLOW_METHOD
        ):
      return 1
    return 0

  security.declarePrivate('isActionSupported')
  def isActionSupported(self, document, action, **kw):
    '''
    Returns a true value if the given action name
    is possible in the current state.
    '''
    sdef = document._getDefaultAcquiredValue(self.getStateBaseCategory())
    if sdef is None:
      return 0
    if action in sdef.getDestinationValueList():
      tdef = self._getOb(action, None)
      if (tdef is not None and
        tdef.trigger_type == TRIGGER_USER_ACTION and
        self._checkTransitionGuard(tdef, document, **kw)):
        return 1
    return 0

  def _checkTransitionGuard(self, tdef, document, **kw):
    guard = tdef.getGuard()
    if guard is None:
      return 1
    if guard.check(getSecurityManager(), self, document, **kw):
      return 1
    return 0

  def _findAutomaticTransition(self, document, sdef):
    tdef = None
    for tid in sdef.getDestinationIdList():
      t = self._getOb(id=tid)
      if t is not None and t.trigger_type == TRIGGER_AUTOMATIC:
        if self._checkTransitionGuard(t, document):
          tdef = t
          break
    return tdef

  ### zwj: following parts related to the security features

  security.declarePrivate('updateRoleMappingsFor')
  def updateRoleMappingsFor(self, document):
    """Changes the object permissions according to the current state.
    """
    changed = 0
    sdef = document._getDefaultAcquiredValue(self.getStateBaseCategory())
    managed_permission = self.getManagedPermissionList()
    if sdef is None:
        return 0
    ### zwj: get all matrix cell objects
    permission_role_matrix_cells = sdef.objectValues(portal_type = "PermissionRoles")
    ### zwj: build a permission roles dict
    for perm_role in permission_role_matrix_cells:
      permission,role = perm_role.getPermissionRole()
      ### zwj: double check the right role and permission are obtained
      if permission != 'None':
        if self.erp5_permission_roles.has_key(permission):
          self.erp5_permission_roles[permission] += (role,)
        else:
          self.erp5_permission_roles.update({permission : (role,)})
    ### zwj: update role list to permission
    for permission_roles in self.erp5_permission_roles.keys():
      if modifyRolesForPermission(document, permission_roles, self.erp5_permission_roles[permission_roles]):
        changed = 1
        ### zwj: clean Permission Role list for next role mapping
      del self.erp5_permission_roles[permission_roles]
    return changed

  def getRoleList(self):
    return sorted(self.getPortalObject().getDefaultModule('acl_users').valid_roles())

  security.declarePrivate('doActionFor')
  def doActionFor(self, document, action, *args, **kw):
    sdef = document._getDefaultAcquiredValue(self.getStateBaseCategory())
    if sdef is None:
      raise WorkflowException(_(u'Object is in an undefined state.'))
    if self.isActionSupported(document, action, **kw):
      wf_id = self.getId()
      if wf_id is None:
        raise WorkflowException(
            _(u'Requested workflow definition not found.'))
    tdef = self._getOb(id=action)
    ### check again the action object is available
    if tdef not in self.objectValues(portal_type='Transition'):
      raise Unauthorized(action)
    if tdef is None or tdef.trigger_type != TRIGGER_USER_ACTION:
      msg = _(u"Transition '${action_id}' is not triggered by a user "
        u"action.", mapping={'action_id': action})
      raise WorkflowException(msg)
    if not self._checkTransitionGuard(tdef, document, **kw):
      raise Unauthorized(action)
    ### execute action
    self._changeStateOf(document, tdef)

  def _changeStateOf(self, document, tdef=None, kwargs=None):
    '''
    Changes state.  Can execute multiple transitions if there are
    automatic transitions.  tdef set to None means the object
    was just created.
    '''
    moved_exc = None
    while 1:
      try:
        sdef = tdef.execute(document, kwargs)
      except ObjectMoved, moved_exc:
        document = moved_exc.getNewObject()
        state_bc_id = self.getStateBaseCategory()
        status_dict = self.getCurrentStatusDict(document)
        sdef = self._getOb(status_dict[state_bc_id])
        # Re-raise after all transitions.
      if sdef is None:
        break
      tdef = self._findAutomaticTransition(document, sdef)
      if tdef is None:
        # No more automatic transitions.
        break
      # Else continue.
    if moved_exc is not None:
        # Re-raise.
      raise moved_exc
  ### Security feature end

  ###########
  ## Graph ##
  ###########

  getGraph = getGraph

  def getPOT(self, *args, **kwargs):
      """
      get the pot, copy from:
      "dcworkfow2dot.py":http://awkly.org/Members/sidnei/weblog_storage/blog_27014
      and Sidnei da Silva owns the copyright of the this function
      """
      out = []
      transition_dict = {}
      out.append('digraph "%s" {' % self.getTitle())
      transition_with_init_state_list = []
      for state in self.contentValues(portal_type='State'):
        out.append('%s [shape=box,label="%s",' \
                     'style="filled",fillcolor="#ffcc99"];' % \
                     (state.getId(), state.getTitle()))
        # XXX Use API instead of getDestinationValueList
        for available_transition in state.getDestinationValueList():
          transition_with_init_state_list.append(available_transition.getId())
          destination_state = available_transition.getDestinationValue()
          if destination_state is None:
            # take care of 'remain in state' transitions
            destination_state = state
          #
          key = (state.getId(), destination_state.getId())
          value = transition_dict.get(key, [])
          value.append(available_transition.getTitle())
          transition_dict[key] = value

      # iterate also on transitions, and add transitions with no initial state
      for transition in self.contentValues(portal_type='Transition'):
        trans_id = transition.getId()
        if trans_id not in transition_with_init_state_list:
          destination_state = transition.getDestinationValue()
          if destination_state is None:
            dest_state_id = None
          else:
            dest_state_id = destination_state.getId()

          key = (None, dest_state_id)
          value = transition_dict.get(key, [])
          value.append(transition.getTitle())
          transition_dict[key] = value

      for k, v in transition_dict.items():
          out.append('%s -> %s [label="%s"];' % (k[0], k[1],
                                                 ',\\n'.join(v)))

      out.append('}')
      return '\n'.join(out)
