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

# Optimized rendering of global actions (cache)

from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition, StateChangeInfo, ObjectMoved, createExprContext, aq_parent, aq_inner
from Products.DCWorkflow import DCWorkflow
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD, TransitionDefinition
from AccessControl import getSecurityManager, ClassSecurityInfo, ModuleSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import  _getAuthenticatedUser
from DocumentTemplate.DT_Util import TemplateDict
from DateTime import DateTime
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Utils import convertToMixedCase
from string import join

def DCWorkflowDefinition_listGlobalActions(self, info):
    '''
    Allows this workflow to
    include actions to be displayed in the actions box.
    Called on every request.
    Returns the actions to be displayed to the user.
    '''
    def _listGlobalActions(user=None, id=None, portal_path=None):
      if not self.worklists:
          return None  # Optimization
      sm = getSecurityManager()
      portal = self._getPortalRoot()
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
              # to implement worklists and search of local roles
              searchres_len = 0
              var_match_keys = qdef.getVarMatchKeys()
              if var_match_keys:
                  # Check the catalog for items in the worklist.
                  catalog = getToolByName(self, 'portal_catalog')
                  dict = {}
                  for k in var_match_keys:
                      v = qdef.getVarMatch(k)
                      v_fmt = map(lambda x, info=info: x%info, v)
                      dict[k] = v_fmt
                  # Patch for ERP5 by JP Smets in order
                  # to implement worklists and search of local roles
                  if not (guard is None or guard.check(sm, self, portal)):
                      dict['local_roles'] = guard.roles
                  # Patch to use ZSQLCatalog and get high speed
                  # LOG("PatchedDCWorkflowDefinition", 0, dict)
                  searchres_len = int(apply(catalog.countResults, (), dict)[0][0])
                  if searchres_len == 0:
                      continue
              if fmt_data is None:
                  fmt_data = TemplateDict()
                  fmt_data._push(info)
              fmt_data._push({'count': searchres_len})
              # Patch for ERP5 by JP Smets in order
              # to implement worklists and search of local roles
              if dict.has_key('local_roles'):
                fmt_data._push({'local_roles': join(guard.roles,';')})
              else:
                fmt_data._push({'local_roles': ''})
              res.append((id, {'name': qdef.actbox_name % fmt_data,
                              'url': qdef.actbox_url % fmt_data,
                              'worklist_id': id,
                              'workflow_title': self.title,
                              'workflow_id': self.id,
                              'permissions': (),  # Predetermined.
                              'category': qdef.actbox_category}))
              fmt_data._pop()
      res.sort()
      return map((lambda (id, val): val), res)

    # Return Cache
    _listGlobalActions = CachingMethod(_listGlobalActions, id='listGlobalActions', cache_duration = 300)
    user = str(_getAuthenticatedUser(self))
    return _listGlobalActions(user=user, id=self.id, portal_path=self._getPortalRoot().getPhysicalPath())


DCWorkflowDefinition.listGlobalActions = DCWorkflowDefinition_listGlobalActions

class ValidationFailed(Exception):
    """Transition can not be executed because data is not in consistent state"""

DCWorkflow.ValidationFailed = ValidationFailed

ModuleSecurityInfo('Products.DCWorkflow.DCWorkflow').declarePublic('ValidationFailed')


def DCWorkflowDefinition_executeTransition(self, ob, tdef=None, kwargs=None):
    '''
    Private method.
    Puts object in a new state.
    '''
    sci = None
    econtext = None
    moved_exc = None

    # Figure out the old and new states.
    old_sdef = self._getWorkflowStateOf(ob)
    old_state = old_sdef.getId()
    if tdef is None:
        new_state = self.initial_state
        former_status = {}
    else:
        new_state = tdef.new_state_id
        if not new_state:
            # Stay in same state.
            new_state = old_state
        former_status = self._getStatusOf(ob)
    new_sdef = self.states.get(new_state, None)
    if new_sdef is None:
        raise WorkflowException, (
            'Destination state undefined: ' + new_state)

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
            before_script_error_message = str(validation_exc)
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
        sci.setWorkflowVariable(ob, workflow_id=self.id, error_message = before_script_error_message)
        return new_sdef

    # Update state.
    status[self.state_var] = new_state
    tool = aq_parent(aq_inner(self))
    tool.setStatusOf(self.id, ob, status)

    # Make sure that the error message is empty. # Why ?
    #sci = StateChangeInfo(
    #    ob, self, status, tdef, old_sdef, new_sdef, kwargs)
    #sci.setWorkflowVariable(ob, error_message = '')

    # Update role to permission assignments.
    self.updateRoleMappingsFor(ob)

    # Execute the "after" script.
    if tdef is not None and tdef.after_script_name:
        # Script can be either script or workflow method
        #LOG('_executeTransition', 0, 'new_sdef.transitions = %s' % (repr(new_sdef.transitions)))
        if tdef.after_script_name in filter(lambda k: self.transitions[k].trigger_type == TRIGGER_WORKFLOW_METHOD,
                                                                                  new_sdef.transitions):
          script = getattr(ob, convertToMixedCase(tdef.after_script_name))
          script()
        else:
          script = self.scripts[tdef.after_script_name]
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
            if sdef.permission_roles is not None:
                roles = sdef.permission_roles.get(p, roles)
                if type(roles) is type(()):
                  role_type = 'tuple'
                roles = list(roles)
            # We will check that each role is activated
            # in each DCWorkflow
            for other_workflow,other_sdef in other_data_list:
              if p in other_workflow.permissions:
                for role in roles:
                  other_roles = other_sdef.permission_roles.get(p, [])
                  if type(other_roles) is type(()) :
                    role_type = 'tuple'
                  if role not in other_roles :
                    refused_roles.append(role)
            for role in refused_roles :
              roles.remove(role)
            if role_type=='tuple':
              roles = tuple(roles)
            if modifyRolesForPermission(ob, p, roles):
                changed = 1
    return changed

DCWorkflowDefinition.updateRoleMappingsFor = updateRoleMappingsFor

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
    return self.getWorkflow().scripts.keys() + [k for k in self.getWorkflow().transitions.keys() if self.getWorkflow().transitions[k].trigger_type == TRIGGER_WORKFLOW_METHOD]

TransitionDefinition.getAvailableScriptIds = ERP5TransitionDefinition.getAvailableScriptIds
