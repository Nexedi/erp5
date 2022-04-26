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
from __future__ import absolute_import
"""
DCWorkflow implementation *deprecated* in favor of ERP5 Workflow.
"""
from Products.ERP5Type import WITH_LEGACY_WORKFLOW
assert WITH_LEGACY_WORKFLOW

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
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.ERP5Type.Workflow import addWorkflowFactory
from Products.CMFActivity.ActiveObject import ActiveObject
from Products.ERP5Type import Permissions
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.Core.Workflow import createExpressionContext

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

  # Do not seem to be used for InteractionWorkflow but must be defined
  # (GuardMixin.checkGuard())
  isManagerBypass = ConstantGetter('isManagerBypass', value=False)

  security = ClassSecurityInfo()

  manage_options = (
    {'label': 'Properties', 'action': 'manage_properties'},
    {'label': 'Interactions', 'action': 'interactions/manage_main'},
    {'label': 'Variables', 'action': 'variables/manage_main'},
    {'label': 'Scripts', 'action': 'scripts/manage_main'},
    ) + App.Undo.UndoSupport.manage_options

  def __init__(self, id):
    self.id = id
    from .Interaction import Interaction
    self._addObject(Interaction('interactions'))
    from Products.DCWorkflow.Variables import Variables
    self._addObject(Variables('variables'))
    from Products.DCWorkflow.Worklists import Worklists
    self._addObject(Worklists('worklists'))
    from Products.DCWorkflow.Scripts import Scripts
    self._addObject(Scripts('scripts'))

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
    # BBB for when an upgrade to callInterationScript still has unexecuted
    # activeScript activities leftover from the previous code.
    self.callInterationScript(
      script_name=script_name,
      ob=self.unrestrictedTraverse(ob_url),
      status=status,
      tdef_id=tdef_id,
    )

  security.declarePrivate('callInterationScript')
  def callInterationScript(self, script_name, ob, status, tdef_id):
    self.scripts[script_name](
      StateChangeInfo(
        ob, self, status,
        self.interactions.get(tdef_id),
        None, None, None,
      ),
    )

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

  def getVariableValueDict(self):
    if self.variables is None:
      return {}
    return self.variables

  security.declareProtected(Permissions.AccessContentsInformation, 'getId')
  def getId(self):
    return self.id

  security.declareProtected(Permissions.AccessContentsInformation, 'getReference')
  def getReference(self):
    return self.id

  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
  def getTitle(self):
    return self.title

  security.declareProtected(Permissions.AccessContentsInformation, 'getDescription')
  def getDescription(self):
    return self.description

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionValueByReference')
  def getTransitionValueByReference(self, transition_id):
    if self.interactions is not None:
      return self.interactions.get(transition_id, None)
    return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionValueList')
  def getTransitionValueList(self):
    if self.interactions is not None:
      return list(self.interactions.values())
    return []

  security.declareProtected(Permissions.AccessContentsInformation, 'getTransitionReferenceList')
  def getTransitionReferenceList(self):
    if self.interactions is not None:
      return self.interactions.objectIds()
    return []

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariableValueList')
  def getVariableValueList(self):
    if self.variables is not None:
      return list(self.variables.values())
    return []

  security.declareProtected(Permissions.AccessContentsInformation, 'getPortalType')
  def getPortalType(self):
    return self.__class__.__name__

  security.declarePrivate('showAsXML')
  def showAsXML(self, root=None):
    from lxml.etree import Element, SubElement, tostring
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
    interaction_prop_id_to_show = {
      'actbox_category':'string', 'actbox_url':'string',
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
            reference=tdef.getReference(),portal_type='Interaction Workflow Interaction'))
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
    variable_prop_id_to_show = {
      'description':'text',
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
    script_prop_id_to_show = {
      'body':'string', 'parameter_signature':'string',
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

    if return_as_object:
      return root
    return tostring(root, encoding='utf-8',
                    xml_declaration=True, pretty_print=True)

addWorkflowFactory(InteractionWorkflowDefinition, id='interaction_workflow',
                   title='Web-configurable interaction workflow')

## Avoid copy/paste from Products.ERP5Type.Core.InteractionWorkflowInteraction
from functools import partial as _p
from Products.ERP5Type.Core.InteractionWorkflow import InteractionWorkflow as ERP5InteractionWorkflow
InteractionWorkflowDefinition.security = ClassSecurityInfo()
_s = InteractionWorkflowDefinition.security
for method_name, security in (
    ('getChainedPortalTypeList', _p(_s.declareProtected, Permissions.View)),
    ('listObjectActions', _s.declarePrivate),
    ('_changeStateOf', _s.declarePrivate),
    ('notifyWorkflowMethod', _s.declarePrivate),
    ('wrapWorkflowMethod', _s.declarePrivate),
    ('_getWorkflowStateOf', None),
    ('isInfoSupported', _s.declarePrivate),
    ('getInfoFor', _s.declarePrivate),
    ('isWorkflowMethodSupported', _s.declarePrivate),
    ('notifyBefore', _s.declarePrivate),
    ('notifySuccess', _s.declarePrivate),
    ):
  if security is not None:
    security(method_name)
  func = getattr(ERP5InteractionWorkflow, method_name)
  import six
  if six.PY2:
    func = func.__func__
  setattr(InteractionWorkflowDefinition, method_name, func)

Globals.InitializeClass(InteractionWorkflowDefinition)
