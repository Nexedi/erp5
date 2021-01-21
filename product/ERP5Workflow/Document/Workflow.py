##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#               2014 Wenjie Zheng <wenjie.zheng@tiolive.com>
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

import os
import sys
import warnings

from AccessControl import ClassSecurityInfo
from AccessControl.unauthorized import Unauthorized
from AccessControl.Permission import Permission
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent
from copy import deepcopy
from DateTime import DateTime
from DocumentTemplate.DT_Util import TemplateDict
from lxml import etree
from lxml.etree import Element, SubElement
from Products.CMFCore.Expression import Expression
from Products.CMFCore.WorkflowCore import WorkflowException, ObjectDeleted,\
                                          ObjectMoved
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.DCWorkflow.Expression import StateChangeInfo, createExprContext
from Products.DCWorkflow.utils import Message as _
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.patches.DCWorkflow import _marker
from Products.ERP5Type.patches.WorkflowTool import SECURITY_PARAMETER_ID,\
                                                   WORKLIST_METADATA_KEY
from Products.ERP5Type.Utils import UpperCase, convertToMixedCase, deprecated
from Products.ERP5Type.XMLObject import XMLObject

#from Products.ERP5Workflow.Document.Transition import TRIGGER_AUTOMATIC,\
#                                    TRIGGER_USER_ACTION, TRIGGER_WORKFLOW_METHOD
TRIGGER_AUTOMATIC = 0
TRIGGER_USER_ACTION = 1
TRIGGER_WORKFLOW_METHOD = 2

from Products.ERP5Workflow.Document.WorkflowScript import SCRIPT_PREFIX
from tempfile import mktemp
from types import StringTypes
from zLOG import LOG, INFO, WARNING

from Products.CMFCore.Expression import getEngine

userGetIdOrUserNameExpression = Expression('user/getIdOrUserName')
userGetIdOrUserNameExpression._v_compiled = getEngine().compile(
  userGetIdOrUserNameExpression.text)

ACTIVITY_GROUPING_COUNT = 100

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

def ac_all_inherited_permissions_dict(ob):
  # Get all permissions not defined in ourself that are inheri  ted
  # This will be a sequence of tuples with a name as the first item and
  # an empty tuple as the second.
  permission_roles_tuple_list = getattr(ob, '__ac_permissions__', ())
  # permission_roles_tuple_list: [(permission1, (roleA, roleB)), ...]
  permission_roles_dict = {p[0]: p[1] for p in permission_roles_tuple_list}
  permission_roles_dict = gather_permission_dict(ob.__class__, permission_roles_dict)
  if hasattr(ob, '_subobject_permissions'):
    for p in ob._subobject_permissions():
      permission_name=p[0]
      roles = p[1]
      if not permission_roles_dict.has_key(permission_name):
        permission_roles_dict[permission_name] = roles
  return permission_roles_dict

def modifyRolesForPermissionDict(ob, new_permission_roles_dict):
  # copied and modified version of modifyRolesForPermission
  # in Products.DCWorkflow.utils
  # this has been refactored to pass a dict as parameter
  # and avoid multiple expensive calls to ac_inherited_permissions

  '''
  Modifies multiple role to permission mappings.  roles is a list to
  acquire, a tuple to not acquire.
  '''
  # This mimics what AccessControl/Role.py does.

  new_permission_roles_dict_length = len(new_permission_roles_dict)
  modified = False
  inherited_permission_dict = ac_all_inherited_permissions_dict(ob)
  for name, new_roles in new_permission_roles_dict.iteritems():
    old_roles = inherited_permission_dict[name]
    p = Permission(name, old_roles, ob)
    old_roles = p.getRoles()
    if type(old_roles) != type(new_roles) or sorted(old_roles) != sorted(new_roles):
      p.setRoles(new_roles)
      modified = True
  return modified

