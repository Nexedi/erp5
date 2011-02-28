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

import unittest
import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from zLOG import LOG
from Products.PluggableAuthService import PluggableAuthService
from zope.interface.verify import verifyClass
from DateTime import DateTime

class TestUserManagement(ERP5TypeTestCase):
  """Tests User Management in ERP5Security.
  """

  def getTitle(self):
    """Title of the test."""
    return "ERP5Security: User Management"

  def getBusinessTemplateList(self):
    """List of BT to install. """
    return ('erp5_base',)

  def beforeTearDown(self):
    """Clears person module and invalidate caches when tests are finished."""
    self.getPersonModule().manage_delObjects([x for x in
                             self.getPersonModule().objectIds()])
    transaction.commit()
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
    self.failUnless(isinstance(self.getUserFolder(),
        PluggableAuthService.PluggableAuthService))

  def loginAsUser(self, username):
    uf = self.portal.acl_users
    user = uf.getUserById(username).__of__(uf)
    newSecurityManager(None, user)

  def _makePerson(self, open_assignment=1, assignment_start_date=None,
                  assignment_stop_date=None, **kw):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', **kw)
    assignment = new_person.newContent(portal_type = 'Assignment',
                                       start_date=assignment_start_date,
                                       stop_date=assignment_stop_date,)
    if open_assignment:
      assignment.open()
    transaction.commit()
    self.tic()
    return new_person

  def _assertUserExists(self, login, password):
    """Checks that a user with login and password exists and can log in to the
    system.
    """
    from Products.PluggableAuthService.interfaces.plugins import\
                                                      IAuthenticationPlugin
    uf = self.getUserFolder()
    self.assertNotEquals(uf.getUserById(login, None), None)
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

  def test_PersonWithLoginPasswordAreUsers(self):
    """Tests a person with a login & password is a valid user."""
    p = self._makePerson(reference='the_user', password='secret',)
    self._assertUserExists('the_user', 'secret')

  def test_PersonLoginCaseSensitive(self):
    """Login/password are case sensitive."""
    p = self._makePerson(reference='the_user', password='secret',)
    self._assertUserExists('the_user', 'secret')
    self._assertUserDoesNotExists('the_User', 'secret')

  def test_PersonLoginIsNotStripped(self):
    """Make sure 'foo ', ' foo' and ' foo ' do not match user 'foo'. """
    p = self._makePerson(reference='foo', password='secret',)
    self._assertUserExists('foo', 'secret')
    self._assertUserDoesNotExists('foo ', 'secret')
    self._assertUserDoesNotExists(' foo', 'secret')
    self._assertUserDoesNotExists(' foo ', 'secret')

  def test_PersonLoginCannotBeComposed(self):
    """Make sure ZSQLCatalog keywords cannot be used at login time"""
    p = self._makePerson(reference='foo', password='secret',)
    self._assertUserExists('foo', 'secret')
    self._assertUserDoesNotExists('bar', 'secret')
    self._assertUserDoesNotExists('bar OR foo', 'secret')

  def test_PersonLoginQuote(self):
    p = self._makePerson(reference="'", password='secret',)
    self._assertUserExists("'", 'secret')

  def test_PersonLogin_OR_Keyword(self):
    p = self._makePerson(reference='foo OR bar', password='secret',)
    self._assertUserExists('foo OR bar', 'secret')
    self._assertUserDoesNotExists('foo', 'secret')

  def test_PersonLoginCatalogKeyWord(self):
    # use something that would turn the username in a ZSQLCatalog catalog keyword
    p = self._makePerson(reference="foo%", password='secret',)
    self._assertUserExists("foo%", 'secret')
    self._assertUserDoesNotExists("foo", 'secret')
    self._assertUserDoesNotExists("foobar", 'secret')

  def test_PersonLoginNGT(self):
    p = self._makePerson(reference='< foo', password='secret',)
    self._assertUserExists('< foo', 'secret')

  def test_PersonLoginNonAscii(self):
    """Login can contain non ascii chars."""
    p = self._makePerson(reference='j\xc3\xa9', password='secret',)
    self._assertUserExists('j\xc3\xa9', 'secret')

  def test_PersonWithLoginWithEmptyPasswordAreNotUsers(self):
    """Tests a person with a login but no password is not a valid user."""
    self._makePerson(reference='the_user')
    self._assertUserDoesNotExists('the_user', None)
    self._makePerson(reference='another_user', password='',)
    self._assertUserDoesNotExists('another_user', '')

  def test_PersonWithEmptyLoginAreNotUsers(self):
    """Tests a person with empty login & password is a valid user."""
    self._makePerson(reference='', password='secret')
    self._assertUserDoesNotExists('', 'secret')

  def test_PersonWithLoginWithNotAssignmentAreNotUsers(self):
    """Tests a person with a login & password and no assignment open is not a valid user."""
    self._makePerson(reference='the_user', password='secret', open_assignment=0)
    self._assertUserDoesNotExists('the_user', 'secret')

  def test_PersonWithSuperUserLoginCannotBeCreated(self):
    """Tests one cannot create person with the "super user" special login."""
    from Products.ERP5Security.ERP5UserManager import SUPER_USER
    self.assertRaises(RuntimeError, self._makePerson, reference=SUPER_USER)

  def test_PersonWithSuperUserLogin(self):
    """Tests one cannot use the "super user" special login."""
    from Products.ERP5Security.ERP5UserManager import SUPER_USER
    self._assertUserDoesNotExists(SUPER_USER, '')

  def test_searchUsers(self):
    p1 = self._makePerson(reference='person1')
    p2 = self._makePerson(reference='person2')
    self.assertEquals(set(['person1', 'person2']),
      set([x['userid'] for x in
        self.portal.acl_users.searchUsers(id='person')]))

  def test_searchUsersExactMatch(self):
    p = self._makePerson(reference='person')
    p1 = self._makePerson(reference='person1')
    p2 = self._makePerson(reference='person2')
    self.assertEquals(['person', ],
         [x['userid'] for x in
           self.portal.acl_users.searchUsers(id='person', exact_match=True)])

  def test_MultiplePersonReference(self):
    """Tests that it's refused to create two Persons with same reference."""
    self._makePerson(reference='new_person')
    self.assertRaises(RuntimeError, self._makePerson, reference='new_person')

  def test_MultiplePersonReferenceWithoutCommit(self):
    """
    Tests that it's refused to create two Persons with same reference.
    Check if both persons are created in the same transaction
    """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', reference='new_person')
    self.assertRaises(RuntimeError, person_module.newContent,
                     portal_type='Person', reference='new_person')

  def test_MultiplePersonReferenceWithoutTic(self):
    """
    Tests that it's refused to create two Persons with same reference.
    Check if both persons are created in 2 different transactions.
    """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', reference='new_person')
    transaction.commit()
    self.assertRaises(RuntimeError, person_module.newContent,
                     portal_type='Person', reference='new_person')

  def test_MultiplePersonReferenceConcurrentTransaction(self):
    """
    Tests that it's refused to create two Persons with same reference.
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
                       portal_type='Person', reference='new_person')
    finally:
      Base.serialize = Base.serialize_call

  def test_PersonCopyAndPaste(self):
    """If we copy and paste a person, login must not be copyied."""
    person = self._makePerson(reference='new_person')
    person_module = self.getPersonModule()
    copy_data = person_module.manage_copyObjects([person.getId()])
    changed, = person_module.manage_pasteObjects(copy_data)
    self.assertNotEquals(person_module[changed['new_id']].getReference(),
                         person_module[changed['id']].getReference())

  def test_PreferenceTool_setNewPassword(self):
    # Preference Tool has an action to change password
    pers = self._makePerson(reference='the_user', password='secret',)
    transaction.commit()
    self.tic()
    self._assertUserExists('the_user', 'secret')
    self.loginAsUser('the_user')
    self.portal.REQUEST.set('current_password', 'secret')
    self.portal.REQUEST.set('new_password', 'new_secret')
    self.portal.portal_preferences.PreferenceTool_setNewPassword()
    self._assertUserExists('the_user', 'new_secret')
    self._assertUserDoesNotExists('the_user', 'secret')

    # password is not stored in plain text
    self.assertNotEquals('new_secret', pers.getPassword())


  def test_OpenningAssignmentClearCache(self):
    """Openning an assignment for a person clear the cache automatically."""
    pers = self._makePerson(reference='the_user', password='secret',
                            open_assignment=0)
    self._assertUserDoesNotExists('the_user', 'secret')
    assi = pers.newContent(portal_type='Assignment')
    assi.open()
    self._assertUserExists('the_user', 'secret')
    assi.close()
    self._assertUserDoesNotExists('the_user', 'secret')

  def test_PersonNotIndexedNotCached(self):
    pers = self._makePerson(password='secret',)
    pers.setReference('the_user')
    # not indexed yet
    self._assertUserDoesNotExists('the_user', 'secret')

    transaction.commit()
    self.tic()

    self._assertUserExists('the_user', 'secret')

  def test_PersonNotValidNotCached(self):
    pers = self._makePerson(reference='the_user', password='other',)
    self._assertUserDoesNotExists('the_user', 'secret')
    pers.setPassword('secret')
    self._assertUserExists('the_user', 'secret')


  def test_AssignmentWithDate(self):
    """Tests a person with an assignment with correct date is a valid user."""
    date = DateTime()
    p = self._makePerson(reference='the_user', password='secret',
                         assignment_start_date=date-5,
                         assignment_stop_date=date+5)
    self._assertUserExists('the_user', 'secret')

  def test_AssignmentWithBadStartDate(self):
    """Tests a person with an assignment with bad start date is not a valid user."""
    date = DateTime()
    p = self._makePerson(reference='the_user', password='secret',
                         assignment_start_date=date+1,
                         assignment_stop_date=date+5)
    self._assertUserDoesNotExists('the_user', 'secret')

  def test_AssignmentWithBadStopDate(self):
    """Tests a person with an assignment with bad stop date is not a valid user."""
    date = DateTime()
    p = self._makePerson(reference='the_user', password='secret',
                         assignment_start_date=date-5,
                         assignment_stop_date=date-1)
    self._assertUserDoesNotExists('the_user', 'secret')

  def test_DeletedPersonIsNotUser(self):
    p = self._makePerson(reference='the_user', password='secret')
    self._assertUserExists('the_user', 'secret')

    p.delete()
    transaction.commit()

    self._assertUserDoesNotExists('the_user', 'secret')

  def test_ReallyDeletedPersonIsNotUser(self):
    p = self._makePerson(reference='the_user', password='secret')
    self._assertUserExists('the_user', 'secret')

    p.getParentValue().deleteContent(p.getId())
    transaction.commit()

    self._assertUserDoesNotExists('the_user', 'secret')

  def test_InvalidatedPersonIsUser(self):
    p = self._makePerson(reference='the_user', password='secret')
    self._assertUserExists('the_user', 'secret')

    p.validate()
    p.invalidate()
    transaction.commit()

    self._assertUserExists('the_user', 'secret')

  def test_PersonLoginIsPossibleToUnset(self):
    """Make sure that it is possible to remove reference"""
    person = self._makePerson(reference='foo', password='secret',)
    person.setReference(None)
    transaction.commit()
    self.tic()
    self.assertEqual(None, person.getReference())

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
    # configure group, site, function categories
    for bc in ['group', 'site', 'function']:
      base_cat = self.getCategoryTool()[bc]
      code = bc[0].upper()
      base_cat.newContent(portal_type='Category',
                          id='subcat',
                          codification="%s1" % code)
    # add another function subcategory.
    self.getCategoryTool()['function'].newContent(portal_type='Category',
                                                  id='another_subcat',
                                                  codification='F2')
    self.defined_category = "group/subcat\n"\
                            "site/subcat\n"\
                            "function/subcat"
    # any member can add organisations
    self.portal.organisation_module.manage_permission(
            'Add portal content', roles=['Member', 'Manager'], acquire=1)

    self.username = 'usérn@me'
    # create a user and open an assignement
    pers = self.getPersonModule().newContent(portal_type='Person',
                                             reference=self.username,
                                             password=self.username)
    assignment = pers.newContent( portal_type='Assignment',
                                  group='subcat',
                                  site='subcat',
                                  function='subcat' )
    assignment.open()
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    """Called before teardown."""
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
    transaction.commit()
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
    return ('erp5_base', 'erp5_web', 'erp5_ingestion', 'erp5_dms',)

  def test_RolesManagerInterfaces(self):
    """Tests group manager plugin respects interfaces."""
    from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
    from Products.ERP5Security.ERP5RoleManager import ERP5RoleManager
    verifyClass(IRolesPlugin, ERP5RoleManager)

  def testMemberRole(self):
    """Test users have the Member role.
    """
    self.loginAsUser(self.username)
    self.failUnless('Member' in
            getSecurityManager().getUser().getRolesInContext(self.portal))
    self.failUnless('Member' in
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
    transaction.abort()

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
    transaction.abort()

  def testSeveralFunctionsOnASingleAssignment(self):
    """Test dynamic role generation when an assignment defines several functions
    """
    assignment, = self.portal.portal_catalog(portal_type='Assignment',
                                             parent_reference=self.username)
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
    transaction.abort()

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
    self.failIf(obj._getAcquireLocalRoles())
    # the local role is set on the module
    self.assertEquals(['Assignor'], module.__ac_local_roles__.get('F1_G1_S1'))
    # but not on the document
    self.assertEquals(None, obj.__ac_local_roles__.get('F1_G1_S1'))
    # same testing with roles in context.
    self.loginAsUser(self.username)
    self.failUnless('Assignor' in
            getSecurityManager().getUser().getRolesInContext(module))
    self.failIf('Assignor' in
            getSecurityManager().getUser().getRolesInContext(obj))

  def testGetUserByLogin(self):
    """Test getUserByLogin method
    """
    self.loginAsUser(self.username)

    # getUserByLogin accept login as a string
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    person_list = self.portal.acl_users.erp5_users.getUserByLogin(self.username)
    self.assertEquals(1, len(person_list))
    self.assertEquals(self.username, person_list[0].getReference())

    # getUserByLogin accept login as a list
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    person_list = self.portal.acl_users.erp5_users.getUserByLogin([self.username])
    self.assertEquals(1, len(person_list))
    self.assertEquals(self.username, person_list[0].getReference())

    # getUserByLogin accept login as a tuple
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    person_list = self.portal.acl_users.erp5_users.getUserByLogin((self.username,))
    self.assertEquals(1, len(person_list))
    self.assertEquals(self.username, person_list[0].getReference())

    # PreferenceTool pass a user as parameter
    user = getSecurityManager().getUser()
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    person_list = self.portal.acl_users.erp5_users.getUserByLogin(user)
    self.assertEquals(1, len(person_list))
    self.assertEquals(self.username, person_list[0].getReference())

  def testLocalRoleWithTraverser(self):
    """Make sure that local role works correctly when traversing
    """
    self.assert_(not self.portal.portal_types.Person.acquire_local_roles)

    self.getPersonModule().newContent(portal_type='Person',
                                      id='first_last',
                                      first_name='First',
                                      last_name='Last')
    loginable_person = self.getPersonModule().newContent(portal_type='Person',
                                                         reference='guest',
                                                         password='guest')
    assignment = loginable_person.newContent(portal_type='Assignment',
                                             function='another_subcat')
    assignment.open()
    transaction.commit()
    self.tic()

    person_module_type_information = self.getTypesTool()['Person Module']
    person_module_type_information.newContent(portal_type='Role Information',
      role_name='Auditor',
      description='',
      title='An Auditor role for testing',
      role_category='function/another_subcat')
    person_module_type_information.updateRoleMapping()
    transaction.commit()
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
    transaction.commit()
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
    self.stepTic()

    reference = 'UserReferenceTextWhichShouldBeHardToGeneratedInAnyHumanOrComputerLanguage'
    loginable_person = self.getPersonModule().newContent(portal_type='Person',
                                                         reference=reference,
                                                         password='guest')
    assignment = loginable_person.newContent(portal_type='Assignment',
                                             function='another_subcat')
    assignment.open()
    portal_types = portal.portal_types
    for portal_type in ('Person Module', 'Person', 'Web Site Module', 'Web Site',
                        'Web Page'):
      type_information = portal_types[portal_type]
      type_information.newContent(
        portal_type='Role Information',
        role_name=('Auditor', 'Assignee'),
        role_category='function/another_subcat')
      type_information.updateRoleMapping()
    self.stepTic()

    # encrypt & decrypt works
    key = erp5_auth_key_plugin.encrypt(reference)
    self.assertNotEquals(reference, key)
    self.assertEquals(reference, erp5_auth_key_plugin.decrypt(key))
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
    self.stepTic()
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

  def testERP5ExternalAuthenticationPlugin(self):
    """
     Make sure that we can grant security using a ERP5 External Authentication Plugin.
    """
    user_id_key = 'openAMid'
    # add key authentication PAS plugin
    portal = self.portal
    uf = portal.acl_users
    uf.manage_addProduct['ERP5Security'].addERP5ExternalAuthenticationPlugin(
      id='erp5_external_authentication_plugin', \
      title='ERP5 External Authentication Plugin',\
      user_id_key=user_id_key,)

    erp5_external_authentication_plugin = getattr(uf, 'erp5_external_authentication_plugin')
    erp5_external_authentication_plugin.manage_activateInterfaces(
      interfaces=['IExtractionPlugin',
                  'IAuthenticationPlugin'])
    self.stepTic()

    reference = 'external_auth_person'
    loginable_person = self.getPersonModule().newContent(portal_type='Person',
                                                         reference=reference,
                                                         password='guest')
    assignment = loginable_person.newContent(portal_type='Assignment',
                                             function='another_subcat')
    assignment.open()
    self.stepTic()

    base_url = portal.absolute_url(relative=1)

    # without key we are Anonymous User so we should be redirected with proper HTML
    # status code to login_form
    response = self.publish(base_url)
    self.assertEqual(response.getStatus(), 302)
    # TODO we should not have redirect but output 403 or 404, because
    # login process should be provided by an external application.
    # self.assertTrue('location' in response.headers.keys())
    # self.assertTrue(response.headers['location'].endswith('login_form'))

    # view front page we should be logged in if we use authentication key
    response = self.publish(base_url, env={user_id_key.replace('-', '_').upper():reference})
    self.assertEqual(response.getStatus(), 200)
    self.assertTrue(reference in response.getBody())

  def _createZodbUser(self, login, role_list=None):
    if role_list is None:
      role_list = ['Member', 'Assignee', 'Assignor', 'Author', 'Auditor',
          'Associate']
    uf = self.portal.acl_users
    uf._doAddUser(login, '', role_list, [])

  def test_owner_local_role_on_clone(self):
    # check that tested stuff is ok
    parent_type = 'Person'
    self.assertEquals(self.portal.portal_types[parent_type].acquire_local_roles, 0)

    original_owner_id = 'original_user' + self.id()
    cloning_owner_id = 'cloning_user' + self.id()
    self._createZodbUser(original_owner_id)
    self._createZodbUser(cloning_owner_id)
    transaction.commit()
    module = self.portal.getDefaultModule(portal_type=parent_type)
    self.login(original_owner_id)
    document = module.newContent(portal_type=parent_type)
    self.stepTic()
    self.login(cloning_owner_id)
    cloned_document = document.Base_createCloneDocument(batch_mode=1)
    self.stepTic()
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
    self.assertEquals(self.portal.portal_types[acquiring_type].acquire_local_roles, 1)
    self.assertEquals(self.portal.portal_types[parent_type].acquire_local_roles, 0)

    original_owner_id = 'original_user' + self.id()
    cloning_owner_id = 'cloning_user' + self.id()
    self._createZodbUser(original_owner_id)
    self._createZodbUser(cloning_owner_id)
    transaction.commit()
    module = self.portal.getDefaultModule(portal_type=parent_type)
    self.login(original_owner_id)
    document = module.newContent(portal_type=parent_type)
    subdocument = document.newContent(portal_type=acquiring_type)
    self.stepTic()
    self.login(cloning_owner_id)
    cloned_document = document.Base_createCloneDocument(batch_mode=1)
    self.stepTic()
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestUserManagement))
  suite.addTest(unittest.makeSuite(TestLocalRoleManagement))
  return suite
