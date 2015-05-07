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
from DateTime import DateTime
from DocumentTemplate.DT_Util import TemplateDict
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException, ObjectDeleted,\
                                          ObjectMoved
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.DCWorkflowGraph.config import DOT_EXE
from Products.DCWorkflowGraph.DCWorkflowGraph import bin_search, getGraph
from Products.DCWorkflow.utils import Message as _
from Products.DCWorkflow.utils import modifyRolesForPermission
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition as DCWorkflow
from Products.ERP5.Tool import ERP5WorkflowTool
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.patches.Expression import Expression_createExprContext
from Products.ERP5Type.patches.WorkflowTool import SECURITY_PARAMETER_ID,\
                                                          WORKLIST_METADATA_KEY
from Products.ERP5Type.Utils import UpperCase, convertToMixedCase
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Workflow.Document.Transition import TRIGGER_AUTOMATIC,\
                                    TRIGGER_USER_ACTION, TRIGGER_WORKFLOW_METHOD
from tempfile import mktemp
from types import StringTypes
from zLOG import LOG, ERROR, DEBUG, WARNING

class Workflow(IdAsReferenceMixin("workflow_", "prefix"), XMLObject):
  """
  A ERP5 Workflow.
  """

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
    """
    Set initial state on the Document
    """
    state_var = self.getStateVariable()
    object = self.getStateChangeInformation(document, self.getSourceValue())

    # Initialize workflow history
    state_id = self.getSourceValue().getReference()
    status_dict = {state_var: state_id}
    variable_list = self.objectValues(portal_type='Variable')
    former_status = self._getOb(status_dict[state_var], None)
    ec = Expression_createExprContext(StateChangeInfo(document, self, former_status))

    for variable in variable_list:
      if variable.for_status == 0:
        continue
      if variable.default_expr is not None:
        expr = Expression(variable.default_expr)
        value = expr(ec)
      else:
        value = variable.getInitialValue(object=object)
      status_dict[variable.getReference()] = value

    self._updateWorkflowHistory(document, status_dict)
    self.updateRoleMappingsFor(document)

  def _generateHistoryKey(self):
    """
    Generate a key used in the workflow history.
    """
    history_key = self.unrestrictedTraverse(self.getRelativeUrl()).getId()
    return '_'.join(history_key.split('_')[1:])

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

  def isWorkflowMethodSupported(self, document, transition_id):
    transition = self._getOb('transition_' + transition_id)
    sdef = self._getWorkflowStateOf(document, id_only=0)
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
    sdef = self._getWorkflowStateOf(document, id_only=0)
    if sdef is None:
      return 0

    if action in sdef.getDestinationIdList():
      tdef = self._getOb(action, None)
      if (tdef is not None and
        tdef.trigger_type == TRIGGER_USER_ACTION and
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
      vdef = self.objectValues(portal_type='Variable').get(name, None)
      if vdef is None:
          return 0
      return 1

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

  def getRoleList(self):
    return sorted(self.getPortalObject().getDefaultModule('acl_users').valid_roles())

  security.declarePrivate('doActionFor')
  def doActionFor(self, document, action, *args, **kw):
    sdef = self._getWorkflowStateOf(document, id_only=0)
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
    if tdef is None or tdef.trigger_type != TRIGGER_USER_ACTION:
      msg = _(u"Transition '${action_id}' is not triggered by a user "
        u"action.", mapping={'action_id': action})
      raise WorkflowException(msg)
    if not self._checkTransitionGuard(tdef, document, **kw):
      raise Unauthorized(action)
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
        if tdef is not None and tdef.trigger_type == TRIGGER_USER_ACTION and \
                tdef.actbox_name and self._checkTransitionGuard(tdef, document):
            if fmt_data is None:
                fmt_data = TemplateDict()
                fmt_data._push(info)
            fmt_data._push({'transition_id': tid})
            res.append((tid, {
                'id': tid,
                'name': tdef.actbox_name % fmt_data,
                'url': str(tdef.actbox_url) % fmt_data,
                'icon': str(tdef.actbox_icon) % fmt_data,
                'permissions': (),  # Predetermined.
                'category': tdef.actbox_category,
                'transition': tdef}))
            fmt_data._pop()
            LOG("362 listing user action '%s'"%tid,WARNING," in Workflow.py")
      res.sort()

      return [ result[1] for result in res ]

  def getWorklistVariableMatchDict(self, info, check_guard=True):
    """
      Return a dict which has an entry per worklist definition
      (worklist id as key) and which value is a dict composed of
      variable matches.
    """
    if not info.object.getPortalType() in ['Workflow', 'Interaction Workflow']:
      # avoid getting DC workflow
      return

    if not self.objectValues(portal_type='Worklist'):
      return None

    portal = self.getPortalObject()
    def getPortalTypeListForWorkflow(workflow_id):
        workflow_tool = portal.portal_workflow
        result = []
        append = result.append
        for workflow_id in info.object.getTypeInfo().getTypeERP5WorkflowList():
            append(info.object.getTypeInfo().getId())
        return result

    portal_type_list = getPortalTypeListForWorkflow(self.id)
    if not portal_type_list:
      return None
    variable_match_dict = {}
    security_manager = getSecurityManager()
    workflow_id = self.id
    workflow_title = self.getTitle()
    for worklist_definition in self.objectValues(portal_type='Worklist'):
      worklist_id = worklist_definition.getId()
      action_box_name = worklist_definition.getActboxName()
      guard = worklist_definition.getGuard()
      if action_box_name:
        variable_match = {}
        for key in worklist_definition.getVarMatchKeys():
          var = worklist_definition.getVarMatch(key)
          if isinstance(var, Expression):
            evaluated_value = var(Expression_createExprContext(StateChangeInfo(portal,
                                  self, kwargs=info.__dict__.copy())))
            if isinstance(evaluated_value, (str, int, long)):
              evaluated_value = [str(evaluated_value)]
          else:
            evaluated_value = [str(x) % info for x in var]
          variable_match[key] = evaluated_value

        if 'portal_type' in variable_match and len(variable_match['portal_type']):
          portal_type_intersection = set(variable_match['portal_type']).intersection(portal_type_list)
          # in case the current workflow is not associated with portal_types
          # defined on the worklist, don't display the worklist for this
          # portal_type.
          LOG ('420 portal type list are: %s'%portal_type_list, WARNING, ' in Workflow.py')
          LOG ('421 matched portal type are: %s'%variable_match['portal_type'], WARNING, ' in Workflow.py')
          LOG ('422 len of intersection portal type are: %s'%len(portal_type_intersection), WARNING, ' in Workflow.py')
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
          fmt_data._push({(k, ('&%s:list=' % k).join(v)) for\
                                             k, v in variable_match.iteritems()})

          variable_match[WORKLIST_METADATA_KEY] = {
                                                'format_data': fmt_data,
                                                 'worklist_title': action_box_name,
                                                 'worklist_id': worklist_id,
                                                 'workflow_title': workflow_title,
                                                 'workflow_id': workflow_id,
                                                 'action_box_url': worklist_definition.actbox_url,
                                                 'action_box_category': worklist_definition.actbox_category}

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
      state_var = self.getStateVariable()
      if name == state_var:
          return ob._getDefaultAcquiredValue(state_var).getId()

      vdef = self._getOb(name)

      status_dict = self.getCurrentStatusDict(ob)
      former_status = self._getOb(status_dict[state_var], None)

      if former_status == None:
        former_status = self.getSourceValue()

      if vdef.info_guard is not None and not vdef.info_guard.check(
          getSecurityManager(), self, ob):
          return default

      if status_dict is not None and name in status_dict:
          value = status_dict[name]
      # Not set yet.  Use a default.
      if vdef.default_expr is not None:
          ec = Expression_createExprContext(StateChangeInfo(ob, self, former_status))
          expr = Expression(vdef.default_expr)
          value = expr(ec)
      else:
          value = vdef.default_value
      return value

  def _getWorkflowStateOf(self, ob, id_only=0):
      tool = getToolByName(self, 'portal_workflow')
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
    if tdef is None or tdef.trigger_type != TRIGGER_WORKFLOW_METHOD:
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
    status_dict['undo'] = 0

    if current_state_value == None:
      current_state_value = self.getSourceValue()
    old_state = current_state_value.getReference()
    old_sdef = current_state_value

    if tdef is None:
      new_sdef = self.getSourceValue()
      if not new_state:
        return
      former_status = {}
    else:
      new_sdef = tdef.getDestinationValue()
      if new_sdef == None:
        new_state = old_state
      else:
        new_state = new_sdef.getReference()
      former_status = current_state_value.getReference()

    # Execute the "before" script.
    before_script_success = 1
    if tdef is not None and tdef.getBeforeScriptId():
      script_id = tdef.getBeforeScriptId()
      if script_id:
        script = self._getOb(script_id)
        # Pass lots of info to the script in a single parameter.
        kwargs = form_kw
        sci = StateChangeInfo(
              document, self, former_status, tdef, old_sdef, new_sdef, kwargs)
        try:
          #LOG('_executeTransition', 0, "script = %s, sci = %s" % (repr(script), repr(sci)))
          script.execute(sci)  # May throw an exception.
        except ValidationFailed, validation_exc:
          before_script_success = 0
          before_script_error_message = deepcopy(validation_exc.msg)
          validation_exc_traceback = sys.exc_traceback
        except ObjectMoved, moved_exc:
          ob = moved_exc.getNewObject()
          # Re-raise after transition

    # update variables
    state_values = None
    if new_sdef is not None:
      state_values = getattr(new_sdef,'var_values', None)
    if state_values is None:
      state_values = {}

    if state_values is None: state_values = {}
    tdef_exprs = None
    if tdef is not None:
      tdef_exprs = tdef.objectValues(portal_type='Variable')
    if tdef_exprs is None: tdef_exprs = {}

    for vdef in self.objectValues(portal_type='Variable'):
      id = vdef.getId()
      id_no_suffix = vdef.getReference()
      if vdef.for_status == 0:
        continue
      expr = None
      if id_no_suffix in state_values:
        value = state_values[id_no_suffix]
      elif id in tdef_exprs:
        expr = tdef_exprs[id]
      elif not vdef.update_always and id in former_status:
        # Preserve former value
        value = former_status[id]
      else:
        if vdef.default_expr is not None:
          expr = vdef.default_expr
        else:
          value = vdef.default_value
      if expr is not None:
        # Evaluate an expression.
        if econtext is None:
          # Lazily create the expression context.
          if sci is None:
            kwargs = form_kw
            sci = StateChangeInfo(
                document, self, former_status, tdef,
                old_sdef, new_sdef, kwargs)
          econtext = Expression_createExprContext(sci)
        expr = Expression(expr)
        value = expr(econtext)
      if id_no_suffix == "action":
        status_dict[id_no_suffix] = '_'.join(value.split('_')[1:])
      else:
        status_dict[id_no_suffix] = value

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
    # Update all transition variables
    if form_kw is not None:
      object.REQUEST.other.update(form_kw)

    for variable in self.objectValues(portal_type='Transition Variable'):
      status_dict[variable.getCausalityTitle()] = variable.getInitialValue(object=object)

    tool.setStatusOf(self.getReference(), document, status_dict)
    self.updateRoleMappingsFor(document)

    # Execute the "after" script.
    script_id = getattr(tdef, 'getAfterScriptId')()
    if script_id is not None:
      kwargs = form_kw
      # Script can be either script or workflow method
      if script_id in old_sdef.getDestinationIdList() and \
          self._getOb(script_id).trigger_type == TRIGGER_WORKFLOW_METHOD:
        getattr(document, convertToMixedCase(self._getOb(script_id).getReference()))()
      else:
        script = self._getOb(script_id)
        # Pass lots of info to the script in a single parameter.
        if script.getTypeInfo().getId() == 'Workflow Script':
          sci = StateChangeInfo(
              document, self, former_status, tdef, old_sdef, new_sdef, kwargs)
          script.execute(sci)  # May throw an exception.
        else:
          raise NotImplementedError ('Unsupported Script %s for state %s'%(script_id, old_sdef.getReference()))
    # Return the new state object.
    if moved_exc is not None:
        # Propagate the notification that the object has moved.
        raise moved_exc
    else:
        return new_sdef

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
      for state in self.objectValues(portal_type='State'):
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
      for transition in self.objectValues(portal_type='Transition'):
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
