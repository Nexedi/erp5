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

from Products.DCWorkflow import Guard
def formatNameUnion(names):
  names = list(names)
  if len(names) == 2:
    return ' or '.join(names)
  elif len(names) > 2:
    names[-1] = ' or ' + names[-1]
  return '; '.join(names)
Guard.formatNameUnion = formatNameUnion


class AssertPermissionMethod(object):
  """A method object to check that a user have a permission on a document.
  """
  def __init__(self, permission_name):
    self._permission_name = permission_name

  def __get__(self, instance, cls=None):
    self._instance = instance
    return self

  def __call__(self, username, document):
    sm = getSecurityManager()
    try:
      self._instance._loginAsUser(username)
      user = getSecurityManager().getUser()
      if not user.has_permission(self._permission_name, document):
        groups = []
        if hasattr(user, 'getGroups'):
          groups = user.getGroups()
        self._instance.fail(
          'User %s does NOT have %s permission on %s %s (user roles: [%s], '
          'roles needed: [%s], existing local roles:\n%s\n'
          'your user groups: [%s])' %
          (username, self._permission_name, document.getPortalTypeName(),
            document, ', '.join(user.getRolesInContext(document)),
           ', '.join([x['name'] for x in
                      document.rolesOfPermission(self._permission_name)
                      if x['selected']]),
           pformat(document.get_local_roles()),
           ', '.join(groups)))
    finally:
      setSecurityManager(sm)


