# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                                    Jerome Perrin <jerome@nexedi.com>
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

"""Tests ERP5 User Management.
"""

import itertools
import transaction
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl import SpecialUsers
from Products.PluggableAuthService import PluggableAuthService
from Products.PluggableAuthService.interfaces.plugins \
  import IAuthenticationPlugin, IUserEnumerationPlugin
from zope.interface.verify import verifyClass
from DateTime import DateTime
from Products import ERP5Security
from Products.DCWorkflow.DCWorkflow import ValidationFailed

AUTO_LOGIN = object()

class TestUserManagement(ERP5TypeTestCase):
  """Tests User Management in ERP5Security.
  """
  _login_generator = itertools.count().next

  def getTitle(self):
    """Title of the test."""
    return "ERP5Security: User Management"

  def getBusinessTemplateList(self):
    """List of BT to install. """
    return ('erp5_base', 'erp5_administration',)

  def beforeTearDown(self):
    """Clears person module and invalidate caches when tests are finished."""
    transaction.abort()
    self.getPersonModule().manage_delObjects([x for x in
                             self.getPersonModule().objectIds()])
    self.tic()

  def login(self):
    uf = self.getUserFolder()
    uf._doAddUser('alex', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)

  def getUserFolder(self):
    """Returns the acl_users. """
    return self.getPortal().acl_users

  def test_GroupManagerInterfaces(self):
    """Tests group manager plugin respects interfaces."""
    # XXX move to GroupManager test class
    from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
    from Products.ERP5Security.ERP5GroupManager import ERP5GroupManager
    verifyClass(IGroupsPlugin, ERP5GroupManager)

  def test_UserManagerInterfaces(self):
    """Tests user manager plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import\
                IAuthenticationPlugin, IUserEnumerationPlugin
    from Products.ERP5Security.ERP5UserManager import ERP5UserManager
    verifyClass(IAuthenticationPlugin, ERP5UserManager)
    verifyClass(IUserEnumerationPlugin, ERP5UserManager)

  def test_UserFolder(self):
    """Tests user folder has correct meta type."""
    self.assertTrue(isinstance(self.getUserFolder(),
        PluggableAuthService.PluggableAuthService))

  def loginAsUser(self, username):
    uf = self.portal.acl_users
    user = uf.getUserById(username).__of__(uf)
    newSecurityManager(None, user)

  def _makePerson(self, login=AUTO_LOGIN, open_assignment=1, assignment_start_date=None,
                  assignment_stop_date=None, tic=True, password='secret', group_value=None, **kw):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', **kw)
    assignment = new_person.newContent(portal_type = 'Assignment',
                                       start_date=assignment_start_date,
                                       stop_date=assignment_stop_date,
                                       group_value=group_value,)
    if open_assignment:
      assignment.open()
    if login is not None:
      if login is AUTO_LOGIN:
        login = 'login_%s' % self._login_generator()
      new_person.newContent(
        portal_type='ERP5 Login',
        reference=login,
        password=password,
      ).validate()
    if tic:
      self.tic()
    return new_person.Person_getUserId(), login, password

  def _assertUserExists(self, login, password):
    """Checks that a user with login and password exists and can log in to the
    system.
    """
    from Products.PluggableAuthService.interfaces.plugins import\
                                                      IAuthenticationPlugin
    uf = self.getUserFolder()
    self.assertNotEquals(uf.getUser(login), None)
    for plugin_name, plugin in uf._getOb('plugins').listPlugins(
                                IAuthenticationPlugin ):
      if plugin.authenticateCredentials(
                  {'login':login, 'password':password}) is not None:
        break
    else:
      self.fail("No plugin could authenticate '%s' with password '%s'" %
              (login, password))

  def _assertUserDoesNotExists(self, login, password):
    """Checks that a user with login and password does not exists and cannot
    log in to the system.
    """
    from Products.PluggableAuthService.interfaces.plugins import\
                                                        IAuthenticationPlugin
    uf = self.getUserFolder()
    for plugin_name, plugin in uf._getOb('plugins').listPlugins(
                              IAuthenticationPlugin ):
      if plugin.authenticateCredentials(
                {'login':login, 'password':password}) is not None:
        self.fail(
           "Plugin %s should not have authenticated '%s' with password '%s'" %
           (plugin_name, login, password))

  def _getOrCreateGroupValue(self):
    group_id = 'dummy_group'
    group = self.portal.portal_categories.group
    if group_id in group.objectIds():
      return group[group_id]
    else:
      return self.portal.portal_categories.group.newContent(
        id=group_id
      )

  def _createDummyDocument(self):
    types_tool = self.portal.portal_types
    # Create Portal Types if needed
    if 'Dummy Object' not in types_tool.objectIds():
      dummy_type = types_tool.newContent(
        'Dummy Object',
        'Base Type',
        type_class='XMLObject'
      )
      dummy_type.newContent(
        portal_type='Role Information',
        role_category_list=self.portal.portal_categories.\
          group.dummy_group.getRelativeUrl(),
        role_name_list=('Assignee', )
      )
    if 'Dummy Module' not in types_tool.objectIds():
      types_tool.newContent(
        'Dummy Module',
        'Base Type',
        type_class='Folder',
        type_filter_content_type=1,
        type_allowed_content_type_list=('Dummy Object', ),
      )
    # clean-up dummy_module in any way
    if 'dummy_module' in self.portal.objectIds():
      self.portal.manage_delObjects(['dummy_module'])
    self.tic()
    self.portal.newContent(portal_type='Dummy Module', id='dummy_module')
    dummy_document = self.portal.dummy_module.newContent(portal_type='Dummy Object')
    self.tic()
    return dummy_document

  def test_PersonWithLoginPasswordAreUsers(self):
    """Tests a person with a login & password is a valid user."""
    _, login, password = self._makePerson()
    self._assertUserExists(login, password)

  def test_PersonLoginCaseSensitive(self):
    """Login/password are case sensitive."""
    login = 'case_test_user'
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists('case_test_User', password)

  def test_PersonLoginIsNotStripped(self):
    """Make sure 'foo ', ' foo' and ' foo ' do not match user 'foo'. """
    _, login, password = self._makePerson()
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists(login + ' ', password)
    self._assertUserDoesNotExists(' ' + login, password)
    self._assertUserDoesNotExists(' ' + login + ' ', password)

  def test_PersonLoginCannotBeComposed(self):
    """Make sure ZSQLCatalog keywords cannot be used at login time"""
    _, login, password = self._makePerson()
    self._assertUserExists(login, password)
    doest_not_exist = 'bar'
    self._assertUserDoesNotExists(doest_not_exist, password)
    self._assertUserDoesNotExists(login + ' OR ' + doest_not_exist, password)
    self._assertUserDoesNotExists(doest_not_exist + ' OR ' + login, password)

  def test_PersonLoginQuote(self):
    login = "'"
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)
    login = '"'
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)

  def test_PersonLogin_OR_Keyword(self):
    base_login = 'foo'
    login = base_login + ' OR bar'
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists(base_login, password)

  def test_PersonLoginCatalogKeyWord(self):
    # use something that would turn the username in a ZSQLCatalog catalog keyword
    base_login ='foo'
    login = base_login + '%'
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists(base_login, password)
    self._assertUserDoesNotExists(base_login + "bar", password)

  def test_PersonLoginNGT(self):
    login = '< foo'
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists('fo', password)

  def test_PersonLoginNonAscii(self):
    """Login can contain non ascii chars."""
    login = 'j\xc3\xa9'
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)

  def test_PersonWithLoginWithEmptyPasswordAreNotUsers(self):
    """Tests a person with a login but no password is not a valid user."""
    password = None
    _, login, _ = self._makePerson(password=password)
    self._assertUserDoesNotExists(login, password)
    password = ''
    _, login, self._makePerson(password=password)
    self._assertUserDoesNotExists(login, password)

  def test_PersonWithEmptyLoginAreNotUsers(self):
    """Tests a person with empty login & password is not a valid user."""
    _, login, _ = self._makePerson()
    pas_user, = self.portal.acl_users.searchUsers(login=login, exact_match=True)
    pas_login, = pas_user['login_list']
    login_value = self.portal.restrictedTraverse(pas_login['path'])
    login_value.invalidate()
    login_value.setReference('')
    self.commit()
    self.assertRaises(ValidationFailed, login_value.validate)
    self.assertRaises(ValidationFailed, self.portal.portal_workflow.doActionFor, login_value, 'validate_action')

  def test_PersonWithLoginWithNotAssignmentAreNotUsers(self):
    """Tests a person with a login & password and no assignment open is not a valid user."""
    _, login, password = self._makePerson(open_assignment=0)
    self._assertUserDoesNotExists(login, password)

  def _testUserNameExistsButCannotLoginAndCannotCreate(self, login):
    self.assertTrue(self.getUserFolder().searchUsers(login=login, exact_match=True))
    self._assertUserDoesNotExists(login, '')
    self.assertRaises(ValidationFailed, self._makePerson, login=login)

  def test_PersonWithSuperUserLogin(self):
    """Tests one cannot use the "super user" special login."""
    self._testUserNameExistsButCannotLoginAndCannotCreate(ERP5Security.SUPER_USER)

  def test_PersonWithAnonymousLogin(self):
    """Tests one cannot use the "anonymous user" special login."""
    self._testUserNameExistsButCannotLoginAndCannotCreate(SpecialUsers.nobody.getUserName())

  def test_PersonWithSystemUserLogin(self):
    """Tests one cannot use the "system user" special login."""
    self._testUserNameExistsButCannotLoginAndCannotCreate(SpecialUsers.system.getUserName())

  def test_searchUserId(self):
    substring = 'person_id'
    user_id_set = {substring + '1', '1' + substring}
    for user_id in user_id_set:
      self._makePerson(user_id=user_id)
    self.assertEqual(
      user_id_set,
      {x['userid'] for x in self.portal.acl_users.searchUsers(id=substring, exact_match=False)},
    )

  def test_searchLogin(self):
    substring = 'person_login'
    login_set = {substring + '1', '1' + substring}
    for login in login_set:
      self._makePerson(login=login)
    self.assertEqual(
      login_set,
      {x['login'] for x in self.portal.acl_users.searchUsers(login=substring, exact_match=False)},
    )

  def test_searchUsersIdExactMatch(self):
    substring = 'person2_id'
    self._makePerson(user_id=substring)
    self._makePerson(user_id=substring + '1')
    self._makePerson(user_id='1' + substring)
    self.assertEqual(
      [substring],
      [x['userid'] for x in self.portal.acl_users.searchUsers(id=substring, exact_match=True)],
    )

  def test_searchUsersLoginExactMatch(self):
    substring = 'person2_login'
    self._makePerson(login=substring)
    self._makePerson(login=substring + '1')
    self._makePerson(login='1' + substring)
    self.assertEqual(
      [substring],
      [x['login'] for x in self.portal.acl_users.searchUsers(login=substring, exact_match=True)],
    )

  def test_MultipleUsers(self):
    """Tests that it's refused to create two Persons with same user id."""
    user_id, login, _ = self._makePerson()
    self.assertRaises(ValidationFailed, self._makePerson, user_id=user_id)
    self.assertRaises(ValidationFailed, self._makePerson, login=login)

  def test_MultiplePersonReferenceWithoutCommit(self):
    """
    Tests that it's refused to create two Persons with same user id.
    Check if both persons are created in the same transaction
    """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', user_id='new_person')
    self.assertRaises(ValidationFailed, person_module.newContent,
                     portal_type='Person', user_id='new_person')

  def test_MultiplePersonReferenceWithoutTic(self):
    """
    Tests that it's refused to create two Persons with same user id.
    Check if both persons are created in 2 different transactions.
    """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', user_id='new_person')
    self.commit()
    self.assertRaises(ValidationFailed, person_module.newContent,
                     portal_type='Person', user_id='new_person')

  def test_MultiplePersonReferenceConcurrentTransaction(self):
    """
    Tests that it's refused to create two Persons with same user id.
    Check if both persons are created in 2 concurrent transactions.
    For now, just verify that serialize is called on person_module.
    """
    class DummyTestException(Exception):
      pass

    def verify_serialize_call(self):
      # Check that serialize is called on person module
      if self.getRelativeUrl() == 'person_module':
        raise DummyTestException
      else:
        return self.serialize_call()

    # Replace serialize by a dummy method
    from Products.ERP5Type.Base import Base
    Base.serialize_call = Base.serialize
    Base.serialize = verify_serialize_call

    person_module = self.getPersonModule()
    try:
      self.assertRaises(DummyTestException, person_module.newContent,
                       portal_type='Person', user_id='new_person')
    finally:
      Base.serialize = Base.serialize_call

  def test_PersonCopyAndPaste(self):
    """If we copy and paste a person, login must not be copyied."""
    user_id, _, _ = self._makePerson(user_id='new_person')
    user, = self.portal.acl_users.searchUsers(id=user_id, exact_match=True)
    user_value = self.portal.restrictedTraverse(user['path'])
    container = user_value.getParentValue()
    changed, = container.manage_pasteObjects(
      container.manage_copyObjects([user_value.getId()]),
    )
    self.assertNotEquals(
      container[changed['new_id']].Person_getUserId(),
      user_id,
    )

  def test_Preference_created_for_new_user_on_getActiveUserPreference(self):
    # Creating a user will create a preference on the first time `getActiveUserPreference`
    # is called
    preference_tool = self.portal.portal_preferences
    preference_count = len(preference_tool.contentValues())

    user_id, login, password = self._makePerson()
    # creating a person does not create a preference
    self.assertEqual(preference_count, len(preference_tool.contentValues()))

    self.loginAsUser(user_id)

    # getActiveUserPreference will create a user preference
    new_preference = preference_tool.getActiveUserPreference()
    self.assertNotEqual(None, new_preference)
    self.assertEqual(preference_count+1, len(preference_tool.contentValues()))
    self.assertEqual('enabled', new_preference.getPreferenceState())

    self.tic()

    # subsequent calls to getActiveUserPreference returns the same preference
    active_preference = preference_tool.getActiveUserPreference()
    self.assertEqual(active_preference, new_preference)
    self.assertEqual(preference_count+1, len(preference_tool.contentValues()))

  def test_PreferenceTool_setNewPassword(self):
    # Preference Tool has an action to change password
    user_id, login, password = self._makePerson()
    self._assertUserExists(login, password)
    pas_user, = self.portal.acl_users.searchUsers(id=user_id, exact_match=True)
    pas_login, = pas_user['login_list']
    login_value = self.portal.restrictedTraverse(pas_login['path'])
    new_password = 'new' + password

    self.loginAsUser(user_id)
    result = self.portal.portal_preferences.PreferenceTool_setNewPassword(
      dialog_id='PreferenceTool_viewChangePasswordDialog',
      current_password='bad' + password,
      new_password=new_password,
    )
    self.assertEqual(result, self.portal.absolute_url()+'/portal_preferences/PreferenceTool_viewChangePasswordDialog?portal_status_message=Current%20password%20is%20wrong.')

    self.login()
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists(login, new_password)

    self.loginAsUser(user_id)
    result = self.portal.portal_preferences.PreferenceTool_setNewPassword(
      dialog_id='PreferenceTool_viewChangePasswordDialog',
      current_password=password,
      new_password=new_password,
    )
    self.assertEqual(result, self.portal.absolute_url()+'/logout')

    self.login()
    self._assertUserExists(login, new_password)
    self._assertUserDoesNotExists(login, password)
    # password is not stored in plain text
    self.assertNotEquals(new_password, self.portal.restrictedTraverse(pas_user['path']).getPassword())

  def test_OpenningAssignmentClearCache(self):
    """Openning an assignment for a person clear the cache automatically."""
    user_id, login, password = self._makePerson(open_assignment=0)
    self._assertUserDoesNotExists(login, password)
    user, = self.portal.acl_users.searchUsers(id=user_id, exact_match=True)
    pers = self.portal.restrictedTraverse(user['path'])
    assi = pers.newContent(portal_type='Assignment')
    assi.open()
    self.commit()
    self._assertUserExists(login, password)
    assi.close()
    self.commit()
    self._assertUserDoesNotExists(login, password)

  def test_PersonNotIndexedNotCached(self):
    user_id, login, password = self._makePerson(tic=False)
    # not indexed yet
    self._assertUserDoesNotExists(login, password)
    self.tic()
    self._assertUserExists(login, password)

  def test_PersonNotValidNotCached(self):
    user_id, login, password = self._makePerson()
    password += '2'
    pas_user, = self.portal.acl_users.searchUsers(login=login, exact_match=True)
    pas_login, = pas_user['login_list']
    self._assertUserDoesNotExists(login, password)
    self.portal.restrictedTraverse(pas_login['path']).setPassword(password)
    self._assertUserExists(login, password)

  def test_PersonLoginMigration(self):
    if 'erp5_users' not in self.portal.acl_users:
      self.portal.acl_users.manage_addProduct['ERP5Security'].addERP5UserManager('erp5_users')
    self.portal.acl_users.erp5_users.manage_activateInterfaces([
      'IAuthenticationPlugin',
      'IUserEnumerationPlugin',
    ])
    pers = self.portal.person_module.newContent(
      portal_type='Person',
      reference='the_user',
      user_id=None,
    )
    pers.newContent(
      portal_type='Assignment',
    ).open()
    pers.setPassword('secret')
    self.assertEqual(len(pers.objectValues(portal_type='ERP5 Login')), 0)
    self.tic()
    self._assertUserExists('the_user', 'secret')
    self.portal.portal_templates.fixConsistency(filter={'constraint_type': 'post_upgrade'})
    self.portal.portal_caches.clearAllCache()
    self.tic()
    self._assertUserExists('the_user', 'secret')
    self.assertEqual(pers.getPassword(), None)
    self.assertEqual(pers.Person_getUserId(), 'the_user')
    login = pers.objectValues(portal_type='ERP5 Login')[0]
    login.setPassword('secret2')
    self.portal.portal_caches.clearAllCache()
    self.tic()
    self._assertUserDoesNotExists('the_user', 'secret')
    self._assertUserExists('the_user', 'secret2')
    self.assertFalse('erp5_users' in \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IAuthenticationPlugin)])
    self.assertFalse('erp5_users' in \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IUserEnumerationPlugin)])

  def test_ERP5LoginUserManagerMigration(self):
    acl_users= self.portal.acl_users
    acl_users.manage_delObjects(ids=['erp5_login_users'])
    portal_templates = self.portal.portal_templates
    self.assertNotEqual(portal_templates.checkConsistency(filter={'constraint_type': 'post_upgrade'}) , [])
    # call checkConsistency again to check if FIX does not happen by checkConsistency().
    self.assertNotEqual(portal_templates.checkConsistency(filter={'constraint_type': 'post_upgrade'}) , [])
    portal_templates.fixConsistency(filter={'constraint_type': 'post_upgrade'})
    self.assertEqual(portal_templates.checkConsistency(filter={'constraint_type': 'post_upgrade'}) , [])
    self.assertTrue('erp5_login_users' in \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IAuthenticationPlugin)])
    self.assertTrue('erp5_login_users' in \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IUserEnumerationPlugin)])

  def test_AssignmentWithDate(self):
    """Tests a person with an assignment with correct date is a valid user."""
    date = DateTime()
    _, login, password = self._makePerson(
      assignment_start_date=date - 5,
      assignment_stop_date=date + 5,
    )
    self._assertUserExists(login, password)

  def test_AssignmentWithBadStartDate(self):
    """Tests a person with an assignment with bad start date is not a valid user."""
    date = DateTime()
    _, login, password = self._makePerson(
      assignment_start_date=date + 1,
      assignment_stop_date=date + 5,
    )
    self._assertUserDoesNotExists(login, password)

  def test_AssignmentWithBadStopDate(self):
    """Tests a person with an assignment with bad stop date is not a valid user."""
    date = DateTime()
    _, login, password = self._makePerson(
      assignment_start_date=date - 5,
      assignment_stop_date=date - 1,
    )
    self._assertUserDoesNotExists(login, password)

  def test_securityGroupAssignmentCorrectDate(self):
    """
      Tests a person with an assignment with correct date
      gets correctly assigned to security groups.
    """
    date = DateTime()
    user_id, login, password = self._makePerson(
      assignment_start_date=date - 5,
      assignment_stop_date=date + 5,
      group_value=self._getOrCreateGroupValue()
    )
    self.assertIn(
      'Assignee',
      self.portal.acl_users.getUserById(user_id).\
        getRolesInContext(self._createDummyDocument())
    )

  def test_securityGroupAssignmentBadStartDate(self):
    """
      Tests a person with an assignment with bad (future) start date
      does not get assigned to security groups.
    """
    date = DateTime()
    user_id, login, password = self._makePerson(
      assignment_start_date=date + 1,
      assignment_stop_date=date + 5,
      group_value=self._getOrCreateGroupValue()
    )
    self.assertNotIn(
      'Assignee',
      self.portal.acl_users.getUserById(user_id).\
        getRolesInContext(self._createDummyDocument())
    )

  def test_securityGroupAssignmentBadStopDate(self):
    """
      Tests a person with an assignment with bad (past) stop date
      does not get assigned to security groups.
    """
    date = DateTime()
    user_id, login, password = self._makePerson(
      assignment_start_date=date - 5,
      assignment_stop_date=date - 1,
      group_value=self._getOrCreateGroupValue()
    )
    self.assertNotIn(
      'Assignee',
      self.portal.acl_users.getUserById(user_id).\
        getRolesInContext(self._createDummyDocument())
    )

  def test_DeletedPersonIsNotUser(self):
    user_id, login, password = self._makePerson()
    self._assertUserExists(login, password)
    acl_user, = self.portal.acl_users.searchUsers(id=user_id, exact_match=True)
    self.portal.restrictedTraverse(acl_user['path']).delete()
    self.commit()
    self._assertUserDoesNotExists(login, password)

  def test_ReallyDeletedPersonIsNotUser(self):
    user_id, login, password = self._makePerson()
    acl_user, = self.portal.acl_users.searchUsers(id=user_id, exact_match=True)
    p = self.portal.restrictedTraverse(acl_user['path'])
    self._assertUserExists(login, password)
    p.getParentValue().deleteContent(p.getId())
    self.commit()
    self._assertUserDoesNotExists(login, password)

  def test_InvalidatedPersonIsUser(self):
    user_id, login, password = self._makePerson()
    acl_user, = self.portal.acl_users.searchUsers(id=user_id, exact_match=True)
    p = self.portal.restrictedTraverse(acl_user['path'])
    self._assertUserExists(login, password)
    p.validate()
    p.invalidate()
    self.commit()
    self._assertUserExists(login, password)

  def test_UserIdIsPossibleToUnset(self):
    """Make sure that it is possible to remove user id"""
    user_id, login, password = self._makePerson()
    acl_user, = self.portal.acl_users.searchUsers(id=user_id, exact_match=True)
    person = self.portal.restrictedTraverse(acl_user['path'])
    person.setUserId(None)
    self.tic()
    self.assertEqual(None, person.Person_getUserId())

  def test_duplicatePersonUserId(self):
    user_id, _, _ = self._makePerson()
    self.assertRaises(ValidationFailed, self._makePerson, user_id=user_id)

  def test_duplicateLoginReference(self):
    _, login1, _ = self._makePerson()
    _, login2, _ = self._makePerson()
    pas_user2, = self.portal.acl_users.searchUsers(login=login2, exact_match=True)
    pas_login2, = pas_user2['login_list']
    login2_value = self.portal.restrictedTraverse(pas_login2['path'])
    login2_value.invalidate()
    login2_value.setReference(login1)
    self.commit()
    self.assertRaises(ValidationFailed, login2_value.validate)
    self.assertRaises(ValidationFailed, self.portal.portal_workflow.doActionFor, login2_value, 'validate_action')

  def _duplicateLoginReference(self, commit):
    _, login1, _ = self._makePerson(tic=False)
    user_id2, login2, _ = self._makePerson(tic=False)
    if commit:
      self.commit()
    # Note: cannot rely on catalog, on purpose.
    person_value, = [
      x for x in self.portal.person_module.objectValues()
      if x.Person_getUserId() == user_id2
    ]
    login_value, = [
      x for x in person_value.objectValues(portal_type='ERP5 Login')
      if x.getReference() == login2
    ]
    login_value.invalidate()
    login_value.setReference(login1)
    self.portal.portal_workflow.doActionFor(login_value, 'validate_action')
    result = [x for x in self.portal.portal_catalog(portal_type='ERP5 Login') if x.checkConsistency()]
    self.assertEqual(result, [])
    self.tic()
    result = [x for x in self.portal.portal_catalog(portal_type='ERP5 Login') if x.checkConsistency()]
    self.assertEqual(len(result), 2)

  def test_duplicateLoginReferenceInSameTransaction(self):
    self._duplicateLoginReference(False)

  def test_duplicateLoginReferenceInAnotherTransaction(self):
    self._duplicateLoginReference(True)

