# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
assert WITH_LEGACY_WORKFLOW

## ERP5 Workflow: This must go before any Products.DCWorkflow imports as this
## patch createExprContext() from-imported in several of its modules
from Products.ERP5Type.Core.Workflow import createExpressionContext, StateChangeInfo

# Optimized rendering of global actions (cache)
from Products.ERP5Type.Globals import DTMLFile
from Products.ERP5Type import Permissions, _dtmldir
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Acquisition import aq_inner, aq_parent
from Products.DCWorkflow.DCWorkflow import ObjectDeleted, ObjectMoved
from Products.DCWorkflow import DCWorkflow
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD, TransitionDefinition
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.CMFCore.permissions import ManagePortal
from AccessControl import getSecurityManager, ModuleSecurityInfo
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
from six import reraise

# Avoid copy/paste of code from ERP5 Workflow by dynamically adding methods to
# DCWorkflow classes
from Products.ERP5Type.Core.Workflow import (Workflow as ERP5Workflow,
                                             ValidationFailed,
                                             _marker,
                                             userGetIdOrUserNameExpression)
from Products.ERP5Type.Tool.WorkflowTool import SECURITY_PARAMETER_ID
from Products.ERP5Type.mixin.guardable import GuardableMixin as ERP5Guardable

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
            # and nothing else
            if (not qdef.isGuarded() or
                qdef.checkGuard(sm, self, portal, check_roles=False)):
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
                      v_fmt = v(createExpressionContext(StateChangeInfo(portal,
                                self, kwargs=info.__dict__.copy())))
                    else:
                      v_fmt = map(lambda x, info=info: x%info, v)
                    dict[k] = v_fmt
                  # Patch to automatically filter workflists per portal type
                  # so that the same state can be used for different
                  # worklists and they are not merged
                  if 'portal_type' not in dict:
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
DCWorkflowDefinition.listObjectActions = ERP5Workflow.__dict__['listObjectActions']

from Products.DCWorkflow.Expression import Expression

DCWorkflowDefinition.security.declarePrivate('getWorklistVariableMatchDict')
DCWorkflowDefinition.getWorklistVariableMatchDict = ERP5Workflow.getWorklistVariableMatchDict.__func__

DCWorkflowDefinition.security.declarePrivate('isWorkflowMethodSupported')
DCWorkflowDefinition.isWorkflowMethodSupported = ERP5Workflow.isWorkflowMethodSupported.__func__

TransitionDefinition__init__orig = TransitionDefinition.__init__
def TransitionDefinition__init__(self, *args, **kw):
  TransitionDefinition__init__orig(self, *args, **kw)
  self.guard = Guard()
  self.guard.permissions = ('Modify portal content',)

TransitionDefinition.__init__ = TransitionDefinition__init__

DCWorkflow.ValidationFailed = ValidationFailed
ModuleSecurityInfo('Products.DCWorkflow.DCWorkflow').declarePublic('ValidationFailed')

# XXX: Code duplicated in Products.ERP5Type.Core.Workflow Patch
# executeTransition from DCWorkflowDefinition, to put ValidationFailed error
# messages in workflow history.
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
        except ValidationFailed as validation_exc:
            before_script_success = 0
            before_script_error_message = deepcopy(validation_exc.msg)
            validation_exc_traceback = sys.exc_traceback
        except ObjectMoved as moved_exc:
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
        if id in state_values:
            value = state_values[id]
        elif id in tdef_exprs:
            expr = tdef_exprs[id]
        elif not vdef.update_always and id in former_status:
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
                econtext = createExpressionContext(sci)
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
            reraise(validation_exc, None, validation_exc_traceback)
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

# XXX: Code duplicated in Products.ERP5Type.Core.Workflow
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
    raise WorkflowException('Destination state undefined: ' + new_state_id)

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
    if id in state_values:
      value = state_values[id]
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
          sci = StateChangeInfo(ob, self, former_status, tdef, old_sdef,
                                new_sdef, kwargs)
        econtext = createExpressionContext(sci)
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

