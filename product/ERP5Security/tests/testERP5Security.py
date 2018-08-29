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

import mock
import itertools
import transaction
import unittest
import urlparse
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
from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable


AUTO_LOGIN = object()


class UserManagementTestCase(ERP5TypeTestCase):
  """TestCase for user manement, with utilities to create users and helpers
  assertion methods.
  """
  _login_generator = itertools.count().next


  def getBusinessTemplateList(self):
    """List of BT to install. """
    return (
      'erp5_full_text_mroonga_catalog',
      'erp5_core_proxy_field_legacy',
      'erp5_base',
      'erp5_administration',
    )

  def beforeTearDown(self):
    """Clears person module and invalidate caches when tests are finished."""
    transaction.abort()
    self.getPersonModule().manage_delObjects([x for x in
                             self.getPersonModule().objectIds()])
    self.tic()

  def getUserFolder(self):
    """Returns the acl_users. """
    return self.portal.acl_users

  def loginAsUser(self, username):
    uf = self.getUserFolder()
    user = uf.getUserById(username).__of__(uf)
    newSecurityManager(None, user)

  def _makePerson(self, login=AUTO_LOGIN, open_assignment=1, assignment_start_date=None,
                  assignment_stop_date=None, tic=True, password='secret', group_value=None,
                  set_transactional_user=False, **kw):
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
    if set_transactional_user:
      getTransactionalVariable()["transactional_user"] = new_person 
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
    self.assertNotEqual(uf.getUser(login), None)
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
        role_category_list=(
          self.portal.portal_categories.group.dummy_group.getRelativeUrl(),
        ),
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


class RoleManagementTestCaseBase(UserManagementTestCase):
  """Test case with required configuration to test role definitions.
  """
  def afterSetUp(self):
    """Initialize requirements of security configuration.
    """
    super(RoleManagementTestCaseBase, self).afterSetUp()
    # create a security configuration script
    skin_folder = self.portal.portal_skins.custom
    if self._security_configuration_script_id not in skin_folder.objectIds():
      createZODBPythonScript(
        skin_folder,
        self._security_configuration_script_id,
        '',
        self._security_configuration_script_body,
      )
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

  def beforeTearDown(self):
    """Clean up after test.
    """
    # clear base categories
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


class RoleManagementTestCaseOld(RoleManagementTestCaseBase):
  """
  RoleManagementTestCaseBase variant using the deprecated security declaration API.
  """
  _security_configuration_script_id = 'ERP5Type_getSecurityCategoryMapping'
  _security_configuration_script_body = """return ((
  'ERP5Type_getSecurityCategoryFromAssignment',
  context.getPortalObject().getPortalAssignmentBaseCategoryList()
),)"""


class RoleManagementTestCase(RoleManagementTestCaseBase):
  """
  RoleManagementTestCaseBase variant using the current security declaration API.
  """
  _security_configuration_script_id = 'ERP5User_getUserSecurityCategoryValueList'
  _security_configuration_script_body = """return context.ERP5User_getSecurityCategoryValueFromAssignment(
  rule_dict={
    tuple(context.getPortalObject().getPortalAssignmentBaseCategoryList()): ((), )
  },
)"""