class TestUserManagementExternalAuthentication(TestUserManagement):
  def getTitle(self):
    """Title of the test."""
    return "ERP5Security: User Management with External Authentication plugin"

  def afterSetUp(self):
    self.user_id_key = 'openAMid'
    # add key authentication PAS plugin
    uf = self.portal.acl_users
    plugin_id = 'erp5_external_authentication_plugin'
    if plugin_id not in uf.objectIds():
      uf.manage_addProduct['ERP5Security'].addERP5ExternalAuthenticationPlugin(
        id=plugin_id, \
        title='ERP5 External Authentication Plugin',\
        user_id_key=self.user_id_key,)

      getattr(uf, plugin_id).manage_activateInterfaces(
        interfaces=['IExtractionPlugin'])
      self.tic()

  def testERP5ExternalAuthenticationPlugin(self):
    """
     Make sure that we can grant security using a ERP5 External Authentication Plugin.
    """

    _, login, _ = self._makePerson()
    pas_user, = self.portal.acl_users.searchUsers(login=login, exact_match=True)
    reference = self.portal.restrictedTraverse(pas_user['path']).getReference()

    base_url = self.portal.absolute_url(relative=1)

    # without key we are Anonymous User so we should be redirected with proper HTML
    # status code to login_form
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    # TODO we should not have redirect but output 403 or 404, because
    # login process should be provided by an external application.
    # self.assertTrue('location' in response.headers.keys())
    # self.assertTrue(response.headers['location'].endswith('login_form'))

    # view front page we should be logged in if we use authentication key
    response = self.publish(base_url, env={self.user_id_key.replace('-', '_').upper(): login})
    self.assertEqual(response.getStatus(), 200)
    self.assertTrue(reference in response.getBody())