DCWorkflowDefinition.wrapWorkflowMethod = ERP5Workflow.wrapWorkflowMethod.__func__

def StateDefinition_getStatePermissionRoleListDict(self):
  if self.permission_roles is None:
    return {}
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

# XXX: Code duplicated in Products.ERP5Type.Core.Workflow Patch
# updateRoleMappingsFor so that if 2 workflows define security, then we should
# do an AND operation between each permission
def updateRoleMappingsFor(self, ob):
    '''
    Changes the object permissions according to the current
    state.
    '''
    changed = 0
    sdef = self._getWorkflowStateOf(ob)

    tool = aq_parent(aq_inner(self))
    other_workflow_list = \
       [x for x in tool.getWorkflowValueListFor(ob) if x.id != self.id and x.getPortalType() in ('DCWorkflowDefinition', 'Workflow')]
    other_data_list = []
    for other_workflow in other_workflow_list:
      other_sdef = other_workflow._getWorkflowStateOf(ob)
      if other_sdef is not None and other_sdef.getStatePermissionRoleListDict():
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
                other_roles = other_sdef.getStatePermissionRoleListDict().get(p, [])
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

#######################################################################
## From here on, patches to have the same API as ERP5 Workflow as
## portal_workflow can contain both until its Workflows are migrated...
def DCWorkflowDefinition_getVariableValueDict(self):
  if self.variables is not None:
    return self.variables
  return {}
def DCWorkflowDefinition_getVariableValueByReference(self, reference):
  if self.variables is not None:
    return self.variables.get(reference, None)
  return None
def DCWorkflowDefinition_getVariableReferenceList(self):
  if self.variables is not None:
    return self.variables.objectIds()
  return []
def DCWorkflowDefinition_getStateVariable(self):
  return self.state_var
def DCWorkflowDefinition_getStateValueByReference(self, reference):
  if self.states is not None:
    return self.states.get(reference, None)
  return None
def DCWorkflowDefinition_getStateValueList(self):
  if self.states is not None:
    return self.states.values()
  return []
def DCWorkflowDefinition_getStateReferenceList(self):
  if self.states is not None:
    return self.states.objectIds()
  return []
def DCWorkflowDefinition_getTransitionValueByReference(self, reference):
  if self.transitions is not None:
    return self.transitions.get(reference, None)
  return None
def DCWorkflowDefinition_getTransitionValueList(self):
  if self.transitions is not None:
    return self.transitions.values()
  else:
    return []
def DCWorkflowDefinition_getTransitionIdByReference(self, reference):
  return reference
def DCWorkflowDefinition_getTransitionReferenceList(self):
  if self.transitions is not None:
    return self.transitions.objectIds()
  return []
def DCWorkflowDefinition_getWorklistValueByReference(self, reference):
  return self.worklists.get(reference, None)
def DCWorkflowDefinition_getWorklistValueList(self):
  return self.worklists.values()
def DCWorkflowDefinition_getWorklistReferenceList(self):
  return self.worklists.objectIds()
def DCWorkflowDefinition_propertyIds(self):
  return sorted(self.__dict__.keys())
def DCWorkflowDefinition_getScriptIdByReference(self, reference):
  return reference
def DCWorkflowDefinition_getScriptValueByReference(self, reference):
  if self.scripts is not None:
    return self.scripts.get(reference, None)
  return None
def DCWorkflowDefinition_getScriptValueList(self):
  if self.scripts is not None:
    return self.scripts.values()
  return []
def StateDefinition_getDestinationIdList(self):
  return self.transitions
def StateDefinition_getDestinationValueList(self):
  if self.transitions: # empty tuple by default
    return [v for i, v in self.getWorkflow().transitions.items()
            if i in self.transitions]
  return []
def StateDefinition_getStateTypeList(self):
  return getattr(self, 'type_list', ())
def StateDefinition_setStateTypeList(self, state_type_list):
  self.type_list = state_type_list
