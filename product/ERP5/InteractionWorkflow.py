# -*- coding: utf-8 -*-
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

import transaction
from Products.ERP5Type import Globals
import App
from types import StringTypes
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.SecurityManagement import setSecurityManager
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_WORKFLOW_METHOD
from Products.DCWorkflow.Expression import StateChangeInfo, createExprContext
from Products.ERP5Type.Workflow import addWorkflowFactory
from Products.CMFActivity.ActiveObject import ActiveObject
from Products.ERP5Type import Permissions

# show as xml library
from lxml.etree import Element, SubElement, tostring

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
    Returns a true value if the given workflow method
    is supported in the current state.
    '''
    tdef = self.interactions.get(method_id, None)
    return tdef is not None and self._checkTransitionGuard(tdef, ob)

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
      assert tdef.trigger_type == TRIGGER_WORKFLOW_METHOD
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
      assert tdef.trigger_type == TRIGGER_WORKFLOW_METHOD

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

      # Queue the "Before Commit" scripts
      sm = getSecurityManager()
      for script_name in tdef.before_commit_script_name:
        transaction.get().addBeforeCommitHook(self._before_commit,
                                              (sci, script_name, sm))

      # Execute "activity" scripts
      for script_name in tdef.activate_script_name:
        self.activate(activity='SQLQueue')\
            .activeScript(script_name, ob.getRelativeUrl(),
                          status, tdef.id)

  def _before_commit(self, sci, script_name, security_manager):
    # check the object still exists before calling the script
    ob = sci.object
    while ob.isTempObject():
      ob = ob.getParentValue()
    if aq_base(self.unrestrictedTraverse(ob.getPhysicalPath(), None)) is \
       aq_base(ob):
      current_security_manager = getSecurityManager()
      try:
        # Who knows what happened to the authentication context
        # between here and when the interaction was executed... So we
        # need to switch to the security manager as it was back then
        setSecurityManager(security_manager)
        self.scripts[script_name](sci)
      finally:
        setSecurityManager(current_security_manager)

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

  def _checkTransitionGuard(self, t, ob, **kw):
    # This check can be implemented with a guard expression, but
    # it has a lot of overhead to use a TALES, so we make a special
    # treatment for the frequent case, that is, disallow the trigger
    # on a temporary document.
    if t.temporary_document_disallowed:
      isTempDocument = getattr(ob, 'isTempDocument', None)
      if isTempDocument is not None:
        if isTempDocument():
          return 0

    return DCWorkflowDefinition._checkTransitionGuard(self, t, ob, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'getReference')
  def getReference(self):
    return self.id

  security.declarePrivate('getTransitionValueById')
  def getTransitionValueById(self, transition_id):
    if self.interactions is not None:
      return self.interactions.get(transition_id, None)
    return None

  security.declarePrivate('getTransitionValueList')
  def getTransitionValueList(self):
    if self.interactions is not None:
      return self.interactions.values()
    return []

  security.declarePrivate('getTransitionIdList')
  def getTransitionIdList(self):
    if self.interactions is not None:
      return self.interactions.objectIds()
    return []

  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalType')
  def getPortalType(self):
    return self.__class__.__name__

  security.declarePrivate('showAsXML')
  def showAsXML(self, root=None):
    if root is None:
      root = Element('erp5')
      return_as_object = False
    interaction_workflow_prop_id_to_show = {
          'description':'text', 'manager_bypass':'int'}
    interaction_workflow = SubElement(root, 'interaction_workflow',
                        attrib=dict(reference=self.getReference(),
                        portal_type='Interaction Workflow'))

    for prop_id in sorted(interaction_workflow_prop_id_to_show):
      prop_value = self.__dict__.get(prop_id, None)
      if prop_value is None or prop_value == [] or prop_value == ():
        prop_value = ''
      prop_type = interaction_workflow_prop_id_to_show[prop_id]
      sub_object = SubElement(interaction_workflow, prop_id, attrib=dict(type=prop_type))
      sub_object.text = str(prop_value)

    # 1. Interaction as XML
    interaction_reference_list = []
    interaction_id_list = sorted(self.interactions.keys())
    interaction_prop_id_to_show = {'actbox_category':'string', 'actbox_url':'string',
    'actbox_name':'string', 'activate_script_name':'string',
    'after_script_name':'string', 'before_commit_script_name':'string',
    'description':'text', 'guard':'object', 'method_id':'string',
    'once_per_transaction':'string', 'portal_type_filter':'string',
    'portal_type_group_filter':'string', 'script_name':'string',
    'temporary_document_disallowed':'string', 'trigger_type':'string'}
    for tid in interaction_id_list:
      interaction_reference_list.append(tid)
    interactions = SubElement(interaction_workflow, 'interactions', attrib=dict(
      interaction_list=str(interaction_reference_list),
      number_of_element=str(len(interaction_reference_list))))
    for tid in interaction_id_list:
      tdef = self.interactions[tid]
      interaction = SubElement(interactions, 'interaction', attrib=dict(
            reference=tdef.getReference(),portal_type='Interaction'))
      guard = SubElement(interaction, 'guard', attrib=dict(type='object'))
      for property_id in sorted(interaction_prop_id_to_show):
        # creationg guard
        if property_id == 'guard':
          for prop_id in sorted(['groups', 'permissions', 'expr', 'roles']):
            guard_obj = getattr(tdef, 'guard')
            if guard_obj is not None:
              if prop_id in guard_obj.__dict__:
                if prop_id == 'expr':
                  prop_value =  getattr(guard_obj.expr, 'text', '')
                else: prop_value = guard_obj.__dict__[prop_id]
              else:
                prop_value = ''
            else:
              prop_value = ''
            guard_config = SubElement(guard, prop_id, attrib=dict(type='guard configuration'))
            if prop_value is None or prop_value == () or prop_value == []:
              prop_value = ''
            guard_config.text = str(prop_value)
        # no-property definded action box configuration
        elif property_id in sorted(['actbox_name', 'actbox_url', 'actbox_category']):
          property_value = getattr(tdef, property_id, None)
          sub_object = SubElement(interaction, property_id, attrib=dict(type='string'))
        else:
          if property_id in tdef.__dict__:
            property_value = tdef.__dict__[property_id]
          else:
            property_value = ''
          property_type = interaction_prop_id_to_show[property_id]
          sub_object = SubElement(interaction, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value == [] or property_value == ():
          property_value = ''
        if property_id in ['once_per_transaction', 'temporary_document_disallowed']:
          if property_value == True:
            property_value = '1'
          elif property_value == False or property_value is '':
            property_value = '0'
        sub_object.text = str(property_value)

    # 2. Variable as XML
    variable_reference_list = []
    variable_id_list = sorted(self.variables.keys())
    variable_prop_id_to_show = {'description':'text',
          'default_expr':'string', 'for_catalog':'int', 'for_status':'int',
          'update_always':'int'}
    for vid in variable_id_list:
      variable_reference_list.append(vid)
    variables = SubElement(interaction_workflow, 'variables', attrib=dict(variable_list=str(variable_reference_list),
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

    # 3. Script as XML
    script_reference_list = []
    script_id_list = sorted(self.scripts.keys())
    script_prop_id_to_show = {'body':'string', 'parameter_signature':'string',
          'proxy_roles':'tokens'}
    for sid in script_id_list:
      script_reference_list.append(sid)
    scripts = SubElement(interaction_workflow, 'scripts', attrib=dict(script_list=str(script_reference_list),
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
        if property_value is None or property_value == [] or property_value == ():
          property_value = ''
        sub_object.text = str(property_value)

    # return xml object
    if return_as_object:
      return root
    return tostring(root, encoding='utf-8',
                          xml_declaration=True, pretty_print=True)

Globals.InitializeClass(InteractionWorkflowDefinition)

addWorkflowFactory(InteractionWorkflowDefinition, id='interaction_workflow',
                   title='Web-configurable interaction workflow')
