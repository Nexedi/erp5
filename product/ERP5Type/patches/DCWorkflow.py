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

# Optimized rendering of global actions (cache)

from collections import  defaultdict
from Products.ERP5Type.Globals import DTMLFile
from Products.ERP5Type import Permissions, _dtmldir
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition, StateChangeInfo, createExprContext
from Products.DCWorkflow.DCWorkflow import ObjectDeleted, ObjectMoved, aq_parent, aq_inner
from Products.DCWorkflow import DCWorkflow
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD, TransitionDefinition
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.DCWorkflow.permissions import ManagePortal
from AccessControl import getSecurityManager, ModuleSecurityInfo, Unauthorized
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import  _getAuthenticatedUser
from DocumentTemplate.DT_Util import TemplateDict
from DateTime import DateTime
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Utils import convertToMixedCase
import sys
from Acquisition import aq_base
from copy import deepcopy

# Patch WorkflowUIMixin to add description on workflows
from Products.DCWorkflow.WorkflowUIMixin import WorkflowUIMixin as WorkflowUIMixin_class
from Products.DCWorkflow.Guard import Guard, _checkPermission
from Products.DCWorkflow.States import StateDefinition
from Products.DCWorkflow.Variables import VariableDefinition
from Products.DCWorkflow.Worklists import WorklistDefinition
from types import StringTypes
from zLOG import LOG, INFO, WARNING
# Libraries related to showAsXML
from lxml import etree
from lxml.etree import Element, SubElement

ACTIVITY_GROUPING_COUNT = 100

_marker = ''

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
        return expr(createExprContext(StateChangeInfo(
            ob,
            wf_def,
            kwargs=kw,
        )))
    return 1

DCWorkflowDefinition.security = ClassSecurityInfo()

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
                  searchres_len = catalog.countResults(**dict)[0][0]
                  if not searchres_len:
                    continue
              else:
                  searchres_len = 0
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
    ob = info.object
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
        return ()
    fmt_data = None
    result = []
    for transition_id in sdef.transitions:
        tdef = self.transitions.get(transition_id)
        if (
            tdef is not None and
            tdef.trigger_type == TRIGGER_USER_ACTION and
            tdef.actbox_name and
            self._checkTransitionGuard(tdef, ob)
        ):
            if fmt_data is None:
                fmt_data = TemplateDict()
                fmt_data._push(info)
            fmt_data._push({'transition_id': transition_id})
            result.append({
                'id': transition_id,
                'name': tdef.actbox_name % fmt_data,
                'url': tdef.actbox_url % fmt_data,
                'icon': tdef.actbox_icon % fmt_data,
                'permissions': (),  # Predetermined.
                'category': tdef.actbox_category,
                'transition': tdef,
            })
            fmt_data._pop()
    result.sort(key=lambda x: x['id'])
    return result
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
  worklist_items = self.worklists.items()
  if not worklist_items:
    return None
  portal = self.getPortalObject()
  def getPortalTypeListByWorkflowIdDict():
    workflow_tool = portal.portal_workflow
    result = defaultdict(list)
    for type_info in workflow_tool._listTypeInfo():
      portal_type = type_info.id
      for workflow_id in type_info.getTypeWorkflowList():
        result[workflow_id].append(portal_type)
    return result
  portal_type_list = CachingMethod(
    getPortalTypeListByWorkflowIdDict,
    id='_getPortalTypeListByWorkflowIdDict',
    cache_factory='erp5_ui_long',
  )()[self.id]
  if not portal_type_list:
    return None
  portal_type_set = set(portal_type_list)
  variable_match_dict = {}
  security_manager = getSecurityManager()
  workflow_id = self.id
  workflow_title = self.title
  for worklist_id, worklist_definition in worklist_items:
    action_box_name = worklist_definition.actbox_name
    if action_box_name:
      variable_match = {}
      for key, var in (worklist_definition.var_matches or {}).iteritems():
        if isinstance(var, Expression):
          evaluated_value = var(createExprContext(StateChangeInfo(portal,
                                self, kwargs=info.__dict__.copy())))
          if isinstance(evaluated_value, (str, int, long)):
            evaluated_value = [str(evaluated_value)]
        else:
          if not isinstance(var, tuple):
            var = (var, )
          evaluated_value = [x % info for x in var]
        variable_match[key] = evaluated_value
      portal_type_match = variable_match.get('portal_type')
      if portal_type_match:
        # in case the current workflow is not associated with portal_types
        # defined on the worklist, don't display the worklist for this
        # portal_type.
        variable_match['portal_type'] = list(
          portal_type_set.intersection(portal_type_match)
        )
      if not variable_match.setdefault('portal_type', portal_type_list):
        continue
      guard = worklist_definition.guard
      if (
        guard is None or
        not check_guard or
        Guard_checkWithoutRoles(guard, security_manager, self, portal)
      ):
        format_data = TemplateDict()
        format_data._push(info)
        variable_match.setdefault(SECURITY_PARAMETER_ID, getattr(guard, 'roles', ()))
        format_data._push({
            k: ('&%s:list=' % k).join(v)
            for k, v in variable_match.iteritems()
        })
        variable_match[WORKLIST_METADATA_KEY] = {
            'format_data': format_data,
            'worklist_title': action_box_name,
            'worklist_id': worklist_id,
            'workflow_title': workflow_title,
            'workflow_id': workflow_id,
            'action_box_url': worklist_definition.actbox_url,
            'action_box_category': worklist_definition.actbox_category,
        }
        variable_match_dict[worklist_id] = variable_match

  if variable_match_dict:
    return variable_match_dict
  return None