class AssertNoPermissionMethod(object):
  """A method object to check that a user does not have a permission on a
  document.
  """
  def __init__(self, permission_name):
    self._permission_name = permission_name

  def __get__(self, instance, cls=None):
    self._instance = instance
    return self

  def __call__(self, username, document):
    sm = getSecurityManager()
    try:
      self._instance._loginAsUser(username)
      user = getSecurityManager().getUser()
      if user.has_permission(self._permission_name, document):
        self._instance.fail(
          'User %s has %s permission on %s %s (roles: [%s])' %
          (username, self._permission_name, document.getPortalTypeName(),
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
    self.portal = self.getPortal()
    self.workflow_tool = self.portal.portal_workflow

  def tearDown(self):
    """Clean up for next test.
    """
    self.abort()
    self.portal.portal_caches.clearAllCache()
    super(SecurityTestCase, self).tearDown()

  def _loginAsUser(self, username):
    """Login as a given username. The user must exist.
       In case Username is None, we consider test as Anonymous.
    """
    if username is None:
      newSecurityManager(None, SpecialUsers.nobody)
    else:
      uf = self.portal.acl_users
      user = uf.getUserById(username)
      self.assertNotEquals(user, None, 'No user %s' % username)
      newSecurityManager(None, user.__of__(uf))

  # Permission methods
  failIfUserCanViewDocument = AssertNoPermissionMethod(
                                     Permissions.View)
  failIfUserCanAccessDocument = AssertNoPermissionMethod(
                                     Permissions.AccessContentsInformation)
  failIfUserCanModifyDocument = AssertNoPermissionMethod(
                                     Permissions.ModifyPortalContent)
  failIfUserCanAddDocument = AssertNoPermissionMethod(
                                     Permissions.AddPortalContent)
  failIfUserCanChangeLocalRoles = AssertNoPermissionMethod(
                                     Permissions.ChangeLocalRoles)
  failIfUserCanDeleteDocument = AssertNoPermissionMethod(
                                     Permissions.DeleteObjects)

  def failIfUserHavePermissionOnDocument(self, permission_name, username, document):
    """Fail If the user have a permission on document.
    XXX why isn't it a method object ?
    """
    method = AssertNoPermissionMethod(permission_name)
    method._instance = self
    return method(username, document)

  failUnlessUserCanViewDocument = assertUserCanViewDocument =\
                AssertPermissionMethod(Permissions.View)
  failUnlessUserCanAccessDocument = assertUserCanAccessDocument =\
                AssertPermissionMethod(Permissions.AccessContentsInformation)
  failUnlessUserCanModifyDocument = assertUserCanModifyDocument = \
                AssertPermissionMethod(Permissions.ModifyPortalContent)
  failUnlessUserCanAddDocument = assertUserCanAddDocument =\
                AssertPermissionMethod(Permissions.AddPortalContent)
  failUnlessUserCanChangeLocalRoles = assertUserCanChangeLocalRoles =\
                AssertPermissionMethod(Permissions.ChangeLocalRoles)
  failUnlessUserCanDeleteDocument = assertUserCanDeleteDocument =\
                AssertPermissionMethod(Permissions.DeleteObjects)

  def failUnlessUserHavePermissionOnDocument(self, permission_name, username, document):
    """Fail Unless the user have a permission on document."""
    method = AssertPermissionMethod(permission_name)
    method._instance = self
    return method(username, document)
  assertUserHavePermissionOnDocument = failUnlessUserHavePermissionOnDocument

  # Workflow Transition Methods
  def failIfUserCanPassWorkflowTransition(self, username, transition, document):
    """Fails if the user can pass the workflow transition on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(username)
      user = getSecurityManager().getUser()
      valid_transition_list =[ai['id'] for ai in
                              self.workflow_tool.listActions(object=document) if
                              ai['category'] == 'workflow']
      if transition in valid_transition_list:
        self.fail('User %s can pass %s transition on %s %s. Roles: [%s]' % (
                  username, transition, document.getPortalTypeName(), document,
                  ", ".join(user.getRolesInContext(document))))
    finally:
      setSecurityManager(sm)

  def failUnlessUserCanPassWorkflowTransition(self, username,
                                              transition, document):
    """Fails unless the user can pass the workflow transition on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(username)
      user = getSecurityManager().getUser()
      valid_transition_list =[ai['id'] for ai in
                              self.workflow_tool.listActions(object=document) if
                              ai['category'] == 'workflow']
      if transition not in valid_transition_list:
        # Build a comprehensive error message
        workflow_states_description = []
        workflow_transitions_description = []
        for wf in self.workflow_tool.getWorkflowsFor(document) or []:
          if wf.getId() == 'edit_workflow':
            continue
          if isinstance(wf, InteractionWorkflowDefinition):
            continue
          for wf_transition_id in wf._getWorkflowStateOf(
                                                document).getTransitions():
            wf_transition = wf.transitions[wf_transition_id]
            if wf_transition.trigger_type == TRIGGER_USER_ACTION:
              workflow_transitions_description.append(
                "%s%s[%s]: %s" % (
                  wf_transition_id == transition and "* " or "  ",
                  wf_transition_id, wf.getId(),
                  wf_transition.getGuardSummary()))

          workflow_states_description.append("%s on %s" % (
                  wf._getWorkflowStateOf(document, id_only=1), wf.getId()))

        document_description = "%s at %s (%s)" % (
              document.getPortalType(), document.getPath(),
              ", ".join(workflow_states_description))

        self.fail('User %s can NOT pass %s transition on %s.\n '
                  'Roles: [%s]\n Available transitions:\n\t%s' % ( username,
                  transition, document_description,
                  ", ".join(user.getRolesInContext(document)),
                  "\n\t".join(workflow_transitions_description)))
    finally:
      setSecurityManager(sm)

  assertUserCanPassWorkflowTransition = failUnlessUserCanPassWorkflowTransition

  def assertUserHasWorklist(self, username, worklist_id, document_count):
    self.portal.portal_workflow.refreshWorklistCache()
    self.portal.portal_caches.clearAllCache()
    sm = getSecurityManager()
    try:
      self._loginAsUser(username)
      global_action_list = [x for x in
        self.portal.portal_workflow.listActions(object=self.portal)
        if x['category'] == 'global']
      worklist_action_list = [x for x in global_action_list
        if x['worklist_id'] == worklist_id]
      if not(worklist_action_list):
        self.fail("User %s does not have worklist %s.\nWorklists: %s" % (
          username, worklist_id, pformat(global_action_list)))
      worklist_action, = worklist_action_list
      self.assertEquals(document_count, worklist_action['count'],
        "User %s has %s documents in her %s worklist, not %s" % (
          username, worklist_action['count'], worklist_id, document_count))
    finally:
      setSecurityManager(sm)

  def assertUserHasNoWorklist(self, username, worklist_id):
    self.portal.portal_workflow.refreshWorklistCache()
    self.portal.portal_caches.clearAllCache()
    sm = getSecurityManager()
    try:
      self._loginAsUser(username)
      worklist_action_list = [x for x in
        self.portal.portal_workflow.listActions(object=self.portal)
        if x['category'] == 'global' and x['worklist_id'] == worklist_id]
      if worklist_action_list:
        self.fail("User %s has worklist %s: %s" % (username, worklist_id, pformat(worklist_action_list)))
    finally:
      setSecurityManager(sm)

  # Simple check for an user Role
  def failIfUserHaveRoleOnDocument(self, username, role, document):
    """Fails if the user have the role on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(username)
      user = getSecurityManager().getUser()
      if role in user.getRolesInContext(document):
        self.fail('User %s have %s role on %s at %s' % (
          username, role, document.getPortalType(), document.getRelativeUrl()))
    finally:
      setSecurityManager(sm)

  def failUnlessUserHaveRoleOnDocument(self, username, role, document):
    """Fails if the user does not have the role on the document."""
    sm = getSecurityManager()
    try:
      self._loginAsUser(username)
      user = getSecurityManager().getUser()
      if role not in user.getRolesInContext(document):
        self.fail('User %s does not have %s role on %s at %s '
                  '(user roles: %s)' % ( username, role,
                  document.getPortalType(), document.getRelativeUrl(),
                  user.getRolesInContext(document)))
    finally:
      setSecurityManager(sm)

  assertUserHaveRoleOnDocument = failUnlessUserHaveRoleOnDocument