class TestUserManagement(UserManagementTestCase):
  """Tests User Management in ERP5Security.
  """
  def test_PersonWithLoginPasswordAreUsers(self):
    """Tests a person with a login & password is a valid user."""
    _, login, password = self._makePerson()
    self._assertUserExists(login, password)

  def test_AnonymousCanCreateUser(self):
    """Anonymous user can create users, as long as the user creation is done
    from a security context which allows it.
    (ie. there should not be interaction workflow raising Unauthorized)
    """
    test_script_id = 'ERP5Site_createTestUser%s' % self.id()
    createZODBPythonScript(
        self.portal.portal_skins.custom,
        test_script_id,
        'login, password',
        '''if 1:
          new_person = context.getPortalObject().person_module.newContent(
              portal_type='Person')
          new_person.newContent(portal_type='Assignment').open()
          new_person.newContent(
              portal_type='ERP5 Login',
              reference=login,
              password=password,
          ).validate()
        ''')
    script = getattr(self.portal, test_script_id)
    script.manage_proxy(('Manager', 'Owner',))
    self.logout()

    login = 'login-%s' % self._login_generator()
    script(login, 'password')
    self.tic()
    self._assertUserExists(login, 'password')

  def test_PersonLoginCaseSensitive(self):
    """Login/password are case sensitive."""
    login = 'case_test_user'
    _, _, password = self._makePerson(login=login)
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists('case_test_User', password)

  def test_PersonLoginIsStripped(self):
    """Make sure 'foo ', ' foo' and ' foo ' match user 'foo'. """
    _, login, password = self._makePerson()
    self._assertUserExists(login, password)
    self._assertUserExists(login + ' ', password)
    self._assertUserExists(' ' + login, password)
    self._assertUserExists(' ' + login + ' ', password)

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

  def test_PersonWithLoginWithNonePasswordAreNotUsers(self):
    """Tests a person with a login but None as a password is not a valid user."""
    # check password set to None at creation
    _, login, _ = self._makePerson(password=None)
    self._assertUserDoesNotExists(login, None)
    self._assertUserDoesNotExists(login, 'None')
    self._assertUserDoesNotExists(login, '')

    # check password set to None after being set
    user_data, = self.portal.acl_users.searchUsers(login=login, exact_match=True)
    erp5_login = self.portal.restrictedTraverse(user_data['login_list'][0]['path'])
    erp5_login.setPassword('secret')
    self.tic()
    self._assertUserExists(login, 'secret')
    erp5_login.setPassword(None)
    self.tic()
    self._assertUserDoesNotExists(login, 'secret')
    self._assertUserDoesNotExists(login, None)
    self._assertUserDoesNotExists(login, 'None')
    self._assertUserDoesNotExists(login, '')

  def test_PersonWithLoginWithEmptyStringPasswordAreNotUsers(self):
    """Tests a person with a login but no password is not a valid user."""
    _, login, _ = self._makePerson(password='')
    self._assertUserDoesNotExists(login, '')
    self._assertUserDoesNotExists(login, 'None')

    # check password set to '' after being set
    user_data, = self.portal.acl_users.searchUsers(login=login, exact_match=True)
    erp5_login = self.portal.restrictedTraverse(user_data['login_list'][0]['path'])
    erp5_login.setPassword('secret')
    self.tic()
    self._assertUserExists(login, 'secret')
    erp5_login.setPassword('')
    self.tic()
    self._assertUserDoesNotExists(login, 'secret')
    self._assertUserDoesNotExists(login, None)
    self._assertUserDoesNotExists(login, 'None')
    self._assertUserDoesNotExists(login, '')

  def test_PersonWithLoginWithoutPasswordAreNotUsers(self):
    """Tests a person with a login but no password set is not a valid user."""
    # similar to _makePerson, but not passing password= to newContent
    login = 'login_%s' % self._login_generator()
    new_person = self.portal.person_module.newContent(portal_type='Person')
    new_person.newContent(portal_type='Assignment').open()
    new_person.newContent(
        portal_type='ERP5 Login',
        reference=login,
    ).validate()
    self.tic()
    self._assertUserDoesNotExists(login, '')
    self._assertUserDoesNotExists(login, 'None')

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

  def test_UnindexedPersonIsNotUser(self):
    user_id, login, password = self._makePerson(tic=False)
    self._assertUserDoesNotExists(login, password)
    self.tic()
    self._assertUserExists(login, password)

  def test_TransactionalPersonWithLoginPasswordAreUsers(self):
    """Tests a person created on same transaction with a login & password
       is a valid user if you set transactional variable."""
    _, login, password = self._makePerson(tic=0, set_transactional_user=True)
    self._assertUserExists(login, password)

  def test_TransactionalPersonLoginCaseSensitive(self):
    """Login/password are case sensitive."""
    login = 'case_test_user'
    _, _, password = self._makePerson(login=login, tic=0, set_transactional_user=True)
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists('case_test_User', password)

  def test_TransactionalPersonLoginNonAscii(self):
    """Login can contain non ascii chars."""
    login = 'j\xc3\xa9'
    _, _, password = self._makePerson(login=login, tic=0, set_transactional_user=True)
    self._assertUserExists(login, password)

  def test_TransactionalPersonWithLoginWithNonePasswordAreNotUsers(self):
    """Tests a person created on same transaction with a login but None as 
      a password is not a valid user."""
    # check password set to None at creation
    _, login, _ = self._makePerson(password=None, tic=0, set_transactional_user=True)
    self._assertUserDoesNotExists(login, None)
    self._assertUserDoesNotExists(login, 'None')
    self._assertUserDoesNotExists(login, '')

  def test_TransactionalPersonWithLoginWithEmptyStringPasswordAreNotUsers(self):
    """Tests a person created on samea transaction with a login but no password 
      is not a valid user."""
    _, login, _ = self._makePerson(password='', tic=0, set_transactional_user=True)
    self._assertUserDoesNotExists(login, '')
    self._assertUserDoesNotExists(login, 'None')

  def test_TransactionalPersonWithLoginWithoutPasswordAreNotUsers(self):
    """Tests a person created on same transaction with a login but 
      no password set is not a valid user."""
    # similar to _makePerson, but not passing password= to newContent
    login = 'login_%s' % self._login_generator()
    new_person = self.portal.person_module.newContent(portal_type='Person')
    new_person.newContent(portal_type='Assignment').open()
    new_person.newContent(
        portal_type='ERP5 Login',
        reference=login,
    ).validate()
    getTransactionalVariable()['transactional_user'] = new_person
    self._assertUserDoesNotExists(login, '')
    self._assertUserDoesNotExists(login, 'None')

  def test_TransactionalOrganisationAreNotUsers(self):
    """Tests a organisation as transactional user fails to login."""
    # similar to _makePerson, but not passing password= to newContent
    login = 'login_%s' % self._login_generator()
    organisation = self.portal.organisation_module.newContent(
      portal_type='Organisation', reference=login)
    getTransactionalVariable()['transactional_user'] = organisation

    # Just to check that fails
    self.assertRaises(AttributeError, self._assertUserDoesNotExists, login, '')