def DCWorkflowDefinition_getPortalType(self):
  return self.__class__.__name__
def method_getReference(self):
  return self.id
# ERP5 Accessors to avoid accessing the property directly
def method_getId(self):
  return self.id
def method_getTitle(self):
  return self.title
def method_getDescription(self):
  return self.description
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
    state = SubElement(states, 'state', attrib=dict(reference=sid,portal_type='Workflow State'))
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
          attrib=dict(reference=tid, portal_type='Workflow Transition'))
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

def method_isGuarded(self):
  return getattr(self, 'guard', None) is not None

def method_getGuardRoleList(self):
  if not self.isGuarded():
    return []
  return self.guard.roles or []

def method_getGuardGroupList(self):
  if not self.isGuarded():
    return []
  return self.guard.groups or []

def method_getGuardPermissionList(self):
  if not self.isGuarded():
    return []
  return self.guard.permissions or []

def method_getGuardExpressionInstance(self):
  if not self.isGuarded():
    return []
  return self.guard.expr

def method_checkGuard(self, *args, **kwargs):
  return ERP5Guardable.checkGuard.__func__(self, *args, **kwargs)

def method_getAction(self):
  return self.actbox_url
def method_getActionType(self):
  return self.actbox_category
def method_getActionName(self):
  return self.actbox_name
def method_getIcon(self):
  return self.actbox_icon
def method_getTransitionVariableValueList(self):
  if self.var_exprs is None:
    return []
  return self.var_exprs
def method_getBeforeScriptValueList(self):
  script_dict = self.getWorkflow().scripts
  return [script_dict[script_name] for script_name in self.script_name]
def method_getAfterScriptValueList(self):
  script_dict = self.getWorkflow().scripts
  return [script_dict[script_name] for script_name in self.after_script_name]

DCWorkflowDefinition.security.declareProtected(Permissions.ModifyPortalContent,
                                               'convertToERP5Workflow')
