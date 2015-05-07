# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005,2015 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import sys
from Acquisition import aq_base
from AccessControl import getSecurityManager, ModuleSecurityInfo, Unauthorized
from copy import deepcopy
from DateTime import DateTime
from DocumentTemplate.DT_Util import TemplateDict
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.DCWorkflow import DCWorkflow
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition,\
                              StateChangeInfo, createExprContext,\
                              ObjectDeleted, ObjectMoved, aq_parent, aq_inner
from Products.DCWorkflow.Guard import Guard, _checkPermission
from Products.DCWorkflow.States import StateDefinition
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD,\
                                      TransitionDefinition, TRIGGER_USER_ACTION
from Products.DCWorkflow.Variables import VariableDefinition
from Products.DCWorkflow.Worklists import WorklistDefinition
from Products.DCWorkflow.WorkflowUIMixin import WorkflowUIMixin as WorkflowUIMixin_class
from Products.ERP5Type import _dtmldir
# Optimized rendering of global actions (cache)
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Globals import DTMLFile
# Patch WorkflowUIMixin to add description on workflows
from Products.ERP5Type.Utils import convertToMixedCase
from zLOG import LOG, WARNING

ACTIVITY_GROUPING_COUNT = 100

def WorkflowUIMixin_setProperties( self, title
                                 , description='' # the only addition to WorkflowUIMixin.setProperties
                                 , manager_bypass=0, props=None, REQUEST=None):
  """Sets basic properties.
  """
  self.title = str(title)
  self.description = str(description)
  self.manager_bypass = manager_bypass and 1 or 0
  g = Guard()
  if g.changeFromProperties(props or REQUEST):
      self.creation_guard = g
  else:
      self.creation_guard = None
  if REQUEST is not None:
      return self.manage_properties(
          REQUEST, manage_tabs_message='Properties changed.')

WorkflowUIMixin_class.setProperties = WorkflowUIMixin_setProperties
WorkflowUIMixin_class.manage_properties = DTMLFile('workflow_properties', _dtmldir)

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

def DCWorkflowDefinition_listGlobalActions(self, info):
    '''
    Allows this workflow to
    include actions to be displayed in the actions box.
    Called on every request.
    Returns the actions to be displayed to the user.
    '''
    if not self.worklists:
      return None  # Optimization
    _getPortalTypeListForWorkflow = CachingMethod(self.getPortalTypeListForWorkflow,
                                                  id=('_getPortalTypeListForWorkflow', self.id),
                                                  cache_factory = 'erp5_ui_long')
    portal_type_list = _getPortalTypeListForWorkflow()
    if not portal_type_list:
      return None

    def _listGlobalActions(user=None, id=None, portal_path=None):
      portal = self._getPortalRoot()
      portal_url = portal.portal_url
      portal_url = portal_url()
      sm = getSecurityManager()
      res = []
      fmt_data = None
      # We want to display some actions depending on the current date
      # So, we can now put this kind of expression : <= "%(now)s"
      # May be this patch should be moved to listFilteredActions in the future
      info.now = DateTime()
      for id, qdef in self.worklists.items():
          if qdef.actbox_name:
            guard = qdef.guard
            # Patch for ERP5 by JP Smets in order
            # to take into account the expression of the guard
            # and nothing else - ERP5Workflow definitely needed some day
            if guard is None or Guard_checkWithoutRoles(
                                          guard, sm, self, portal):
              dict = {}
              # Patch for ERP5 by JP Smets in order
              # to implement worklists and search of local roles
              searchres_len = 0
              var_match_keys = qdef.getVarMatchKeys()
              if var_match_keys:
                  # Check the catalog for items in the worklist.
                  catalog = portal.portal_catalog
                  for k in var_match_keys:
                    v = qdef.getVarMatch(k)
                    if isinstance(v, Expression):
                      v_fmt = v(createExprContext(StateChangeInfo(portal,
                                self, kwargs=info.__dict__.copy())))
                    else:
                      v_fmt = map(lambda x, info=info: x%info, v)
                    dict[k] = v_fmt
                  # Patch to automatically filter workflists per portal type
                  # so that the same state can be used for different
                  # worklists and they are not merged
                  if not dict.has_key('portal_type'):
                    dict['portal_type'] = portal_type_list
                  # Patch for ERP5 by JP Smets in order
                  # to implement worklists and search of local roles
                  # we do not take into account the guard here
                  if guard is not None and guard.roles:
                    dict['local_roles'] = guard.roles
                  # Patch to use ZSQLCatalog and get high speed
                  # LOG("PatchedDCWorkflowDefinition", 0, dict)
                  searchres_len = int(apply(catalog.countResults, (), dict)[0][0])
                  if searchres_len == 0:
                    continue
              if fmt_data is None:
                  fmt_data = TemplateDict()
                  fmt_data._push(info)
              # Patches for ERP5 by JP Smets:
              # - add "portal_type" to filter per portal type more easily
              #   (ie. without hardcoding it all)
              # - "local_roles" to allow filtering by local roles
              if 'local_roles' in dict:
                local_roles = '&local_roles='.join(dict['local_roles'])
              else:
                local_roles = ''
              fmt_data._push({
                  'count': searchres_len,
                  'portal_type': '&portal_type='.join(dict['portal_type']),
                  'local_roles': local_roles,
              })
              res.append((id, {'name': qdef.actbox_name % fmt_data,
                              'url': '%s/%s' % (portal_url, qdef.actbox_url % fmt_data),
                              'worklist_id': id,
                              'workflow_title': self.title,
                              'workflow_id': self.id,
                              'permissions': (),  # Predetermined.
                              'category': qdef.actbox_category}))
              fmt_data._pop()
      res.sort()
      return map((lambda (id, val): val), res)

    # Return Cache
    _listGlobalActions = CachingMethod(_listGlobalActions, id='listGlobalActions', cache_factory = 'erp5_ui_short')
    user = str(_getAuthenticatedUser(self))
    return _listGlobalActions(user=user, id=self.id, portal_path=self._getPortalRoot().getPhysicalPath())