class DuplicatePrevention(UserManagementTestCase):
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
    self.assertNotEqual(
      container[changed['new_id']].Person_getUserId(),
      user_id,
    )

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

  def test_duplicateLoginReference_stripped(self):
    _, login1, _ = self._makePerson()
    _, login2, _ = self._makePerson()
    pas_user2, = self.portal.acl_users.searchUsers(login=login2, exact_match=True)
    pas_login2, = pas_user2['login_list']
    login2_value = self.portal.restrictedTraverse(pas_login2['path'])
    login2_value.invalidate()
    login2_value.setReference(login1 + ' ')
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

  def test_AutoGenerateExistingUserId(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    # Create a state where the next generated user_id is already taken.
    # This test assumes that generated user id are "P%i" % i where i is inscreasing
    self.assertEqual(person.getUserId()[0], 'P')
    latest_user_id = int(person.getUserId()[1:])
    person.setUserId('P%i' % (latest_user_id + 1))
    self.tic()

    # When generating an user id we check this user id already exists
    # and fail if we generate an already existant user id
    self.assertRaisesRegex(
        ValidationFailed,
        'user id P%i already exists' % (latest_user_id + 1),
        self.portal.person_module.newContent,
        portal_type='Person')
    self.abort()

    # This error is not permanent, the id is skipped and next generation should succeed
    self.assertEqual(
        self.portal.person_module.newContent(portal_type='Person').getUserId(),
        'P%i' % (latest_user_id + 2))


class TestPreferences(UserManagementTestCase):

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
    parsed_url = urlparse.urlparse(result)
    self.assertEqual(
        parsed_url.path.split('/')[-2:],
        ['portal_preferences', 'PreferenceTool_viewChangePasswordDialog'])
    self.assertEqual(
        urlparse.parse_qs(parsed_url.query),
        {'portal_status_message': ['Current password is wrong.'], 'portal_status_level': ['error']})

    self.login()
    self._assertUserExists(login, password)
    self._assertUserDoesNotExists(login, new_password)

    self.loginAsUser(user_id)
    result = self.portal.portal_preferences.PreferenceTool_setNewPassword(
      dialog_id='PreferenceTool_viewChangePasswordDialog',
      current_password=password,
      new_password=new_password,
    )
    self.assertEqual(result, self.portal.absolute_url()+'/portal_preferences')

    self.login()
    self._assertUserExists(login, new_password)
    self._assertUserDoesNotExists(login, password)
    # password is not stored in plain text
    self.assertNotEqual(new_password, self.portal.restrictedTraverse(pas_user['path']).getPassword())


class TestAssignmentAndRoles(UserManagementTestCase):
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


class TestPermissionCache(UserManagementTestCase):
  def test_OpenningAssignmentClearCache(self):
    """Openning an assignment for a person clear the cache automatically.

    XXX this works only on a single zope and not on a ZEO cluster.
    """
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


class TestPASAPI(UserManagementTestCase):
  """Test low level PAS API works as expected.
  """
  def test_GroupManagerInterfaces(self):
    """Tests group manager plugin respects interfaces."""
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

  def test_LoginUserManagerInterfaces(self):
    """Tests login user manager plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import\
                IAuthenticationPlugin, IUserEnumerationPlugin
    from Products.ERP5Security.ERP5LoginUserManager import ERP5LoginUserManager
    verifyClass(IAuthenticationPlugin, ERP5LoginUserManager)
    verifyClass(IUserEnumerationPlugin, ERP5LoginUserManager)

  def test_ERP5AccessTokenExtractionPluginInterfaces(self):
    """Tests access token extraction plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import\
                IAuthenticationPlugin, ILoginPasswordHostExtractionPlugin
    from Products.ERP5Security.ERP5AccessTokenExtractionPlugin import\
                ERP5AccessTokenExtractionPlugin
    verifyClass(IAuthenticationPlugin, ERP5AccessTokenExtractionPlugin)
    verifyClass(ILoginPasswordHostExtractionPlugin, ERP5AccessTokenExtractionPlugin)

  def test_ERP5BearerExtractionPluginInterfaces(self):
    """Tests bearer extraction plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import\
                ILoginPasswordHostExtractionPlugin
    from Products.ERP5Security.ERP5BearerExtractionPlugin import\
                ERP5BearerExtractionPlugin
    verifyClass(ILoginPasswordHostExtractionPlugin, ERP5BearerExtractionPlugin)

  def test_ERP5OpenIdConnectExtractionPluginInterfaces(self):
    """Tests openid connect extraction plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import\
                ILoginPasswordHostExtractionPlugin
    from Products.ERP5Security.ERP5ExternalOpenIdConnectExtractionPlugin import\
                ERP5OpenIdConnectExtractionPlugin
    verifyClass(ILoginPasswordHostExtractionPlugin, ERP5OpenIdConnectExtractionPlugin)

  def test_ERP5DumbHTTPExtractionPluginInterfaces(self):
    """Tests dumb HTTP extraction plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import\
                ILoginPasswordHostExtractionPlugin
    from Products.ERP5Security.ERP5DumbHTTPExtractionPlugin import\
                ERP5DumbHTTPExtractionPlugin
    verifyClass(ILoginPasswordHostExtractionPlugin, ERP5DumbHTTPExtractionPlugin)

  def test_RoleManagerInterfaces(self):
    """Tests role manager plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
    from Products.ERP5Security.ERP5RoleManager import ERP5RoleManager
    verifyClass(IRolesPlugin, ERP5RoleManager)

  def test_UserFolder(self):
    """Tests user folder has correct meta type."""
    self.assertTrue(isinstance(self.getUserFolder(),
        PluggableAuthService.PluggableAuthService))

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


class TestMigration(UserManagementTestCase):
  """Tests migration to from login on the person to ERP5 Login documents.
  """
  def _enableERP5UsersPlugin(self):
    """enable the legacy erp5_users plugin"""
    if 'erp5_users' not in self.portal.acl_users:
      self.portal.acl_users.manage_addProduct['ERP5Security'].addERP5UserManager('erp5_users')
    self.portal.acl_users.erp5_users.manage_activateInterfaces([
      'IAuthenticationPlugin',
      'IUserEnumerationPlugin',
    ])

  def _createERP5UserPerson(self, username, password):
    pers = self.portal.person_module.newContent(
      portal_type='Person',
      reference=username,
      user_id=None,
    )
    pers.newContent(
      portal_type='Assignment',
    ).open()
    pers.setPassword(password)
    self.assertEqual(len(pers.objectValues(portal_type='ERP5 Login')), 0)
    self.tic()
    return pers

  def test_PersonLoginMigration(self):
    # migration creates ERP5 Login for person and disable erp5_users plugin at the end.
    self._enableERP5UsersPlugin()
    pers = self._createERP5UserPerson('the_user', 'secret')
    self._assertUserExists('the_user', 'secret')
    person_module_serial = self.portal.person_module._p_serial
    self.portal.portal_templates.fixConsistency(filter={'constraint_type': 'post_upgrade'})
    self.portal.portal_caches.clearAllCache()
    # during migration, old users can still login
    def stop_condition(message_list):
      self._assertUserExists('the_user', 'secret')
      return False
    self.tic(stop_condition=stop_condition)
    # running this migration did not modify person module
    self.assertEqual(self.portal.person_module._p_serial, person_module_serial)
    self._assertUserExists('the_user', 'secret')
    self.assertEqual(pers.getPassword(), None)
    self.assertEqual(pers.Person_getUserId(), 'the_user')
    login = pers.objectValues(portal_type='ERP5 Login')[0]
    login.setPassword('secret2')
    self.portal.portal_caches.clearAllCache()
    self.tic()
    self._assertUserDoesNotExists('the_user', 'secret')
    self._assertUserExists('the_user', 'secret2')
    self.assertNotIn('erp5_users', \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IAuthenticationPlugin)])
    self.assertNotIn('erp5_users', \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IUserEnumerationPlugin)])

  def test_ERP5LoginUserManagerMigration(self):
    # migration creates and activate erp5_login_users plugin
    acl_users= self.portal.acl_users
    acl_users.manage_delObjects(ids=['erp5_login_users'])
    portal_templates = self.portal.portal_templates
    self.assertNotEqual(portal_templates.checkConsistency(filter={'constraint_type': 'post_upgrade'}) , [])
    # call checkConsistency again to check if FIX does not happen by checkConsistency().
    self.assertNotEqual(portal_templates.checkConsistency(filter={'constraint_type': 'post_upgrade'}) , [])
    portal_templates.fixConsistency(filter={'constraint_type': 'post_upgrade'})
    self.assertEqual(portal_templates.checkConsistency(filter={'constraint_type': 'post_upgrade'}) , [])
    self.assertIn('erp5_login_users', \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IAuthenticationPlugin)])
    self.assertIn('erp5_login_users', \
                     [x[0] for x in self.portal.acl_users.plugins.listPlugins(IUserEnumerationPlugin)])

  def test_DuplicateUserIdPreventionDuringMigration(self):
    self._enableERP5UsersPlugin()
    pers = self._createERP5UserPerson('old_user_id', 'secret')
    self.assertRaisesRegex(
        ValidationFailed,
        'user id old_user_id already exists',
        self.portal.person_module.newContent,
        portal_type='Person',
        reference='old_user_id')
    self.abort()

    self.portal.portal_templates.fixConsistency(filter={'constraint_type': 'post_upgrade'})
    self.commit()
    # Sanity check
    self.assertTrue(
      self.portal.portal_activities.countMessage(
        method_id='ERP5Site_disableERP5UserManager',
      ),
    )
    def stop_condition(message_list):
      # Once ERP5Site_disableERP5UserManager has been executed, the unicity
      # constraint on Person.reference disappears (and re-appears on
      # Person.user_id and ERP5User.reference, but this is not what is being
      # tested here). So only check this constraint for as long as that
      # activity is present.
      if any(m.method_id == 'ERP5Site_disableERP5UserManager' for m in message_list):
        self.assertRaisesRegex(
          ValidationFailed,
          'user id old_user_id already exists',
          self.portal.person_module.newContent,
          portal_type='Person',
          reference='old_user_id')
        self.abort()
      return False
    self.tic(stop_condition=stop_condition)
    self.portal.person_module.newContent(portal_type='Person', reference='old_user_id')
    self.assertRaisesRegex(
        ValidationFailed,
        'user id old_user_id already exists',
        self.portal.person_module.newContent,
        portal_type='Person',
        user_id='old_user_id')
    self.abort()

  def test_DuplicateUserIdFromInitUserIdPreventionDuringMigration(self):
    self._enableERP5UsersPlugin()
    self._createERP5UserPerson('P1234', 'secret')

    # mock user id generator to generate a value that was used as reference on that existing person.
    def generateNewId(id_group, id_generator, *args, **kw):
      if id_group == 'user_id' and id_generator == 'non_continuous_integer_increasing':
        return 1234 # this will be 'P%i' and become P1234
      return mock.DEFAULT

    with mock.patch.object(self.portal.portal_ids.__class__, 'generateNewId', side_effect=generateNewId):
      self.assertRaisesRegex(
            ValidationFailed,
            'user id P1234 already exists',
            self.portal.person_module.newContent,
            portal_type='Person',)
      self.abort()

      self.portal.portal_templates.fixConsistency(filter={'constraint_type': 'post_upgrade'})
      def stop_condition(message_list):
        if any(m.method_id != 'immediateReindexObject' for m in message_list):
          self.assertRaisesRegex(
            ValidationFailed,
            'user id P1234 already exists',
            self.portal.person_module.newContent,
            portal_type='Person',)
          self.abort()
        return False
      self.tic(stop_condition=stop_condition)

      self.assertRaisesRegex(
          ValidationFailed,
          'user id P1234 already exists',
          self.portal.person_module.newContent,
          portal_type='Person',)
      self.abort()

  def test_NonMigratedPersonCanBecomeUserLater(self):
    self._enableERP5UsersPlugin()
    non_migrated_person = self.portal.person_module.newContent(
        portal_type='Person',
        user_id=None,
    )
    self.tic()

    self.portal.portal_templates.fixConsistency(filter={'constraint_type': 'post_upgrade'})
    self.tic()
    non_migrated_person.newContent(portal_type='Assignment').open()
    non_migrated_person.newContent(portal_type='ERP5 Login', reference='login', password='password').validate()
    self.tic()
    self._assertUserExists('login', 'password')
    self.assertTrue(non_migrated_person.getUserId())


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
    self.assertIn('Logged In', response.getBody())
    self.assertIn(login, response.getBody())


