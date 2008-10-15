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
from types import StringTypes
from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
from Products.DCWorkflow.Expression import StateChangeInfo, createExprContext
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.CMFActivity.ActiveObject import ActiveObject
from Products.ERP5Type import Permissions

from zLOG import LOG

_MARKER = []

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
    a la Qt.

    Try to mimic: Workflow...

    Question: should be use it for values ? or use a global value model ?

    Status : OK


    Implementation:

    A new kind of workflow (stateless). Follow the DCWorkflow class.
    Provide filters (per portal_type, etc.). Allow inspection of objects ?
    """
    meta_type = 'Workflow'
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

    security.declareProtected(Permissions.View, 'getChainedPortalTypeList')
    def getChainedPortalTypeList(self):
        """Returns the list of portal types that are chained to this
        interaction workflow."""
        chained_ptype_list = []
        wf_tool = getToolByName(self, 'portal_workflow')
        types_tool = getToolByName(self, 'portal_types')
        for ptype in types_tool.objectIds():
            if self.getId() in wf_tool._chains_by_type.get(ptype, []) :
                chained_ptype_list.append(ptype)
        return chained_ptype_list
      
    security.declarePrivate('listObjectActions')
    def listObjectActions(self, info):
        return []

    security.declarePrivate('_changeStateOf')
    def _changeStateOf(self, ob, tdef=None, kwargs=None) :
      """
      InteractionWorkflow is stateless. Thus, this function should do nothing.
      """
      return

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
        vdef = self.variables.get(name, _MARKER)
        if vdef is _MARKER:
          return default
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

        NOTE: this method is not used in ERP5 because
        of transition_list approach
        '''
        tdef = self.interactions.get(method_id, None)
        if (tdef is not None and
          tdef.trigger_type == TRIGGER_WORKFLOW_METHOD and
          self._checkTransitionGuard(tdef, ob)):
          return 1
        return 0


    security.declarePrivate('wrapWorkflowMethod')
    def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
        '''
        Allows the user to request a workflow action.  This method
        must perform its own security checks.
        '''
        return

    security.declarePrivate('notifyWorkflowMethod')
    def notifyWorkflowMethod(self, ob, transition_list, args=None, kw=None):
      """
      InteractionWorkflow is stateless. Thus, this function should do nothing.
      """
      return

    security.declarePrivate('notifyBefore')
    def notifyBefore(self, ob, transition_list, args=None, kw=None):
        '''
        Notifies this workflow of an action before it happens,
        allowing veto by exception.  Unless an exception is thrown, either
        a notifySuccess() or notifyException() can be expected later on.
        The action usually corresponds to a method name.
        '''
        if type(transition_list) in StringTypes:
          return

        # Wrap args into kw since this is the only way
        # to be compatible with DCWorkflow
        # A better approach consists in extending DCWorkflow
        if kw is None:
          kw = {'workflow_method_args' : args}
        else:
          kw = kw.copy()
          kw['workflow_method_args'] = args
        filtered_transition_list = []

        for t_id in transition_list:
          tdef = self.interactions[t_id]
          if tdef.trigger_type == TRIGGER_WORKFLOW_METHOD:
            if (tdef.portal_type_filter is None or \
                ob.getPortalType() in tdef.portal_type_filter) and \
                self._checkTransitionGuard(tdef, ob, **kw):
              filtered_transition_list.append(tdef.id)
              former_status = self._getStatusOf(ob)
              # Execute the "before" script.
              for script_name in tdef.script_name:
                script = self.scripts[script_name]
                # Pass lots of info to the script in a single parameter.
                sci = StateChangeInfo(
                    ob, self, former_status, tdef, None, None, kwargs=kw)
                script(sci)  # May throw an exception

        return filtered_transition_list

    security.declarePrivate('notifySuccess')
    def notifySuccess(self, ob, transition_list, result, args=None, kw=None):
        '''
        Notifies this workflow that an action has taken place.
        '''
        if type(transition_list) in StringTypes:
          return

        kw = kw.copy()
        kw['workflow_method_args'] = args
        kw['workflow_method_result'] = result

        for t_id in transition_list:
          tdef = self.interactions[t_id]
          if tdef.trigger_type == TRIGGER_WORKFLOW_METHOD:
            if (tdef.portal_type_filter is None or \
                ob.getPortalType() in tdef.portal_type_filter):
              # Initialize variables
              former_status = self._getStatusOf(ob)
              econtext = None
              sci = None

              # Update variables.
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

              sci = StateChangeInfo(
                    ob, self, former_status, tdef, None, None, kwargs=kw)
              # Execute the "after" script.
              for script_name in tdef.after_script_name:
                script = self.scripts[script_name]
                # Pass lots of info to the script in a single parameter.
                script(sci)  # May throw an exception

              # Execute Before Commit
              transaction = get_transaction()
              for script_name in tdef.before_commit_script_name:
                script = self.scripts[script_name]
                transaction.beforeCommitHook(script, sci)

              # Execute "activity" scripts
              for script_name in tdef.activate_script_name:
                self.activate(activity='SQLQueue')\
                    .activeScript(script_name, ob.getRelativeUrl(),
                                  status, tdef.id)

    security.declarePrivate('activeScript')
    def activeScript(self, script_name, ob_url, status, tdef_id):
          script = self.scripts[script_name]
          ob = self.unrestrictedTraverse(ob_url)
          tdef = self.interactions.get(tdef_id)
          sci = StateChangeInfo(
                        ob, self, status, tdef, None, None, None)
          script(sci)

    def _getWorkflowStateOf(self, ob, id_only=0):
          return None

Globals.InitializeClass(InteractionWorkflowDefinition)

addWorkflowFactory(InteractionWorkflowDefinition, id='interaction_workflow',
                                     title='Web-configurable interaction workflow')