def convertToERP5Workflow(self, temp_object=False):
  """
  Convert DC Workflow and Interaction Workflow to ERP5 objects
  """
  from Products.ERP5Type.Utils import UpperCase
  portal = self.getPortalObject()
  workflow_tool = portal.portal_workflow

  # XXX: These _init scripts are not available before upgrading erp5_core and
  #      are only use to set default values which is not needed here as all
  #      properties are copied from DCWorkflows...
  for x in ('Workflow', 'Workflow Script', 'Workflow Transition', 'Worklist'):
    getattr(portal.portal_types, x).setTypeInitScriptId(None)

  workflow_class_name = self.__class__.__name__
  if temp_object:
    new_id = self.id
  else:
    new_id = 'converting_' + self.id
  from base64 import b64encode
  import cPickle
  uid = b64encode(cPickle.dumps(new_id))
  if workflow_class_name == 'DCWorkflowDefinition':
    portal_type = 'Workflow'
  else:
    portal_type = 'Interaction Workflow'
  workflow = workflow_tool.newContent(id=new_id, temp_object=temp_object,
                                      portal_type=portal_type)
  if workflow_class_name == 'DCWorkflowDefinition':
    workflow.setStateVariable(self.state_var)
    workflow.setWorkflowManagedPermissionList(self.permissions)
    workflow.setManagerBypass(self.manager_bypass)

  if temp_object:
    # give temp workflow an uid for form_dialog.
    workflow.uid = uid
  workflow.default_reference = self.id
  workflow.setTitle(self.title)
  workflow.setDescription(self.description)

  if not temp_object:
    # create state and transitions (Workflow)
    # or interactions (Interaction Workflow)

    # create scripts (portal_type = Workflow Script)
    dc_workflow_script_list = self.scripts
    for script_id in dc_workflow_script_list:
      script = dc_workflow_script_list.get(script_id)
      # add a prefix if there is a script & method conflict
      workflow_script = workflow.newContent(portal_type='Workflow Script',
                                            temp_object=temp_object)
      workflow_script.setReference(script.id)
      workflow_script.setTitle(script.title)
      workflow_script.setParameterSignature(script._params)
      workflow_script.setBody(script._body)
      workflow_script.setProxyRole(script._proxy_roles)

    if workflow_class_name == 'DCWorkflowDefinition':
      # remove default state and variables
      for def_var in workflow.objectValues(portal_type='Workflow Variable'):
        workflow._delObject(def_var.getId())
      try:
        workflow._delObject('state_draft')
      except KeyError:
        pass
      dc_workflow_transition_value_list = self.transitions
      dc_workflow_transition_id_list = dc_workflow_transition_value_list.objectIds()

      # create transition (portal_type = Transition)
      for tid in dc_workflow_transition_value_list:
        tdef = dc_workflow_transition_value_list.get(tid)
        transition = workflow.newContent(portal_type='Workflow Transition', temp_object=temp_object)
        if tdef.title == '' or tdef.title is None:
          tdef.title = UpperCase(tdef.id)
        transition.setTitle(tdef.title)
        transition.setReference(tdef.id)
        transition.setTriggerType(tdef.trigger_type)
        transition.setActionType(tdef.actbox_category)
        transition.setIcon(tdef.actbox_icon)
        transition.setActionName(tdef.actbox_name)
        transition.setAction(tdef.actbox_url)
        transition.setDescription(tdef.description)

        # configure guard
        if tdef.guard:
          transition.setGuardRoleList(tdef.guard.roles)
          transition.setGuardPermissionList(tdef.guard.permissions)
          transition.setGuardGroupList(tdef.guard.groups)
          if tdef.guard.expr is not None:
            transition.setGuardExpression(tdef.guard.expr.text)
        else:
          # Override value set in WorkflowTransition_init
          transition.setGuardPermissionList([])

      for transition in workflow.objectValues(portal_type='Workflow Transition'):
        # configure after/before scripts
        # we have to loop again over transitions because some
        # before/after/... scripts are transitions and obviously, all of
        # them were not defined on the new workflow in the previous loop
        old_transition = dc_workflow_transition_value_list.get(transition.getReference())
        script_path_list = self.getScriptPathList(workflow,
                                                  old_transition.script_name)
        transition.setBeforeScriptValueList(script_path_list)

        script_path_list = self.getScriptPathList(workflow,
                                                  old_transition.after_script_name)
        transition.setAfterScriptValueList(script_path_list)

      # create states (portal_type = State)
      workflow_managed_role_list = workflow.getManagedRoleList()
      for sid in self.states:
        sdef = self.states.get(sid)
        state = workflow.newContent(portal_type='Workflow State', temp_object=temp_object)
        if sdef.title == '' or sdef.title is None:
          sdef.title = UpperCase(sdef.id)
        if hasattr(sdef, 'type_list'):
          state.setStateType(sdef.type_list)
        state.setTitle(sdef.title)
        state.setReference(sdef.id)
        state.setDescription(sdef.description)

        acquire_permission_list = []
        permission_roles_dict = {}
        permission_roles = sdef.permission_roles or {}
        for permission in self.permissions:
          roles = permission_roles.get(permission, None)
          if roles is None:
            acquire_permission_list.append(permission)
            permission_roles_dict[permission] = ()
          else:
            if isinstance(roles, list): # type 'list' means acquisition
              acquire_permission_list.append(permission)
            permission_roles_dict[permission] = list(roles)

        state.setAcquirePermission(acquire_permission_list)
        state.setStatePermissionRoleListDict(permission_roles_dict)

      # default state using category setter
      state_path = getattr(workflow, 'state_' + self.initial_state).getPath()
      state_path = 'source/' + '/'.join(state_path.split('/')[2:])
      workflow.setCategoryList([state_path])
      # set state's possible transitions:
      for sid in self.states:
        sdef = workflow._getOb('state_'+sid)
        sdef.setDestinationValueList([
          workflow.getTransitionValueByReference(tid)
          for tid in self.states.get(sid).transitions if workflow.getTransitionValueByReference(tid) is not None])
      # set transition's destination state:
      for tid in dc_workflow_transition_value_list:
        tdef = workflow.getTransitionValueByReference(tid)
        state = getattr(workflow, 'state_' + dc_workflow_transition_value_list.get(tid).new_state_id, None)
        if state is None:
          # it's a remain in state transition.
          continue
        state_path = 'destination/' + '/'.join(state.getPath().split('/')[2:])
        tdef.setCategoryList(tdef.getCategoryList() + [state_path])
      # worklists (portal_type = Worklist)
      for qid, qdef in self.worklists.items():
        worklist = workflow.newContent(portal_type='Worklist', temp_object=temp_object)
        worklist.setTitle(qdef.title)
        worklist.setReference(qdef.id)
        worklist.setDescription(qdef.description)
        criterion_property_list = qdef.var_matches.keys()
        for key, value in qdef.var_matches.items():
          if not isinstance(value, (tuple, list)):
            raise AssertionError("%s: %s: %s: must be a list or tuple" % (qdef.id, key, value))
          worklist.setCriterion(key, value)
        worklist.setAction(qdef.actbox_url)
        worklist.setActionType(qdef.actbox_category)
        worklist.setIcon(qdef.actbox_icon)
        worklist.setActionName(qdef.actbox_name)
        # configure guard
        if qdef.guard:
          if qdef.guard.roles:
            worklist.setCriterion(SECURITY_PARAMETER_ID, qdef.guard.roles)
            criterion_property_list.append(SECURITY_PARAMETER_ID)
          worklist.setGuardPermissionList(qdef.guard.permissions)
          worklist.setGuardGroupList(qdef.guard.groups)
          if qdef.guard.expr is not None:
            worklist.setGuardExpression(qdef.guard.expr.text)
        worklist.setCriterionPropertyList(criterion_property_list)
    elif workflow_class_name == 'InteractionWorkflowDefinition':
      dc_workflow_interaction_value_dict = self.interactions
      # create interactions (portal_type = Interaction)
      for tid in dc_workflow_interaction_value_dict:
        interaction = workflow.newContent(portal_type='Interaction Workflow Interaction', temp_object=temp_object)
        tdef = dc_workflow_interaction_value_dict.get(tid)
        if tdef.title:
          interaction.setTitle(tdef.title)
        interaction.setReference(tdef.id)

        # configure after/before/before commit/activate scripts
        # no need to loop again over interactions as made for transitions
        # because interactions xxx_script are not interactions
        script_path_list = self.getScriptPathList(workflow, tdef.script_name)
        interaction.setBeforeScriptValueList(script_path_list)

        script_path_list = self.getScriptPathList(workflow, tdef.after_script_name)
        interaction.setAfterScriptValueList(script_path_list)

        script_path_list = self.getScriptPathList(workflow, tdef.activate_script_name)
        interaction.setActivateScriptValueList(script_path_list)

        script_path_list = self.getScriptPathList(workflow, tdef.before_commit_script_name)
        interaction.setBeforeCommitScriptValueList(script_path_list)

        # configure guard
        if tdef.guard:
          interaction.setGuardRoleList(tdef.guard.roles)
          interaction.setGuardPermissionList(tdef.guard.permissions)
          interaction.setGuardGroupList(tdef.guard.groups)
          if tdef.guard.expr is not None:
            # Here add expression text, convert to expression in getMatchVar.
            interaction.setGuardExpression(tdef.guard.expr.text)
        interaction.setPortalTypeFilter(tdef.portal_type_filter)
        interaction.setPortalTypeGroupFilter(tdef.portal_type_group_filter)
        interaction.setTemporaryDocumentDisallowed(tdef.temporary_document_disallowed)
        #interaction.setTransitionFormId() # this is not defined in DC interaction?
        interaction.setTriggerMethodId(tdef.method_id)
        interaction.setTriggerOncePerTransaction(tdef.once_per_transaction)
        interaction.setTriggerType(tdef.trigger_type)
        interaction.setDescription(tdef.description)

    # create variables (portal_type = Workflow Variable)
    for variable_id, variable_definition in self.variables.items():
      variable = workflow.newContent(portal_type='Workflow Variable', temp_object=temp_object)
      variable.setTitle(variable_definition.title)
      variable.setReference(variable_id)
      variable.setAutomaticUpdate(variable_definition.update_always)
      if getattr(variable_definition, 'default_expr', None) is not None:
        # for a very specific case, action return the reference of transition
        # in order to generation correct workflow history.
        if variable_id == 'action':
          variable.setVariableDefaultExpression('transition/getReference|nothing')
        else:
          variable.setVariableDefaultExpression(variable_definition.default_expr.text)
      # default_expr has precedence over default_value if defined...
      elif variable_definition.default_value:
        if '/' not in variable_definition.default_value:
          default_value = "python: '%s'" % variable_definition.default_value
        else:
          default_value = variable_definition.default_value
        variable.setVariableDefaultExpression(default_value)
      if variable_definition.info_guard:
        variable.info_guard = variable_definition.info_guard
        variable.setGuardRoleList(variable_definition.info_guard.roles)
        variable.setGuardPermissionList(variable_definition.info_guard.permissions)
        variable.setGuardGroupList(variable_definition.info_guard.groups)
        if variable_definition.info_guard.expr is not None:
          # Here add expression text, convert to expression in getMatchVar.
          variable.setGuardExpression(tdef.info_guard.expr.text)
      variable.setForCatalog(variable_definition.for_catalog)
      variable.setStatusIncluded(variable_definition.for_status)
      variable.setDescription(variable_definition.description)
    # Configure transition variable:
    if getattr(self, 'transitions', None) is not None:
      dc_workflow_transition_value_list = self.transitions
      for tid in dc_workflow_transition_value_list:
        origin_tdef = dc_workflow_transition_value_list[tid]
        transition = workflow.getTransitionValueByReference(tid)
        if origin_tdef.var_exprs is None:
          var_exprs = {}
        else: var_exprs = origin_tdef.var_exprs
        for key in var_exprs:
          tr_var = transition.newContent(portal_type='Workflow Transition Variable', temp_object=temp_object)
          tr_var.setReference(key)
          tr_var.setVariableDefaultExpression(var_exprs[key].text)
          tr_var_path = getattr(workflow, 'variable_'+key).getPath()
          tr_var_path = '/'.join(tr_var_path.split('/')[2:])
          tr_var.setCausalityList([tr_var_path])
    # Configure interaction variable:
    if getattr(self, 'interactions', None) is not None:
      dc_workflow_interaction_value_list = self.interactions
      for tid in dc_workflow_interaction_value_list:
        origin_tdef = dc_workflow_interaction_value_list[tid]
        interaction = workflow._getOb('interaction_'+tid)
        if origin_tdef.var_exprs is None:
          var_exprs = {}
        else: var_exprs = origin_tdef.var_exprs
        for key in var_exprs:
          tr_var = interaction.newContent(portal_type='Workflow Transition Variable', temp_object=temp_object)
          tr_var.setReference(key)
          tr_var.setVariableDefaultExpression(var_exprs[key].text)
          tr_var_path = getattr(workflow, 'variable_'+key).getPath()
          tr_var_path = '/'.join(tr_var_path.split('/')[2:])
          tr_var.setCausalityList([tr_var_path])
    # move dc workflow to trash bin
    trash_tool = getattr(portal, 'portal_trash', None)
    if trash_tool is not None:
      # move old workflow to trash tool;
      LOG("convertToERP5Workflow", 0,
          "Move old workflow '%s' into a trash bin" % self.id)
      workflow_tool._delOb(self.id)
      from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
      trashbin = UnrestrictedMethod(trash_tool.newTrashBin)(self.id)
      trashbin._setOb(self.id, self)
    # override temporary id:
    workflow.setId(workflow.default_reference)
  if not temp_object:
    # update translation so that the catalog contains translated states, ...
    portal.ERP5Site_updateTranslationTable()
  return workflow