class _TestLocalRoleManagementMixIn(object):
  """Tests Local Role Management with ERP5Security.

  """
  def getTitle(self):
    return "ERP5Security: User Role Management"

  def afterSetUp(self):
    """Called after setup completed.
    """
    super(_TestLocalRoleManagementMixIn, self).afterSetUp()

    # any member can add organisations
    self.portal.organisation_module.manage_permission(
            'Add portal content', roles=['Member', 'Manager'], acquire=1)

    self.username = 'usérn@me'
    user_list = self.portal.acl_users.getUserById(self.username)
    if not user_list:
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
    else:
      user, = user_list
      pers = user.getUserValue()
    self.person = pers
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

  def _createOrGetObject(self, container, content_id, new_content_kw):
    try:
      return container[content_id]
    except KeyError:
      return container.newContent(
        id=content_id,
        **new_content_kw
      )

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
    self.assertIn('Member',
            getSecurityManager().getUser().getRolesInContext(self.portal))
    self.assertIn('Member',
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
    self.assertIn('Assignor', user.getRolesInContext(obj))
    self.assertNotIn('Assignee', user.getRolesInContext(obj))

    person_value = self.person
    user_id = person_value.getUserId()
    getUserById = self.portal.acl_users.getUserById
    def assertRoleItemsEqual(expected_role_set):
      self.assertCountEqual(getUserById(user_id).getGroups(), expected_role_set)
    # check if assignment change is effective immediately
    assertRoleItemsEqual(['F1_G1_S1'])
    self.login()
    assignment = self.person.newContent( portal_type='Assignment',
                                  group='subcat',
                                  site='subcat',
                                  function='another_subcat' )
    assignment.open()
    assertRoleItemsEqual(['F1_G1_S1', 'F2_G1_S1'])
    assignment.setGroup('another_subcat')
    assertRoleItemsEqual(['F1_G1_S1', 'F2_G1_S1'])
    self.abort()

  def testLocalRolesGroupId(self):
    """Assigning a role with local roles group id.
    """
    self._getTypeInfo().newContent(portal_type='Role Information',
      role_name='Assignor',
      local_role_group_value=self._createOrGetObject(
        container=self.portal.portal_categories.local_role_group,
        content_id='Alternate',
        new_content_kw={
          'portal_type': 'Category',
          'reference': 'Alternate',
        },
      ),
      role_category=self.defined_category)

    self.loginAsUser(self.username)
    user = getSecurityManager().getUser()

    obj = self._makeOne()
    self.assertEqual(['Assignor'], obj.__ac_local_roles__.get('F1_G1_S1'))
    self.assertIn('Assignor', user.getRolesInContext(obj))
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
    self.assertIn('Assignee', user.getRolesInContext(obj))
    self.assertNotIn('Assignor', user.getRolesInContext(obj))
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
    self.assertIn('Assignee', user.getRolesInContext(obj))
    self.assertNotIn('Assignor', user.getRolesInContext(obj))
    self.abort()

  def testAcquireLocalRoles(self):
    """Tests that document does not acquire loal roles from their parents if
    "acquire local roles" is not checked."""
    ti = self._getTypeInfo()
    ti.setTypeAcquireLocalRole(False)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change
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
    self.assertIn('Assignor',
            getSecurityManager().getUser().getRolesInContext(module))
    self.assertNotIn('Assignor',
            getSecurityManager().getUser().getRolesInContext(obj))

  def testLocalRoleWithTraverser(self):
    """Make sure that local role works correctly when traversing
    """
    self.assertTrue(not self.portal.portal_types.Person.acquire_local_roles)

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


class TestLocalRoleManagementOld(_TestLocalRoleManagementMixIn, RoleManagementTestCaseOld):
  pass


class TestLocalRoleManagement(_TestLocalRoleManagementMixIn, RoleManagementTestCase):
  pass


class _TestKeyAuthenticationMixIn(object):
  def getBusinessTemplateList(self):
    """This test also uses web and dms
    """
    return super(_TestKeyAuthenticationMixIn, self).getBusinessTemplateList() + (
        'erp5_core_proxy_field_legacy', # for erp5_web
        'erp5_base', 'erp5_web', 'erp5_ingestion', 'erp5_dms', 'erp5_administration')


  def testKeyAuthentication(self):
    """
     Make sure that we can grant security using a key.
    """
    # add key authentication PAS plugin
    portal = self.portal
    uf = portal.acl_users
    try:
      erp5_auth_key_plugin = getattr(uf, "erp5_auth_key")
    except AttributeError:
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
    self.assertNotEqual(reference, key)
    self.assertEqual(reference, erp5_auth_key_plugin.decrypt(key))
    base_url = portal.absolute_url(relative=1)

    # without key we are Anonymous User so we should be redirected with proper HTML
    # status code to login_form
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    self.assertIn('location', response.headers.keys())
    self.assertTrue(response.headers['location'].endswith('login_form'))

    # view front page we should be logged in if we use authentication key
    response = self.publish('%s?__ac_key=%s' %(base_url, key))
    self.assertEqual(response.getStatus(), 200)
    self.assertIn(reference, response.getBody())

    # check if key authentication works other page than front page
    person_module = portal.person_module
    base_url = person_module.absolute_url(relative=1)
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    self.assertIn('location', response.headers.keys())
    self.assertTrue('%s/login_form?came_from=' % portal.getId(), response.headers['location'])
    response = self.publish('%s?__ac_key=%s' %(base_url, key))
    self.assertEqual(response.getStatus(), 200)
    self.assertIn(reference, response.getBody())

    # check if key authentication works with web_mode too
    web_site = portal.web_site_module.newContent(portal_type='Web Site')
    web_page = portal.web_page_module.newContent(portal_type='Web Page', reference='ref')
    web_page.release()
    self.tic()
    base_url = web_site.absolute_url(relative=1)
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    self.assertIn('location', response.headers.keys())
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
    response = self.publish(
      base_url + '/' + web_page.getReference(),
      basic=reference + ':guest',
    )
    self.assertEqual(response.getStatus(), 200)
    response = self.publish(
      base_url + '/' + web_page.getReference(),
      basic='%s:%s' % (self.manager_username, self.manager_password),
    )
    self.assertEqual(response.getStatus(), 200)


class TestKeyAuthenticationOld(_TestKeyAuthenticationMixIn, RoleManagementTestCaseOld):
  pass


class TestKeyAuthentication(_TestKeyAuthenticationMixIn, RoleManagementTestCase):
  pass


class TestOwnerRole(UserManagementTestCase):
  def _createZodbUser(self, login, role_list=None):
    if role_list is None:
      role_list = ['Member', 'Assignee', 'Assignor', 'Author', 'Auditor',
          'Associate']
    uf = self.portal.acl_users
    uf._doAddUser(login, self.newPassword(), role_list, [])

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


class TestAuthenticationCookie(UserManagementTestCase):
  """Test the authentication cookie.

  Most of this functionality is already tested in testCookieiCrumbler, this
  test uses a fully setup ERP5 site.
  """
  def testCookieAttributes(self):
    """ERP5 sets some cookie attributes
    """
    _, login, password = self._makePerson()
    self.tic()
    request = self.portal.REQUEST
    request.form['__ac_name'] = login
    request.form['__ac_password'] = password
    request['PARENTS'] = [self.portal]
    request.method = request.environ['REQUEST_METHOD'] = 'POST'
    # (the secure flag is only set if we accessed through https)
    request.setServerURL('https', 'example.com')

    request.traverse('/')

    response = request.RESPONSE
    ac_cookie, = [v for (k, v) in response.listHeaders() if k.lower() == 'set-cookie' and '__ac=' in v]
    # Secure flag so that cookie is sent only on https
    self.assertIn('; Secure', ac_cookie)

    # HttpOnly flag so that javascript cannot access cookie
    self.assertIn('; httponly', ac_cookie.lower())

    # SameSite=Lax flag so that cookie is not sent on cross origin requests.
    # We set Lax (and not strict) so that opening a link to ERP5 from an
    # external site does not prompt for login.
    self.assertIn('; SameSite=Lax', ac_cookie)


class TestReindexObjectSecurity(UserManagementTestCase):
  def afterSetUp(self):
    super(TestReindexObjectSecurity, self).afterSetUp()
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
    self.tic()

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


class TestUserCaption(UserManagementTestCase):

  def test_zodb_user(self):
    self.login()
    self.assertEqual(self.portal.Base_getUserCaption(), 'ERP5TypeTestCase')

  def test_anonymous_user(self):
    self.logout()
    self.assertEqual(self.portal.Base_getUserCaption(), 'Anonymous User')

  def test_erp5_login(self):
    user_id, login, _ = self._makePerson()
    self.tic()
    self.login(user_id)
    self.assertEqual(self.portal.Base_getUserCaption(), login)
