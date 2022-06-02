##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#    Jerome Perrin <jerome@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

"""Base Class for security tests using ERP5Security and DCWorkflow
"""

from pprint import pformat
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl import SpecialUsers
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type import Permissions
from Products.ERP5.InteractionWorkflow import InteractionWorkflowDefinition


from Products.ERP5Type.Base import Base
from typing import Callable


class AssertPermissionMethod(object):
  """A method object to check that a user have a permission on a document.
  """
  def __init__(self, permission_name):
    # type: (str) -> None
    self._permission_name = permission_name

  def __get__(self, instance, cls=None):
    self._instance = instance
    return self

  def __call__(self, user_id, document):
    # type: (str, Base) -> None
    sm = getSecurityManager()
    try:
      self._instance._loginAsUser(user_id)
      user = getSecurityManager().getUser()
      if not user.has_permission(self._permission_name, document):
        groups = []
        if hasattr(user, 'getGroups'):
          groups = user.getGroups()
        self._instance.fail(
          'User %s does NOT have %s permission on %s %s (user roles: [%s], '
          'roles needed: [%s], existing local roles:\n%s\n'
          'your user groups: [%s])' %
          (user_id, self._permission_name, document.getPortalTypeName(),
            document, ', '.join(user.getRolesInContext(document)),
           ', '.join([x['name'] for x in
                      document.rolesOfPermission(self._permission_name)
                      if x['selected']]),
           pformat(document.get_local_roles()),
           ', '.join(sorted(groups))))
    finally:
      setSecurityManager(sm)


class AssertNoPermissionMethod(object):
  """A method object to check that a user does not have a permission on a
  document.
  """
  def __init__(self, permission_name):
    # type: (str) -> None
    self._permission_name = permission_name

  def __get__(self, instance, cls=None):
    self._instance = instance
    return self

  def __call__(self, user_id, document):
    # type: (str, Base) -> None
    sm = getSecurityManager()
    try:
      self._instance._loginAsUser(user_id)
      user = getSecurityManager().getUser()
      if user.has_permission(self._permission_name, document):
        self._instance.fail(
          'User %s has %s permission on %s %s (roles: [%s])' %
          (user_id, self._permission_name, document.getPortalTypeName(),
            document, ', '.join(user.getRolesInContext(document))))
    finally:
      setSecurityManager(sm)