DCWorkflowDefinition.security.declarePrivate('getWorklistVariableMatchDict')
DCWorkflowDefinition.getWorklistVariableMatchDict = DCWorkflowDefinition_getWorklistVariableMatchDict

def DCWorkflowDefinition_isWorkflowMethodSupported(self, ob, method_id, state=None):
    '''
    Returns a true value if the given workflow method
    is supported in the current state.
    '''
    if state is None:
      state = self._getWorkflowStateOf(ob)
    if state is None:
        return False
    if method_id in state.transitions:
        tdef = self.transitions.get(method_id, None)
        if (tdef is not None and
            tdef.trigger_type == TRIGGER_WORKFLOW_METHOD and
            self._checkTransitionGuard(tdef, ob)):
            return True
    return False
DCWorkflowDefinition.security.declarePrivate('isWorkflowMethodSupported')
DCWorkflowDefinition.isWorkflowMethodSupported = DCWorkflowDefinition_isWorkflowMethodSupported

TransitionDefinition__init__orig = TransitionDefinition.__init__
def TransitionDefinition__init__(self, *args, **kw):
  TransitionDefinition__init__orig(self, *args, **kw)
  self.guard = Guard()
  self.guard.permissions = ('Modify portal content',)

TransitionDefinition.__init__ = TransitionDefinition__init__

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

from Products.CMFCore.Expression import getEngine

userGetIdOrUserNameExpression = Expression('user/getIdOrUserName')
userGetIdOrUserNameExpression._v_compiled = getEngine().compile(
  userGetIdOrUserNameExpression.text)

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
                # PATCH : if Default expression for 'actor' is 'user/getUserName',
                # we use 'user/getIdOrUserName' instead to store user ID for ERP5
                # user.
                if id == 'actor' and vdef.default_expr.text == 'user/getUserName':
                  expr = userGetIdOrUserNameExpression
                else:
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

def StateDefinition_getStatePermissionRolesDict(self):
  return self.permission_roles

def StateDefinition_getAcquirePermissionList(self):
  return _marker

def DCWorkflowDefinition_getWorkflowManagedPermissionList(self):
  permission_list = self.permissions
  if permission_list:
    permission_list = permission_list if isinstance(permission_list, list) else list(permission_list)
  else:
    permission_list = []
  return permission_list
