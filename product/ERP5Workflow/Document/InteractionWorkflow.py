##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
#                    Wenjie Zheng <wenjie.zheng@tiolive.com>
#
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

import App
import transaction

from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.SecurityManagement import setSecurityManager
from Acquisition import aq_base
from Products.CMFActivity.ActiveObject import ActiveObject
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Expression import StateChangeInfo
from Products.ERP5Type import Permissions, PropertySheet, Globals
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.patches.Expression import Expression_createExprContext
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Workflow import addWorkflowFactory
from Products.ERP5Workflow.Document.Transition import TRIGGER_WORKFLOW_METHOD
from Products.ERP5Workflow.Document.Workflow import Workflow
from types import StringTypes
from zLOG import LOG, INFO, WARNING

# show as xml library
from lxml import etree
from lxml.etree import Element, SubElement
from xml.sax.saxutils import escape, unescape
from xml_marshaller.xml_marshaller import Marshaller
MARSHALLER_NAMESPACE_URI = 'http://www.erp5.org/namespaces/marshaller'
marshaller = Marshaller(namespace_uri=MARSHALLER_NAMESPACE_URI,
                                                            as_tree=True).dumps

_MARKER = []

class InteractionWorkflow(IdAsReferenceMixin("interactionworkflow_", "prefix"), XMLObject):
  """
  An ERP5 Interaction Workflow.
  """
  meta_type = 'ERP5 Workflow'
  portal_type = 'Interaction Workflow'
  _isAWorkflow = True # DCWorkflow Tool compatibility
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  default_reference = ''
  managed_permission_list = ()
  managed_role = ()

  intaractions = None
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
    PropertySheet.InteractionWorkflow,
  )


  def notifyCreated(self, document):
    pass

  security.declareProtected(Permissions.View, 'getChainedPortalTypeList')
  def getChainedPortalTypeList(self):
    """Returns the list of portal types that are chained to this
    interaction workflow."""
    chained_ptype_list = []
    wf_tool = getToolByName(self, 'portal_workflow')
    types_tool = getToolByName(self, 'portal_types')
    for ptype in types_tool.objectValues():
      if self.getId() in ptype.getTypeWorkflowList():
        chained_ptype_list.append(ptype.getId())
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
    vdef = self._getOb(name, None)
    if vdef is not None:
      if vdef.getTypeInfo().getId() == 'Variable':
        return 1
      return 0
    return 0

  security.declarePrivate('getInfoFor')
  def getInfoFor(self, ob, name, default):
    '''
    Allows the user to request information provided by the
    workflow.  This method must perform its own security checks.
    '''
    vdef = self._getOb(name, _MARKER)
    if vdef is _MARKER:
      return default
    if vdef.info_guard is not None and not vdef.info_guard.check(
      getSecurityManager(), self, ob):
      return default
    status = self.getCurrentStatusDict(ob)
    if status is not None and name in status:
      value = status[name]
    # Not set yet.  Use a default.
    elif vdef.default_expr is not None:
      ec = Expression_createExprContext(StateChangeInfo(ob, self, status))
      value = vdef.default_expr(ec)
    else:
      value = vdef.default_value

    return value

  security.declarePrivate('isWorkflowMethodSupported')
  def isWorkflowMethodSupported(self, ob, tid):
    '''
    Returns a true value if the given workflow method
    is supported in the current state.
    '''
    tdef = self._getOb('interaction_' + tid)
    if tdef is not None and self._checkTransitionGuard(tdef, ob):
      return 1
    return 0

  def _checkTransitionGuard(self, tdef, document, **kw):
    if tdef.temporary_document_disallowed:
      isTempDocument = getattr(document, 'isTempDocument', None)
      if isTempDocument is not None:
        if isTempDocument():
          return 0

    guard = tdef.getGuard()
    if guard is None:
      return 1
    if guard.check(getSecurityManager(), self, document, **kw):
      return 1
    return 0

  security.declarePrivate('getValidRoleList')
  def getValidRoleList(self):
    return sorted(self.getPortalObject().getDefaultModule('acl_users').valid_roles())

  security.declarePrivate('_updateWorkflowHistory')
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

  security.declarePrivate('getStateChangeInformation')
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

  security.declarePrivate('getCurrentStatusDict')
  def getCurrentStatusDict(self, document):
    """
    Get the current status dict.
    """
    workflow_key = self._generateHistoryKey()
    hist = document.workflow_history
    # Copy is requested
    result = hist.get(hist.keys()[-1])
    #result = document.workflow_history[workflow_key][-1].copy()
    return result

  security.declarePrivate('_generateHistoryKey')
  def _generateHistoryKey(self):
    """
    Generate a key used in the workflow history.
    """
    history_key = self.unrestrictedTraverse(self.getRelativeUrl()).getReference()
    return history_key

  security.declarePrivate('getinteraction_workflowVariableMatchDict')
  def getWorklistVariableMatchDict(self, info, check_guard=True):
    return None

  def _getWorkflowStateOf(self, ob, id_only=0):
    return None

  security.declarePrivate('getScriptValueList')
  def getScriptValueList(self):
    scripts = {}
    for script in self.objectValues(portal_type='Workflow Script'):
      scripts[script.getId()] = script
    return scripts

  security.declarePrivate('getTransitionValueList')
  def getTransitionValueList(self):
    interaction_dict = {}
    for tdef in self.objectValues(portal_type="Interaction"):
      interaction_dict[tdef.getReference()] = tdef
    return interaction_dict

  security.declarePrivate('getTransitionIdList')
  def getTransitionIdList(self):
    id_list = []
    for ob in self.objectValues(portal_type="Interaction"):
      id_list.append(ob.getReference())
    return id_list

  security.declarePrivate('notifyWorkflowMethod')
  def notifyWorkflowMethod(self, ob, transition_list, args=None, kw=None):
    """ InteractionWorkflow is stateless. Thus, this function should do nothing.
    """
    pass

  security.declarePrivate('notifyBefore')
  def notifyBefore(self, ob, transition_list, args=None, kw=None):
    status_dict = self.getCurrentStatusDict(ob)
    if type(transition_list) in StringTypes:
      return

    if kw is None:
      kw = {'workflow_method_args' : args}
    else:
      kw = kw.copy()
      kw['workflow_method_args'] = args
    filtered_transition_list = []

    for t_id in transition_list:
      tdef = self._getOb('interaction_' + t_id )
      assert tdef.trigger_type == TRIGGER_WORKFLOW_METHOD
      filtered_transition_list.append(tdef.getId())
      former_status = {}

      sci = StateChangeInfo(
      ob, self, former_status, tdef, None, None, kwargs=kw)

      before_script_list = []
      before_script_list.append(tdef.getBeforeScriptName())
      if before_script_list != [] and tdef.getBeforeScriptName() is not None:
        for script_name in before_script_list:
          script = self._getOb(script_name)
          script.execute(sci)
    return filtered_transition_list

  security.declarePrivate('notifySuccess')
  def notifySuccess(self, ob, transition_list, result, args=None, kw=None):
    """
    Notifies this workflow that an action has taken place.
    """
    if type(transition_list) in StringTypes:
      return

    if kw is None:
      kw = {'workflow_method_args' : args}
    else:
      kw = kw.copy()
      kw['workflow_method_args'] = args

    for t_id in transition_list:
      tdef = self._getOb('interaction_' + t_id )
      assert tdef.trigger_type == TRIGGER_WORKFLOW_METHOD
      former_status = {}
      econtext = None
      sci = None

      # Update variables.
      tdef_exprs = tdef.var_exprs
      if tdef_exprs is None: tdef_exprs = {}
      status = {}

      for vdef in self.objectValues(portal_type='Variable'):
        id = vdef.getId()
        if not vdef.for_status:
          continue
        expr = None
        if id in tdef_exprs:
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
              sci = StateChangeInfo(
                  ob, self, former_status, tdef,
                  None, None, None)
            econtext = Expression_createExprContext(sci)
          value = expr(econtext)
        status[id] = value

      sci = StateChangeInfo(
            ob, self, former_status, tdef, None, None, kwargs=kw)

      # Execute the "after" script.
      after_script_list = []
      after_script_list.append(tdef.getAfterScriptName())
      if after_script_list != [] and tdef.getAfterScriptName() is not None:
        for script_name in after_script_list:
          script = self ._getOb(script_name)
          # Pass lots of info to the script in a single parameter.
          script.execute(sci)  # May throw an exception

      # Queue the "Before Commit" scripts
      sm = getSecurityManager()
      before_commit_script_list = []
      before_commit_script_list.append(tdef.getBeforeCommitScriptName())
      if before_commit_script_list != [] and tdef.getBeforeCommitScriptName() is not None:
        for script_name in before_commit_script_list:
          transaction.get().addBeforeCommitHook(tdef._before_commit,
                                                (sci, script_name, sm))

      # Execute "activity" scripts
      activity_script_list = []
      activity_script_list.append(tdef.getActivateScriptName())
      if activity_script_list != [] and tdef.getActivateScriptName() is not None:
        for script_name in activity_script_list:
          self .activate(activity='SQLQueue')\
              .activeScript(script_name, ob.getRelativeUrl(),
                            status, tdef.getId())

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
        self._getOb(script_name)(sci)
      finally:
        setSecurityManager(current_security_manager)

  def activeScript(self, script_name, ob_url, former_status, tdef_id):
    script = self._getOb(script_name)
    ob = self.unrestrictedTraverse(ob_url)
    tdef = self._getOb(tdef_id)
    sci = StateChangeInfo(
          ob, self, former_status, tdef, None, None, kwargs=kw)
    script.execute(sci)

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

  def getStateValueList(self):
    return None

  def getManagedRoleList(self):
    return sorted(self.getPortalObject().getDefaultModule('acl_users').valid_roles())

  def showAsXML(self, root=None):
    if root is None:
      root = Element('erp5')
      return_as_object = False

    # Define a list of property to show to users:
    # It seems even in DC interaction workflow, creation guard hasn't been configured;
    # so it is not used? thus I didn't show creation guard as xml here. (zwj)
    interaction_workflow_prop_id_to_show = sorted(['title', 'description',
          'manager_bypass'])
    # workflow as XML, need to rename DC workflow's portal_type before comparison.
    interaction_workflow = SubElement(root, 'interaction_workflow',
                        attrib=dict(reference=self.getReference(),
                        portal_type=self.getPortalType()))

    for prop_id in sorted(interaction_workflow_prop_id_to_show):
      prop_value = self.getProperty(prop_id)
      prop_type = self.getPropertyType(prop_id)
      sub_object = SubElement(interaction_workflow, prop_id, attrib=dict(type=prop_type))
      sub_object.text = str(prop_value)

    # 1. Interaction as XML
    interaction_reference_list = []
    interaction_list = self.objectValues(portal_type='Interaction')
    interaction_prop_id_to_show = sorted(['actbox_category', 'actbox_url', 'actbox_name',
    'activate_script_name', 'after_script_name', 'before_commit_script_name',
    'description', 'groups', 'roles', 'expr', 'permissions', 'method_id',
    'once_per_transaction', 'portal_type_filter', 'portal_type_group_filter',
    'script_name', 'temporary_document_disallowed', 'trigger_type'])
    for tdef in interaction_list:
      interaction_reference_list.append(tdef.getReference())
    interactions = SubElement(interaction_workflow, 'interactions', attrib=dict(
      interaction_list=str(interaction_reference_list),
      number_of_element=str(len(interaction_reference_list))))
    for tdef in interaction_list:
      interaction = SubElement(interactions, 'interaction', attrib=dict(
            reference=tdef.getReference(),portal_type=tdef.getPortalType()))
      guard = SubElement(interaction, 'guard', attrib=dict(type='object'))
      for property_id in interaction_prop_id_to_show:
        # creationg guard
        if property_id in ['groups', 'permissions', 'roles']:
          if property_id == 'groups': prop_id = 'group_list'
          if property_id == 'permissions': prop_id = 'permission_list'
          if property_id == 'roles': prop_id = 'role_list'
          property_value = tdef.getProperty(prop_id)
          if property_value is not None:
            property_value = tuple(property_value)
          sub_object = SubElement(guard, property_id, attrib=dict(type='guard configuration'))
        elif property_id == 'expr':
          property_value = tdef.getProperty(prop_id)
          sub_object = SubElement(guard, property_id, attrib=dict(type='guard configuration'))
        # no-property definded action box configuration
        elif property_id in ['actbox_name', 'actbox_url', 'actbox_category', 'trigger_type']:
          property_value = getattr(tdef, property_id, None)
          sub_object = SubElement(interaction, property_id, attrib=dict(type='string'))
        elif property_id in ['activate_script_name', 'after_script_name', 'before_commit_script_name',
              'method_id', 'once_per_transaction', 'portal_type_filter', 'portal_type_group_filter',
              'script_name', 'temporary_document_disallowed']:
          if property_id == 'activate_script_name': prop_id = 'activate_script_name_list'
          if property_id == 'after_script_name': prop_id = 'after_script_name_list'
          if property_id == 'before_commit_script_name': prop_id = 'before_commit_script_name_list'
          if property_id == 'method_id': prop_id = 'trigger_method_id_list'
          if property_id == 'once_per_transaction': prop_id = 'trigger_once_per_transaction'
          if property_id == 'portal_type_filter': prop_id = 'portal_type_filter_list'
          if property_id == 'portal_type_group_filter': prop_id = 'portal_type_group_filter_list'
          if property_id == 'script_name': prop_id = 'before_script_name_list'
          if property_id == 'temporary_document_disallowed': prop_id = 'temporary_document_disallowed'
          property_value = tdef.getProperty(prop_id)

          if property_id in ['activate_script_name', 'after_script_name',
            'before_commit_script_name','script_name'] and property_value is not None:
            list_temp =[]
            for value in property_value:
              list_temp.append(self._getOb(value).getReference())
            property_value = list_temp
          sub_object = SubElement(interaction, property_id, attrib=dict(type='string'))
        else:
          property_value = tdef.getProperty(property_id)
          property_type = tdef.getPropertyType(property_id)
          sub_object = SubElement(interaction, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)

    # 2. Variable as XML
    variable_reference_list = []
    variable_list = self.objectValues(portal_type='Variable')
    variable_prop_id_to_show = ['description', 'default_expr',
          'for_catalog', 'for_status', 'update_always']
    for vdef in variable_list:
      variable_reference_list.append(vdef.getReference())
    variables = SubElement(interaction_workflow, 'variables', attrib=dict(variable_list=str(variable_reference_list),
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

    # 3. Script as XML
    script_reference_list = []
    script_list = self.objectValues(portal_type='Workflow Script')
    script_prop_id_to_show = sorted(['body', 'parameter_signature','proxy_roles'])
    for sdef in script_list:
      script_reference_list.append(sdef.getReference())
    scripts = SubElement(interaction_workflow, 'scripts', attrib=dict(script_list=str(script_reference_list),
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