class SecurityTestCase(ERP5TypeTestCase):
  """Base class for security tests.
  """
  def _setup(self):
    """set up and login as default user"""
    super(SecurityTestCase, self)._setup()
    self.login()
    self.workflow_tool = self.portal.portal_workflow

  def tearDown(self):
    """Clean up for next test.
    """
    self.abort()
    self.portal.portal_caches.clearAllCache()
    super(SecurityTestCase, self).tearDown()

  def _loginAsUser(self, user_id):
    """Login as a given user_id. The user must exist.
       In case user_id is None, we consider test as Anonymous.
    """
    if user_id is None:
      newSecurityManager(None, SpecialUsers.nobody)
    else:
      uf = self.portal.acl_users
      user = uf.getUserById(user_id)
      self.assertNotEquals(user, None, 'No user %s' % user_id)
      newSecurityManager(None, user.__of__(uf))

  # Permission methods
  failIfUserCanViewDocument = assertUserCanNotViewDocument = AssertNoPermissionMethod(
        Permissions.View)  # type: Callable[[SecurityTestCase, str, Base], None]
  failIfUserCanAccessDocument = assertUserCanNotAccessDocument = AssertNoPermissionMethod(
        Permissions.AccessContentsInformation)  # type: Callable[[SecurityTestCase, str, Base], None]
  failIfUserCanModifyDocument = assertUserCanNotModifyDocument = AssertNoPermissionMethod(
        Permissions.ModifyPortalContent)  # type: Callable[[SecurityTestCase, str, Base], None]
  failIfUserCanAddDocument = assertUserCanNotAddDocument = AssertNoPermissionMethod(
        Permissions.AddPortalContent)  # type: Callable[[SecurityTestCase, str, Base], None]
  failIfUserCanChangeLocalRoles = assertUserCanNotChangeLocalRoles = AssertNoPermissionMethod(
        Permissions.ChangeLocalRoles)  # type: Callable[[SecurityTestCase, str, Base], None]
  failIfUserCanDeleteDocument = assertUserCanNotDeleteDocument = AssertNoPermissionMethod(
        Permissions.DeleteObjects)  # type: Callable[[SecurityTestCase, str, Base], None]

  def failIfUserHavePermissionOnDocument(self, permission_name, user_id, document):
    # type: (str, str, Base) -> None
    """Fail If the user have a permission on document.
    XXX why isn't it a method object ?
    """
    method = AssertNoPermissionMethod(permission_name)
    method._instance = self
    return method(user_id, document)

  failUnlessUserCanViewDocument = assertUserCanViewDocument =\
      AssertPermissionMethod(Permissions.View)  # type: Callable[[SecurityTestCase, str, Base], None]
  failUnlessUserCanAccessDocument = assertUserCanAccessDocument =\
      AssertPermissionMethod(Permissions.AccessContentsInformation)  # type: Callable[[SecurityTestCase, str, Base], None]
  failUnlessUserCanModifyDocument = assertUserCanModifyDocument = \
      AssertPermissionMethod(Permissions.ModifyPortalContent)  # type: Callable[[SecurityTestCase, str, Base], None]
  failUnlessUserCanAddDocument = assertUserCanAddDocument =\
      AssertPermissionMethod(Permissions.AddPortalContent)  # type: Callable[[SecurityTestCase, str, Base], None]
  failUnlessUserCanChangeLocalRoles = assertUserCanChangeLocalRoles =\
      AssertPermissionMethod(Permissions.ChangeLocalRoles)  # type: Callable[[SecurityTestCase, str, Base], None]
  failUnlessUserCanDeleteDocument = assertUserCanDeleteDocument =\
      AssertPermissionMethod(Permissions.DeleteObjects)  # type: Callable[[SecurityTestCase, str, Base], None]

  def failUnlessUserHavePermissionOnDocument(self, permission_name, user_id, document):
    # type: (str, str, Base) -> None
    """Fail Unless the user have a permission on document."""
    method = AssertPermissionMethod(permission_name)
    method._instance = self
    return method(user_id, document)
  assertUserHavePermissionOnDocument = failUnlessUserHavePermissionOnDocument

  # Workflow Transition Methods
  def failIfUserCanPassWorkflowTransition(self, user_id, transition, document):
    # type: (str, str, Base) -> None
    """Fails if the user can pass the workflow transition on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(user_id)
      user = getSecurityManager().getUser()
      valid_transition_list =[ai['id'] for ai in
                              self.workflow_tool.listActions(object=document) if
                              ai['category'] == 'workflow']
      if transition in valid_transition_list:
        self.fail('User %s can pass %s transition on %s %s. Roles: [%s]' % (
                  user_id, transition, document.getPortalTypeName(), document,
                  ", ".join(user.getRolesInContext(document))))
    finally:
      setSecurityManager(sm)

  assertUserCanNotPassWorkflowTransition = failIfUserCanPassWorkflowTransition # type: Callable[[SecurityTestCase, str, str, Base], None]

  def failUnlessUserCanPassWorkflowTransition(self, user_id,
                                              transition, document):
    # type: (str, str, Base) -> None
    """Fails unless the user can pass the workflow transition on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(user_id)
      user = getSecurityManager().getUser()
      valid_transition_list =[ai['id'] for ai in
                              self.workflow_tool.listActions(object=document) if
                              ai['category'] == 'workflow']
      if transition not in valid_transition_list:
        # Build a comprehensive error message
        workflow_states_description = []
        workflow_transitions_description = []
        for wf in self.workflow_tool.getWorkflowValueListFor(document) or []:
          if wf.getId() == 'edit_workflow':
            continue
          if wf.__class__.__name__ in (
              'InteractionWorkflowDefinition',
              'Interaction Workflow',
            ):
            continue
          for wf_transition in wf._getWorkflowStateOf(document).getDestinationValueList():
            if wf_transition.getTriggerType() == TRIGGER_USER_ACTION:
              workflow_transitions_description.append(
                "%s%s[%s]\n\t\tExpression: %s\n\t\tPermissions: %s\n\t\tGroups: %s" % (
                  wf_transition.getReference() == transition and "* " or "  ",
                  wf_transition.getReference(),
                  wf.getId(),
                  wf_transition.getGuardExpression() or '',
                  ', '.join(wf_transition.getGuardPermissionList()),
                  ', '.join(wf_transition.getGuardGroupList()),
                )
              )

          workflow_states_description.append("%s on %s" % (
                  wf._getWorkflowStateOf(document, id_only=1), wf.getId()))

        document_description = "%s at %s (%s)" % (
              document.getPortalType(), document.getPath(),
              ", ".join(workflow_states_description))

        self.fail('User %s can NOT pass %s transition on %s.\n '
                  'Roles: [%s]\n Available transitions:\n\t%s' % ( user_id,
                  transition, document_description,
                  ", ".join(user.getRolesInContext(document)),
                  "\n\t".join(workflow_transitions_description)))
    finally:
      setSecurityManager(sm)

  assertUserCanPassWorkflowTransition = failUnlessUserCanPassWorkflowTransition # type: Callable[[SecurityTestCase, str, str, Base], None]

  def assertUserHasWorklist(self, user_id, worklist_id, document_count):
    # type: (str, str, int) -> None
    self.portal.portal_workflow.refreshWorklistCache()
    self.portal.portal_caches.clearAllCache()
    sm = getSecurityManager()
    try:
      self._loginAsUser(user_id)
      global_action_list = [x for x in
        self.portal.portal_workflow.listActions(object=self.portal)
        if x['category'] == 'global']
      worklist_action_list = [x for x in global_action_list
        if x['worklist_id'] == worklist_id]
      if not(worklist_action_list):
        self.fail("User %s does not have worklist %s.\nWorklists: %s" % (
          user_id, worklist_id, pformat(global_action_list)))
      worklist_action, = worklist_action_list
      self.assertEquals(document_count, worklist_action['count'],
        "User %s has %s documents in her %s worklist, not %s" % (
          user_id, worklist_action['count'], worklist_id, document_count))
    finally:
      setSecurityManager(sm)

  def assertUserHasNoWorklist(self, user_id, worklist_id):
    # type: (str, str) -> None
    self.portal.portal_workflow.refreshWorklistCache()
    self.portal.portal_caches.clearAllCache()
    sm = getSecurityManager()
    try:
      self._loginAsUser(user_id)
      worklist_action_list = [x for x in
        self.portal.portal_workflow.listActions(object=self.portal)
        if x['category'] == 'global' and x['worklist_id'] == worklist_id]
      if worklist_action_list:
        self.fail("User %s has worklist %s: %s" % (user_id, worklist_id, pformat(worklist_action_list)))
    finally:
      setSecurityManager(sm)

  # Simple check for an user Role
  def failIfUserHaveRoleOnDocument(self, user_id, role, document):
    # type: (str, str, Base) -> None
    """Fails if the user have the role on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(user_id)
      user = getSecurityManager().getUser()
      if role in user.getRolesInContext(document):
        self.fail('User %s have %s role on %s at %s' % (
          user_id, role, document.getPortalType(), document.getRelativeUrl()))
    finally:
      setSecurityManager(sm)

  assertUserDoesNotHaveRoleOnDocument = failIfUserHaveRoleOnDocument  # type: Callable[[SecurityTestCase, str, str, Base], None]

  def failUnlessUserHaveRoleOnDocument(self, user_id, role, document):
    # type: (str, str, Base) -> None
    """Fails if the user does not have the role on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(user_id)
      user = getSecurityManager().getUser()
      if role not in user.getRolesInContext(document):
        self.fail('User %s does not have %s role on %s at %s '
                  '(user roles: %s)' % ( user_id, role,
                  document.getPortalType(), document.getRelativeUrl(),
                  user.getRolesInContext(document)))
    finally:
      setSecurityManager(sm)

  assertUserHaveRoleOnDocument = failUnlessUserHaveRoleOnDocument  # type: Callable[[SecurityTestCase, str, str, Base], None]
