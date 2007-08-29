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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase,\
                                                     get_request
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import getSecurityManager
from zLOG import LOG
from Products.ERP5Type.Cache import clearCache
from Products.PluggableAuthService import PluggableAuthService
try:
  from Interface.Verify import verifyClass
except ImportError:
  from zope.interface.verify import verifyClass

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
    # XXX Isn't it better to clear the cache when deleting a Person ?
    clearCache(cache_factory_list=('erp5_content_short', ))
    self.getPersonModule().manage_delObjects([x for x in
                             self.getPersonModule().objectIds()])
    get_transaction().commit()
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

  def _makePerson(self, open_assignment=1, **kw):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', **kw)
    assignment = new_person.newContent(portal_type = 'Assignment')
    if open_assignment:
      assignment.open()
    get_transaction().commit()
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
    self._assertUserDoesNotExists('the_User', 'secret')
  
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
    """Tests a person with a login & password is a valid user."""
    self._makePerson(reference='', password='secret')
    self._assertUserDoesNotExists('', 'secret')
  
  def test_PersonWithLoginWithNotAssignmentAreNotUsers(self):
    """Tests a person with a login & password and no assignment open is not a valid user."""
    self._makePerson(reference='the_user', open_assignment=0)
    self._assertUserDoesNotExists('the_user', None)

  def test_PersonWithSuperUserLoginCannotBeCreated(self):
    """Tests one cannot create person with the "super user" special login."""
    from Products.ERP5Security.ERP5UserManager import SUPER_USER
    self.assertRaises(RuntimeError, self._makePerson, reference=SUPER_USER)
  
  def test_PersonWithSuperUserLogin(self):
    """Tests one cannot use the "super user" special login."""
    from Products.ERP5Security.ERP5UserManager import SUPER_USER
    self._assertUserDoesNotExists(SUPER_USER, '')

  def test_MultiplePersonReference(self):
    """Tests that it's refused to create two Persons with same reference."""
    self._makePerson(reference='new_person')
    self.assertRaises(RuntimeError, self._makePerson, reference='new_person')

  def test_PersonCopyAndPaste(self):
    """If we copy and paste a person, login must not be copyied."""
    person = self._makePerson(reference='new_person')
    person_module = self.getPersonModule()
    copy_data = person_module.manage_copyObjects([person.getId()])
    changed, = person_module.manage_pasteObjects(copy_data)
    self.assertNotEquals(person_module[changed['new_id']].getReference(),
                         person_module[changed['id']].getReference())
  
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
    self.defined_category = "group/subcat\n"\
                            "site/subcat\n"\
                            "function/subcat"
    # any member can add organisations
    self.portal.organisation_module.manage_permission(
            'Add portal content', roles=['Member', 'Manager'], acquire=1)

    self.username = 'username'
    # create a user and open an assignement
    pers = self.getPersonModule().newContent(portal_type='Person',
                                             reference=self.username,
                                             password=self.username)
    assignment = pers.newContent( portal_type='Assignment',
                                  group='subcat',
                                  site='subcat',
                                  function='subcat' )
    assignment.open()
    get_transaction().commit()
    self.tic()
  
  def beforeTearDown(self):
    """Called before teardown."""
    # clear base categories
    for bc in ['group', 'site', 'function']:
      base_cat = self.getCategoryTool()[bc]
      base_cat.manage_delObjects([x for x in base_cat.objectIds()])
    # clear role definitions
    for ti in self.getTypesTool().objectValues(spec=('ERP5 Type Information',)):
      ti._roles = ()
    # clear modules
    for module in self.portal.objectValues(spec=('ERP5 Folder',)):
      module.manage_delObjects([x for x in module.objectIds()])
    # commit this
    get_transaction().commit()
    self.tic()
    # XXX Isn't it better to clear the cache when deleting a Person ?
    clearCache(cache_factory_list=('erp5_content_short', ))

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
    return ('erp5_base',)
  
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
    ti = self._getTypeInfo()
    ti.addRole(id='Assignor', description='desc.',
           name='an Assignor role for testing',
           condition='',
           category=self.defined_category,
           base_category_script='ERP5Type_getSecurityCategoryFromAssignment',
           base_category='')
    obj = self._makeOne()
    self.assertEquals(['Assignor'], obj.__ac_local_roles__.get('F1_G1_S1'))
    
    self.loginAsUser(self.username)
    self.failUnless('Assignor' in
            getSecurityManager().getUser().getRolesInContext(obj))
        
  def testDynamicLocalRole(self):
    """Test simple case of setting a dynamic role.
    The site category is not defined explictly the role, and will have the
    current site of the user.
    """
    ti = self._getTypeInfo()
    ti.addRole(id='Assignor', description='desc.',
           name='an Assignor role for testing',
           condition='',
           category='group/subcat\nfunction/subcat',
           base_category_script='ERP5Type_getSecurityCategoryFromAssignment',
           base_category='site')
    
    self.loginAsUser(self.username)
    obj = self._makeOne()
    self.assertEquals(['Assignor'], obj.__ac_local_roles__.get('F1_G1_S1'))
    self.failUnless('Assignor' in
            getSecurityManager().getUser().getRolesInContext(obj))

  def testAcquireLocalRoles(self):
    """Tests that document does not acquire loal roles from their parents if
    "acquire local roles" is not checked."""
    ti = self._getTypeInfo()
    ti.acquire_local_roles = False
    module_ti = self._getModuleTypeInfo()
    module_ti.addRole(id='Assignor', description='desc.',
           name='an Assignor role for testing',
           condition='',
           category=self.defined_category,
           base_category_script='ERP5Type_getSecurityCategoryFromAssignment',
           base_category='')
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
    
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestUserManagement))
  suite.addTest(unittest.makeSuite(TestLocalRoleManagement))
  return suite