DCWorkflowDefinition.convertToERP5Workflow = convertToERP5Workflow
DCWorkflowDefinition.getReference = method_getReference
DCWorkflowDefinition.getId = method_getId
DCWorkflowDefinition.getTitle = method_getTitle
DCWorkflowDefinition.getDescription = method_getDescription
DCWorkflowDefinition.isManagerBypass = lambda self: self.manager_bypass
DCWorkflowDefinition.getSourceValue = DCWorkflowDefinition_getSourceValue
DCWorkflowDefinition.notifyWorkflowMethod = ERP5Workflow.notifyWorkflowMethod.__func__
DCWorkflowDefinition.notifyBefore = ERP5Workflow.notifyBefore.__func__
DCWorkflowDefinition.notifySuccess = ERP5Workflow.notifySuccess.__func__
DCWorkflowDefinition.getVariableValueDict = DCWorkflowDefinition_getVariableValueDict
DCWorkflowDefinition.getVariableValueByReference = DCWorkflowDefinition_getVariableValueByReference
DCWorkflowDefinition.getStateValueByReference = DCWorkflowDefinition_getStateValueByReference
DCWorkflowDefinition.getStateValueList = DCWorkflowDefinition_getStateValueList
DCWorkflowDefinition.getTransitionValueByReference = DCWorkflowDefinition_getTransitionValueByReference
DCWorkflowDefinition.getTransitionValueList = DCWorkflowDefinition_getTransitionValueList
DCWorkflowDefinition.getWorklistValueByReference = DCWorkflowDefinition_getWorklistValueByReference
DCWorkflowDefinition.getWorklistValueList = DCWorkflowDefinition_getWorklistValueList
DCWorkflowDefinition.getScriptValueList = DCWorkflowDefinition_getScriptValueList
DCWorkflowDefinition.getScriptValueByReference = DCWorkflowDefinition_getScriptValueByReference
DCWorkflowDefinition.getVariableReferenceList = DCWorkflowDefinition_getVariableReferenceList
DCWorkflowDefinition.getStateReferenceList = DCWorkflowDefinition_getStateReferenceList
DCWorkflowDefinition.getTransitionReferenceList = DCWorkflowDefinition_getTransitionReferenceList
DCWorkflowDefinition.getWorklistReferenceList = DCWorkflowDefinition_getWorklistReferenceList
DCWorkflowDefinition.setStateVariable = DCWorkflowDefinition_setStateVariable
DCWorkflowDefinition.showAsXML = DCWorkflowDefinition_showAsXML
DCWorkflowDefinition.showDict = DCWorkflowDefinition_showDict
DCWorkflowDefinition.propertyIds = DCWorkflowDefinition_propertyIds
DCWorkflowDefinition.getStateVariable = DCWorkflowDefinition_getStateVariable
DCWorkflowDefinition.getPortalType = DCWorkflowDefinition_getPortalType
DCWorkflowDefinition.getScriptIdByReference = DCWorkflowDefinition_getScriptIdByReference
DCWorkflowDefinition.getTransitionIdByReference = DCWorkflowDefinition_getTransitionIdByReference
StateDefinition.getReference = method_getReference
StateDefinition.getId = method_getId
StateDefinition.getTitle = method_getTitle
StateDefinition.getDescription = method_getDescription
StateDefinition.getDestinationIdList = StateDefinition_getDestinationIdList
StateDefinition.getDestinationValueList = StateDefinition_getDestinationValueList
StateDefinition.getDestinationReferenceList = StateDefinition_getDestinationIdList
StateDefinition.showDict = DCWorkflowDefinition_showDict
StateDefinition.getStateTypeList = StateDefinition_getStateTypeList
StateDefinition.setStateTypeList = StateDefinition_setStateTypeList
StateDefinition.getStatePermissionRoleListDict = StateDefinition_getStatePermissionRoleListDict
StateDefinition.getAcquirePermissionList = StateDefinition_getAcquirePermissionList
TransitionDefinition.getParentValue = TransitionDefinition_getParentValue
TransitionDefinition.getReference = method_getReference
TransitionDefinition.getId = method_getId
TransitionDefinition.getTitle = method_getTitle
TransitionDefinition.getDescription = method_getDescription
TransitionDefinition.getTriggerType = lambda self: self.trigger_type
TransitionDefinition.getAction = method_getAction
TransitionDefinition.getActionType = method_getActionType
TransitionDefinition.getActionName = method_getActionName
TransitionDefinition.getIcon = method_getIcon
TransitionDefinition.getTransitionVariableValueList = method_getTransitionVariableValueList
TransitionDefinition.getBeforeScriptValueList = method_getBeforeScriptValueList
TransitionDefinition.getAfterScriptValueList = method_getAfterScriptValueList
TransitionDefinition.showDict = DCWorkflowDefinition_showDict
TransitionDefinition.isGuarded = method_isGuarded
TransitionDefinition.getGuardRoleList = method_getGuardRoleList
TransitionDefinition.getGuardGroupList = method_getGuardGroupList
TransitionDefinition.getGuardPermissionList = method_getGuardPermissionList
TransitionDefinition.getGuardExpressionInstance = method_getGuardExpressionInstance
TransitionDefinition.checkGuard = method_checkGuard
VariableDefinition.getReference = method_getReference
VariableDefinition.getId = method_getId
VariableDefinition.getTitle = method_getTitle
VariableDefinition.getDescription = method_getDescription
VariableDefinition.getVariableDefaultExpression = lambda self: self.var_expr
VariableDefinition.checkGuard = method_checkGuard
VariableDefinition.showDict = DCWorkflowDefinition_showDict
VariableDefinition.getStatusIncluded = lambda self: self.for_status
VariableDefinition.getAutomaticUpdate = lambda self: self.update_always
def WorklistDefinition_getGuardRoleList(self):
  """
  For Worklists only, guard.roles has been migrated to SECURITY_PARAMETER_ID
  """
  return []