DCWorkflowDefinition.listGlobalActions = DCWorkflowDefinition_listGlobalActions

# Patches over original listObjectActions:
# - Factorise consecutive tests.
# - Add "transition_id" when rendering name, url and icon properties.
def DCWorkflowDefinition_listObjectActions(self, info):
    '''
    Allows this workflow to
    include actions to be displayed in the actions box.
    Called only when this workflow is applicable to
    info.object.
    Returns the actions to be displayed to the user.
    '''
    fmt_data = None
    ob = info.object
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
        return None
    res = []
    for tid in sdef.transitions:
        tdef = self.transitions.get(tid, None)
        if tdef is not None and tdef.trigger_type == TRIGGER_USER_ACTION and \
                tdef.actbox_name and self._checkTransitionGuard(tdef, ob):
            if fmt_data is None:
                fmt_data = TemplateDict()
                fmt_data._push(info)
            fmt_data._push({'transition_id': tid})
            res.append((tid, {
                'id': tid,
                'name': tdef.actbox_name % fmt_data,
                'url': tdef.actbox_url % fmt_data,
                'icon': tdef.actbox_icon % fmt_data,
                'permissions': (),  # Predetermined.
                'category': tdef.actbox_category,
                'transition': tdef}))
            fmt_data._pop()
    res.sort()
    return [ result[1] for result in res ]
DCWorkflowDefinition.listObjectActions = DCWorkflowDefinition_listObjectActions

from Products.DCWorkflow.Expression import Expression

