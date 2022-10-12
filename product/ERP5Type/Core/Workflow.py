# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2001 Zope Foundation and Contributors.
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

## Used in Products.ERP5Type.patches.DCWorkflow so this needs to go first...
from six import string_types as basestring
from Products.ERP5Type.Utils import ensure_list
from Acquisition import aq_parent, aq_inner
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from AccessControl import getSecurityManager
from Products.PageTemplates.Expressions import getEngine
from six import reraise
import six

def createExpressionContext(sci):
    '''
    An expression context provides names for TALES expressions.
    '''
    ob = sci.object
    wf = sci.workflow
    container = aq_parent(aq_inner(ob))
    data = {
        'here':         ob,
        'object':       ob,
        'container':    container,
        'folder':       container,
        'nothing':      None,
        'root':         ob.getPhysicalRoot(),
        'request':      getattr( ob, 'REQUEST', None ),
        'modules':      SecureModuleImporter,
        'user':         getSecurityManager().getUser(),
        'state_change': sci,
        'transition':   sci.transition,
        'status':       sci.status,
        'kwargs':       sci.kwargs,
        'workflow':     wf,
        }
    # BBB: support 'scripts.xxx' in TALES expression for legacy workflow,
    # that should be 'workflow.script_xxx' instead in ERP5 Workflow.
    if WITH_LEGACY_WORKFLOW and wf.meta_type == 'Workflow':
        data['scripts'] = wf.scripts
    return getEngine().getContext(data)

from MultiMapping import MultiMapping
class SafeMapping(MultiMapping):
  """
  Mapping with security declarations and limited method exposure.

  Since it subclasses MultiMapping, this class can be used to wrap
  one or more mapping objects.  Restricted Python code will not be
  able to mutate the SafeMapping or the wrapped mappings, but will be
  able to read any value.

  Imported from Products.DCWorkflow.Expression
  """
  __allow_access_to_unprotected_subobjects__ = 1
  push = pop = None
  _push = MultiMapping.push
  _pop = MultiMapping.pop

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.WorkflowCore import ObjectDeleted, ObjectMoved
from AccessControl import ClassSecurityInfo
class StateChangeInfo(object):
  """
  Provides information for expressions and scripts.

  Imported from Products.DCWorkflow.Expression
  """
  _date = None

  ObjectDeleted = ObjectDeleted
  ObjectMoved = ObjectMoved

  security = ClassSecurityInfo()
  security.setDefaultAccess('allow')

  def __init__(self, object, workflow, status=None, transition=None,
               old_state=None, new_state=None, kwargs=None):
    if kwargs is None:
      kwargs = {}
    else:
      # Don't allow mutation
      kwargs = SafeMapping(kwargs)
    if status is None:
      tool = aq_parent(aq_inner(workflow))
      status = tool.getStatusOf(workflow.id, object)
      if status is None:
        status = {}
    if status:
      # Don't allow mutation
      status = SafeMapping(status)
    self.object = object
    self.workflow = workflow
    self.old_state = old_state
    self.new_state = new_state
    self.transition = transition
    self.status = status
    self.kwargs = kwargs

  def __getitem__(self, name):
    if name[:1] != '_' and hasattr(self, name):
      return getattr(self, name)
    raise KeyError(name)

  def getHistory(self):
    wf = self.workflow
    tool = aq_parent(aq_inner(wf))
    wf_id = wf.id
    h = tool.getHistoryOf(wf_id, self.object)
    if h:
      return [d.copy() for d in h]  # Don't allow mutation
    else:
      return ()

  def getPortal(self):
    ob = aq_inner(self.object)
    while ob is not None:
      if ISiteRoot.providedBy(ob):
        return ob
      ob = aq_parent(ob)
    return None

  def getDateTime(self):
    date = self._date
    if not date:
      date = self._date = DateTime()
    return date

  def setWorkflowVariable(self, **kw):
    """
    Allows to go through security checking and let a script allows to modify
    a workflow variable
    """
    history = self.object.workflow_history[self.workflow.getReference()]
    history[-1].update(kw)
    history._p_changed = 1

from Products.ERP5Type.Globals import InitializeClass
InitializeClass(StateChangeInfo)
from Products.PythonScripts.Utility import allow_class
allow_class(StateChangeInfo)

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
if WITH_LEGACY_WORKFLOW:
  ## Patch for ERP5 Workflow: This must go before any Products.DCWorkflow
  ## imports as createExprContext() is from-imported in several of its modules
  import Products.DCWorkflow.Expression
  Products.DCWorkflow.Expression.createExprContext = createExpressionContext
  import inspect
  for _, __m in inspect.getmembers(Products.DCWorkflow, inspect.ismodule):
    if 'createExprContext' in __m.__dict__:
      assert __m.__dict__['createExprContext'] is createExpressionContext

import sys

from collections import  defaultdict
from AccessControl.unauthorized import Unauthorized
from AccessControl.Permission import Permission
from Acquisition import aq_base
from copy import deepcopy
from DateTime import DateTime
from DocumentTemplate.DT_Util import TemplateDict
from Products.CMFCore.Expression import Expression
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.DCWorkflow.utils import Message as _
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.Utils import convertToMixedCase
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Core.WorkflowTransition import (TRIGGER_AUTOMATIC,
                                                       TRIGGER_USER_ACTION,
                                                       TRIGGER_WORKFLOW_METHOD)

_marker = ''

from Products.CMFCore.Expression import getEngine
userGetIdOrUserNameExpression = Expression('user/getIdOrUserName')
userGetIdOrUserNameExpression._v_compiled = getEngine().compile(
  userGetIdOrUserNameExpression.text)

class ValidationFailed(Exception):
  """
  Transition can not be executed because data is not in consistent state
  """
  __allow_access_to_unprotected_subobjects__ = {'msg': 1}
  def __init__(self, message_instance=None):
    """
    Redefine init in order to register the message class instance
    """
    Exception.__init__(self, message_instance)
    self.msg = message_instance
from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.ERP5Type.Core.Workflow').declarePublic('ValidationFailed')