class TestLocalRoleManagement(ERP5TypeTestCase):
  """Tests Local Role Management with ERP5Security.

  This test should probably part of ERP5Type ?
  """
  def getTitle(self):
    return "ERP5Security: User Role Management"

  def afterSetUp(self):
    """Called after setup completed.
    """
    self.portal = self.getPortal()
    # create a security configuration script
    skin_folder = self.portal.portal_skins.custom
    if 'ERP5Type_getSecurityCategoryMapping' not in skin_folder.objectIds():
      createZODBPythonScript(
        skin_folder, 'ERP5Type_getSecurityCategoryMapping', '',
        """return ((
          'ERP5Type_getSecurityCategoryFromAssignment',
          context.getPortalObject().getPortalAssignmentBaseCategoryList()
          ),)
        """)
    # configure group, site, function categories
    category_tool = self.getCategoryTool()
    for bc in ['group', 'site', 'function']:
      base_cat = category_tool[bc]
      code = bc[0].upper()
      if base_cat.get('subcat', None) is not None:
        continue
      base_cat.newContent(portal_type='Category',
                          id='subcat',
                          codification="%s1" % code)
      base_cat.newContent(portal_type='Category',
                          id='another_subcat',
                          codification="%s2" % code)
    self.defined_category = "group/subcat\n"\
                            "site/subcat\n"\
                            "function/subcat"
    # any member can add organisations
    self.portal.organisation_module.manage_permission(
            'Add portal content', roles=['Member', 'Manager'], acquire=1)

    self.username = 'usérn@me'
    # create a user and open an assignement
    pers = self.getPersonModule().newContent(portal_type='Person',
                                             user_id=self.username)
    assignment = pers.newContent( portal_type='Assignment',
                                  group='subcat',
                                  site='subcat',
                                  function='subcat' )
    assignment.open()
    pers.newContent(portal_type='ERP5 Login',
                    reference=self.username,
                    password=self.username).validate()
    self.person = pers
    self.tic()

  def beforeTearDown(self):
    """Called before teardown."""
    # clear base categories
    self.person.getParentValue().manage_delObjects([self.person.getId()])
    for bc in ['group', 'site', 'function']:
      base_cat = self.getCategoryTool()[bc]
      base_cat.manage_delObjects(list(base_cat.objectIds()))
    # clear role definitions
    for ti in self.getTypesTool().objectValues():
      ti.manage_delObjects([x.id for x in ti.getRoleInformationList()])
    # clear modules
    for module in self.portal.objectValues():
      if module.getId().endswith('_module'):
        module.manage_delObjects(list(module.objectIds()))
    # commit this
    self.tic()

  def loginAsUser(self, username):
    uf = self.portal.acl_users
    user = uf.getUserById(username).__of__(uf)
    newSecurityManager(None, user)

  def _getTypeInfo(self):
    return self.getTypesTool()['Organisation']

  def _getModuleTypeInfo(self):
    return self.getTypesTool()['Organisation Module']

  def _makeOne(self):
    return self.getOrganisationModule().newContent(portal_type='Organisation')

  def getBusinessTemplateList(self):
    """List of BT to install. """
    return ('erp5_base', 'erp5_web', 'erp5_ingestion', 'erp5_dms', 'erp5_administration')

  def test_RolesManagerInterfaces(self):
    """Tests group manager plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
    from Products.ERP5Security.ERP5RoleManager import ERP5RoleManager
    verifyClass(IRolesPlugin, ERP5RoleManager)

  def testMemberRole(self):
    """Test users have the Member role.
    """
    self.loginAsUser(self.username)
    self.assertTrue('Member' in
            getSecurityManager().getUser().getRolesInContext(self.portal))
    self.assertTrue('Member' in
            getSecurityManager().getUser().getRoles())

  def testSimpleLocalRole(self):
    """Test simple case of setting a role.
    """
    self._getTypeInfo().newContent(portal_type='Role Information',
      role_name='Assignor',
      description='desc.',
      title='an Assignor role for testing',
      role_category=self.defined_category)
    self.loginAsUser(self.username)
    user = getSecurityManager().getUser()

    obj = self._makeOne()
    self.assertEqual(['Assignor'], obj.__ac_local_roles__.get('F1_G1_S1'))
    self.assertTrue('Assignor' in user.getRolesInContext(obj))
    self.assertFalse('Assignee' in user.getRolesInContext(obj))

    # check if assignment change is effective immediately
    self.login()
    res = self.publish(self.portal.absolute_url_path() + \
                       '/Base_viewSecurity?__ac_name=%s&__ac_password=%s' % \
                       (self.username, self.username))
    self.assertEqual([x for x in res.body.splitlines() if x.startswith('-->')],
                     ["--> ['F1_G1_S1']"], res.body)
    assignment = self.person.newContent( portal_type='Assignment',
                                  group='subcat',
                                  site='subcat',
                                  function='another_subcat' )
    assignment.open()
    res = self.publish(self.portal.absolute_url_path() + \
                       '/Base_viewSecurity?__ac_name=%s&__ac_password=%s' % \
                       (self.username, self.username))
    self.assertEqual([x for x in res.body.splitlines() if x.startswith('-->')],
                     ["--> ['F1_G1_S1']", "--> ['F2_G1_S1']"], res.body)
    assignment.setGroup('another_subcat')
    res = self.publish(self.portal.absolute_url_path() + \
                       '/Base_viewSecurity?__ac_name=%s&__ac_password=%s' % \
                       (self.username, self.username))
    self.assertEqual([x for x in res.body.splitlines() if x.startswith('-->')],
                     ["--> ['F1_G1_S1']", "--> ['F2_G2_S1']"], res.body)
    self.abort()

  def testLocalRolesGroupId(self):
    """Assigning a role with local roles group id.
    """
    self.portal.portal_categories.local_role_group.newContent(
      portal_type='Category',
      reference = 'Alternate',
      id = 'Alternate')
    self._getTypeInfo().newContent(portal_type='Role Information',
      role_name='Assignor',
      local_role_group_value=self.portal.portal_categories.local_role_group.Alternate,
      role_category=self.defined_category)

    self.loginAsUser(self.username)
    user = getSecurityManager().getUser()

    obj = self._makeOne()
    self.assertEqual(['Assignor'], obj.__ac_local_roles__.get('F1_G1_S1'))
    self.assertTrue('Assignor' in user.getRolesInContext(obj))
    self.assertEqual({('F1_G1_S1', 'Assignor')},
      obj.__ac_local_roles_group_id_dict__.get('Alternate'))
    self.abort()


  def testDynamicLocalRole(self):
    """Test simple case of setting a dynamic role.
    The site category is not defined explictly the role, and will have the
    current site of the user.
    """
    for role, function in (('Assignee', 'subcat'),
                           ('Assignor', 'another_subcat')):
      self._getTypeInfo().newContent(portal_type='Role Information',
        role_name=role,
        title='an Assignor role for testing',
        role_category_list=('group/subcat', 'function/' + function),
        role_base_category_script_id='ERP5Type_getSecurityCategoryFromAssignment',
        role_base_category='site')
    self.loginAsUser(self.username)
    user = getSecurityManager().getUser()

    obj = self._makeOne()
    self.assertEqual(['Assignee'], obj.__ac_local_roles__.get('F1_G1_S1'))
    self.assertEqual(['Assignor'], obj.__ac_local_roles__.get('F2_G1_S1'))
    self.assertTrue('Assignee' in user.getRolesInContext(obj))
    self.assertFalse('Assignor' in user.getRolesInContext(obj))
    self.abort()

  def testSeveralFunctionsOnASingleAssignment(self):
    """Test dynamic role generation when an assignment defines several functions
    """
    assignment, = self.portal.portal_catalog(portal_type='Assignment',
                                             parent_reference=self.person.getReference())
    assignment.setFunctionList(('subcat', 'another_subcat'))
    self._getTypeInfo().newContent(portal_type='Role Information',
      role_name='Assignee',
      title='an Assignor role for testing',
      role_category_list=('group/subcat', 'site/subcat'),
      role_base_category_script_id='ERP5Type_getSecurityCategoryFromAssignment',
      role_base_category='function')
    self.loginAsUser(self.username)
    user = getSecurityManager().getUser()

    obj = self._makeOne()
    self.assertEqual(['Assignee'], obj.__ac_local_roles__.get('F1_G1_S1'))
    self.assertEqual(['Assignee'], obj.__ac_local_roles__.get('F2_G1_S1'))
    self.assertTrue('Assignee' in user.getRolesInContext(obj))
    self.assertFalse('Assignor' in user.getRolesInContext(obj))
    self.abort()

  def testAcquireLocalRoles(self):
    """Tests that document does not acquire loal roles from their parents if
    "acquire local roles" is not checked."""
    ti = self._getTypeInfo()
    ti.acquire_local_roles = False
    self._getModuleTypeInfo().newContent(portal_type='Role Information',
      role_name='Assignor',
      description='desc.',
      title='an Assignor role for testing',
      role_category=self.defined_category,
      role_base_category_script_id='ERP5Type_getSecurityCategoryFromAssignment')
    obj = self._makeOne()
    module = obj.getParentValue()
    module.updateLocalRolesOnSecurityGroups()
    # we said the we do not want acquire local roles.
    self.assertFalse(obj._getAcquireLocalRoles())
    # the local role is set on the module
    self.assertEqual(['Assignor'], module.__ac_local_roles__.get('F1_G1_S1'))
    # but not on the document
    self.assertEqual(None, obj.__ac_local_roles__.get('F1_G1_S1'))
    # same testing with roles in context.
    self.loginAsUser(self.username)
    self.assertTrue('Assignor' in
            getSecurityManager().getUser().getRolesInContext(module))
    self.assertFalse('Assignor' in
            getSecurityManager().getUser().getRolesInContext(obj))

  def testLocalRoleWithTraverser(self):
    """Make sure that local role works correctly when traversing
    """
    self.assert_(not self.portal.portal_types.Person.acquire_local_roles)

    self.getPersonModule().newContent(portal_type='Person',
                                      id='first_last',
                                      first_name='First',
                                      last_name='Last')
    loginable_person = self.getPersonModule().newContent(portal_type='Person',
                                                         user_id='guest',
                                                         password='guest')
    assignment = loginable_person.newContent(portal_type='Assignment',
                                             function='another_subcat')
    assignment.open()
    loginable_person.newContent(portal_type='ERP5 Login',
                                reference='guest',
                                password='guest').validate()
    self.tic()

    person_module_type_information = self.getTypesTool()['Person Module']
    person_module_type_information.newContent(portal_type='Role Information',
      role_name='Auditor',
      description='',
      title='An Auditor role for testing',
      role_category='function/another_subcat')
    person_module_type_information.updateRoleMapping()
    self.tic()

    person_module_path = self.getPersonModule().absolute_url(relative=1)
    response = self.publish(person_module_path,
                            basic='guest:guest')
    self.assertEqual(response.getStatus(), 200)
    response = self.publish('/%s/first_last/getFirstName' % person_module_path,
                            basic='guest:guest')
    self.assertEqual(response.getStatus(), 401)

    # Organisation does not have explicitly declared getTitle method in
    # the class definition.
    # Add organisation and make sure guest cannot access to its getTitle.
    self.getOrganisationModule().newContent(portal_type='Organisation',
                                            id='my_company',
                                            title='Nexedi')
    self.tic()
    response = self.publish('/%s/my_company/getTitle' % self.getOrganisationModule().absolute_url(relative=1),
                            basic='guest:guest')
    self.assertEqual(response.getStatus(), 401)

  def testKeyAuthentication(self):
    """
     Make sure that we can grant security using a key.
    """
    # add key authentication PAS plugin
    portal = self.portal
    uf = portal.acl_users
    uf.manage_addProduct['ERP5Security'].addERP5KeyAuthPlugin(
         id="erp5_auth_key", \
         title="ERP5 Auth key",\
         encryption_key='fdgfhkfjhltylutyu',
         cookie_name='__key',\
         default_cookie_name='__ac')

    erp5_auth_key_plugin = getattr(uf, "erp5_auth_key")
    erp5_auth_key_plugin.manage_activateInterfaces(
       interfaces=['IExtractionPlugin',
                   'IAuthenticationPlugin',
                   'ICredentialsUpdatePlugin',
                   'ICredentialsResetPlugin'])
    self.tic()

    reference = 'UserReferenceTextWhichShouldBeHardToGeneratedInAnyHumanOrComputerLanguage'
    loginable_person = self.getPersonModule().newContent(portal_type='Person',
                                                         reference=reference)
    assignment = loginable_person.newContent(portal_type='Assignment',
                                             function='another_subcat')
    assignment.open()
    loginable_person.newContent(portal_type='ERP5 Login',
                                reference=reference,
                                password='guest').validate()
    portal_types = portal.portal_types
    for portal_type in ('Person Module', 'Person', 'Web Site Module', 'Web Site',
                        'Web Page'):
      type_information = portal_types[portal_type]
      type_information.newContent(
        portal_type='Role Information',
        role_name=('Auditor', 'Assignee'),
        role_category='function/another_subcat')
      type_information.updateRoleMapping()
    self.tic()

    # encrypt & decrypt works
    key = erp5_auth_key_plugin.encrypt(reference)
    self.assertNotEquals(reference, key)
    self.assertEqual(reference, erp5_auth_key_plugin.decrypt(key))
    base_url = portal.absolute_url(relative=1)

    # without key we are Anonymous User so we should be redirected with proper HTML
    # status code to login_form
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    self.assertTrue('location' in response.headers.keys())
    self.assertTrue(response.headers['location'].endswith('login_form'))

    # view front page we should be logged in if we use authentication key
    response = self.publish('%s?__ac_key=%s' %(base_url, key))
    self.assertEqual(response.getStatus(), 200)
    self.assertTrue(reference in response.getBody())

    # check if key authentication works other page than front page
    person_module = portal.person_module
    base_url = person_module.absolute_url(relative=1)
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    self.assertTrue('location' in response.headers.keys())
    self.assertTrue('%s/login_form?came_from=' % portal.getId(), response.headers['location'])
    response = self.publish('%s?__ac_key=%s' %(base_url, key))
    self.assertEqual(response.getStatus(), 200)
    self.assertTrue(reference in response.getBody())

    # check if key authentication works with web_mode too
    web_site = portal.web_site_module.newContent(portal_type='Web Site')
    web_page = portal.web_page_module.newContent(portal_type='Web Page', reference='ref')
    web_page.release()
    self.tic()
    base_url = web_site.absolute_url(relative=1)
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    self.assertTrue('location' in response.headers.keys())
    self.assertTrue('%s/login_form?came_from=' % portal.getId(), response.headers['location'])
    # web site access
    response = self.publish('%s?__ac_key=%s' %(base_url, key))
    self.assertEqual(response.getStatus(), 200)
    # web page access by path
    response = self.publish('%s/%s?__ac_key=%s' %(base_url, web_page.getRelativeUrl(),
                                                  key))
    self.assertEqual(response.getStatus(), 200)
    # web page access by reference
    response = self.publish('%s/%s?__ac_key=%s' %(base_url, web_page.getReference(),
                                                  key))
    self.assertEqual(response.getStatus(), 200)
    response = self.publish('%s/%s?__ac_name=%s&__ac_password=%s' % (
      base_url, web_page.getReference(), reference, 'guest'))
    self.assertEqual(response.getStatus(), 200)
    response = self.publish('%s/%s?__ac_name=%s&__ac_password=%s' % (
      base_url, web_page.getReference(), 'ERP5TypeTestCase', ''))
    self.assertEqual(response.getStatus(), 200)

  def _createZodbUser(self, login, role_list=None):
    if role_list is None:
      role_list = ['Member', 'Assignee', 'Assignor', 'Author', 'Auditor',
          'Associate']
    uf = self.portal.acl_users
    uf._doAddUser(login, '', role_list, [])

  def test_owner_local_role_on_clone(self):
    # check that tested stuff is ok
    parent_type = 'Person'
    self.assertEqual(self.portal.portal_types[parent_type].acquire_local_roles, 0)

    original_owner_id = 'original_user' + self.id()
    cloning_owner_id = 'cloning_user' + self.id()
    self._createZodbUser(original_owner_id)
    self._createZodbUser(cloning_owner_id)
    self.commit()
    module = self.portal.getDefaultModule(portal_type=parent_type)
    self.loginByUserName(original_owner_id)
    document = module.newContent(portal_type=parent_type)
    self.tic()
    self.loginByUserName(cloning_owner_id)
    cloned_document = document.Base_createCloneDocument(batch_mode=1)
    self.tic()
    self.login()
    # real assertions
    # roles on original document
    self.assertEqual(
        document.get_local_roles(),
        (((original_owner_id), ('Owner',)),)
    )

    # roles on cloned document
    self.assertEqual(
        cloned_document.get_local_roles(),
        (((cloning_owner_id), ('Owner',)),)
    )

  def test_owner_local_role_on_clone_with_subobjects(self):
    # check that tested stuff is ok
    parent_type = 'Person'
    acquiring_type = 'Email'
    self.assertEqual(self.portal.portal_types[acquiring_type].acquire_local_roles, 1)
    self.assertEqual(self.portal.portal_types[parent_type].acquire_local_roles, 0)

    original_owner_id = 'original_user' + self.id()
    cloning_owner_id = 'cloning_user' + self.id()
    self._createZodbUser(original_owner_id)
    self._createZodbUser(cloning_owner_id)
    self.commit()
    module = self.portal.getDefaultModule(portal_type=parent_type)
    self.loginByUserName(original_owner_id)
    document = module.newContent(portal_type=parent_type)
    subdocument = document.newContent(portal_type=acquiring_type)
    self.tic()
    self.loginByUserName(cloning_owner_id)
    cloned_document = document.Base_createCloneDocument(batch_mode=1)
    self.tic()
    self.login()
    self.assertEqual(1, len(document.contentValues()))
    self.assertEqual(1, len(cloned_document.contentValues()))
    cloned_subdocument = cloned_document.contentValues()[0]
    # real assertions
    # roles on original documents
    self.assertEqual(
        document.get_local_roles(),
        (((original_owner_id), ('Owner',)),)
    )
    self.assertEqual(
        subdocument.get_local_roles(),
        (((original_owner_id), ('Owner',)),)
    )

    # roles on cloned original documents
    self.assertEqual(
        cloned_document.get_local_roles(),
        (((cloning_owner_id), ('Owner',)),)
    )
    self.assertEqual(
        cloned_subdocument.get_local_roles(),
        (((cloning_owner_id), ('Owner',)),)
    )

  def _checkMessageMethodIdList(self, expected_method_id_list):
    actual_method_id_list = sorted([
        message.method_id
        for message in self.portal.portal_activities.getMessageList()
    ])
    self.assertEqual(expected_method_id_list, actual_method_id_list)

  def test_reindexObjectSecurity_on_modules(self):
    person_module = self.portal.person_module
    portal_activities = self.portal.portal_activities
    check = self._checkMessageMethodIdList

    check([])
    # We need at least one person for this test.
    self.assertTrue(len(person_module.keys()))
    # When we update security of a module...
    person_module.reindexObjectSecurity()
    self.commit()
    # we don't want all underlying objects to be recursively
    # reindexed. After all, its contents do not acquire local roles.
    check(['immediateReindexObject'])
    self.tic()
    check([])
    # But non-module objects, with subobjects that acquire local
    # roles, should reindex their security recursively:
    person, = [rec.getObject()
               for rec in person_module.searchFolder(user_id=self.username)]
    self.assertTrue(len(person.objectIds()))
    person.reindexObjectSecurity()
    self.commit()
    # One reindexation activity per subobject, and one on the person itself.
    check(['immediateReindexObject'] * (len(person) + 1))
    self.tic()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestUserManagement))
  suite.addTest(unittest.makeSuite(TestUserManagementExternalAuthentication))
  suite.addTest(unittest.makeSuite(TestLocalRoleManagement))
  return suite