DCWorkflowDefinition.getWorkflowManagedPermissionList = DCWorkflowDefinition_getWorkflowManagedPermissionList

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
       [x for x in tool.getWorkflowsFor(ob) if x.id != self.id and x.getPortalType() in ('DCWorkflowDefinition', 'Workflow')]
    other_data_list = []
    for other_workflow in other_workflow_list:
      other_sdef = other_workflow._getWorkflowStateOf(ob)
      if other_sdef is not None and other_sdef.getStatePermissionRolesDict() is not None:
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
              if p in other_workflow.getWorkflowManagedPermissionList():
                other_roles = other_sdef.getStatePermissionRolesDict().get(p, [])
                acquire_permission_list = other_sdef.getAcquirePermissionList()
                if acquire_permission_list is _marker: # DC Workflow
                  other_role_type = 'tuple' if type(other_roles) is type(()) else 'list'
                else: # ERP5 Workflow
                  other_role_type = 'list' if p in acquire_permission_list else 'tuple'
                other_role_type_list.append(other_role_type)
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
  type_info_list = wf_tool._listTypeInfo()
  wf_id = self.id
  portal_type_list = []
  # get the list of portal types to update
  if wf_id in wf_tool._default_chain:
    include_default = True
  else:
    include_default = False
  for type_info in type_info_list:
    if wf_id in type_info.getTypeWorkflowList() or include_default:
        portal_type_list.append(type_info.getId())
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

DCWorkflowDefinition.security.declareProtected(Permissions.AccessContentsInformation,
                                               'getPortalTypeListForWorkflow')
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

DCWorkflowDefinition.security.declarePrivate('getFutureStateSet')
DCWorkflowDefinition.getFutureStateSet = DCWorkflowDefinition_getFutureStateSet

InitializeClass(DCWorkflowDefinition)

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

# following patches are required for the new workflow tool compatibility.
def DCWorkflowDefinition_getVariableValueDict(self):
  if self.variables is not None:
    return self.variables
  return {}
def DCWorkflowDefinition_getVariableValueById(self, variable_id):
  if self.variables is not None:
    return self.variables.get(variable_id, None)
  return None
def DCWorkflowDefinition_getVariableIdList(self):
  if self.variables is not None:
    return self.variables.objectIds()
  return []
def DCWorkflowDefinition_getStateVariable(self):
  return self.state_var
def DCWorkflowDefinition_getStateValueById(self, state_id):
  if self.states is not None:
    return self.states.get(state_id, None)
  return None
def DCWorkflowDefinition_getStateValueList(self):
  if self.states is not None:
    return self.states.values()
  return []
def DCWorkflowDefinition_getStateIdList(self):
  if self.states is not None:
    return self.states.objectIds()
  return []
def DCWorkflowDefinition_getTransitionValueById(self, transition_id):
  if self.transitions is not None:
    return self.transitions.get(transition_id, None)
  return None
def DCWorkflowDefinition_getTransitionValueList(self):
  if self.transitions is not None:
    return self.transitions.values()
  else:
    return []
def DCWorkflowDefinition_getTransitionIdByReference(self, reference):
  return reference
def DCWorkflowDefinition_getTransitionIdList(self):
  if self.transitions is not None:
    return self.transitions.objectIds()
  return []
def DCWorkflowDefinition_getWorklistValueById(self, worklist_id):
  if self.worklists is not None:
    return self.worklists.get(worklist_id, None)
  return None
def DCWorkflowDefinition_getWorklistValueList(self):
  if self.worklists is not None:
    return self.worklists.values()
  return []
def DCWorkflowDefinition_getWorklistIdList(self):
  if self.worklists is not None:
    return self.worklists.objectIds()
  return []
def DCWorkflowDefinition_propertyIds(self):
  return sorted(self.__dict__.keys())
def DCWorkflowDefinition_getScriptIdByReference(self, reference):
  return reference
def DCWorkflowDefinition_getScriptValueById(self, script_id):
  if self.scripts is not None:
    return self.scripts.get(script_id, None)
  return None
def DCWorkflowDefinition_getScriptValueList(self):
  if self.scripts is not None:
    return self.scripts.values()
  return []