class Workflow(XMLObject):
  """
  ERP5 Workflow implementation deprecating DCWorkflow
  """
  meta_type = 'ERP5 Workflow'
  portal_type = 'Workflow'
  add_permission = Permissions.AddPortalContent

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (
    'Base',
    'XMLObject',
    'CategoryCore',
    'DublinCore',
    'Comment',
    'Workflow',
  )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getReference')
  def getReference(self):
    """
    For a Workflow, 'reference' is the same as ID. This getter is defined here
    for API consistency sake with its subobjects using reference as ID are
    prefixed (state_XXX, transition_XXX...).
    """
    return self.id

  def _setReference(self, reference):
    return self.setId(reference)

  security.declareProtected(Permissions.ModifyPortalContent, 'setReference')
  setReference = _setReference

  def cb_isMoveable(self):
    return self.cb_userHasCopyOrMovePermission()

  security.declarePrivate('notifyCreated')
  def notifyCreated(self, ob):
    """
    Notifies this workflow after an object has been created and added.
    """
    try:
      self._changeStateOf(ob, None)
    except (ObjectDeleted,ObjectMoved):
      pass

  security.declarePublic('getDateTime')
  def getDateTime(self):
    """
    Return current date time.
    """
    return DateTime()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateChangeInformation')
  def getStateChangeInformation(self, ob, state, transition=None):
    """
    Return an object used for variable tales expression.
    """
    if transition is None:
      transition_url = None
    else:
      transition_url = transition.getRelativeUrl()
    return self.asContext(document=ob,
                          transition=transition,
                          transition_url=transition_url,
                          state=state)

  security.declarePrivate('isWorkflowMethodSupported')
  def isWorkflowMethodSupported(self, ob, transition_reference, state=None):
    """
    Returns a true value if the given workflow method
    is supported in the current state.
    """
    # The optional argument state is used to avoid multiple expensive calls to
    # _getWorkflowStateOf. This method should be kept private.
    if state is None:
      state = self._getWorkflowStateOf(ob)
      if state is None:
        return False
    if (self.getTransitionIdByReference(transition_reference) in
        state.getDestinationIdList()):
      transition = self.getTransitionValueByReference(transition_reference)
      if (transition is not None and
          transition.getTriggerType() == TRIGGER_WORKFLOW_METHOD and
          self._checkTransitionGuard(transition, ob)):
        return True
    return False

  security.declarePrivate('isActionSupported')
  def isActionSupported(self, ob, action, state=None, **kw):
    """
    Returns a true value if the given action name
    is possible in the current state.
    """
    if state is None:
      state = self._getWorkflowStateOf(ob)
      if state is None:
        return 0

    action_id = self.getTransitionIdByReference(action)
    if action_id in state.getDestinationIdList():
      transition = getattr(self, action_id, None)
      if (transition is not None and
        transition.getTriggerType() == TRIGGER_USER_ACTION and
        self._checkTransitionGuard(transition, ob, **kw)):
        return 1
    return 0

  security.declarePrivate('isInfoSupported')
  def isInfoSupported(self, ob, name):
    """
    Returns a true value if the given info name is supported
    """
    if name == self.getStateVariable():
      return True
    return name in self.getVariableReferenceList()

  def _checkTransitionGuard(self, t, ob, **kw):
    return t.checkGuard(getSecurityManager(), self, ob, **kw)

  def _findAutomaticTransition(self, ob, sdef):
    transition = None
    checkTransitionGuard = self._checkTransitionGuard
    for possible_transition in sdef.getDestinationValueList():
      if possible_transition.getTriggerType() == TRIGGER_AUTOMATIC:
        if checkTransitionGuard(possible_transition, ob):
          transition = possible_transition
          break
    return transition

  security.declarePrivate('updateRoleMappingsFor')
  def updateRoleMappingsFor(self, ob, **kw):
    # Patch updateRoleMappingsFor so that if 2 workflows define security, then
    # we should do an AND operation between each roles list for a given
    # permission
    # XXX(WORKFLOW): this is not tested: add a test with multiple workflows
    # defining different permissions
    """
    Changes the object permissions according to the current
    state.
    """
    changed = False
    state = self._getWorkflowStateOf(ob)
    tool = aq_parent(aq_inner(self))
    other_data_list = []
    new_permission_roles_dict = {}

    def modifyRolesForPermissionDict(ob, new_permission_roles_dict):
      """
      Copied and modified version of modifyRolesForPermission
      (Products.DCWorkflow.utils) to pass a dict as parameter and avoid multiple
      expensive calls to ac_inherited_permissions.

      Modifies multiple role to permission mappings.  roles is a list to
      acquire, a tuple to not acquire.
      """
      modified = False
      def ac_all_inherited_permissions_dict(ob):
        # Get all permissions not defined in ourself that are inherited
        # This will be a sequence of tuples with a name as the first item and
        # an empty tuple as the second.
        permission_roles_tuple_list = getattr(ob, '__ac_permissions__', ())
        # permission_roles_tuple_list: [(permission1, (roleA, roleB)), ...]
        permission_roles_dict = {p[0]: p[1] for p in permission_roles_tuple_list}
        def gather_permission_dict(klass, result):
          for base in klass.__bases__:
            if '__ac_permissions__' in base.__dict__:
              for p in base.__ac_permissions__:
                name=p[0]
                if name in result:
                  continue
                result[name] = ()
            gather_permission_dict(base, result)
          return result
        permission_roles_dict = gather_permission_dict(ob.__class__, permission_roles_dict)
        if hasattr(ob, '_subobject_permissions'):
          for p in ob._subobject_permissions():
            permission_name=p[0]
            roles = p[1]
            if permission_name not in permission_roles_dict:
              permission_roles_dict[permission_name] = roles
        return permission_roles_dict
      inherited_permission_dict = ac_all_inherited_permissions_dict(ob)
      for name, new_roles in six.iteritems(new_permission_roles_dict):
        old_roles = inherited_permission_dict.get(name, ())
        p = Permission(name, old_roles, ob)
        old_roles = p.getRoles()
        if type(old_roles) != type(new_roles) or sorted(old_roles) != sorted(new_roles):
          p.setRoles(new_roles)
          modified = True
      return modified

    # Be careful, permissions_roles should not change from list to tuple or
    # vice-versa (in modifyRolesForPermission, list means acquire roles, tuple
    # means do not acquire)
    if state is not None and self.getWorkflowManagedPermissionList():
      # apply expensive operations out of the loop (see below), for the other
      # workflow associated to object ob
      for other_workflow in tool.getWorkflowValueListFor(ob):
        other_workflow_type = other_workflow.getPortalType()
        if other_workflow.getId() == self.getId() or other_workflow_type not in \
        ('DCWorkflowDefinition', 'Workflow'):
          continue
        other_state = other_workflow._getWorkflowStateOf(ob)
        if other_state is not None:
          other_state_permission_role_list_dict = other_state.getStatePermissionRoleListDict()
          if other_state_permission_role_list_dict:
            other_data_list.append(
              (other_workflow, other_state, other_state_permission_role_list_dict,)
            )

      # take care of the current state of ob for this workflow (self)
      state_permission_role_list_dict = state.getStatePermissionRoleListDict()
      acquired_permission_list = state.getAcquirePermissionList()
      for permission in self.getWorkflowManagedPermissionList():
        default_roles = []
        role_type = list
        other_role_type_list = []
        if state_permission_role_list_dict:
          roles = state_permission_role_list_dict.get(permission, default_roles)
          # store acquisition settings
          if acquired_permission_list is _marker or roles is default_roles:
            role_type = type(roles)
          else:
            role_type = list if permission in acquired_permission_list else tuple

          roles = set(roles)
          # in every other workflow activated on the current object, get the
          # roles associated to permission; in case of role defined
          for (other_workflow, other_state, other_state_permission_role_list_dict) \
          in other_data_list:
            other_acquired_permission_list = other_state.getAcquirePermissionList()
            if permission in other_workflow.getWorkflowManagedPermissionList():
              other_roles = other_state_permission_role_list_dict.get(permission, default_roles)
              if other_acquired_permission_list is _marker: # compatibility with DCWorkflow
                other_role_type_list.append(type(other_roles))
              else: # ERP5 workflows
                other_role_type_list.append(
                  list if (other_roles is default_roles or permission in
                  other_acquired_permission_list) else tuple
                )
              # get the common values between the roles set and the other
              # workflows roles for the same permission
              roles = roles.intersection(other_roles)

          roles = sorted(roles)
          if role_type is tuple and list not in other_role_type_list:
            # at least, one of other workflows manage security and for all are
            # role_type are tuple (= no role acquisition for this permission)
            roles = tuple(roles)

          new_permission_roles_dict[permission] = roles
      changed = modifyRolesForPermissionDict(ob, new_permission_roles_dict)
    return changed

  def getManagedRoleList(self):
    return sorted(self.getPortalObject().acl_users.valid_roles())

  security.declarePrivate('doActionFor')
  def doActionFor(self, ob, action, comment='', **kw):
    """
    Allows the user to request a workflow action.  This method
    must perform its own security checks.
    """
    state = self._getWorkflowStateOf(ob)
    kw['comment'] = comment
    if state is None:
      raise WorkflowException(_(u'Object is in an undefined state.'))

    is_action_supported = kw.get('is_action_supported',
                                 self.isActionSupported(ob, action, state=state, **kw))
    if not is_action_supported:
      # action is not allowed from the current state
      raise Unauthorized(action)

    transition = self.getTransitionValueByReference(action)

    if transition is None or transition.getTriggerType() != TRIGGER_USER_ACTION:
      msg = _(u"Transition '${action_id}' is not triggered by a user "
        u"action.", mapping={'action_id': action})
      raise WorkflowException(msg)
    if not self._checkTransitionGuard(transition, ob, **kw):
      raise Unauthorized(action)
    self._changeStateOf(ob, transition, kw)

  def _changeStateOf(self, ob, tdef=None, kwargs=None):
    """
    Changes state.  Can execute multiple transitions if there are
    automatic transitions. transition set to None means the object
    was just created.
    """
    moved_exc = None
    transition = tdef
    while 1:
      try:
        state = self._executeTransition(ob, transition, kwargs)
      except ObjectMoved as e:
        moved_exc = e
        ob = moved_exc.getNewObject()
        state = self._getWorkflowStateOf(ob)
        # Re-raise after all transitions.
      if state is None:
        break
      transition = self._findAutomaticTransition(ob, state)
      if transition is None:
        # No more automatic transitions.
        break
      # Else continue.
    if moved_exc is not None:
      # Re-raise.
      raise moved_exc

  security.declarePrivate('listObjectActions')
  def listObjectActions(self, info):
    """
    Allows this workflow to
    include actions to be displayed in the actions box.
    Called only when this workflow is applicable to
    info.object.
    Returns the actions to be displayed to the user.
    """
    ob = info.object
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
      return ()
    fmt_data = None
    result = []
    for tdef in sdef.getDestinationValueList():
      if (
          tdef is not None and
          tdef.getTriggerType() == TRIGGER_USER_ACTION and
          tdef.getActionName() and
          self._checkTransitionGuard(tdef, ob)
      ):
        if fmt_data is None:
          fmt_data = TemplateDict()
          fmt_data._push(info)
        transition_reference = tdef.getReference()
        fmt_data._push({'transition_id': transition_reference})
        result.append({
          'id': transition_reference,
          'name': tdef.getActionName() % fmt_data,
          'url': tdef.getAction() % fmt_data,
          'icon': tdef.getIcon() % fmt_data,
          'permissions': (),  # Predetermined.
          'category': tdef.getActionType(),
          'transition': tdef,
        })
        fmt_data._pop()
    result.sort(key=lambda x: x['id'])
    return result

  security.declarePrivate('getWorklistVariableMatchDict')
  def getWorklistVariableMatchDict(self, info, check_guard=True):
    """
      Return a dict which has an entry per worklist definition
      (worklist id as key) and which value is a dict composed of
      variable matches.
    """
    worklist_value_list = self.getWorklistValueList()
    if not worklist_value_list:
      return None
    expression_context = None
    state_change_information = None

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
    workflow_id = self.getId()
    workflow_title = self.getTitle()
    from Products.ERP5Type.Tool.WorkflowTool import (SECURITY_PARAMETER_ID,
                                                     WORKLIST_METADATA_KEY)
    for worklist_definition in worklist_value_list:
      action_box_name = worklist_definition.getActionName()
      guard_role_list = worklist_definition.getGuardRoleList()
      if action_box_name:
        variable_match = worklist_definition.getIdentityCriterionDict()
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
        if (
          not worklist_definition.isGuarded() or
          not check_guard or
          worklist_definition.checkGuard(security_manager,
                                         self,
                                         portal)
        ):
          format_data = TemplateDict()
          format_data._push(info)
          variable_match.setdefault(SECURITY_PARAMETER_ID, guard_role_list)
          format_data._push({
              k: ('&%s:list=' % k).join(v)
              for k, v in six.iteritems(variable_match)
          })
          worklist_id = worklist_definition.getReference()
          variable_match[WORKLIST_METADATA_KEY] = {
            'format_data': format_data,
            'worklist_title': action_box_name,
            'worklist_id': worklist_id,
            'workflow_title': workflow_title,
            'workflow_id': workflow_id,
            'action_box_url': worklist_definition.getAction(),
            'action_box_category': worklist_definition.getActionType(),
          }
          variable_match_dict[worklist_id] = variable_match

    if variable_match_dict:
      return variable_match_dict
    return None

  security.declarePrivate('getInfoFor')
  def getInfoFor(self, ob, name, default):
    """
    Allows the user to request information provided by the
    workflow.  This method must perform its own security checks.
    """
    if name == self.getStateVariable():
      return self._getWorkflowStateOf(ob, 1)
    vdef = self.getVariableValueByReference(name)
    if not vdef.checkGuard(getSecurityManager(), self, ob):
      return default
    status = self.getCurrentStatusDict(ob)
    variable_default_expression = vdef.getVariableDefaultExpressionInstance()
    if status is not None and name in status:
      value = status[name]

    # Not set yet.  Use a default.
    elif variable_default_expression is not None:
      ec = createExpressionContext(StateChangeInfo(ob, self, status))
      value = variable_default_expression(ec)
    else:
      value = ''

    return value

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCurrentStatusDict')
  def getCurrentStatusDict(self, document):
    """
    Get the current status dict. It's the same as _getStatusOf.
    """
    workflow_key = self.getReference()
    workflow_history = self.getParentValue().getHistoryOf(workflow_key, document)
    # Copy is requested
    if workflow_history:
      return workflow_history[-1].copy()
    return {}

  def _getStatusOf(self, ob):
    tool = self.getParentValue()
    status = tool.getStatusOf(self.getId(), ob)
    if status is None:
      return {}
    else:
      # Copy is requested
      return status.copy()

  def _getWorkflowStateOf(self, ob, id_only=False):
    reference = self.getReference()
    status = self.getParentValue().getStatusOf(reference, ob)
    if status is None:
      state = self.getSourceValue()
    else:
      state_parameter = status.get(self.getStateVariable(), None)
      if state_parameter:
        state_id = 'state_' + state_parameter
        state = self._getOb(state_id)
      if (state_parameter is None) or (state is None):
        state = self.getSourceValue()
    if id_only:
      if state is None:
        return None
      return state.getReference()
    else:
      return state

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariableValueDict')
  def getVariableValueDict(self):
    return {variable.getReference(): variable
            for variable in self.objectValues(portal_type="Workflow Variable")}

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariableValueList')
  def getVariableValueList(self):
    return self.objectValues(portal_type="Workflow Variable")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariableReferenceList')
  def getVariableReferenceList(self):
    return [variable.getReference()
            for variable in self.objectValues(portal_type="Workflow Variable")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariableValueByReference')
  def getVariableValueByReference(self, reference):
    return self._getOb('variable_' + reference, default=None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateValueByReference')
  def getStateValueByReference(self, reference):
    return self._getOb('state_' + reference, default=None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateValueList')
  def getStateValueList(self):
    return self.objectValues(portal_type="Workflow State")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateReferenceList')
  def getStateReferenceList(self):
    return [state.getReference()
            for state in self.objectValues(portal_type="Workflow State")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWorklistValueList')
  def getWorklistValueList(self):
    return self.objectValues(portal_type="Worklist")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWorklistReferenceList')
  def getWorklistReferenceList(self):
    return [w.getReference() for w in self.objectValues(portal_type="Worklist")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionIdByReference')
  def getTransitionIdByReference(self, reference):
    return 'transition_' + reference

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getScriptIdByReference')
  def getScriptIdByReference(self, reference):
    from Products.ERP5Type.Core.WorkflowScript import SCRIPT_PREFIX
    return SCRIPT_PREFIX + reference

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getScriptValueByReference')
  def getScriptValueByReference(self, reference):
    from Products.ERP5Type.Core.WorkflowScript import SCRIPT_PREFIX
    return self._getOb(SCRIPT_PREFIX + reference, None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWorklistValueByReference')
  def getWorklistValueByReference(self, reference):
    return self._getOb('worklist_' + reference, None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionValueByReference')
  def getTransitionValueByReference(self, reference):
    return self._getOb('transition_' + reference, None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionValueList')
  def getTransitionValueList(self):
    return self.objectValues(portal_type="Workflow Transition")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionReferenceList')
  def getTransitionReferenceList(self):
    return [transition.getReference() for transition
            in self.objectValues(portal_type="Workflow Transition")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getScriptValueList')
  def getScriptValueList(self):
    return self.objectValues(portal_type='Workflow Script')

  security.declarePrivate('notifyWorkflowMethod')
  def notifyWorkflowMethod(self, ob, transition_list, args=None, kw=None):
    """ Execute workflow methods.
    """
    if isinstance(transition_list, basestring):
      method_id = transition_list
    elif len(transition_list) == 1:
      method_id = transition_list[0]
    else:
      raise ValueError('WorkflowMethod should be attached to exactly 1 transition per DCWorkflow instance.')
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
      raise WorkflowException('Object is in an undefined state')
    prefix_method_id = self.getTransitionIdByReference(method_id)
    if prefix_method_id not in sdef.getDestinationIdList():
      raise Unauthorized(method_id)
    tdef = self.getTransitionValueByReference(method_id)
    if tdef is None or tdef.getTriggerType() != TRIGGER_WORKFLOW_METHOD:
      raise WorkflowException(
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

  security.declarePrivate('notifyBefore')
  def notifyBefore(self, ob, transition_list, args=None, kw=None):
    """
    Notifies this workflow of an action before it happens,
    allowing veto by exception.  Unless an exception is thrown, either
    a notifySuccess() or notifyException() can be expected later on.
    The action usually corresponds to a method name.
    """
    pass

  security.declarePrivate('notifySuccess')
  def notifySuccess(self, ob, transition_list, result, args=None, kw=None):
    """
    Notifies this workflow that an action has taken place.
    """
    pass

  security.declarePrivate('notifyException')
  def notifyException(self, ob, action, exc):
    """
    Notifies this workflow that an action failed.
    """
    pass

  def _executeTransition(self, ob, tdef=None, kwargs=None):
    """
    Execute transition.
    """
    sci = None
    econtext = None
    moved_exc = None
    validation_exc = None
    object_context = None

    # Figure out the old and new states.
    old_state = self._getWorkflowStateOf(ob)
    if not old_state:
      # Do nothing if there is no initial state. We may want to create
      # workflows with no state at all, only for worklists.
      return
    old_state_reference = old_state.getReference()

    tool = self.getParentValue()
    state_var = self.getStateVariable()

    # `status_dict` will hold the new status.
    # Unlike DCWorkflow implementation, we don't start with an empty dict, but start
    # by making a copy of the current status dict, this way the string used as keys
    # will be the same string instances and this will reduce the pickle size:
    # Copying existing dict saves space: when __setitem__(key, value) points at an
    # existing key, python will just keep the existing string as key, which then
    # means if both history entries are pickled together, the keys will be stored
    # just once instead of once per dict.
    # This is especially important with ERP5's WorkflowVariable implemented with
    # IdAsReferenceMixin, because every call to getReference return a different string.
    status_dict = self.getCurrentStatusDict(ob)

    if tdef is None:
      new_state = old_state
      new_state_reference = old_state_reference
      former_status = {}
    else:
      new_state = tdef.getDestinationValue()
      new_state_reference = old_state_reference if new_state is None\
                            else new_state.getReference()
      former_status = status_dict

    # Execute the "before" script.
    before_script_success = True

    if tdef is not None:
      script_value_list = tdef.getBeforeScriptValueList()
      if script_value_list:
        if sci is None:
          sci = StateChangeInfo(ob, self, former_status, tdef, old_state,
                                new_state, kwargs)
        for script in script_value_list:
          # Pass lots of info to the script in a single parameter.
          if script.getPortalType() != 'Workflow Script':
            raise NotImplementedError ('Unsupported Script %s for state %s' %
                                       (script.getId(), old_state_reference))
          script = getattr(self, script.getId())
          try:
            script(sci)  # May throw an exception.
          except ValidationFailed as e:
            validation_exc = e
            before_script_success = False
            before_script_error_message = deepcopy(validation_exc.msg)
            validation_exc_traceback = sys.exc_info()[2]
          except ObjectMoved as e:
            moved_exc = e
            ob = moved_exc.getNewObject()
            # Re-raise after transition

    transition_expression_dict = {}
    if tdef is not None:
      transition_expression_dict = {
        variable.getCausalityId(): variable.getVariableDefaultExpressionInstance()
        for variable in tdef.objectValues(portal_type='Workflow Transition Variable')
      }

    # Update all transition variables
    if kwargs is not None:
      if object_context is None:
        # XXX(WORKFLOW): investigate: should I keep source value here, or can I use  old_state (see test results also)
        object_context = self.getStateChangeInformation(ob, self.getSourceValue())

    for vdef in self.getVariableValueList():
      variable_id = vdef.getId()
      variable_reference = vdef.getReference()
      if not vdef.getStatusIncluded():
        continue

      expr = None
      value = None
      if variable_id in transition_expression_dict:
        expr = transition_expression_dict[variable_id]
      elif not vdef.getAutomaticUpdate() and variable_reference in former_status:
        # Preserve former value
        value = former_status[variable_reference]
      else:
        variable_default_expression = vdef.getVariableDefaultExpressionInstance()
        if variable_default_expression is not None:
          # PATCH : if Default expression for 'actor' is 'user/getUserName',
          # we use 'user/getIdOrUserName' instead to store user ID for ERP5
          # user.
          if (variable_reference == 'actor' and
              vdef.getVariableDefaultExpression() == 'user/getUserName'):
            expr = userGetIdOrUserNameExpression
          else:
            expr = variable_default_expression
        else:
            value = ''

      if expr not in (None, ''):
        # Evaluate an expression.
        if econtext is None:
          # Lazily create the expression context.
          if sci is None:
            sci = StateChangeInfo(
                ob, self, former_status, tdef,
                old_state, new_state, kwargs)
          econtext = createExpressionContext(sci)
        value = expr(econtext)
      status_dict[variable_reference] = value
    # Do not proceed in case of failure of before script
    if not before_script_success:
      status_dict[state_var] = old_state_reference # Remain in state
      tool.setStatusOf(self.getReference(), ob, status_dict)
      if sci is None:
        sci = StateChangeInfo(
          ob, self, former_status, tdef, old_state, new_state, kwargs)
      # put the error message in the workflow history
      sci.setWorkflowVariable(error_message=before_script_error_message)
      if validation_exc :
        # reraise validation failed exception
        reraise(type(validation_exc), validation_exc, validation_exc_traceback)
      return new_state

    # update state
    status_dict[state_var] = new_state_reference

    tool.setStatusOf(self.getReference(), ob, status_dict)
    self.updateRoleMappingsFor(ob)

    # Execute the "after" script.
    if tdef is not None:
      script_value_list = tdef.getAfterScriptValueList()
      if script_value_list:
        if sci is None:
          sci = StateChangeInfo(ob, self, former_status, tdef, old_state,
                                new_state, kwargs)
        old_state_destination_list = old_state.getDestinationValueList()
        for script in script_value_list:
          # Script can be either script or workflow method
          if script in old_state_destination_list and \
              script.getTriggerType() == TRIGGER_WORKFLOW_METHOD:
            getattr(ob, convertToMixedCase(script.getReference()))()
          else:
            # Pass lots of info to the script in a single parameter.
            if script.getPortalType() == 'Workflow Script':
              script = getattr(self, script.getId())
              script(sci)  # May throw an exception.

    # Return the new state object.
    if moved_exc is not None:
      # Propagate the notification that the object has moved.
      raise moved_exc
    else:
      return new_state

  security.declarePrivate('wrapWorkflowMethod')
  def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
    """
    Allows the user to request a workflow action.  This method
    must perform its own security checks.
    """
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
      raise WorkflowException('Object is in an undefined state')
    if method_id not in sdef.getTransitionReferenceList():
      raise Unauthorized(method_id)
    tdef = self.getTransitionValueByReference(method_id)
    if tdef is None or tdef.getTriggerType() != TRIGGER_WORKFLOW_METHOD:
      raise WorkflowException(
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
    except ObjectMoved as ex:
      # Re-raise with a different result.
      raise ObjectMoved(ex.getNewObject(), res)
    return res

  def _checkConsistency(self, fixit=False):
    """Checks the workflow definition.
    """
    consistency_message_list = []
    # make sure we have necessary variables
    variable_reference_set = {
        v.getReference()
        for v in self.contentValues(portal_type='Workflow Variable')
    }
    for variable_reference in 'error_message', :
      if variable_reference not in variable_reference_set:
        consistency_message_list.append(
            ConsistencyMessage(
                self,
                object_relative_url=self.getRelativeUrl(),
                message=
                'Required variable {variable_reference} missing in workflow.'.
                format(variable_reference=variable_reference)))
    return consistency_message_list

  security.declareProtected(Permissions.AccessContentsInformation, 'showAsXML')
  def showAsXML(self, root=None):
    from lxml import etree
    from lxml.etree import Element, SubElement

    if root is None:
      root = Element('erp5')
      return_as_object = False

    # Define a list of property to show to users:
    workflow_prop_id_to_show = ['description', 'state_var',
      'permissions', 'initial_state']

    # workflow as XML, need to rename DC workflow's portal_type before comparison.
    workflow = SubElement(root, 'workflow',
                        attrib=dict(reference=self.getReference(),
                        portal_type=self.getPortalType()))

    for prop_id in sorted(workflow_prop_id_to_show):
      # In most case, we should not synchronize acquired properties
      if prop_id not in ('uid', 'workflow_history', 'id', 'portal_type',):
        if prop_id == 'permissions':
          value = tuple(self.getProperty('workflow_managed_permission'))
          prop_type = self.getPropertyType('workflow_managed_permission')
        elif prop_id == 'initial_state':
          source_value = self.getSourceValue()
          if source_value is not None:
            value = source_value.getReference()
          else:
            value = ''
          prop_type = 'string'
        elif prop_id =='state_var':
          value = self.getProperty('state_variable')
          prop_type = self.getPropertyType('state_variable')
        else:
          value = self.getProperty(prop_id)
          prop_type = self.getPropertyType(prop_id)
        if value is None or value ==() or value == ():
          value = ''
        sub_object = SubElement(workflow, prop_id, attrib=dict(type=prop_type))
        sub_object.text = str(value)

    # 1. State as XML
    state_reference_list = []
    state_list = self.getStateValueList()
    # show reference instead of id
    state_prop_id_to_show = ['description',
      'transitions', 'permission_roles']
    for sdef in state_list:
      state_reference_list.append(sdef.getReference())
    states = SubElement(workflow, 'states', attrib=dict(state_list=str(state_reference_list),
                        number_of_element=str(len(state_reference_list))))
    for sdef in state_list:
      state = SubElement(states, 'state', attrib=dict(reference=sdef.getReference(), portal_type=sdef.getPortalType()))
      for property_id in sorted(state_prop_id_to_show):
        if property_id == 'permission_roles':
          property_value = sdef.getProperty('state_permission_role_list_dict')
          property_type = sdef.getPropertyType('state_permission_role_list_dict')
        elif property_id == 'transitions':
          property_value = sdef.getDestinationIdList()
          destination_list = []
          for tr_id in property_value:
            destination_list.append(self._getOb(tr_id).getReference())
          property_value = tuple(destination_list)
          property_type = 'multiple selection'
        else:
          property_value = sdef.getProperty(property_id)
          property_type = sdef.getPropertyType(property_id)

        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object = SubElement(state, property_id, attrib=dict(type=property_type))
        sub_object.text = str(property_value)

    # 2. Transition as XML
    transition_reference_list = []
    transition_list = self.getTransitionValueList()
    transition_prop_id_to_show = ['description', 'new_state_id',
      'trigger_type', 'script_name', 'after_script_name', 'action_type',
      'icon', 'action_name', 'action', 'roles', 'groups',
      'permissions', 'expr', 'transition_variable']
    for tdef in transition_list:
      transition_reference_list.append(tdef.getReference())
    transitions = SubElement(workflow, 'transitions',
          attrib=dict(transition_list=str(transition_reference_list),
          number_of_element=str(len(transition_reference_list))))
    for tdef in transition_list:
      transition = SubElement(transitions, 'transition',
            attrib=dict(reference=tdef.getReference(),
            portal_type=tdef.getPortalType()))
      guard = SubElement(transition, 'guard', attrib=dict(type='object'))
      transition_variables = SubElement(transition, 'transition_variables', attrib=dict(type='object'))
      for property_id in sorted(transition_prop_id_to_show):
        if property_id in ('roles', 'groups', 'permissions', 'expr',):
          if property_id == 'roles':
            property_value = tdef.getGuardRoleList()
          if property_id == 'groups':
            property_value = tdef.getGuardGroupList()
          if property_id == 'permissions':
            property_value = tdef.getGuardPermissionList()
          if property_id == 'expr':
            property_value = tdef.getGuardExpression()
          if property_value is None or property_value == [] or property_value == ():
            property_value = ''
          elif property_id != 'expr':
            property_value = tuple(property_value)
          sub_object = SubElement(guard, property_id, attrib=dict(type='guard configuration'))
        else:
          if property_id == 'new_state_id':
            if tdef.getDestinationValue() is not None:
              property_value = tdef.getDestinationValue().getReference()
            else:
              property_value = ''
            sub_object = SubElement(transition, property_id, attrib=dict(type='string'))
          elif property_id == 'script_name':
            property_value = tdef.getBeforeScriptIdList()
            if property_value == [] or property_value is None:
              property_value = ''
            else:
              property_value = self._getOb(tdef.getBeforeScriptIdList()[0]).getReference()
            sub_object = SubElement(transition, property_id, attrib=dict(type='string'))
          elif property_id == 'after_script_name':
            property_value = tdef.getAfterScriptIdList()
            if property_value == [] or property_value is None:
              property_value = ''
            else:
              property_value = self._getOb(tdef.getAfterScriptIdList()[0]).getReference()
            sub_object = SubElement(transition, property_id, attrib=dict(type='string'))
          elif property_id =='transition_variable':
            tr_var_list = tdef.objectValues(portal_type='Workflow Transition Variable')
            for tr_var in tr_var_list:
              reference = self._getOb(tr_var.getCausalityId()).getReference()
              transition_variable = SubElement(transition_variables, property_id, attrib=dict(id=reference,type='variable'))
              transition_variable.text = str(tr_var.getVariableDefaultExpression())
          else:
            property_value = tdef.getProperty(property_id)
            property_type = tdef.getPropertyType(property_id)
            sub_object = SubElement(transition, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)

    # 3. Variable as XML
    variable_reference_list = []
    variable_list = self.getVariableValueList()
    variable_prop_id_to_show = ['description', 'variable_default_expression',
          'for_catalog', 'for_status', 'automatic_update']
    for vdef in variable_list:
      variable_reference_list.append(vdef.getReference())
    variables = SubElement(workflow, 'variables', attrib=dict(variable_list=str(variable_reference_list),
                           number_of_element=str(len(variable_reference_list))))
    for vdef in variable_list:
      variable = SubElement(variables, 'variable', attrib=dict(reference=vdef.getReference(),
            portal_type=vdef.getPortalType()))
      for property_id in sorted(variable_prop_id_to_show):
        if property_id == 'automatic_update':
          property_value = vdef.getAutomaticUpdate()
          sub_object = SubElement(variable, property_id, attrib=dict(type='int'))
        else:
          property_value = vdef.getProperty(property_id)
          property_type = vdef.getPropertyType(property_id)
          sub_object = SubElement(variable, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)
        # for a very specific case, action return the reference of transition,
        # but in XML should show the same expression as in DC workflow.
        if vdef.getId() == 'variable_action' and property_id == 'variable_default_expression' and property_value != '':
          sub_object.text = str('transition/getId|nothing')

    # 4. Worklist as XML
    worklist_reference_list = []
    worklist_list = self.getWorklistValueList()
    worklist_prop_id_to_show = ['description', 'matched_portal_type_list',
          'matched_validation_state_list', 'matched_simulation_state_list',
          'action_type', 'action_name', 'action', 'icon',
          'roles', 'groups', 'permissions', 'expr']
    for qdef in worklist_list:
      worklist_reference_list.append(qdef.getReference())
    worklists = SubElement(workflow, 'worklists', attrib=dict(worklist_list=str(worklist_reference_list),
                        number_of_element=str(len(worklist_reference_list))))
    for qdef in worklist_list:
      worklist = SubElement(worklists, 'worklist', attrib=dict(reference=qdef.getReference(),
      portal_type=qdef.getPortalType()))
      guard = SubElement(worklist, 'guard', attrib=dict(type='object'))
      for property_id in sorted(worklist_prop_id_to_show):
         # show guard configuration:
        if property_id in ('roles', 'groups', 'permissions', 'expr',):
          if property_id == 'roles':
            property_value = qdef.getGuardRoleList()
          if property_id == 'groups':
            property_value = qdef.getGuardGroupList()
          if property_id == 'permissions':
            property_value = qdef.getGuardPermissionList()
          if property_id == 'expr':
            property_value = qdef.getGuardExpression()
          if property_value is not None:
            property_value = tuple(property_value)
          sub_object = SubElement(guard, property_id, attrib=dict(type='guard configuration'))
        else:
          property_value = qdef.getProperty(property_id)
          state_ref_list = []
          if property_id in ('matched_validation_state_list',
              'matched_simulation_state_list',) and property_value is not None:
            for sid in property_value:
              state_ref = self._getOb(sid).getReference()
              state_ref_list.append(state_ref)
            property_value = tuple(state_ref_list)
          if property_id == 'matched_portal_type_list':
            if property_value is not None:
              property_value = tuple(property_value)
          property_type = qdef.getPropertyType(property_id)
          sub_object = SubElement(worklist, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)

    # 5. Script as XML
    script_reference_list = []
    script_list = self.getScriptValueList()
    script_prop_id_to_show = sorted(['body', 'parameter_signature','proxy_roles'])
    for sdef in script_list:
      script_reference_list.append(sdef.getReference())
    scripts = SubElement(workflow, 'scripts', attrib=dict(script_list=str(script_reference_list),
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPortalTypeListForWorkflow')
  # Get list of portal types for workflow
  def getPortalTypeListForWorkflow(self):
    """
      Get list of portal types for workflow.
    """
    workflow_id = self.getId()
    return [portal_type.getId() for portal_type in self.portal_types.listTypeInfo()
            if workflow_id in portal_type.getTypeWorkflowList()]

  def _executeMetaTransition(self, ob, new_state_id):
    """
    Allow jumping from state to another without triggering any hooks.
    Must be used only under certain conditions.
    """
    sci = None
    econtext = None
    tdef = None
    kwargs = None
    new_state_id_no_prefix = new_state_id
    new_state_id = 'state_' + new_state_id
    # Figure out the old and new states.
    old_sdef = self._getWorkflowStateOf(ob)
    if old_sdef is None:
      old_state = None
    else:
      old_state = old_sdef.getId()
    if old_state == new_state_id:
      # Object is already in expected state
      return
    former_status = self.getCurrentStatusDict(ob)

    new_sdef = self._getOb(new_state_id, None)
    if new_sdef is None:
      raise WorkflowException('Destination state undefined: ' + new_state_id)

    tdef_exprs = {}
    status = {}
    for id_, vdef in six.iteritems(self.getVariableValueDict()):
      if not vdef.getStatusIncluded():
        continue
      expr = None
      if id_ in tdef_exprs:
        expr = tdef_exprs[id_]
      elif not vdef.getAutomaticUpdate() and id_ in former_status:
        # Preserve former value
        value = former_status[id_]
      else:
        variable_default_expression = vdef.getVariableDefaultExpressionInstance()
        if variable_default_expression is not None:
          expr = variable_default_expression
        else:
          value = ''
      if expr is not None:
        # Evaluate an expression.
        if econtext is None:
          # Lazily create the expression context.
          if sci is None:
            sci = StateChangeInfo(ob, self, former_status, tdef, old_sdef,
                                  new_sdef, kwargs)
          econtext = createExpressionContext(sci)
        value = expr(econtext)
      status[id_] = value

    status['comment'] = 'Jump from %r to %r' % (self._getOb(old_state).getReference(), new_state_id_no_prefix,)
    status[self.getStateVariable()] = new_state_id_no_prefix
    tool = self.getParentValue()
    tool.setStatusOf(self.getId(), ob, status)

    # Update role to permission assignments.
    self.updateRoleMappingsFor(ob)
    return new_sdef

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCatalogVariablesFor')
  def getCatalogVariablesFor(self, ob):
    """
    Allows this workflow to make workflow-specific variables
    available to the catalog, making it possible to implement
    worklists in a simple way.
    Returns a mapping containing the catalog variables
    that apply to ob.
    """
    res = {}
    status = self.getCurrentStatusDict(ob)
    for variable in self.getVariableValueList():
      if variable.getForCatalog():
        variable_id = variable.getReference()
        variable_default_expression = variable.getVariableDefaultExpressionInstance()
        if variable_id in status:
          value = status[variable_id]
        elif variable_default_expression is not None:
          ec = createExpressionContext(StateChangeInfo(ob, self, status))
          # convert string to expression before execute it.
          value = variable_default_expression(ec)
        else:
          value = ''

        res[variable_id] = value

    # Always provide the state variable.
    state_var = self.getStateVariable()
    source_value = self.getSourceValue()
    if source_value is not None:
      initial_state = source_value.getReference()
    else:
      initial_state = None
    res[state_var] = status.get(state_var, initial_state)

    return res

  def _setWorkflowManagedPermissionList(self, permission_list):
    self._baseSetWorkflowManagedPermission(permission_list)

    # Add/remove the added/removed Workflow permissions to each state
    for state in self.getStateValueList():
      state.setAcquirePermissionList(permission_list)

      permission_role_list_dict = state.getStatePermissionRoleListDict()
      state.setStatePermissionRoleListDict({
        permission: permission_role_list_dict.get(permission, [])
        for permission in permission_list})

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSourceValue')
  def getSourceValue(self):
    """
    returns the source object
    """
    # this function is redefined here for performance reasons:
    # avoiding the usage of categories speeds up workflow *a lot*
    source_path_list = [path for path in self.getCategoryList()
                        if path.startswith('source/')]
    if source_path_list:
      source_id = source_path_list[0].split('/')[-1]
      return self._getOb(source_id)
    return None

if WITH_LEGACY_WORKFLOW:
  import warnings
  def __getattr__(self, name):
    """
    Allow a Workflow Script to call another Workflow Script directly without
    SCRIPT_PREFIX. This can be dropped as soon as DCWorkflow Compatibility is
    not required anymore.
    """
    if not name or name[0] == '_': # Optimization (Folder.__getattr__)
      raise AttributeError(name)
    try:
      return super(Workflow, self).__getattr__(name)
    except AttributeError:
      from Products.ERP5Type.Core.WorkflowScript import SCRIPT_PREFIX
      if name.startswith(SCRIPT_PREFIX):
        raise
      prefixed_name = SCRIPT_PREFIX + name
      if not hasattr(aq_base(self), prefixed_name):
        raise
      warnings.warn(
        "%r: Script calling %s instead of %s" % (self, name, prefixed_name),
        DeprecationWarning)
      return self._getOb(prefixed_name)
  Workflow.__getattr__ = __getattr__

  from Products.ERP5Type.Utils import deprecated
  from ComputedAttribute import ComputedAttribute
  from Products.PythonScripts.Utility import allow_class

  Workflow.state_var = ComputedAttribute(
    deprecated('`state_var` attribute is deprecated; use getStateVariable()')\
              (lambda self: self.getStateVariable()))
  Workflow.security.declareProtected(Permissions.AccessContentsInformation, 'state_var')

  class _ContainerTab(dict):
    """
    Backward compatibility for Products.DCWorkflow.ContainerTab
    """
    def __init__(self, workflow, value_list):
      super(_ContainerTab, self).__init__()
      self._workflow = workflow
      # Allow to get object either by ID or Reference
      for value in value_list:
        self[value.getId()] = value
        self[value.getReference()] = value
    def objectIds(self):
      return ensure_list(self.keys())
    def objectValues(self):
      return ensure_list(self.values())
    def __getattr__(self, name):
      try:
        return self[name]
      except KeyError as e:
        raise AttributeError(e)
  allow_class(_ContainerTab)

  Workflow.states = ComputedAttribute(
    deprecated('`states` is deprecated; use getStateValueList()')\
              (lambda self: _ContainerTab(self, self.getStateValueList())),
    1) # must be Acquisition-wrapped
  Workflow.security.declareProtected(Permissions.AccessContentsInformation, 'states')

  Workflow.transitions = ComputedAttribute(
    deprecated('`transitions` is deprecated; use getTransitionValueList()')\
              (lambda self: _ContainerTab(self, self.getTransitionValueList())),
    1) # must be Acquisition-wrapped
  Workflow.security.declareProtected(Permissions.AccessContentsInformation, 'transitions')

  # Patterns:
  #   wf.scripts[SCRIPT_REFERENCE]
  #   another_workflow_with_the_same_script_id.scripts[SCRIPT_ID]
  Workflow.scripts = ComputedAttribute(
    deprecated('`scripts` is deprecated; use getScriptValueList()')\
              (lambda self: _ContainerTab(self, self.getScriptValueList())),
    1) # must be Acquisition-wrapped
  Workflow.security.declareProtected(Permissions.AccessContentsInformation, 'scripts')

  class _ContainerTabWorkflowVariable(_ContainerTab):
    @deprecated('variables.getStateVar() is deprecated; use workflow.getStateVariable()')
    def getStateVar(self):
      return self._workflow.getStateVariable()
    @deprecated('variables.setStateVar() is deprecated; use workflow.setStateVariable()')
    def setStateVar(self, v):
      return self._workflow.setStateVariable(v)
  allow_class(_ContainerTabWorkflowVariable)

  Workflow.variables = ComputedAttribute(
    deprecated('`variables` is deprecated; use getVariableValueList()')\
              (lambda self: _ContainerTabWorkflowVariable(self, self.getVariableValueList())),
    1) # must be Acquisition-wrapped
  Workflow.security.declareProtected(Permissions.AccessContentsInformation, 'variables')

  Workflow.worklists = ComputedAttribute(
    deprecated('`worklists` is deprecated; use getWorklistValueList()')\
              (lambda self: _ContainerTabWorkflowVariable(self, self.getWorklistValueList())),
    1) # must be Acquisition-wrapped
  Workflow.security.declareProtected(Permissions.AccessContentsInformation, 'worklists')

InitializeClass(Workflow)
