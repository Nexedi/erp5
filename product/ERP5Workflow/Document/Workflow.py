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

import os
import sys

from AccessControl import ClassSecurityInfo
from AccessControl.unauthorized import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent
from copy import deepcopy
from DateTime import DateTime
from DocumentTemplate.DT_Util import TemplateDict
from lxml import etree
from lxml.etree import Element, SubElement
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException, ObjectDeleted,\
                                          ObjectMoved
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.DCWorkflowGraph.config import DOT_EXE
from Products.DCWorkflowGraph.DCWorkflowGraph import bin_search, getGraph
from Products.DCWorkflow.utils import Message as _
from Products.DCWorkflow.utils import modifyRolesForPermission
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition as DCWorkflow
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.DCWorkflow.Expression import createExprContext
from Products.ERP5Type.patches.WorkflowTool import SECURITY_PARAMETER_ID,\
                                                          WORKLIST_METADATA_KEY
from Products.ERP5Type.Utils import UpperCase, convertToMixedCase
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Workflow.Document.Transition import TRIGGER_AUTOMATIC,\
                                    TRIGGER_USER_ACTION, TRIGGER_WORKFLOW_METHOD
from tempfile import mktemp
from types import StringTypes
from zLOG import LOG, INFO, WARNING

class Workflow(IdAsReferenceMixin("", "prefix"), XMLObject):
  """
  A ERP5 Workflow.
  """
  id = ''
  meta_type = 'ERP5 Workflow'
  portal_type = 'Workflow'
  _isAWorkflow = True # DCWorkflow Tool compatibility
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  default_reference = ''
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
    PropertySheet.Reference,
    PropertySheet.Workflow,
  )

  def notifyCreated(self, document):

    """Notifies this workflow after an object has been created and added.
    """
    try:
        self._changeStateOf(document, None)
    except ( ObjectDeleted, ObjectMoved ):
        # Swallow.
        pass

  initializeDocument = notifyCreated

  def _generateHistoryKey(self):
    """
    Generate a key used in the workflow history.
    """
    history_key = self.getReference()
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
    document.workflow_history[workflow_key] += (status_dict,)
    # XXX this _p_changed marks the document modified, but the
    # only the PersistentMapping is modified
    # document._p_changed = 1
    # XXX this _p_changed is apparently not necessary
    #document.workflow_history._p_changed = 1

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

  def isWorkflowMethodSupported(self, document, transition_id):
    transition = self._getOb('transition_' + transition_id)
    sdef = self._getWorkflowStateOf(document, id_only=0)
    if sdef is None:
      return 0
    if (transition in sdef.getDestinationValueList() and
        self._checkTransitionGuard(transition, document) and
        transition.getTriggerType() == TRIGGER_WORKFLOW_METHOD
        ):
      return 1
    return 0

  security.declarePrivate('isActionSupported')
  def isActionSupported(self, document, action, **kw):
    '''
    Returns a true value if the given action name
    is possible in the current state.
    '''
    sdef = self._getWorkflowStateOf(document, id_only=0)
    if sdef is None:
      return 0

    if action in sdef.getDestinationIdList():
      tdef = self._getOb(action, None)
      if (tdef is not None and
        tdef.getTriggerType() == TRIGGER_USER_ACTION and
        self._checkTransitionGuard(tdef, document, **kw)):
        return 1
    return 0

  security.declarePrivate('isInfoSupported')
  def isInfoSupported(self, ob, name):
      '''
      Returns a true value if the given info name is supported.
      '''
      if name == self.getStateVariable():
          return 1
      vdef = self.getVariableValueList().get(name, None)
      if vdef is None:
          return 0
      return 1

  def _checkTransitionGuard(self, tdef, document, **kw):
    guard = tdef.getGuard()
    if guard is None:
      # in new workflow transition, guard shouldn't be none any more, this
      # condiction is only kept for debugging.
      return 1
    if guard.check(getSecurityManager(), self, document, **kw):
      return 1
    return 0

  def _findAutomaticTransition(self, document, sdef):
    tdef = None
    for t in sdef.getDestinationValueList():
      if t.getTriggerType() == TRIGGER_AUTOMATIC:
        if self._checkTransitionGuard(t, document):
          tdef = t
          break
    return tdef

  security.declarePrivate('updateRoleMappingsFor')
  def updateRoleMappingsFor(self, document):
    """Changes the object permissions according to the current state.
    """
    changed = 0
    sdef = self._getWorkflowStateOf(document, id_only=0)
    managed_permission = self.getManagedPermissionList()
    if sdef is None:
        return 0
    # zwj: get all matrix cell objects
    permission_role_matrix_cells = sdef.objectValues(portal_type = "PermissionRoles")
    # zwj: build a permission roles dict
    for perm_role in permission_role_matrix_cells:
      permission, role = perm_role.getPermissionRole()
      # zwj: double check the right role and permission are obtained
      if permission != 'None':
        if self.erp5_permission_roles.has_key(permission):
          self.erp5_permission_roles[permission] += (role,)
        else:
          self.erp5_permission_roles.update({permission : (role,)})
    # zwj: update role list to permission
    for permission_roles in self.erp5_permission_roles.keys():
      if modifyRolesForPermission(document, permission_roles, self.erp5_permission_roles[permission_roles]):
        changed = 1
        # zwj: clean Permission Role list for the next role mapping
      del self.erp5_permission_roles[permission_roles]
    return changed

  def getManagedRoleList(self):
    return sorted(self.getPortalObject().getDefaultModule('acl_users').valid_roles())

  security.declarePrivate('doActionFor')
  def doActionFor(self, document, action, comment='', **kw):
    '''
    Allows the user to request a workflow action.  This method
    must perform its own security checks.
    '''
    sdef = self._getWorkflowStateOf(document, id_only=0)
    kw['comment'] = comment
    if sdef is None:
      raise WorkflowException(_(u'Object is in an undefined state.'))
    if self.isActionSupported(document, action, **kw):
      wf_id = self.getId()
      if wf_id is None:
        raise WorkflowException(
            _(u'Requested workflow not found.'))
    tdef = self._getOb(id=action)

    if tdef not in self.objectValues(portal_type='Transition'):
      raise Unauthorized(action)
    if tdef is None or tdef.getTriggerType() != TRIGGER_USER_ACTION:
      msg = _(u"Transition '${action_id}' is not triggered by a user "
        u"action.", mapping={'action_id': action})
      raise WorkflowException(msg)
    if not self._checkTransitionGuard(tdef, document, **kw):
      raise Unauthorized(action)
    self._changeStateOf(document, tdef, kw)

  def _changeStateOf(self, document, tdef=None, kwargs=None):
    '''
    Changes state.  Can execute multiple transitions if there are
    automatic transitions.  tdef set to None means the object
    was just created.
    '''
    moved_exc = None
    while 1:
      try:
        sdef = self._executeTransition(document, tdef, kwargs)
      except ObjectMoved, moved_exc:
        document = moved_exc.getNewObject()
        sdef = self._getWorkflowStateOf(document, id_only=0)
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

  def listObjectActions(self, info):
      fmt_data = None
      document = info.object
      sdef = self._getWorkflowStateOf(document, id_only=0)
      if sdef is None:
          return None
      res = []

      for tid in sdef.getDestinationIdList():
        tdef = self._getOb(id=tid)
        if tdef is not None and tdef.getTriggerType() == TRIGGER_USER_ACTION and \
                tdef.getActboxName() and self._checkTransitionGuard(tdef, document):
            if fmt_data is None:
                fmt_data = TemplateDict()
                fmt_data._push(info)
            fmt_data._push({'transition_id': tdef.getReference()})
            res.append((tid, {
                'id': tdef.getReference(),
                'name': tdef.getActboxName() % fmt_data,
                'url': str(tdef.getActboxUrl()) % fmt_data,
                'icon': str(tdef.getActboxIcon()) % fmt_data,
                'permissions': (),  # Predetermined.
                'category': tdef.getActboxCategory(),
                'transition': tdef}))
            fmt_data._pop()
      res.sort()

      return [ result[1] for result in res ]

  def getWorklistVariableMatchDict(self, info, check_guard=True):
    """
      Return a dict which has an entry per worklist definition
      (worklist id as key) and which value is a dict composed of
      variable matches.
    """
    if not self.objectValues(portal_type='Worklist'):
      return None

    portal = self.getPortalObject()
    def getPortalTypeListForWorkflow(workflow_id):
        workflow_tool = portal.portal_workflow
        result = []
        append = result.append
        for type_info in portal.portal_types.objectValues():
          portal_type = type_info.id
          if workflow_id in type_info.getTypeWorkflowList():
            append(portal_type)
        return result

    _getPortalTypeListForWorkflow = CachingMethod(getPortalTypeListForWorkflow,
                              id='_getPortalTypeListForWorkflow', cache_factory = 'erp5_ui_long')
    portal_type_list = _getPortalTypeListForWorkflow(self.id)
    if not portal_type_list:
      return None
    variable_match_dict = {}
    security_manager = getSecurityManager()
    workflow_id = self.getId()
    workflow_title = self.getTitle()
    for worklist_id, worklist_definition in self.getWorklistValueList().items():
      action_box_name = worklist_definition.getActboxName()
      guard = worklist_definition.getGuard()
      if action_box_name:
        variable_match = {}
        for key in worklist_definition.getVarMatchKeys():
          var = worklist_definition.getVarMatch(key)
          if isinstance(var, Expression):
            evaluated_value = var(createExprContext(StateChangeInfo(portal,
                                  self, kwargs=info.__dict__.copy())))
            if isinstance(evaluated_value, (str, int, long)):
              evaluated_value = [str(evaluated_value)]
          else:
            evaluated_value = [x % info for x in var]
          variable_match[key] = evaluated_value

        if 'portal_type' in variable_match and len(variable_match['portal_type']):
          portal_type_intersection = set(variable_match['portal_type']).intersection(portal_type_list)
          # in case the current workflow is not associated with portal_types
          # defined on the worklist, don't display the worklist for this
          # portal_type.
          variable_match['portal_type'] = list(portal_type_intersection)
        variable_match.setdefault('portal_type', portal_type_list)

        if len(variable_match.get('portal_type', [])) == 0:
          continue

        is_permitted_worklist = 0
        if guard is None:
          is_permitted_worklist = 1
        elif (not check_guard) or \
            Guard_checkWithoutRoles(guard, security_manager, self, portal):
          is_permitted_worklist = 1
          variable_match[SECURITY_PARAMETER_ID] = guard.roles

        if is_permitted_worklist:
          fmt_data = TemplateDict()
          fmt_data._push(info)
          variable_match.setdefault(SECURITY_PARAMETER_ID, ())
          fmt_data._push({k: ('&%s:list=' % k).join(v) for\
                                            k, v in variable_match.iteritems()})

          variable_match[WORKLIST_METADATA_KEY] = {
                                                'format_data': fmt_data,
                                                 'worklist_title': action_box_name,
                                                 'worklist_id': worklist_id,
                                                 'workflow_title': workflow_title,
                                                 'workflow_id': workflow_id,
                                                 'action_box_url': worklist_definition.getActboxUrl(),
                                                 'action_box_category': worklist_definition.getActboxCategory()}

          variable_match_dict[worklist_id] = variable_match

    if len(variable_match_dict) == 0:
      return None
    return variable_match_dict

  security.declarePrivate('getInfoFor')
  def getInfoFor(self, ob, name, default):
      '''
      Allows the user to request information provided by the
      workflow.  This method must perform its own security checks.
      '''
      if name == self.getStateVariable():
          return self._getWorkflowStateOf(ob, 1)
      vdef = self.getVariableValueList()[name]
      if vdef.getInfoGuard() is not None and not vdef.getInfoGuard().check(
          getSecurityManager(), self, ob):
          return default
      status = self.getCurrentStatusDict(ob)
      default_expr = vdef.getDefaultExpr()
      if status is not None and status.has_key(name):
          value = status[name]

      # Not set yet.  Use a default.
      elif default_expr is not None:
          ec = createExprContext(StateChangeInfo(ob, self, status))
          value = Expression(default_expr)(ec)
      else:
          value = vdef.getInitialValue()

      return value

  def getCurrentStatusDict(self, document):
    """
    Get the current status dict. It's the same as _getStatusOf.
    """
    workflow_key = self._generateHistoryKey()
    workflow_history = self.getParent().getHistoryOf(workflow_key, document)
    # Copy is requested
    if workflow_history:
      return workflow_history[-1].copy()
    return {}

  def _getStatusOf(self, ob):
      tool = self.getParent()
      status = tool.getStatusOf(self.getId(), ob)
      if status is None:
          return {}
      else:
          # Copy is requested
          return status.copy()

  def _getWorkflowStateOf(self, ob, id_only=0):
      tool = self.getParent()
      id_no_suffix = self.getReference()
      status = tool.getStatusOf(id_no_suffix, ob)
      if status is None:
          state = self.getSourceValue()
      else:
          state_id = 'state_' + status.get(self.getStateVariable(), None)
          state = self._getOb(state_id)
          if state is None:
              state = self.getSourceValue()
      if id_only:
          return state.getReference()
      else:
          return state

  def getVariableValueList(self):
    variable_dict = {}
    for vdef in self.objectValues(portal_type="Variable"):
      variable_dict[vdef.getReference()] = vdef
    return variable_dict

  def getVariableIdList(self):
    id_list = []
    for ob in self.objectValues(portal_type="Variable"):
      id_list.append(ob.getReference())
    return id_list

  def getStateValueList(self):
    state_dict = {}
    for sdef in self.objectValues(portal_type="State"):
      state_dict[sdef.getReference()] = sdef
    return state_dict

  def getStateIdList(self):
    id_list = []
    for ob in self.objectValues(portal_type="State"):
      id_list.append(ob.getReference())
    return id_list

  def getWorklistValueList(self):
    worklist_dict = {}
    for qdef in self.objectValues(portal_type="Worklist"):
      worklist_dict[qdef.getReference()] = qdef
    return worklist_dict

  def getWorklistIdList():
    id_list = []
    for ob in self.objectValues(portal_type="Worklist"):
      id_list.append(ob.getReference())
    return id_list

  def getTransitionValueList(self):
    transition_dict = {}
    for tdef in self.objectValues(portal_type="Transition"):
      transition_dict[tdef.getReference()] = tdef
    return transition_dict

  def getTransitionIdList(self):
    id_list = []
    for ob in self.objectValues(portal_type="Transition"):
      id_list.append(ob.getReference())
    return id_list

  def getScriptValueList(self):
    scripts = {}
    for script in self.objectValues(portal_type='Workflow Script'):
      scripts[script.getReference()] = script
    return scripts

  def notifyWorkflowMethod(self, ob, transition_list, args=None, kw=None):
    """ Execute workflow methods.
    """
    if type(transition_list) in StringTypes:
      method_id = transition_list
    elif len(transition_list) == 1:
      method_id = transition_list[0]
    else:
      raise ValueError('WorkflowMethod should be attached to exactly 1 transition per DCWorkflow instance.')
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
      raise WorkflowException, 'Object is in an undefined state'
    prefix_method_id = 'transition_' + method_id
    if prefix_method_id not in sdef.getDestinationIdList():
      raise Unauthorized(method_id)
    tdef = self._getOb(prefix_method_id)
    if tdef is None or tdef.getTriggerType() != TRIGGER_WORKFLOW_METHOD:
      raise WorkflowException, (
         'Transition %s is not triggered by a workflow method'
             % method_id)
    if not self._checkTransitionGuard(tdef, ob):
      raise Unauthorized(method_id)
    self._changeStateOf(ob, tdef, kw)
    if getattr(ob, 'reindexObject', None) is not None:
      if kw is not None:
        activate_kw = kw.get('activate_kw', {})
      else:
        activate_kw = {}
      ob.reindexObject(activate_kw=activate_kw)

  def notifyBefore(self, ob, transition_list, args=None, kw=None):
    pass

  def notifySuccess(self, ob, transition_list, result, args=None, kw=None):
    pass

  def notifyException(self, ob, action, exc):
      '''
      Notifies this workflow that an action failed.
      '''
      pass

  def _executeTransition(self, document, tdef=None, form_kw=None):
    """
    Execute transition.
    """
    sci = None
    econtext = None
    moved_exc = None
    validation_exc = None
    tool = getToolByName(self, 'portal_workflow')

    # Figure out the old and new states.
    state_var = self.getStateVariable()
    status_dict = self.getCurrentStatusDict(document)
    current_state_value = self._getWorkflowStateOf(document, id_only=0)

    if current_state_value == None:
      current_state_value = self.getSourceValue()
    old_state = current_state_value.getReference()
    old_sdef = current_state_value

    if tdef is None:
      new_sdef = self.getSourceValue()
      new_state = new_sdef.getReference()
      if not new_sdef:
        # Do nothing if there is no initial state. We may want to create
        # workflows with no state at all, only for worklists.
        return
      former_status = {}
    else:
      new_sdef = tdef.getDestinationValue()
      if new_sdef == None:
        new_state = old_state
      else:
        new_state = new_sdef.getReference()
      former_status = self.getCurrentStatusDict(document)

    # Execute the "before" script.
    before_script_success = 1
    if tdef is not None and tdef.getBeforeScriptIdList():
      script_id_list = tdef.getBeforeScriptIdList()
      kwargs = form_kw
      sci = StateChangeInfo(
                document, self, former_status, tdef, old_sdef, new_sdef, kwargs)
      for script_id in script_id_list:
        script = self._getOb(script_id, None)
        if script:
          # Pass lots of info to the script in a single parameter.
          if script.getPortalType() != 'Workflow Script':
            raise NotImplementedError ('Unsupported Script %s for state %s'%(script_id, old_sdef.getReference()))
          try:
            script(sci)  # May throw an exception.
          except ValidationFailed, validation_exc:
            before_script_success = 0
            before_script_error_message = deepcopy(validation_exc.msg)
            validation_exc_traceback = sys.exc_traceback
          except ObjectMoved, moved_exc:
            ob = moved_exc.getNewObject()
            # Re-raise after transition

    # update variables
    state_values = None
    # seems state variable is not used in new workflow.
    object = self.getStateChangeInformation(document, self.getSourceValue())
    if new_sdef is not None:
      state_values = getattr(new_sdef,'var_values', None)
    if state_values is None:
      state_values = {}

    tdef_exprs = {}
    transition_variable_list = []
    if tdef is not None:
      transition_variable_list = tdef.objectValues(portal_type='Transition Variable')
    for transition_variable in transition_variable_list:
      tdef_exprs[transition_variable.getCausalityId()] = transition_variable.getDefaultExpr()

    # Update all transition variables
    if form_kw is not None:
      object.REQUEST.other.update(form_kw)
      kwargs = form_kw

    for vdef in self.objectValues(portal_type='Variable'):
      id = vdef.getId()
      variable_reference = vdef.getReference()
      if not vdef.getForStatus() or vdef.getForStatus() == 0:
        continue
      expr = None
      if variable_reference in state_values:
        value = state_values[variable_reference]
      elif id in tdef_exprs:
        expr = tdef_exprs[id]
      elif not vdef.getAutomaticUpdate() and variable_reference in former_status:
        # Preserve former value
        value = former_status[variable_reference]
      else:
        if vdef.getDefaultExpr() is not None:
          expr = vdef.getDefaultExpr()
        else:
          value = vdef.getInitialValue(object=object)
      if expr is not None and expr != '':
        # Evaluate an expression.
        if econtext is None:
          # Lazily create the expression context.
          if sci is None:
            kwargs = form_kw
            sci = StateChangeInfo(
                document, self, former_status, tdef,
                old_sdef, new_sdef, kwargs)
          econtext = createExprContext(sci)
        expr = Expression(expr)
        value = expr(econtext)
      if value is None: value = ''
      status_dict[variable_reference] = value
    # Do not proceed in case of failure of before script
    if not before_script_success:
      status_dict[state_var] = old_state # Remain in state
      tool.setStatusOf(self.getReference(), document, status_dict)
      sci = StateChangeInfo(
        document, self, former_status, tdef, old_sdef, new_sdef, kwargs)
      # put the error message in the workflow history
      sci.setWorkflowVariable(error_message=before_script_error_message)
      if validation_exc :
        # reraise validation failed exception
        raise validation_exc, None, validation_exc_traceback
      return new_sdef

    # update state
    status_dict[state_var] = new_state
    object = self.getStateChangeInformation(document, current_state_value, transition=self)

    tool.setStatusOf(self.getReference(), document, status_dict)
    self.updateRoleMappingsFor(document)

    # Execute the "after" script.
    if tdef is not None and tdef.getAfterScriptIdList():
      script_id_list = tdef.getAfterScriptIdList()
      kwargs = form_kw
      sci = StateChangeInfo(
                document, self, former_status, tdef, old_sdef, new_sdef, kwargs)
      for script_id in script_id_list:
        script = self._getOb(script_id, None)
        if script:
          # Script can be either script or workflow method
          if script_id in old_sdef.getDestinationIdList() and \
              self._getOb(script_id).getTriggerType() == TRIGGER_WORKFLOW_METHOD:
            getattr(document, convertToMixedCase(self._getOb(script_id).getReference()))()
          else:
            # Pass lots of info to the script in a single parameter.
            if script.getPortalType() == 'Workflow Script':
              script(sci)  # May throw an exception.

    # Return the new state object.
    if moved_exc is not None:
        # Propagate the notification that the object has moved.
        raise moved_exc
    else:
        return new_sdef

  def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
    '''
    Allows the user to request a workflow action.  This method
    must perform its own security checks.
    '''
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
        raise WorkflowException, 'Object is in an undefined state'
    if method_id not in sdef.getTransitionIdList():
        raise Unauthorized(method_id)
    tdef = self.getTransitionValueList().get(method_id, None)
    if tdef is None or tdef.getTriggerType() != TRIGGER_WORKFLOW_METHOD:
        raise WorkflowException, (
            'Transition %s is not triggered by a workflow method'
            % method_id)
    if not self._checkTransitionGuard(tdef, ob):
        raise Unauthorized(method_id)
    res = func(*args, **kw)
    try:
        self._changeStateOf(ob, tdef, kw)
    except ObjectDeleted:
        # Re-raise with a different result.
        raise ObjectDeleted(res)
    except ObjectMoved, ex:
        # Re-raise with a different result.
        raise ObjectMoved(ex.getNewObject(), res)
    return res

  def addTransition(self, name):
    tr = self.newContent(portal_type='Transition')
    tr.setReference(name)

  def deleteTransitions(self, name_list):
    for name in name_list:
      self._delObject('transition_'+name)

  def showAsXML(self, root=None):
    if root is None:
      root = Element('erp5')
      return_as_object = False

    # Define a list of property to show to users:
    workflow_prop_id_to_show = ['description', 'state_var',
      'permissions', 'initial_state']

    # workflow as XML, need to rename DC workflow's portal_type before comparison.
    workflow = SubElement(root, 'workflow',
                        attrib=dict(reference=self.getReference(),
                        portal_type=self.getPortalType()))

    for prop_id in sorted(workflow_prop_id_to_show):
      # In most case, we should not synchronize acquired properties
      if prop_id not in ('uid', 'workflow_history', 'id', 'portal_type',):
        if prop_id == 'permissions':
          value = tuple(self.getProperty('workflow_managed_permission_list'))
          prop_type = self.getPropertyType('workflow_managed_permission_list')
        elif prop_id == 'initial_state':
          if self.getSourceValue() is not None:
            value = self.getSourceValue().getReference()
          else:
            value = ''
          prop_type = 'string'
        elif prop_id =='state_var':
          value = self.getProperty('state_variable')
          prop_type = self.getPropertyType('state_variable')
        else:
          value = self.getProperty(prop_id)
          prop_type = self.getPropertyType(prop_id)
        if value is None or value ==() or value == ():
          value = ''
        sub_object = SubElement(workflow, prop_id, attrib=dict(type=prop_type))
        sub_object.text = str(value)

    # 1. State as XML
    state_reference_list = []
    state_list = self.objectValues(portal_type='State')
    # show reference instead of id
    state_prop_id_to_show = ['description',
      'transitions', 'permission_roles']
    for sdef in state_list:
      state_reference_list.append(sdef.getReference())
    states = SubElement(workflow, 'states', attrib=dict(state_list=str(state_reference_list),
                        number_of_element=str(len(state_reference_list))))
    for sdef in state_list:
      state = SubElement(states, 'state', attrib=dict(reference=sdef.getReference(), portal_type=sdef.getPortalType()))
      for property_id in sorted(state_prop_id_to_show):
        if property_id == 'permission_roles':
          property_value = sdef.getProperty('state_permission_roles')
          property_type = sdef.getPropertyType('state_permission_roles')
        elif property_id == 'transitions':
          property_value = sdef.getDestinationIdList()
          destination_list = []
          for tr_id in property_value:
            destination_list.append(self._getOb(tr_id).getReference())
          property_value = tuple(destination_list)
          property_type = 'multiple selection'
        else:
          property_value = sdef.getProperty(property_id)
          property_type = sdef.getPropertyType(property_id)

        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object = SubElement(state, property_id, attrib=dict(type=property_type))
        sub_object.text = str(property_value)

    # 2. Transition as XML
    transition_reference_list = []
    transition_list = self.objectValues(portal_type='Transition')
    transition_prop_id_to_show = ['description', 'new_state_id',
      'trigger_type', 'script_name', 'after_script_name', 'actbox_category',
      'actbox_icon', 'actbox_name', 'actbox_url', 'roles', 'groups',
      'permissions', 'expr', 'transition_variable']
    for tdef in self.objectValues(portal_type='Transition'):
      transition_reference_list.append(tdef.getReference())
    transitions = SubElement(workflow, 'transitions',
          attrib=dict(transition_list=str(transition_reference_list),
          number_of_element=str(len(transition_reference_list))))
    for tdef in transition_list:
      transition = SubElement(transitions, 'transition',
            attrib=dict(reference=tdef.getReference(),
            portal_type=tdef.getPortalType()))
      guard = SubElement(transition, 'guard', attrib=dict(type='object'))
      transition_variables = SubElement(transition, 'transition_variables', attrib=dict(type='object'))
      for property_id in sorted(transition_prop_id_to_show):
        if property_id in ('roles', 'groups', 'permissions', 'expr',):
          if property_id == 'roles':
            property_value = tdef.getRoleList()
          if property_id == 'groups':
            property_value = tdef.getGroupList()
          if property_id == 'permissions':
            property_value = tdef.getPermissionList()
          if property_id == 'expr':
            property_value = tdef.getExpression()
          if property_value is None or property_value == [] or property_value == ():
            property_value = ''
          elif property_id != 'expr':
            property_value = tuple(property_value)
          sub_object = SubElement(guard, property_id, attrib=dict(type='guard configuration'))
        else:
          if property_id == 'new_state_id':
            if tdef.getDestinationValue() is not None:
              property_value = tdef.getDestinationValue().getReference()
            else:
              property_value = ''
            sub_object = SubElement(transition, property_id, attrib=dict(type='string'))
          elif property_id == 'script_name':
            property_value = tdef.getBeforeScriptIdList()
            if property_value == [] or property_value is None:
              property_value = ''
            else:
              property_value = self._getOb(tdef.getBeforeScriptIdList()[0]).getReference()
            sub_object = SubElement(transition, property_id, attrib=dict(type='string'))
          elif property_id == 'after_script_name':
            property_value = tdef.getAfterScriptIdList()
            if property_value == [] or property_value is None:
              property_value = ''
            else:
              property_value = self._getOb(tdef.getAfterScriptIdList()[0]).getReference()
            sub_object = SubElement(transition, property_id, attrib=dict(type='string'))
          elif property_id =='transition_variable':
            tr_var_list = tdef.objectValues(portal_type='Transition Variable')
            for tr_var in tr_var_list:
              reference = self._getOb(tr_var.getCausalityId()).getReference()
              transition_variable = SubElement(transition_variables, property_id, attrib=dict(id=reference,type='variable'))
              transition_variable.text = str(tr_var.getDefaultExpr())
          else:
            property_value = tdef.getProperty(property_id)
            property_type = tdef.getPropertyType(property_id)
            sub_object = SubElement(transition, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)

    # 3. Variable as XML
    variable_reference_list = []
    variable_list = self.objectValues(portal_type='Variable')
    variable_prop_id_to_show = ['description', 'default_expr',
          'for_catalog', 'for_status', 'update_always']
    for vdef in variable_list:
      variable_reference_list.append(vdef.getReference())
    variables = SubElement(workflow, 'variables', attrib=dict(variable_list=str(variable_reference_list),
                        number_of_element=str(len(variable_reference_list))))
    for vdef in variable_list:
      variable = SubElement(variables, 'variable', attrib=dict(reference=vdef.getReference(),
            portal_type=vdef.getPortalType()))
      for property_id in sorted(variable_prop_id_to_show):
        if property_id == 'update_always':
          property_value = vdef.getAutomaticUpdate()
          sub_object = SubElement(variable, property_id, attrib=dict(type='int'))
        elif property_id == 'default_value':
          property_value = vdef.getInitialValue()
          if vdef.getInitialValue() is not None:
            property_value = vdef.getInitialValue()
          sub_object = SubElement(variable, property_id, attrib=dict(type='string'))
        else:
          property_value = vdef.getProperty(property_id)
          property_type = vdef.getPropertyType(property_id)
          sub_object = SubElement(variable, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)
        # for a very specific case, action return the reference of transition,
        # but in XML should show the same expression as in DC workflow.
        if vdef.getId() == 'variable_action' and property_id == 'default_expr' and property_value != '':
          sub_object.text = str('transition/getId|nothing')

    # 4. Worklist as XML
    worklist_reference_list = []
    worklist_list = self.objectValues(portal_type='Worklist')
    worklist_prop_id_to_show = ['description', 'matched_portal_type_list',
          'matched_validation_state_list', 'matched_simulation_state_list',
          'actbox_category', 'actbox_name', 'actbox_url', 'actbox_icon',
          'roles', 'groups', 'permissions', 'expr']
    for qdef in worklist_list:
      worklist_reference_list.append(qdef.getReference())
    worklists = SubElement(workflow, 'worklists', attrib=dict(worklist_list=str(worklist_reference_list),
                        number_of_element=str(len(worklist_reference_list))))
    for qdef in worklist_list:
      worklist = SubElement(worklists, 'worklist', attrib=dict(reference=qdef.getReference(),
      portal_type=qdef.getPortalType()))
      guard = SubElement(worklist, 'guard', attrib=dict(type='object'))
      for property_id in sorted(worklist_prop_id_to_show):
         # show guard configuration:
        if property_id in ('roles', 'groups', 'permissions', 'expr',):
          if property_id == 'roles':
            property_value = qdef.getRoleList()
          if property_id == 'groups':
            property_value = qdef.getGroupList()
          if property_id == 'permissions':
            property_value = qdef.getPermissionList()
          if property_id == 'expr':
            property_value = qdef.getExpression()
          if property_value is not None:
            property_value = tuple(property_value)
          sub_object = SubElement(guard, property_id, attrib=dict(type='guard configuration'))
        else:
          property_value = qdef.getProperty(property_id)
          state_ref_list = []
          if property_id in ('matched_validation_state_list',
              'matched_simulation_state_list',) and property_value is not None:
            for sid in property_value:
              state_ref = self._getOb(sid).getReference()
              state_ref_list.append(state_ref)
            property_value = tuple(state_ref_list)
          if property_id == 'matched_portal_type_list':
            if property_value is not None:
              property_value = tuple(property_value)
          property_type = qdef.getPropertyType(property_id)
          sub_object = SubElement(worklist, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)

    # 5. Script as XML
    script_reference_list = []
    script_list = self.objectValues(portal_type='Workflow Script')
    script_prop_id_to_show = sorted(['body', 'parameter_signature','proxy_roles'])
    for sdef in script_list:
      script_reference_list.append(sdef.getReference())
    scripts = SubElement(workflow, 'scripts', attrib=dict(script_list=str(script_reference_list),
                        number_of_element=str(len(script_reference_list))))
    for sdef in script_list:
      script = SubElement(scripts, 'script', attrib=dict(reference=sdef.getReference(),
        portal_type=sdef.getPortalType()))
      for property_id in script_prop_id_to_show:
        if property_id == 'proxy_roles':
          property_value = tuple(sdef.getProperty('proxy_role_list'))
          property_type = sdef.getPropertyType('proxy_role_list')
        else:
          property_value = sdef.getProperty(property_id)
          property_type = sdef.getPropertyType(property_id)
        sub_object = SubElement(script, property_id, attrib=dict(type=property_type))
        sub_object.text = str(property_value)

    # return xml object
    if return_as_object:
      return root
    return etree.tostring(root, encoding='utf-8',
                          xml_declaration=True, pretty_print=True)

  # Get list of portal types for workflow
  def getPortalTypeListForWorkflow(self):
    """
      Get list of portal types for workflow.
    """
    result = []
    workflow_id = self.getId()
    for portal_type in self.getPortalObject().portal_types.objectValues():
      if workflow_id in portal_type.getTypeWorkflowList():
        result.append(portal_type.getId())
    return result

  def _executeMetaTransition(self, ob, new_state_id):
    """
    Allow jumping from state to another without triggering any hooks.
    Must be used only under certain conditions.
    """
    sci = None
    econtext = None
    tdef = None
    kwargs = None
    new_state_id_no_prefix = new_state_id
    new_state_id = 'state_' + new_state_id
    # Figure out the old and new states.
    old_sdef = self._getWorkflowStateOf(ob)
    if old_sdef is None:
      old_state = self._getWorkflowStateOf(ob, id_only=True)
    else:
      old_state = old_sdef.getId()
    if old_state == new_state_id:
      # Object is already in expected state
      return
    former_status = self.getCurrentStatusDict(ob)

    new_sdef = self._getOb(new_state_id, None)
    if new_sdef is None:
      raise WorkflowException, ('Destination state undefined: ' + new_state_id)

    # Update variables.
    state_values = self.getVariableValueList()
    if state_values is None:
      state_values = {}

    tdef_exprs = {}
    status = {}
    for id, vdef in self.getVariableValueList().items():
      if vdef.getForStatus() == 0:
        continue
      expr = None
      if state_values.has_key(id):
        value = state_values[id]
      elif tdef_exprs.has_key(id):
        expr = tdef_exprs[id]
      elif not vdef.getAutomaticUpdate() and former_status.has_key(id):
        # Preserve former value
        value = former_status[id]
      else:
        default_expr = vdef.getDefaultExpr()
        if default_expr is not None:
          expr = Expression(default_expr)
        else:
          value = vdef.getInitialValue()
      if expr is not None:
        # Evaluate an expression.
        if econtext is None:
          # Lazily create the expression context.
          if sci is None:
            sci = StateChangeInfo(ob, self, former_status, tdef, old_sdef,
                                  new_sdef, kwargs)
          econtext = createExprContext(sci)
        value = expr(econtext)
      status[id] = value

    status['comment'] = 'Jump from %r to %r' % (self._getOb(old_state).getReference(), new_state_id_no_prefix,)
    status[self.getStateVariable()] = new_state_id_no_prefix
    tool = self.getParent()
    tool.setStatusOf(self.getId(), ob, status)

    # Update role to permission assignments.
    self.updateRoleMappingsFor(ob)
    return new_sdef

  security.declarePrivate('allowCreate')
  def allowCreate(self, container, type_name):
      """Returns true if the user is allowed to create a workflow instance.

      The object passed to the guard is the prospective container.

      wenjie: This is a compatibility related patch.

      More detail see TypeTool.pyline 360.
      """
      return 1

  def getCatalogVariablesFor(self, ob):
      '''
      Allows this workflow to make workflow-specific variables
      available to the catalog, making it possible to implement
      worklists in a simple way.
      Returns a mapping containing the catalog variables
      that apply to ob.
      '''
      initial_state = None
      res = {}
      # Always provide the state variable.
      state_var = self.getStateVariable()
      status = self.getCurrentStatusDict(ob)
      for vdef_ref, vdef in self.getVariableValueList().iteritems():
          if vdef.getForCatalog():
              default_expr = vdef.getDefaultExpr()
              if status.has_key(vdef_ref):
                  value = status[vdef_ref]

              # Not set yet.  Use a default.
              elif default_expr is not None:
                  ec = createExprContext(StateChangeInfo(ob, self, status))
                  # convert string to expression before execute it.
                  value = Expression(default_expr)(ec)
              else:
                  value = vdef.getInitialValue()
      if hasattr(self, 'getSourceValue'):
        if self.getSourceValue() is not None:
          initial_state = self.getSourceValue().getReference()
      if state_var is not None:
        res[state_var] = status.get(state_var, initial_state)
      return res

