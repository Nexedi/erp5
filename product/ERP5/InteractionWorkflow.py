##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
##############################################################################

import Globals
import App
from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore.utils import getToolByName, _getAuthenticatedUser
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_AUTOMATIC, TRIGGER_WORKFLOW_METHOD
from Products.CMFCore.WorkflowCore import WorkflowException, \
     ObjectDeleted, ObjectMoved
from Products.DCWorkflow.Expression import StateChangeInfo, createExprContext
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.CMFActivity.ActiveObject import ActiveObject

from zLOG import LOG

class InteractionWorkflowDefinition (DCWorkflowDefinition, ActiveObject):
    """
    The InteractionTool implements portal object
    interaction policies.

    An interaction is defined by
    a domain and a behaviour:

    The domain is defined as:

    - the meta_type it applies to

    - the portal_type it applies to

    - the conditions of application (category membership, value range,
      security, function, etc.)

    The transformation template is defined as:

    - pre method executed before

    - pre async executed anyway

    - post method executed after success before return

    - post method executed after success anyway

    This is similar to signals and slots except is applies to classes
    rather than instances. Similar to
    stateless workflow methods with more options. Similar to ZSQL scipts
    but in more cases.

    Examples of applications:

    - when movement is updated, apply transformation rules to movement

    - when stock is 0, post an event of stock empty

    - when birthday is called, call the happy birthday script
    
    ERP5 main application: specialize behaviour of classes "on the fly".
    Make the architecture as modular as possible. Implement connections
    à la Qt.

    Try to mimic: Workflow...

    Question: should be use it for values ? or use a global value model ?

    Status : OK


    Implementation:

    A new kind of workflow (stateless). Follow the DCWorkflow class.
    Provide filters (per portal_type, etc.). Allow inspection of objects ?
    """
    meta_type = 'Interaction Workflow'
    title = 'Interaction Workflow Definition'

    interactions = None

    security = ClassSecurityInfo()

    manage_options = (
        {'label': 'Properties', 'action': 'manage_properties'},
        {'label': 'Interactions', 'action': 'interactions/manage_main'},
        {'label': 'Variables', 'action': 'variables/manage_main'},
        {'label': 'Scripts', 'action': 'scripts/manage_main'},
        ) + App.Undo.UndoSupport.manage_options

    def __init__(self, id):
        self.id = id
        from Interaction import Interaction
        self._addObject(Interaction('interactions'))
        from Products.DCWorkflow.Variables import Variables
        self._addObject(Variables('variables'))
        from Products.DCWorkflow.Worklists import Worklists
        self._addObject(Worklists('worklists'))
        from Products.DCWorkflow.Scripts import Scripts
        self._addObject(Scripts('scripts'))

    def _executeTransition(self, ob, tdef=None, kwargs=None):
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
        if tdef is not None:
          for script_name in tdef.script_name:
            script = self.scripts[script_name]
            # Pass lots of info to the script in a single parameter.
            sci = StateChangeInfo(
                ob, self, former_status, tdef, old_sdef, new_sdef, kwargs)
            try:
                script(sci)  # May throw an exception.
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

        # Update state.
        status[self.state_var] = new_state
        tool = aq_parent(aq_inner(self))
        tool.setStatusOf(self.id, ob, status)

        # Update role to permission assignments.
        self.updateRoleMappingsFor(ob)

        # Execute the "after" script.
        if tdef is not None:
          for after_script_name in tdef.after_script_name:
              script = self.scripts[after_script_name]
              # Pass lots of info to the script in a single parameter.
              sci = StateChangeInfo(
                  ob, self, status, tdef, old_sdef, new_sdef, kwargs)
              script(sci)  # May throw an exception.

        # Execute the "activate" script.
        if tdef is not None:
          for after_script_name in tdef.activate_script_name:
              script = self.scripts[after_script_name]
              # Pass lots of info to the script in a single parameter.
              sci = StateChangeInfo(
                  ob.activate(activity='SQLQueue'), None, status, tdef, old_sdef, new_sdef, kwargs)
              script(sci)  # May throw an exception.
        
        # Return the new state object.
        if moved_exc is not None:
            # Propagate the notification that the object has moved.
            raise moved_exc
        else:
            return new_sdef

    security.declarePrivate('listObjectActions')
    def listObjectActions(self, info):
        return []

    security.declarePrivate('isInfoSupported')
    def isInfoSupported(self, ob, name):
        '''
        Returns a true value if the given info name is supported.
        '''
        vdef = self.variables.get(name, None)
        if vdef is None:
            return 0
        return 1
    
    security.declarePrivate('getInfoFor')
    def getInfoFor(self, ob, name, default):
        '''
        Allows the user to request information provided by the
        workflow.  This method must perform its own security checks.
        '''
        vdef = self.variables[name]
        if vdef.info_guard is not None and not vdef.info_guard.check(
            getSecurityManager(), self, ob):
            return default
        status = self._getStatusOf(ob)
        if status is not None and status.has_key(name):
            value = status[name]
        # Not set yet.  Use a default.
        elif vdef.default_expr is not None:
            ec = createExprContext(StateChangeInfo(ob, self, status))
            value = vdef.default_expr(ec)
        else:
            value = vdef.default_value

        return value
    
    security.declarePrivate('isWorkflowMethodSupported')
    def isWorkflowMethodSupported(self, ob, method_id):
        '''
        Returns a true value if the given workflow is 
        automatic with the propper method_id
        '''
        return 0
        for t in self.interactions.values():
            if t.trigger_type == TRIGGER_WORKFLOW_METHOD:
                if t.method_id == method_id:
                    if t.portal_type_filter is None:
                      return 1
                    elif ob.getPortalType() in t.portal_type_filter:
                      return 1
        return 0                


    security.declarePrivate('wrapWorkflowMethod')
    def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
        '''
        Allows the user to request a workflow action.  This method
        must perform its own security checks.
        '''
        
        for t in self.interactions.values():
            tdef = None
            if t.trigger_type == TRIGGER_WORKFLOW_METHOD:
                if t.method_id == method_id:
                    if t.portal_type_filter is None:
                      tdef = t
                    elif ob.getPortalType() in t.portal_type_filter:
                      tdef = t
            if tdef is not None:
                # Only execute if guard OK
                if self._checkTransitionGuard(tdef, ob):
                    res = apply(func, args, kw)
                    try:
                        self._changeStateOf(ob, tdef)
                    except ObjectDeleted:
                        # Re-raise with a different result.
                        raise ObjectDeleted(res)
                    except ObjectMoved, ex:
                        # Re-raise with a different result.
                        raise ObjectMoved(ex.getNewObject(), res)
                    return res

    security.declarePrivate('notifyBefore')
    def notifyBefore(self, ob, action, args=None, kw=None):
        '''
        Notifies this workflow of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''
        for t in self.interactions.values():
            tdef = None
            if t.trigger_type == TRIGGER_AUTOMATIC:
                if t.portal_type_filter is None:
                  tdef = t
                elif ob.getPortalType() in t.portal_type_filter:
                  tdef = t
            elif t.trigger_type == TRIGGER_WORKFLOW_METHOD:
                if t.method_id == action:
                    if t.portal_type_filter is None:
                      tdef = t
                    elif ob.getPortalType() in t.portal_type_filter:
                      tdef = t
            if tdef is not None:
                former_status = self._getStatusOf(ob)
                # Execute the "before" script.
                for script_name in tdef.script_name:
                    script = self.scripts[script_name]
                    # Pass lots of info to the script in a single parameter.
                    sci = StateChangeInfo(
                        ob, self, former_status, tdef, None, None, None)
                    try:
                        script(sci)  # May throw an exception.
                    except ObjectMoved, moved_exc:
                        ob = moved_exc.getNewObject()
                        # Re-raise after transition
                return                      

    security.declarePrivate('notifySuccess')
    def notifySuccess(self, ob, action, result, args=None, kw=None):
        '''
        Notifies this workflow that an action has taken place.
        '''
        for t in self.interactions.values():
            tdef = None
            if t.trigger_type == TRIGGER_AUTOMATIC:
                if t.portal_type_filter is None:
                  tdef = t
                elif ob.getPortalType() in t.portal_type_filter:
                  tdef = t
            elif t.trigger_type == TRIGGER_WORKFLOW_METHOD:
                if t.method_id == action:
                    if t.portal_type_filter is None:
                      tdef = t
                    elif ob.getPortalType() in t.portal_type_filter:
                      tdef = t            
            if tdef is not None:
                # Update variables.
                former_status = self._getStatusOf(ob)
                tdef_exprs = tdef.var_exprs
                if tdef_exprs is None: tdef_exprs = {}
                status = {}
                for id, vdef in self.variables.items():
                    if not vdef.for_status:
                        continue
                    expr = None
                    if tdef_exprs.has_key(id):
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
                                    None, None, None)
                            econtext = createExprContext(sci)
                        value = expr(econtext)
                    status[id] = value
        
                # Update state.
                tool = aq_parent(aq_inner(self))
                tool.setStatusOf(self.id, ob, status)
        
                # Execute the "after" script.
                for script_name in tdef.after_script_name:
                    script = self.scripts[script_name]
                    # Pass lots of info to the script in a single parameter.
                    sci = StateChangeInfo(
                        ob, self, status, tdef, None, None, None)
                    try:
                        script(sci)  # May throw an exception.
                    except ObjectMoved, moved_exc:
                        ob = moved_exc.getNewObject()
                        # Re-raise after transition

                # Execute the "after" script.
                for script_name in tdef.activate_script_name:
                    self.activate(activity='SQLQueue').activeScript(script_name, ob.getRelativeUrl(), status, tdef.id)
                
                return
    
    security.declarePrivate('activeScript')
    def activeScript(self, script_name, ob_url, status, tdef_id):
          script = self.scripts[script_name]
          ob = self.restrictedTraverse(ob_url)
          tdef = self.interactions.get(tdef_id)
          sci = StateChangeInfo(
                        ob, self, status, tdef, None, None, None)                        
          script(sci)                         
  
          
Globals.InitializeClass(InteractionWorkflowDefinition)

addWorkflowFactory(InteractionWorkflowDefinition, id='interaction_workflow',
                                     title='Web-configurable interaction workflow')