def WorklistDefinition_getIdentityCriterionDict(self):
  identity_criterion_dict = {k: self.getVarMatch(k) for k in self.getVarMatchKeys()}
  if self.guard is not None and self.guard.roles:
    identity_criterion_dict[SECURITY_PARAMETER_ID] = self.guard.roles
  return identity_criterion_dict
WorklistDefinition.getReference = method_getReference
WorklistDefinition.getId = method_getId
WorklistDefinition.getTitle = method_getTitle
WorklistDefinition.getDescription = method_getDescription
WorklistDefinition.getAction = method_getAction
WorklistDefinition.getActionType = method_getActionType
WorklistDefinition.getActionName = method_getActionName
WorklistDefinition.getIcon = method_getIcon
WorklistDefinition.showDict = DCWorkflowDefinition_showDict
WorklistDefinition.isGuarded = method_isGuarded
WorklistDefinition.getGuardRoleList = WorklistDefinition_getGuardRoleList
WorklistDefinition.getGuardGroupList = method_getGuardGroupList
WorklistDefinition.getGuardPermissionList = method_getGuardPermissionList
WorklistDefinition.getGuardExpressionInstance = method_getGuardExpressionInstance
WorklistDefinition.checkGuard = method_checkGuard
WorklistDefinition.getIdentityCriterionDict = WorklistDefinition_getIdentityCriterionDict

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
            econtext = createExpressionContext(
                StateChangeInfo(ob, wf_def, kwargs=kw))
            res = expr(econtext)
            if not res:
                return 0
        return 1
Guard.check = Guard_check

InitializeClass(DCWorkflowDefinition)

# Add class security in DCWorkflow.Variables.Variables.
from Products.DCWorkflow.Variables import Variables
security = ClassSecurityInfo()
security.declareObjectProtected(ManagePortal)
Variables.security = security
InitializeClass(Variables)