def StateDefinition_getDestinationIdList(self):
  return self.transitions
def StateDefinition_getStateTypeList(self):
  return getattr(self, 'type_list', ())
def DCWorkflowDefinition_getPortalType(self):
  return self.__class__.__name__
def method_getReference(self):
  return self.id
# a necessary funtion in Base_viewDict
def DCWorkflowDefinition_showDict(self):
  attr_dict = {}
  for attr in sorted(self.__dict__.keys()):
    value = getattr(self, attr)
    if value is not None:
      attr_dict[attr] = value
    else:
      continue
  return attr_dict
# generate XML file for the workflow contents comparison between DCWorkflow
# and converted workflow.
def DCWorkflowDefinition_showAsXML(self, root=None):
  if root is None:
    root = Element('erp5')
    return_as_object = False

  # Define a list of __dict__.keys to show to users:
  workflow_prop_id_to_show = {'description':'text',
  'state_var':'string', 'permissions':'multiple selection',
  'initial_state':'string'}

  # workflow as XML, need to rename DC workflow's portal_type before comparison.
  workflow = SubElement(root, 'workflow',
                      attrib=dict(reference=self.id,
                      portal_type='Workflow'))

  for prop_id in sorted(workflow_prop_id_to_show):
    value = getattr(self, prop_id, '')
    if value == () or value == []:
      value = ''
    prop_type = workflow_prop_id_to_show[prop_id]
    sub_object = SubElement(workflow, prop_id, attrib=dict(type=prop_type))
    sub_object.text = str(value)

  # 1. State as XML
  state_reference_list = []
  state_id_list = sorted(self.states.keys())
  # show reference instead of id
  state_prop_id_to_show = {'description':'text',
    'transitions':'multiple selection', 'permission_roles':'string'}
  for sid in state_id_list:
    state_reference_list.append(sid)
  states = SubElement(workflow, 'states', attrib=dict(state_list=str(state_reference_list),
                      number_of_element=str(len(state_reference_list))))
  for sid in state_id_list:
    sdef = self.states[sid]
    state = SubElement(states, 'state', attrib=dict(reference=sid,portal_type='State'))
    for property_id in sorted(state_prop_id_to_show):
      property_value = getattr(sdef, property_id, '')
      if property_value is None or property_value == [] or property_value ==():
        property_value = ''
      property_type = state_prop_id_to_show[property_id]
      sub_object = SubElement(state, property_id, attrib=dict(type=property_type))
      sub_object.text = str(property_value)

  # 2. Transition as XML
  transition_reference_list = []
  transition_id_list = sorted(self.transitions.keys())
  transition_prop_id_to_show = {'description':'text',
    'new_state_id':'string', 'trigger_type':'int', 'script_name':'string',
    'after_script_name':'string', 'actbox_category':'string', 'actbox_icon':'string',
    'actbox_name':'string', 'actbox_url':'string', 'guard':'string', 'transition_variable':'object'}

  for tid in transition_id_list:
    transition_reference_list.append(tid)
  transitions = SubElement(workflow, 'transitions',
        attrib=dict(transition_list=str(transition_reference_list),
        number_of_element=str(len(transition_reference_list))))
  for tid in transition_id_list:
    tdef = self.transitions[tid]
    transition = SubElement(transitions, 'transition',
          attrib=dict(reference=tid, portal_type='Transition'))
    guard = SubElement(transition, 'guard', attrib=dict(type='object'))
    transition_variables = SubElement(transition, 'transition_variables', attrib=dict(type='object'))
    for property_id in sorted(transition_prop_id_to_show):
      if property_id == 'guard':
        guard_obj = getattr(tdef, 'guard', None)
        guard_prop_to_show = sorted({'roles':'guard configuration',
            'groups':'guard configuration', 'permissions':'guard configuration',
            'expr':'guard configuration'})
        for prop_id in guard_prop_to_show:
          if guard_obj is not None:
            if prop_id == 'expr':
              prop_value = getattr(guard_obj.expr, 'text', '')
            else: prop_value = getattr(guard_obj, prop_id, '')
          else:
            prop_value = ''
          sub_object = SubElement(guard, prop_id, attrib=dict(type='guard configuration'))
          if prop_value is None or prop_value == [] or prop_value ==():
            prop_value = ''
          sub_object.text = str(prop_value)
      elif property_id == 'transition_variable':
        if tdef.var_exprs is not None:
          tr_var_list = tdef.var_exprs
        else:
          tr_var_list = {}
        for tr_var in tr_var_list:
          transition_variable = SubElement(transition_variables, property_id, attrib=dict(id=tr_var,type='variable'))
          transition_variable.text = str(tr_var_list[tr_var].text)
      else:
        property_value = getattr(tdef, property_id)
        property_type = transition_prop_id_to_show[property_id]
        sub_object = SubElement(transition, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value == [] or property_value ==():
          property_value = ''
        sub_object.text = str(property_value)

  # 3. Variable as XML
  variable_reference_list = []
  variable_id_list = sorted(self.variables.keys())
  variable_prop_id_to_show = {'description':'text',
        'default_expr':'string', 'for_catalog':'int', 'for_status':'int',
        'update_always':'int'}
  for vid in variable_id_list:
    variable_reference_list.append(vid)
  variables = SubElement(workflow, 'variables', attrib=dict(variable_list=str(variable_reference_list),
                      number_of_element=str(len(variable_reference_list))))
  for vid in variable_id_list:
    vdef = self.variables[vid]
    variable = SubElement(variables, 'variable', attrib=dict(reference=vdef.getReference(),
          portal_type='Workflow Variable'))
    for property_id in sorted(variable_prop_id_to_show):
      if property_id == 'default_expr':
        expression = getattr(vdef, property_id, None)
        if expression is not None:
          property_value = expression.text
        else:
          property_value = ''
      else:
        property_value = getattr(vdef, property_id, '')
      if property_value is None or property_value == [] or property_value ==():
        property_value = ''
      property_type = variable_prop_id_to_show[property_id]
      sub_object = SubElement(variable, property_id, attrib=dict(type=property_type))
      sub_object.text = str(property_value)

  # 4. Worklist as XML
  worklist_reference_list = []
  worklist_id_list = sorted(self.worklists.keys())
  worklist_prop_id_to_show = {'description':'text',
          'matched_portal_type_list':'text',
          'matched_validation_state_list':'string',
          'matched_simulation_state_list':'string', 'actbox_category':'string',
        'actbox_name':'string', 'actbox_url':'string', 'actbox_icon':'string',
        'guard':'object'}
  for qid in worklist_id_list:
    worklist_reference_list.append(qid)
  worklists = SubElement(workflow, 'worklists', attrib=dict(worklist_list=str(worklist_reference_list),
                      number_of_element=str(len(worklist_reference_list))))
  for qid in worklist_id_list:
    qdef = self.worklists[qid]
    worklist = SubElement(worklists, 'worklist', attrib=dict(reference=qdef.getReference(),
          portal_type='Worklist'))
    guard = SubElement(worklist, 'guard', attrib=dict(type='object'))
    var_matches = getattr(qdef, 'var_matches')
    for property_id in sorted(worklist_prop_id_to_show):
      if property_id == 'guard':
        guard_obj = getattr(qdef, 'guard', None)
        guard_prop_to_show = sorted({'roles':'guard configuration',
            'groups':'guard configuration', 'permissions':'guard configuration',
            'expr':'guard configuration'})
        for prop_id in guard_prop_to_show:
          if guard_obj is not None:
            prop_value = getattr(guard_obj, prop_id, '')
          else:
            prop_value = ''
          property_type='guard configuration'
          sub_object = SubElement(guard, prop_id, attrib=dict(type=property_type))
          if prop_value is None or prop_value == [] or prop_value ==():
            prop_value = ''
          sub_object.text = str(prop_value)
      else:
        if property_id == 'matched_portal_type_list':
          var_id = 'portal_type'
          property_value = var_matches.get(var_id)
        elif property_id == 'matched_validation_state_list':
          var_id = 'validation_state'
          property_value = var_matches.get(var_id)
        elif property_id == 'matched_simulation_state_list':
          var_id = 'simulation_state'
          property_value = var_matches.get(var_id)
        else:
          property_value = getattr(qdef, property_id)
        property_type = worklist_prop_id_to_show[property_id]
        sub_object = SubElement(worklist, property_id, attrib=dict(type=property_type))

        if property_value is None or property_value == [] or property_value ==():
          property_value = ''
        sub_object.text = str(property_value)

  # 5. Script as XML
  script_reference_list = []
  script_id_list = sorted(self.scripts.keys())
  script_prop_id_to_show = {'body':'string', 'parameter_signature':'string',
        'proxy_roles':'tokens'}
  for sid in script_id_list:
    script_reference_list.append(sid)
  scripts = SubElement(workflow, 'scripts', attrib=dict(script_list=str(script_reference_list),
                      number_of_element=str(len(script_reference_list))))
  for sid in script_id_list:
    sdef = self.scripts[sid]
    script = SubElement(scripts, 'script', attrib=dict(reference=sid,
      portal_type='Workflow Script'))
    for property_id in sorted(script_prop_id_to_show):
      if property_id == 'body':
        property_value = sdef.getBody()
      elif property_id == 'parameter_signature':
        property_value = sdef.getParams()
      elif property_id == 'proxy_roles':
        property_value = sdef.getProxyRole()
      else:
        property_value = getattr(sdef, property_id)
      property_type = script_prop_id_to_show[property_id]
      sub_object = SubElement(script, property_id, attrib=dict(type=property_type))
      sub_object.text = str(property_value)

  # return xml object
  if return_as_object:
    return root
  return etree.tostring(root, encoding='utf-8',
                        xml_declaration=True, pretty_print=True)

def TransitionDefinition_getParentValue(self):
  return self.aq_parent.aq_parent

def DCWorkflowDefinition_getSourceValue(self):
  return self.states[self.initial_state]

def DCWorkflowDefinition_setStateVariable(self, name):
  self.variables.setStateVar(name)

def DCWorkflowDefinition_addTransition(self, name):
  self.transitions.addTransition(name)

def DCWorkflowDefinition_deleteTransitions(self, name):
  self.transitions.deleteTransitions(name)

def WorklistDefinition_getGuardRoleList(self):
  return self.getGuard().getRolesText().split(';')

def method_isGuarded(self):
  guard = getattr(self, 'guard', None)
  return guard is not None

DCWorkflowDefinition.addTransition = DCWorkflowDefinition_addTransition
DCWorkflowDefinition.deleteTransitions = DCWorkflowDefinition_deleteTransitions
DCWorkflowDefinition.getReference = method_getReference
DCWorkflowDefinition.getSourceValue = DCWorkflowDefinition_getSourceValue
DCWorkflowDefinition.notifyWorkflowMethod = DCWorkflowDefinition_notifyWorkflowMethod
DCWorkflowDefinition.notifyBefore = DCWorkflowDefinition_notifyBefore
DCWorkflowDefinition.notifySuccess = DCWorkflowDefinition_notifySuccess
DCWorkflowDefinition.getVariableValueDict = DCWorkflowDefinition_getVariableValueDict
DCWorkflowDefinition.getVariableValueById = DCWorkflowDefinition_getVariableValueById
DCWorkflowDefinition.getStateValueById = DCWorkflowDefinition_getStateValueById
DCWorkflowDefinition.getStateValueList = DCWorkflowDefinition_getStateValueList
DCWorkflowDefinition.getTransitionValueById = DCWorkflowDefinition_getTransitionValueById
DCWorkflowDefinition.getTransitionValueList = DCWorkflowDefinition_getTransitionValueList
DCWorkflowDefinition.getWorklistValueById = DCWorkflowDefinition_getWorklistValueById
DCWorkflowDefinition.getWorklistValueList = DCWorkflowDefinition_getWorklistValueList
DCWorkflowDefinition.getScriptValueList = DCWorkflowDefinition_getScriptValueList
DCWorkflowDefinition.getScriptValueById = DCWorkflowDefinition_getScriptValueById
DCWorkflowDefinition.getVariableIdList = DCWorkflowDefinition_getVariableIdList
DCWorkflowDefinition.getStateIdList = DCWorkflowDefinition_getStateIdList
DCWorkflowDefinition.getTransitionIdList = DCWorkflowDefinition_getTransitionIdList
DCWorkflowDefinition.getWorklistIdList = DCWorkflowDefinition_getWorklistIdList
DCWorkflowDefinition.setStateVariable = DCWorkflowDefinition_setStateVariable
DCWorkflowDefinition.showAsXML = DCWorkflowDefinition_showAsXML
DCWorkflowDefinition.showDict = DCWorkflowDefinition_showDict
DCWorkflowDefinition.propertyIds = DCWorkflowDefinition_propertyIds
DCWorkflowDefinition.getStateVariable = DCWorkflowDefinition_getStateVariable
DCWorkflowDefinition.getPortalType = DCWorkflowDefinition_getPortalType
DCWorkflowDefinition.getScriptIdByReference = DCWorkflowDefinition_getScriptIdByReference
DCWorkflowDefinition.getTransitionIdByReference = DCWorkflowDefinition_getTransitionIdByReference
StateDefinition.getReference = method_getReference
StateDefinition.getDestinationIdList = StateDefinition_getDestinationIdList
StateDefinition.getDestinationReferenceList = StateDefinition_getDestinationIdList
StateDefinition.showDict = DCWorkflowDefinition_showDict
StateDefinition.getStateTypeList = StateDefinition_getStateTypeList
StateDefinition.getStatePermissionRolesDict = StateDefinition_getStatePermissionRolesDict
StateDefinition.getAcquirePermissionList = StateDefinition_getAcquirePermissionList
TransitionDefinition.getParentValue = TransitionDefinition_getParentValue
TransitionDefinition.getReference = method_getReference
TransitionDefinition.showDict = DCWorkflowDefinition_showDict
TransitionDefinition.isGuarded = method_isGuarded
VariableDefinition.getReference = method_getReference
VariableDefinition.showDict = DCWorkflowDefinition_showDict
WorklistDefinition.getReference = method_getReference
WorklistDefinition.showDict = DCWorkflowDefinition_showDict
WorklistDefinition.getGuardRoleList = WorklistDefinition_getGuardRoleList

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

if True:
    def Guard_check(self, sm, wf_def, ob, **kw):
        """Checks conditions in this guard
        """
        u_roles = None
        # PATCH BEGIN
        # This method returns roles, considering proxy roles in caller
        # scripts.
        # XXX : If we need this method somewhere else, it should be
        # added in SecurityManager class.
        def getRoles():
            stack = sm._context.stack
            if stack:
                eo = stack[-1]
                proxy_roles = getattr(eo, '_proxy_roles', None)
                if proxy_roles:
                    return proxy_roles
            return sm.getUser().getRolesInContext(ob)
        # PATCH END
        if wf_def.manager_bypass:
            # Possibly bypass.
            # PATCH BEGIN
            u_roles = getRoles()
            # PATCH END
            if 'Manager' in u_roles:
                return 1
        if self.permissions:
            for p in self.permissions:
                if _checkPermission(p, ob):
                    break
            else:
                return 0
        if self.roles:
            # Require at least one of the given roles.
            if u_roles is None:
                # PATCH BEGIN
                u_roles = getRoles()
                # PATCH END
            for role in self.roles:
                if role in u_roles:
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

Guard.check = Guard_check

# Add class security in DCWorkflow.Variables.Variables.
from Products.DCWorkflow.Variables import Variables
security = ClassSecurityInfo()
security.declareObjectProtected(ManagePortal)
Variables.security = security
InitializeClass(Variables)