class Workflow(IdAsReferenceMixin("", "prefix"), XMLObject):
  """
  A ERP5 Workflow.
  """
  id = ''
  meta_type = 'ERP5 Workflow'
  portal_type = 'Workflow'
  _isAWorkflow = True # DCWorkflow Tool compatibility
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  default_reference = ''
  workflow_managed_permission = ()
  managed_role = ()
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
    PropertySheet.Comment,
    PropertySheet.Workflow,
  )

  security.declarePrivate('notifyCreated')
  def notifyCreated(self, document):
    """
    Notifies this workflow after an object has been created and added.
    """
    try:
        self._changeStateOf(document, None)
    except ( ObjectDeleted, ObjectMoved ):
        # Swallow.
        pass

  def _generateHistoryKey(self):
    """
    Generate a key used in the workflow history.
    """
    return self.getReference()

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
    # XXX this _p_changed marks the document modified, but only the
    # PersistentMapping is modified
    # document._p_changed = 1
    # XXX this _p_changed is apparently not necessary
    #document.workflow_history._p_changed = 1

  security.declarePublic('getDateTime')
  def getDateTime(self):
    """
    Return current date time.
    """
    return DateTime()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateChangeInformation')
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

  security.declarePrivate('isWorkflowMethodSupported')
  def isWorkflowMethodSupported(self, document, transition_reference, state=None):
    # The optional argument state is used to avoid multiple expensive calls to
    # _getWorkflowStateOf. This method should be kept private.
    if state is None:
      state = self._getWorkflowStateOf(document, id_only=0)

    transition_id = self.getTransitionIdByReference(transition_reference)
    if state is None:
      return False

    if transition_id in state.getDestinationIdList():
      transition = self._getOb(transition_id, None)
      if (transition is not None and
          transition.getTriggerType() == TRIGGER_WORKFLOW_METHOD and
          self._checkTransitionGuard(transition, document)):
        return True
    return False

  security.declarePrivate('isActionSupported')
  def isActionSupported(self, document, action, state=None, **kw):
    '''
    Returns a true value if the given action name
    is possible in the current state.
    '''
    if state is None:
      state = self._getWorkflowStateOf(document, id_only=0)
      if state is None:
        return 0

    if action in state.getDestinationIdList():
      transition = getattr(self, action, None)
      if (transition is not None and
        transition.getTriggerType() == TRIGGER_USER_ACTION and
        self._checkTransitionGuard(transition, document, **kw)):
        return 1
    return 0

  security.declarePrivate('isInfoSupported')
  def isInfoSupported(self, ob, name):
      '''
      Returns a true value if the given info name is supported.
      '''
      if name == self.getStateVariable():
          return True
      return name in self.getVariableIdList()

  def _checkTransitionGuard(self, transition, document, **kw):
    return transition.checkGuard(getSecurityManager(), self, document, **kw)

  def _findAutomaticTransition(self, document, state):
    transition = None
    checkTransitionGuard = self._checkTransitionGuard
    for possible_transition in state.getDestinationValueList():
      if possible_transition.getTriggerType() == TRIGGER_AUTOMATIC:
        if checkTransitionGuard(possible_transition, document):
          transition = possible_transition
          break
    return transition

  security.declarePrivate('updateRoleMappingsFor')
  def updateRoleMappingsFor(self, ob):
    # Patch updateRoleMappingsFor so that if 2 workflows define security, then
    # we should do an AND operation between each roles list for a given
    # permission
    # XXX(WORKFLOW): this is not tested: add a test with multiple workflows
    # defining different permissions
    '''
    Changes the object permissions according to the current
    state.
    '''
    changed = False
    state = self._getWorkflowStateOf(ob)
    tool = aq_parent(aq_inner(self))
    other_data_list = []
    new_permission_roles_dict = {}

    # Be carefull, permissions_roles should not change
    # from list to tuple or vice-versa. (in modifyRolesForPermission,
    # list means acquire roles, tuple means do not acquire)
    if state is not None and self.getWorkflowManagedPermissionList():
      # apply expensive operations out of the loop (see below), for the other
      # workflow associated to object ob
      for other_workflow in tool.getWorkflowsFor(ob):
        other_workflow_type = other_workflow.getPortalType()
        if other_workflow.id == self.id or other_workflow_type not in \
        ('DCWorkflowDefinition', 'Workflow'):
          continue
        other_state = other_workflow._getWorkflowStateOf(ob)
        if other_state is not None:
          other_state_permission_roles_dict = other_state.getStatePermissionRolesDict()
          if other_state_permission_roles_dict is not None:
            other_data_list.append(
              (other_workflow, other_state, other_state_permission_roles_dict,)
            )

      # take care of the current state of ob for this workflow (self)
      state_permission_roles_dict = state.getStatePermissionRolesDict()
      acquired_permission_list = state.getAcquirePermissionList()
      for permission in self.getWorkflowManagedPermissionList():
        default_roles = []
        refused_roles = []
        role_type = list
        other_role_type_list = []
        if state_permission_roles_dict is not None:
          roles = state_permission_roles_dict.get(permission, default_roles)
          # store acquisition settings
          if acquired_permission_list is _marker or roles is default_roles:
            role_type = type(roles)
          else:
            role_type = list if permission in acquired_permission_list else tuple

          roles = set(roles)
          # in every other workflow activated on the current object, get the
          # roles associated to permission; in case of role defined
          for (other_workflow, other_state, other_state_permission_roles_dict) \
          in other_data_list:
            other_acquired_permission_list = other_state.getAcquirePermissionList()
            if permission in other_workflow.getWorkflowManagedPermissionList():
              other_roles = other_state_permission_roles_dict.get(permission, default_roles)
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

  # This method allows to update all objects using one workflow, for example
  # after the permissions per state for this workflow were modified
  security.declareProtected(Permissions.ModifyPortalContent, 'updateRoleMappings')
  def updateRoleMappings(self, REQUEST=None):
    """
    Changes permissions of all objects related to this workflow
    """
    # XXX(WORKFLOW) add test for roles update:
    #  - edit permission/roles on a workflow
    #  - check permission on an existing object of a type using this workflow
    workflow_tool = aq_parent(aq_inner(self))
    type_info_list = workflow_tool._listTypeInfo()
    workflow_id = self.id
    # check the workflow defined on the type objects
    portal_type_id_list = [
      portal_type.getId() for portal_type in type_info_list
      if workflow_id in portal_type.getTypeWorkflowList()
    ]

    if portal_type_id_list:
      object_list = self.portal_catalog(portal_type=portal_type_id_list, limit=None)
      portal_activities = self.portal_activities
      object_path_list = [x.path for x in object_list]
      for i in xrange(0, len(object_list), ACTIVITY_GROUPING_COUNT):
        current_path_list = object_path_list[i:i+ACTIVITY_GROUPING_COUNT]
        portal_activities.activate(activity='SQLQueue',
                                    priority=3)\
              .callMethodOnObjectList(current_path_list,
                                      'updateRoleMappingsFor',
                                      wf_id = self.getId())
    else:
      object_list = []
    if REQUEST is not None:
      message = 'No object updated.'
      if object_list:
        message = '%d object(s) updated: \n %s.' % (len(object_list),
          ', '.join([o.getTitleOrId() + ' (' + o.getPortalType() + ')'
                     for o in object_list]))
      return message
    else:
      return len(object_list)

  def getManagedRoleList(self):
    return sorted(self.getPortalObject().acl_users.valid_roles())

  security.declarePrivate('doActionFor')
  def doActionFor(self, document, action, comment='', is_action_supported=_marker, **kw):
    '''
    Allows the user to request a workflow action.  This method
    must perform its own security checks.
    '''
    state = self._getWorkflowStateOf(document, id_only=0)
    kw['comment'] = comment
    if state is None:
      raise WorkflowException(_(u'Object is in an undefined state.'))

    if is_action_supported is _marker:
      is_action_supported = self.isActionSupported(document, action,
                                                   state=state, **kw)
    if not is_action_supported:
      # action is not allowed from the current state
      raise Unauthorized(action)

    transition = self._getOb(action, None)

    if transition is None or transition.getTriggerType() != TRIGGER_USER_ACTION:
      msg = _(u"Transition '${action_id}' is not triggered by a user "
        u"action.", mapping={'action_id': action})
      raise WorkflowException(msg)
    if not self._checkTransitionGuard(transition, document, **kw):
      raise Unauthorized(action)
    self._changeStateOf(document, transition, kw)

  def _changeStateOf(self, document, tdef=None, kwargs=None):
    '''
    Changes state.  Can execute multiple transitions if there are
    automatic transitions. transition set to None means the object
    was just created.
    '''
    moved_exc = None
    transition = tdef
    while 1:
      try:
        state = self._executeTransition(document, transition, kwargs)
      except ObjectMoved, moved_exc:
        document = moved_exc.getNewObject()
        state = self._getWorkflowStateOf(document, id_only=0)
        # Re-raise after all transitions.
      if state is None:
        break
      transition = self._findAutomaticTransition(document, state)
      if transition is None:
        # No more automatic transitions.
        break
      # Else continue.
    if moved_exc is not None:
        # Re-raise.
      raise moved_exc

  security.declarePrivate('listObjectActions')
  def listObjectActions(self, info):
      fmt_data = None
      document = info.object
      sdef = self._getWorkflowStateOf(document, id_only=0)
      if sdef is None:
          return None
      object_action_list = []
      append = object_action_list.append

      for tid in sdef.getDestinationIdList():
        tdef = self._getOb(id=tid)
        if tdef is not None and tdef.getTriggerType() == TRIGGER_USER_ACTION and \
                tdef.getActionName() and self._checkTransitionGuard(tdef, document):
            if fmt_data is None:
                fmt_data = TemplateDict()
                fmt_data._push(info)
            tdef_reference = tdef.getReference()
            fmt_data._push({'transition_id': tdef_reference})
            append((tid, {
                'id': tdef_reference,
                'name': tdef.getActionName() % fmt_data,
                'url': str(tdef.getAction()) % fmt_data,
                'icon': str(tdef.getIcon()) % fmt_data,
                'permissions': (),  # Predetermined.
                'category': tdef.getActionType(),
                'transition': tdef}))
            fmt_data._pop()
      object_action_list.sort()

      return [ result[1] for result in object_action_list ]

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
    def getPortalTypeListForWorkflow(workflow_id):
      return [type_info.id
              for type_info in portal.portal_types.listTypeInfo()
              if workflow_id in type_info.getTypeWorkflowList()]


    _getPortalTypeListForWorkflow = CachingMethod(getPortalTypeListForWorkflow,
                              id='_getPortalTypeListForWorkflow', cache_factory = 'erp5_ui_long')
    portal_type_list = _getPortalTypeListForWorkflow(self.id)
    if not portal_type_list:
      return None
    variable_match_dict = {}
    security_manager = getSecurityManager()
    workflow_id = self.getId()
    workflow_title = self.getTitle()
    for worklist_value in worklist_value_list:
      action_box_name = worklist_value.getActionName()
      is_guarded = worklist_value.isGuarded()
      guard_role_list = worklist_value.getGuardRoleList()
      if action_box_name:
        variable_match = {}
        for key in worklist_value.getVarMatchKeys():
          var = worklist_value.getVarMatch(key)
          if isinstance(var, Expression):
            if state_change_information is None:
              state_change_information = StateChangeInfo(portal, self,
                                         kwargs=info.__dict__.copy())
              if expression_context is None:
                expression_context = createExprContext(state_change_information)
            evaluated_value = var(expression_context)
            if isinstance(evaluated_value, (str, int, long)):
              evaluated_value = [str(evaluated_value)]
          else:
            evaluated_value = [x % info for x in var]
          variable_match[key] = evaluated_value

        if 'portal_type' in variable_match and len(variable_match['portal_type']):
          portal_type_intersection = set(variable_match['portal_type']).intersection(portal_type_list)
          # in case the current workflow is not associated with portal_types
          # defined on the worklist, don't display the worklist for this
          # portal_type.
          variable_match['portal_type'] = list(portal_type_intersection)
        variable_match.setdefault('portal_type', portal_type_list)

        if len(variable_match.get('portal_type', [])) == 0:
          continue

        is_permitted_worklist = 0
        if not is_guarded:
          is_permitted_worklist = 1
        elif not check_guard or worklist_value.checkGuard(security_manager,
                                                          self, portal,
                                                          check_roles=False):
          is_permitted_worklist = 1
          variable_match[SECURITY_PARAMETER_ID] = guard_role_list

        if is_permitted_worklist:
          fmt_data = TemplateDict()
          fmt_data._push(info)
          variable_match.setdefault(SECURITY_PARAMETER_ID, ())
          fmt_data._push({k: ('&%s:list=' % k).join(v) for\
                                            k, v in variable_match.iteritems()})

          worklist_id = worklist_value.getReference()
          variable_match[WORKLIST_METADATA_KEY] = {
                                                'format_data': fmt_data,
                                                 'worklist_title': action_box_name,
                                                 'worklist_id': worklist_id,
                                                 'workflow_title': workflow_title,
                                                 'workflow_id': workflow_id,
                                                 'action_box_url': worklist_value.getAction(),
                                                 'action_box_category': worklist_value.getActionType()}

          variable_match_dict[worklist_id] = variable_match

    if len(variable_match_dict) == 0:
      return None
    return variable_match_dict

  security.declarePrivate('getInfoFor')
  def getInfoFor(self, ob, name, default):
      '''
      Allows the user to request information provided by the
      workflow.  This method must perform its own security checks.
      '''
      if name == self.getStateVariable():
          return self._getWorkflowStateOf(ob, 1)
      vdef = self.getVariableValueById(name)
      if not vdef.checkGuard(getSecurityManager(), self, ob):
          return default
      status = self.getCurrentStatusDict(ob)
      variable_expression = vdef.getVariableExpressionInstance()
      if status is not None and status.has_key(name):
          value = status[name]

      # Not set yet.  Use a default.
      elif variable_expression is not None:
          ec = createExprContext(StateChangeInfo(ob, self, status))
          value = variable_expression(ec)
      else:
          value = vdef.getVariableValue()

      return value

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCurrentStatusDict')
  def getCurrentStatusDict(self, document):
    """
    Get the current status dict. It's the same as _getStatusOf.
    """
    workflow_key = self._generateHistoryKey()
    workflow_history = self.getParentValue().getHistoryOf(workflow_key, document)
    # Copy is requested
    if workflow_history:
      return workflow_history[-1].copy()
    return {}

  def _getStatusOf(self, ob):
      tool = self.getParent()
      status = tool.getStatusOf(self.getId(), ob)
      if status is None:
          return {}
      else:
          # Copy is requested
          return status.copy()

  def _getWorkflowStateOf(self, ob, id_only=0):
      tool = self.getParentValue()
      reference = self.getReference()
      status = tool.getStatusOf(reference, ob)
      if status is None:
          state = self.getSourceValue()
      else:
          state_id = 'state_' + status.get(self.getStateVariable(), None)
          state = self._getOb(state_id)
          if state is None:
              state = self.getSourceValue()
      if id_only:
          return state.getReference()
      else:
          return state

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariableValueDict')
  def getVariableValueDict(self):
    return {variable.getReference(): variable
            for variable in self.objectValues(portal_type="Workflow Variable")}

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCurrentStatusDict')
  security.declarePrivate('listObjectActions')
  def getVariableValueList(self):
    return self.objectValues(portal_type="Workflow Variable")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariableIdList')
  def getVariableIdList(self):
    return [variable.getReference()
            for variable in self.objectValues(portal_type="Workflow Variable")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getVariableValueById')
  def getVariableValueById(self, variable_id):
    return self._getOb('variable_' + variable_id, default=None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateValueById')
  def getStateValueById(self, stated_id):
    return self._getOb('state_' + stated_id, default=None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateValueList')
  def getStateValueList(self):
    return self.objectValues(portal_type="State")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getStateIdList')
  def getStateIdList(self):
    return [state.getReference()
            for state in self.objectValues(portal_type="State")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWorklistValueList')
  def getWorklistValueList(self):
    return self.objectValues(portal_type="Worklist")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWorklistIdList')
  def getWorklistIdList():
    return [worklist.getReference()
            for worklist in self.objectValues(portal_type="Worklist")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionIdByReference')
  def getTransitionIdByReference(self, transition_reference):
    return 'transition_' + transition_reference

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getScriptIdByReference')
  def getScriptIdByReference(self, script_reference):
    return SCRIPT_PREFIX + script_reference

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getScriptValueById')
  def getScriptValueById(self, script_id):
    return self._getOb(script_id, default=None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getWorklistValueById')
  def getWorklistValueById(self, worklist_reference):
    return self._getOb('worklist_' + worklist_reference, None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionValueById')
  def getTransitionValueById(self, transition_reference):
    return self._getOb('transition_' + transition_reference, None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionValueList')
  def getTransitionValueList(self):
    return self.objectValues(portal_type="Transition")

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTransitionIdList')
  def getTransitionIdList(self):
    return [transition.getReference() for transition
            in self.objectValues(portal_type="Transition")]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getScriptValueList')
  def getScriptValueList(self):
    return self.objectValues(portal_type='Workflow Script')

  security.declarePrivate('notifyWorkflowMethod')
  def notifyWorkflowMethod(self, ob, transition_list, args=None, kw=None):
    """ Execute workflow methods.
    """
    if type(transition_list) in StringTypes:
      method_id = transition_list
    elif len(transition_list) == 1:
      method_id = transition_list[0]
    else:
      raise ValueError('WorkflowMethod should be attached to exactly 1 transition per DCWorkflow instance.')
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
      raise WorkflowException, 'Object is in an undefined state'
    prefix_method_id = 'transition_' + method_id
    if prefix_method_id not in sdef.getDestinationIdList():
      raise Unauthorized(method_id)
    tdef = self._getOb(prefix_method_id)
    if tdef is None or tdef.getTriggerType() != TRIGGER_WORKFLOW_METHOD:
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

  security.declarePrivate('notifyBefore')
  def notifyBefore(self, ob, transition_list, args=None, kw=None):
    pass

  security.declarePrivate('notifySuccess')
  def notifySuccess(self, ob, transition_list, result, args=None, kw=None):
    pass

  security.declarePrivate('notifyException')
  def notifyException(self, ob, action, exc):
      '''
      Notifies this workflow that an action failed.
      '''
      pass

  def _executeTransition(self, document, tdef=None, form_kw=None):
    """
    Execute transition.
    """
    sci = None
    econtext = None
    moved_exc = None
    validation_exc = None
    tool = self.getParentValue()
    object_context = None

    state_var = self.getStateVariable()
    status_dict = self.getCurrentStatusDict(document)
    # Figure out the old and new states.
    old_state = self._getWorkflowStateOf(document, id_only=0)
    if not old_state:
      # Do nothing if there is no initial state. We may want to create
      # workflows with no state at all, only for worklists.
      return
    old_state_reference = old_state.getReference()

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
          sci = StateChangeInfo(document, self, former_status, tdef, old_state,
                                new_state, form_kw)
        for script in script_value_list:
          # Pass lots of info to the script in a single parameter.
          if script.getPortalType() != 'Workflow Script':
            raise NotImplementedError ('Unsupported Script %s for state %s' %
                                       (script.id, old_state_reference))
          script = getattr(self, script.id)
          try:
            script(sci)  # May throw an exception.
          except ValidationFailed, validation_exc:
            before_script_success = False
            before_script_error_message = deepcopy(validation_exc.msg)
            validation_exc_traceback = sys.exc_traceback
          except ObjectMoved, moved_exc:
            ob = moved_exc.getNewObject()
            # Re-raise after transition

    # update variables
    state_values = {}
    # seems state variable is not used in new workflow.
    if new_state is not None:
      state_values = getattr(new_state,'var_values', None) or {}

    transition_expression_dict = {}
    if tdef is not None:
      transition_expression_dict = {
        variable.getCausalityId(): variable.getVariableExpressionInstance()
        for variable in tdef.objectValues(portal_type='Transition Variable')
      }

    # Update all transition variables
    if form_kw is not None:
      if object_context is None:
        # XXX(WORKFLOW): investigate: should I keep source value here, or can I use  old_state (see test results also)
        object_context = self.getStateChangeInformation(document, self.getSourceValue())
      object_context.REQUEST.other.update(form_kw)

    for vdef in self.objectValues(portal_type='Workflow Variable'):
      variable_id = vdef.getId()
      variable_reference = vdef.getReference()
      if not vdef.getStatusIncluded():
        continue

      expr = None
      if variable_reference in state_values:
        value = state_values[variable_reference]
      elif variable_id in transition_expression_dict:
        expr = transition_expression_dict[variable_id]
      elif not vdef.getAutomaticUpdate() and variable_reference in former_status:
        # Preserve former value
        value = former_status[variable_reference]
      else:
        variable_expression = vdef.getVariableExpressionInstance()
        if variable_expression is not None:
          # PATCH : if Default expression for 'actor' is 'user/getUserName',
          # we use 'user/getIdOrUserName' instead to store user ID for ERP5
          # user.
          if variable_id == 'actor' and vdef.getVariableExpression() == 'user/getUserName':
            expr = userGetIdOrUserNameExpression
          else:
            expr = variable_expression
        else:
          if object_context is None:
            object_context = self.getStateChangeInformation(document, self.getSourceValue())
          value = vdef.getVariableValue(object=object_context)

      if expr not in (None, ''):
        # Evaluate an expression.
        if econtext is None:
          # Lazily create the expression context.
          if sci is None:
            sci = StateChangeInfo(
                document, self, former_status, tdef,
                old_state, new_state, form_kw)
          econtext = createExprContext(sci)
        value = expr(econtext)
      status_dict[variable_reference] = value
    # Do not proceed in case of failure of before script
    if not before_script_success:
      status_dict[state_var] = old_state_reference # Remain in state
      tool.setStatusOf(self.getReference(), document, status_dict)
      if sci is None:
        sci = StateChangeInfo(
          document, self, former_status, tdef, old_state, new_state, form_kw)
      # put the error message in the workflow history
      sci.setWorkflowVariable(error_message=before_script_error_message)
      if validation_exc :
        # reraise validation failed exception
        raise validation_exc, None, validation_exc_traceback
      return new_state

    # update state
    status_dict[state_var] = new_state_reference

    tool.setStatusOf(self.getReference(), document, status_dict)
    self.updateRoleMappingsFor(document)

    # Execute the "after" script.
    if tdef is not None:
      script_value_list = tdef.getAfterScriptValueList()
      if script_value_list:
        if sci is None:
          sci = StateChangeInfo(document, self, former_status, tdef, old_state,
                              new_state, form_kw)
        old_state_destination_list = old_state.getDestinationValueList()
        for script in script_value_list:
          # Script can be either script or workflow method
          if script in old_state_destination_list and \
              script.getTriggerType() == TRIGGER_WORKFLOW_METHOD:
            getattr(document, convertToMixedCase(script.getReference()))()
          else:
            # Pass lots of info to the script in a single parameter.
            if script.getPortalType() == 'Workflow Script':
              script = getattr(self, script.id)
              script(sci)  # May throw an exception.

    # Return the new state object.
    if moved_exc is not None:
        # Propagate the notification that the object has moved.
        raise moved_exc
    else:
        return new_state

  security.declarePrivate('wrapWorkflowMethod')
  def wrapWorkflowMethod(self, ob, method_id, func, args, kw):
    '''
    Allows the user to request a workflow action.  This method
    must perform its own security checks.
    '''
    sdef = self._getWorkflowStateOf(ob)
    if sdef is None:
        raise WorkflowException, 'Object is in an undefined state'
    if method_id not in sdef.getTransitionIdList():
        raise Unauthorized(method_id)
    tdef = self.getTransitionValueById(method_id)
    if tdef is None or tdef.getTriggerType() != TRIGGER_WORKFLOW_METHOD:
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

  security.declareProtected(Permissions.AddPortalContent,
                            'addTransition')
  def addTransition(self, name):
    """
    add a new transition to the workflow
    """
    tr = self.newContent(portal_type='Transition')
    tr.setReference(name)

  security.declareProtected(Permissions.DeleteObjects,
                            'deleteTransitions')
  def deleteTransitions(self, name_list):
    """
    remove an set of transition
    """
    for name in name_list:
      self._delObject('transition_'+name)

  security.declareProtected(Permissions.AccessContentsInformation, 'showAsXML')
  def showAsXML(self, root=None):
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
          property_value = sdef.getProperty('state_permission_roles_dict')
          property_type = sdef.getPropertyType('state_permission_roles_dict')
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
            tr_var_list = tdef.objectValues(portal_type='Transition Variable')
            for tr_var in tr_var_list:
              reference = self._getOb(tr_var.getCausalityId()).getReference()
              transition_variable = SubElement(transition_variables, property_id, attrib=dict(id=reference,type='variable'))
              transition_variable.text = str(tr_var.getVariableExpression())
          else:
            property_value = tdef.getProperty(property_id)
            property_type = tdef.getPropertyType(property_id)
            sub_object = SubElement(transition, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)

    # 3. Variable as XML
    variable_reference_list = []
    variable_list = self.objectValues(portal_type='Workflow Variable')
    variable_prop_id_to_show = ['description', 'variable_expression',
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
        elif property_id == 'variable_value':
          property_value = vdef.getVariableValue()
          sub_object = SubElement(variable, property_id, attrib=dict(type='string'))
        else:
          property_value = vdef.getProperty(property_id)
          property_type = vdef.getPropertyType(property_id)
          sub_object = SubElement(variable, property_id, attrib=dict(type=property_type))
        if property_value is None or property_value ==() or property_value == []:
          property_value = ''
        sub_object.text = str(property_value)
        # for a very specific case, action return the reference of transition,
        # but in XML should show the same expression as in DC workflow.
        if vdef.getId() == 'variable_action' and property_id == 'variable_expression' and property_value != '':
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
      old_state = state.getReference()
    else:
      old_state = old_sdef.getId()
    if old_state == new_state_id:
      # Object is already in expected state
      return
    former_status = self.getCurrentStatusDict(ob)

    new_sdef = self._getOb(new_state_id, None)
    if new_sdef is None:
      raise WorkflowException, ('Destination state undefined: ' + new_state_id)

    # Update variables.
    state_values = self.getVariableValueDict()
    if state_values is None:
      state_values = {}

    tdef_exprs = {}
    status = {}
    for id, vdef in state_values.items():
      if not vdef.getStatusIncluded():
        continue
      expr = None
      if state_values.has_key(id):
        value = state_values[id]
      elif tdef_exprs.has_key(id):
        expr = tdef_exprs[id]
      elif not vdef.getAutomaticUpdate() and former_status.has_key(id):
        # Preserve former value
        value = former_status[id]
      else:
        variable_expression = vdef.getVariableExpressionInstance()
        if variable_expression is not None:
          expr = variable_expression
        else:
          value = vdef.getVariableValue()
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

    status['comment'] = 'Jump from %r to %r' % (self._getOb(old_state).getReference(), new_state_id_no_prefix,)
    status[self.getStateVariable()] = new_state_id_no_prefix
    tool = self.getParentValue()
    tool.setStatusOf(self.getId(), ob, status)

    # Update role to permission assignments.
    self.updateRoleMappingsFor(ob)
    return new_sdef

  security.declarePrivate('allowCreate')
  def allowCreate(self, container, type_name):
      """Returns true if the user is allowed to create a workflow instance.

      The object passed to the guard is the prospective container.

      wenjie: This is a compatibility related patch.

      More detail see TypeTool.pyline 360.
      """
      return 1

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCatalogVariablesFor')
  def getCatalogVariablesFor(self, ob):
      '''
      Allows this workflow to make workflow-specific variables
      available to the catalog, making it possible to implement
      worklists in a simple way.
      Returns a mapping containing the catalog variables
      that apply to ob.
      '''
      initial_state = None
      res = {}
      status = self.getCurrentStatusDict(ob)
      for variable in self.getVariableValueList():
        if variable.getForCatalog():
          variable_id = variable.getReference()
          variable_expression = variable.getVariableExpressionInstance()
          if status.has_key(variable_id):
            value = status[variable_id]
          elif variable_expression is not None:
            ec = createExprContext(StateChangeInfo(ob, self, status))
            # convert string to expression before execute it.
            value = variable_expression(ec)
          else:
            value = variable.getVariableValue()

      source_value = self.getSourceValue()
      try:
        initial_state = source_value.getReference()
      except AttributeError:
        pass

      state_var = self.getStateVariable()
      if state_var is not None:
        res[state_var] = status.get(state_var, initial_state)
      return res

  def _setWorkflowManagedPermissionList(self, permission_list):
    self.workflow_managed_permission = permission_list

    # add/remove the added/removed workflow permission to each state
    for state in self.getStateValueList():
      state.setCellRange(sorted(permission_list),
                         sorted(self.getManagedRoleList()),
                         base_id='cell')
      # get list of (unique) acquired permissions on state
      acquired_permission_set = state.getAcquirePermissionSet()

      # get list of roles associated to each permission on state
      permission_roles_dict = state.getStatePermissionRolesDict()

      # add permission from state_permission_roles_dict when added on workflow
      for permission in permission_list:
        if permission not in permission_roles_dict:
          state.state_permission_roles_dict[permission] = []
          # a new permission should be acquired by default
          acquired_permission_set.append(permission)
          state.setAcquirePermissionList(list(acquired_permission_set))

      permission_to_delete = [permission for permission in permission_roles_dict
                              if permission not in permission_list]

      # remove permission from state_permission_roles_dict when removed on workflow
      for permission in permission_to_delete:
        del state.state_permission_roles_dict[permission]
        if permission in acquired_permission_set:
          # in case it was acquired, remove from acquired permission list of the state
          acquired_permission_set.remove(permission)
          state.setAcquirePermissionList(list(acquired_permission_set))

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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'scripts')
  @property
  @deprecated
  def scripts(self):
    """
    Backward compatibility with DC Workflow to avoid modifying existing
    Workflow Scripts code
    """
    script_dict = {}
    for script in self.objectValues(portal_type="Workflow Script"):
      # wf.scripts['foobar']
      script_dict[script.getReference()] = script
      # another_workflow_with_the_same_script_id.scripts[script.getId()]
      script_dict[script.getId()] = script
    return script_dict

from Products.ERP5Workflow import WITH_DC_WORKFLOW_BACKWARD_COMPATIBILITY
if WITH_DC_WORKFLOW_BACKWARD_COMPATIBILITY:
  def __getattr__(self, name):
    '''
    TODO-arnau: Not efficient. Another possible implementation:

      Create a "ScriptContext" (_asScriptContext()) before executing Scripts
      but this has the following problem (besides of the fact that this is
      ONLY for backward compatibility and should be dropped once all projects
      have been migrated):
        1. Workflow Script called and a ScriptContext is created to be able to call scripts not having SCRIPT_PREFIX.
        2. That script calls a Workflow Script from another Workflow.
        => This will fail as ScriptContext is only created for the Workflow.

  def _asScriptContext(self):
    """
      change the context given to the script by adding foo for script_foo to the
      context dict in order to be able to call the script using its reference
      (= not prefixed by script_) from another workflow script

      historically, __getattr__ method of Workflow class was overriden for
      the same purpose, but it was heavyweight: doing a lot of useless
      operations (each time, it was checking for script_foo, even if foo was a
      transition, state, ...)
    """
    script_context = self.asContext()
    # asContext creates a temporary object and temporary object's "activate"
    # method code is: "return self". This means that the script is not put in
    # the activity queue as expected but it is instead directly executed. To fix
    # this, we override the temporary object's "activate" method with the one of
    # the original object.
    script_context.activate = self.activate
    for script in self.objectValues(portal_type="Workflow Script"):
      setattr(script_context, script.getReference(), script)
    return script_context

    '''
    if name[0] == '_': # Optimization (Folder.__getattr__)
      raise AttributeError(name)
    try:
      return super(Workflow, self).__getattr__(name)
    except AttributeError:
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