from Products.ERP5Type.patches.WorkflowTool import SECURITY_PARAMETER_ID, WORKLIST_METADATA_KEY
def DCWorkflowDefinition_getWorklistVariableMatchDict(self, info,
                                                      check_guard=True):
  """
    Return a dict which has an entry per worklist definition
    (worklist id as key) and which value is a dict composed of
    variable matches.
  """
  if not self.worklists:
    return None

  portal = self.getPortalObject()
  def getPortalTypeListForWorkflow(workflow_id):
      workflow_tool = portal.portal_workflow
      result = []
      append = result.append
      for type_info in workflow_tool._listTypeInfo():
        portal_type = type_info.id
        if workflow_id in workflow_tool.getChainFor(portal_type):
          append(portal_type)
      return result

  _getPortalTypeListForWorkflow = CachingMethod(getPortalTypeListForWorkflow,
                            id='_getPortalTypeListForWorkflow', cache_factory = 'erp5_ui_long')
  portal_type_list = _getPortalTypeListForWorkflow(self.id)
  if not portal_type_list:
    return None
  variable_match_dict = {}
  security_manager = getSecurityManager()
  workflow_id = self.id
  workflow_title = self.title
  for worklist_id, worklist_definition in self.worklists.items():
    action_box_name = worklist_definition.actbox_name
    guard = worklist_definition.guard
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
        portal_type_intersection = set(variable_match['portal_type'])\
            .intersection(portal_type_list)
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
        format_data = TemplateDict()
        format_data._push(info)
        variable_match.setdefault(SECURITY_PARAMETER_ID, ())
        format_data._push({k: ('&%s:list=' % k).join(v)
                           for k, v in variable_match.iteritems()})
        variable_match[WORKLIST_METADATA_KEY] = {'format_data': format_data,
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

DCWorkflowDefinition.getWorklistVariableMatchDict = DCWorkflowDefinition_getWorklistVariableMatchDict

class ValidationFailed(Exception):
    """Transition can not be executed because data is not in consistent state"""
    __allow_access_to_unprotected_subobjects__ = {'msg': 1}
    def __init__(self, message_instance=None):
        """
        Redefine init in order to register the message class instance
        """
        Exception.__init__(self, message_instance)
        self.msg = message_instance

DCWorkflow.ValidationFailed = ValidationFailed

ModuleSecurityInfo('Products.DCWorkflow.DCWorkflow').declarePublic('ValidationFailed')

# Patch excecuteTransition from DCWorkflowDefinition, to put ValidationFailed
# error messages in workflow history.
def DCWorkflowDefinition_executeTransition(self, ob, tdef=None, kwargs=None):
    '''
    Private method.
    Puts object in a new state.
    '''
    sci = None
    econtext = None
    moved_exc = None
    validation_exc = None

    # Figure out the old and new states.
    old_state = self._getWorkflowStateOf(ob, True)
    if tdef is None:
        new_state = self.initial_state
        if not new_state:
            # Do nothing if there is no initial state. We may want to create
            # workflows with no state at all, only for worklists.
            return
        former_status = {}
    else:
        new_state = tdef.new_state_id or old_state
        former_status = self._getStatusOf(ob)
    old_sdef = self.states[old_state]
    try:
        new_sdef = self.states[new_state]
    except KeyError:
        raise WorkflowException('Destination state undefined: ' + new_state)

    # Execute the "before" script.
    before_script_success = 1
    if tdef is not None and tdef.script_name:
        script = self.scripts[tdef.script_name]
        # Pass lots of info to the script in a single parameter.
        sci = StateChangeInfo(
            ob, self, former_status, tdef, old_sdef, new_sdef, kwargs)
        try:
            #LOG('_executeTransition', 0, "script = %s, sci = %s" % (repr(script), repr(sci)))
            script(sci)  # May throw an exception.
        except ValidationFailed, validation_exc:
            before_script_success = 0
            before_script_error_message = deepcopy(validation_exc.msg)
            validation_exc_traceback = sys.exc_traceback
        except ObjectMoved, moved_exc:
            ob = moved_exc.getNewObject()
            # Re-raise after transition

    # Update variables.
    state_values = new_sdef.var_values
    if state_values is None: state_values = {}
    tdef_exprs = None
    if tdef is not None: tdef_exprs = tdef.var_exprs
    if tdef_exprs is None: tdef_exprs = {}
    status = {}
    for id, vdef in self.variables.items():
        if not vdef.for_status:
            continue
        expr = None
        if state_values.has_key(id):
            value = state_values[id]
        elif tdef_exprs.has_key(id):
            expr = tdef_exprs[id]
        elif not vdef.update_always and former_status.has_key(id):
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
                    sci = StateChangeInfo(
                        ob, self, former_status, tdef,
                        old_sdef, new_sdef, kwargs)
                econtext = createExprContext(sci)
            value = expr(econtext)
        status[id] = value

    # Do not proceed in case of failure of before script
    if not before_script_success:
        status[self.state_var] = old_state # Remain in state
        tool = aq_parent(aq_inner(self))
        tool.setStatusOf(self.id, ob, status)
        sci = StateChangeInfo(
            ob, self, status, tdef, old_sdef, new_sdef, kwargs)
        # put the error message in the workflow history
        sci.setWorkflowVariable(error_message=before_script_error_message)
        if validation_exc :
            # reraise validation failed exception
            raise validation_exc, None, validation_exc_traceback
        return new_sdef

    # Update state.
    status[self.state_var] = new_state
    tool = aq_parent(aq_inner(self))
    tool.setStatusOf(self.id, ob, status)

    # Update role to permission assignments.
    self.updateRoleMappingsFor(ob)

    # Execute the "after" script.
    script = getattr(tdef, 'after_script_name', None)
    if script:
        # Script can be either script or workflow method
        #LOG('_executeTransition', 0, 'new_sdef.transitions = %s' % (repr(new_sdef.transitions)))
        if script in new_sdef.transitions and  \
           self.transitions[script].trigger_type == TRIGGER_WORKFLOW_METHOD:
          getattr(ob, convertToMixedCase(script))()
        else:
          script = self.scripts[script]
          # Pass lots of info to the script in a single parameter.
          sci = StateChangeInfo(
              ob, self, status, tdef, old_sdef, new_sdef, kwargs)
          script(sci)  # May throw an exception.

    # Return the new state object.
    if moved_exc is not None:
        # Propagate the notification that the object has moved.
        raise moved_exc
    else:
        return new_sdef

DCWorkflowDefinition._executeTransition = DCWorkflowDefinition_executeTransition
from Products.DCWorkflow.utils import modifyRolesForPermission

def _executeMetaTransition(self, ob, new_state_id):
  """
  Allow jumping from state to another without triggering any hooks.
  Must be used only under certain conditions.
  """
  sci = None
  econtext = None
  tdef = None
  kwargs = None
  # Figure out the old and new states.
  old_sdef = self._getWorkflowStateOf(ob)
  if old_sdef is None:
    old_state = self._getWorkflowStateOf(ob, id_only=True)
  else:
    old_state = old_sdef.getId()
  if old_state == new_state_id:
    # Object is already in expected state
    return
  former_status = self._getStatusOf(ob)

  new_sdef = self.states.get(new_state_id, None)
  if new_sdef is None:
    raise WorkflowException, ('Destination state undefined: ' + new_state_id)

  # Update variables.
  state_values = new_sdef.var_values
  if state_values is None:
    state_values = {}

  tdef_exprs = {}
  status = {}
  for id, vdef in self.variables.items():
    if not vdef.for_status:
      continue
    expr = None
    if state_values.has_key(id):
      value = state_values[id]
    elif tdef_exprs.has_key(id):
      expr = tdef_exprs[id]
    elif not vdef.update_always and former_status.has_key(id):
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
          sci = StateChangeInfo(ob, self, former_status, tdef, old_sdef,
                                new_sdef, kwargs)
        econtext = createExprContext(sci)
      value = expr(econtext)
    status[id] = value

  status['comment'] = 'Jump from %r to %r' % (old_state, new_state_id,)
  status[self.state_var] = new_state_id
  tool = aq_parent(aq_inner(self))
  tool.setStatusOf(self.id, ob, status)

  # Update role to permission assignments.
  self.updateRoleMappingsFor(ob)
  return new_sdef

DCWorkflowDefinition._executeMetaTransition = _executeMetaTransition

def DCWorkflowDefinition_wrapWorkflowMethod(self, ob, method_id, func, args, kw):
    '''
    Allows the user to request a workflow action.  This method
    must perform its own security checks.
    '''
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
        raise WorkflowException, 'Object is in an undefined state'
    if method_id not in sdef.transitions:
        raise Unauthorized(method_id)
    tdef = self.transitions.get(method_id, None)
    if tdef is None or tdef.trigger_type != TRIGGER_WORKFLOW_METHOD:
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

DCWorkflowDefinition.wrapWorkflowMethod = DCWorkflowDefinition_wrapWorkflowMethod

# Patch updateRoleMappingsFor so that if 2 workflows define security, then we
# should do an AND operation between each permission
def updateRoleMappingsFor(self, ob):
    '''
    Changes the object permissions according to the current
    state.
    '''
    changed = 0
    sdef = self._getWorkflowStateOf(ob)

    tool = aq_parent(aq_inner(self))
    other_workflow_list = \
       [x for x in tool.getWorkflowsFor(ob) if x.id != self.id and isinstance(x,DCWorkflowDefinition)]
    other_data_list = []
    for other_workflow in other_workflow_list:
      other_sdef = other_workflow._getWorkflowStateOf(ob)
      if other_sdef is not None and other_sdef.permission_roles is not None:
        other_data_list.append((other_workflow,other_sdef))
    # Be carefull, permissions_roles should not change
    # from list to tuple or vice-versa. (in modifyRolesForPermission,
    # list means acquire roles, tuple means do not acquire)
    if sdef is not None and self.permissions:
        for p in self.permissions:
            roles = []
            refused_roles = []
            role_type = 'list'
            other_role_type_list = []
            if sdef.permission_roles is not None:
                roles = sdef.permission_roles.get(p, roles)
                if type(roles) is type(()):
                  role_type = 'tuple'
                roles = list(roles)
            # We will check that each role is activated
            # in each DCWorkflow
            for other_workflow,other_sdef in other_data_list:
              if p in other_workflow.permissions:
                other_roles = other_sdef.permission_roles.get(p, [])
                if type(other_roles) is type(()) :
                  other_role_type_list.append('tuple')
                else:
                  other_role_type_list.append('list')
                for role in roles:
                  if role not in other_roles :
                    refused_roles.append(role)
            for role in refused_roles :
              if role in roles :
                roles.remove(role)
            if role_type == 'tuple' and ((not other_role_type_list) or ('list' not in other_role_type_list)):
              #If at least, one of other workflows manage security and for all are role_type are tuple
              roles = tuple(roles)
            if modifyRolesForPermission(ob, p, roles):
                changed = 1
    return changed

DCWorkflowDefinition.updateRoleMappingsFor = updateRoleMappingsFor

# This patch allows to update all objects using one workflow, for example
# after the permissions per state for this workflow were modified
def updateRoleMappings(self, REQUEST=None):
  """
  Changes permissions of all objects related to this workflow
  """
  wf_tool = aq_parent(aq_inner(self))
  chain_by_type = wf_tool._chains_by_type
  type_info_list = wf_tool._listTypeInfo()
  wf_id = self.id
  portal_type_list = []
  # get the list of portal types to update
  if wf_id in wf_tool._default_chain:
    include_default = 1
  else:
    include_default = 0
  for type_info in type_info_list:
    tid = type_info.getId()
    if chain_by_type.has_key(tid):
      if wf_id in chain_by_type[tid]:
        portal_type_list.append(tid)
    elif include_default == 1:
      portal_type_list.append(tid)
  if portal_type_list:
    object_list = self.portal_catalog(portal_type=portal_type_list, limit=None)
    object_list_len = len(object_list)
    portal_activities = self.portal_activities
    object_path_list = [x.path for x in object_list]
    for i in xrange(0, object_list_len, ACTIVITY_GROUPING_COUNT):
      current_path_list = object_path_list[i:i+ACTIVITY_GROUPING_COUNT]
      portal_activities.activate(activity='SQLQueue',
                                  priority=3)\
            .callMethodOnObjectList(current_path_list,
                                    'updateRoleMappingsFor',
                                    wf_id = self.getId())
  else:
    object_list_len = 0

  if REQUEST is not None:
    return self.manage_properties(REQUEST,
        manage_tabs_message='%d object(s) updated.' % object_list_len)
  else:
    return object_list_len

DCWorkflowDefinition.updateRoleMappings = updateRoleMappings

# this patch allows to get list of portal types for workflow
def getPortalTypeListForWorkflow(self):
  """
    Get list of portal types for workflow.
  """
  result = []
  workflow_id = self.id
  workflow_tool = getToolByName(self, 'portal_workflow')
  for type_info in workflow_tool._listTypeInfo():
    portal_type = type_info.id
    if workflow_id in workflow_tool.getChainFor(portal_type):
      result.append(portal_type)
  return result

DCWorkflowDefinition.getPortalTypeListForWorkflow = getPortalTypeListForWorkflow

def DCWorkflowDefinition_getFutureStateSet(self, state, ignore=(),
                                           _future_state_set=None):
  """Return the states that can be reached from a given state, directly or not.

  This method returns a set of ids of all states that can be reached in any
  number of transitions, starting from the state specified by the 'state'
  parameter. 'ignore' parameter is a list of states to ignore, as if there was
  no transition to them.
  """
  if _future_state_set is None:
    _future_state_set = set()
  _future_state_set.add(state)
  for transition in self.states[state].transitions:
    state = self.transitions[transition].new_state_id
    if state and state not in _future_state_set and state not in ignore:
      self.getFutureStateSet(state, ignore, _future_state_set)
  return _future_state_set

DCWorkflowDefinition.getFutureStateSet = DCWorkflowDefinition_getFutureStateSet

def DCWorkflowDefinition_getStateVariable(self):
  return self.state_var
DCWorkflowDefinition.getStateVariable = DCWorkflowDefinition_getStateVariable

def DCWorkflowDefinition_notifyWorkflowMethod(self, ob, transition_list, args=None, kw=None):
    '''
    Allows the system to request a workflow action.  This method
    must perform its own security checks.
    '''
    if type(transition_list) in StringTypes:
      method_id = transition_list
    elif len(transition_list) == 1:
      method_id = transition_list[0]
    else:
      raise ValueError('WorkflowMethod should be attached to exactly 1 transition per DCWorkflow instance.')
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
        raise WorkflowException, 'Object is in an undefined state'
    if method_id not in sdef.transitions:
        raise Unauthorized(method_id)
    tdef = self.transitions.get(method_id, None)
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

def DCWorkflowDefinition_notifyBefore(self, ob, transition_list, args=None, kw=None):
    '''
    Notifies this workflow of an action before it happens,
    allowing veto by exception.  Unless an exception is thrown, either
    a notifySuccess() or notifyException() can be expected later on.
    The action usually corresponds to a method name.
    '''
    pass

def DCWorkflowDefinition_notifySuccess(self, ob, transition_list, result, args=None, kw=None):
    '''
    Notifies this workflow that an action has taken place.
    '''
    pass

def method_getReference(self):
  return self.id

def DCWorkflowDefinition_getVariableValueList(self):
  if self.variables is not None:
    return self.variables
  return {}

def DCWorkflowDefinition_getVariableIdList(self):
  if self.variables is not None:
    return self.variables.objectIds()
  return []

def DCWorkflowDefinition_getStateValueList(self):
  if self.states is not None:
    return self.states
  return {}

def DCWorkflowDefinition_getStateIdList(self):
  if self.states is not None:
    return self.states.objectIds()
  return []

def DCWorkflowDefinition_getTransitionValueList(self):
  if self.transitions is not None:
    return self.transitions
  else:
    return {}

def DCWorkflowDefinition_getTransitionIdList(self):
  if self.transitions is not None:
    return self.transitions.objectIds()
  return []

def DCWorkflowDefinition_getWorklistValueList(self):
  if self.worklists is not None:
    return self.worklists
  return {}

def DCWorkflowDefinition_getWorklistIdList(self):
  if self.worklists is not None:
    return self.worklists.objectIds()
  return []

def StateDefinition_getDestinationIdList(self):
  return self.transitions

DCWorkflowDefinition.getReference = method_getReference
TransitionDefinition.getReference = method_getReference
StateDefinition.getReference = method_getReference
StateDefinition.getDestinationIdList = StateDefinition_getDestinationIdList
VariableDefinition.getReference = method_getReference
WorklistDefinition.getReference = method_getReference
DCWorkflowDefinition.notifyWorkflowMethod = DCWorkflowDefinition_notifyWorkflowMethod
DCWorkflowDefinition.notifyBefore = DCWorkflowDefinition_notifyBefore
DCWorkflowDefinition.notifySuccess = DCWorkflowDefinition_notifySuccess
DCWorkflowDefinition.getVariableValueList = DCWorkflowDefinition_getVariableValueList
DCWorkflowDefinition.getStateValueList = DCWorkflowDefinition_getStateValueList
DCWorkflowDefinition.getTransitionValueList = DCWorkflowDefinition_getTransitionValueList
DCWorkflowDefinition.getWorklistValueList = DCWorkflowDefinition_getWorklistValueList
DCWorkflowDefinition.getVariableIdList = DCWorkflowDefinition_getVariableIdList
DCWorkflowDefinition.getStateIdList = DCWorkflowDefinition_getStateIdList
DCWorkflowDefinition.getTransitionIdList = DCWorkflowDefinition_getTransitionIdList
DCWorkflowDefinition.getWorklistIdList = DCWorkflowDefinition_getWorklistIdList

# This patch allows to use workflowmethod as an after_script
# However, the right way of doing would be to have a combined state of TRIGGER_USER_ACTION and TRIGGER_WORKFLOW_METHOD
# as well as workflow inheritance. This way, different user actions and dialogs can be specified easliy
# For now, we split UI transitions and logics transitions so that UI can be different and logics the same

class ERP5TransitionDefinition (TransitionDefinition):
  """
    This class is only for backward compatibility.
  """
  pass

def getAvailableScriptIds(self):
  return self.getWorkflow().scripts.keys() + \
   [k for k in self.getWorkflow().transitions.keys() if \
   self.getWorkflow().transitions[k].trigger_type == TRIGGER_WORKFLOW_METHOD]

TransitionDefinition.getAvailableScriptIds = getAvailableScriptIds