def Guard_checkWithoutRoles(self, sm, wf_def, ob, **kw):
    """Checks conditions in this guard.
       This function is the same as Guard.check, but roles are not taken
       into account here (but taken into account as local roles). This version
       is for worklist guards.

       Note that this patched version is not a monkey patch on the class,
       because we only want this specific behaviour for worklists (Guards are
       also used in transitions).
    """
    u_roles = None
    if wf_def.manager_bypass:
        # Possibly bypass.
        u_roles = sm.getUser().getRolesInContext(ob)
        if 'Manager' in u_roles:
            return 1
    if self.permissions:
        for p in self.permissions:
            if _checkPermission(p, ob):
                break
        else:
            return 0
    if self.groups:
        # Require at least one of the specified groups.
        u = sm.getUser()
        b = aq_base( u )
        if hasattr( b, 'getGroupsInContext' ):
            u_groups = u.getGroupsInContext( ob )
        elif hasattr( b, 'getGroups' ):
            u_groups = u.getGroups()
        else:
            u_groups = ()
        for group in self.groups:
            if group in u_groups:
                break
        else:
            return 0
    expr = self.expr
    if expr is not None:
        econtext = createExprContext(
            StateChangeInfo(ob, wf_def, kwargs=kw))
        res = expr(econtext)
        if not res:
            return 0
    return 1
