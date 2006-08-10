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
import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase,\
                                                     get_request
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.Cache import clearCache
from Products.PluggableAuthService import PluggableAuthService
try:
  from Interface.Verify import verifyClass
except ImportError:
  from zope.interface.verify import verifyClass

class TestERP5Security(ERP5TypeTestCase):
  """Test ERP5 Security."""
 
  RUN_ALL_TESTS = 1
  
  def getTitle(self):
    """Title of the test."""
    return "ERP5 Security"
  
  def getBusinessTemplateList(self):
    """List of BT to install. """
    return ('erp5_base',)
  
  def beforeTearDown(self):
    """Clears person module and invalidate caches when tests are finished."""
    clearCache()
    self.getPersonModule().manage_delObjects([x for x in
                             self.getPersonModule().objectIds()])
    get_transaction().commit()
    self.tic()
  
  def login(self, quiet=0, run=1):
    uf = self.getUserFolder()
    uf._doAddUser('alex', '', ['Manager', 'Assignee', 'Assignor',
                               'Associate', 'Auditor', 'Author'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)

  def getUserFolder(self):
    """Returns the acl_users. """
    return self.getPortal().acl_users

  def test_GroupManagerInterfaces(self, run=RUN_ALL_TESTS):
    """Tests group manager plugin respects interfaces."""
    if not run:
      return
    from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
    from Products.ERP5Security.ERP5GroupManager import ERP5GroupManager
    verifyClass(IGroupsPlugin, ERP5GroupManager)

  def test_UserManagerInterfaces(self, run=RUN_ALL_TESTS):
    """Tests user manager plugin respects interfaces."""
    if not run:
      return
    from Products.PluggableAuthService.interfaces.plugins import\
                IAuthenticationPlugin, IUserEnumerationPlugin
    from Products.ERP5Security.ERP5UserManager import ERP5UserManager
    verifyClass(IAuthenticationPlugin, ERP5UserManager)
    verifyClass(IUserEnumerationPlugin, ERP5UserManager)

  def test_RolesManagerInterfaces(self, run=RUN_ALL_TESTS):
    """Tests group manager plugin respects interfaces."""
    if not run:
      return
    from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
    from Products.ERP5Security.ERP5RoleManager import ERP5RoleManager
    verifyClass(IRolesPlugin, ERP5RoleManager)

  def test_UserFolder(self, run=RUN_ALL_TESTS):
    """Tests user folder has correct meta type."""
    if not run:
      return
    self.failUnless(isinstance(self.getUserFolder(),
        PluggableAuthService.PluggableAuthService))

  def _makePerson(self, **kw):
    """Creates a person in person module, and returns the object, after
    indexing is done. """
    person_module = self.getPersonModule()
    new_person = person_module.newContent(
                     portal_type='Person', **kw)
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

  def test_PersonWithLoginPasswordAreUsers(self, run=RUN_ALL_TESTS):
    """Tests a person with a login & password is a valid user."""
    p = self._makePerson(reference='the_user', password='secret',
                        career_role='internal')
    self._assertUserExists('the_user', 'secret')
    
  def test_PersonWithLoginWithEmptyPasswordAreNotUsers(self, run=RUN_ALL_TESTS):
    """Tests a person with a login but no password is not a valid user."""
    self._makePerson(reference='the_user', career_role='internal')
    self._assertUserDoesNotExists('the_user', None)
    self._makePerson(reference='another_user', password='',
                     career_role='internal')
    self._assertUserDoesNotExists('another_user', '')
  
  def test_PersonWithEmptyLoginAreNotUsers(self, run=RUN_ALL_TESTS):
    """Tests a person with a login & password is a valid user."""
    self._makePerson(reference='', password='secret', career_role='internal')
    self._assertUserDoesNotExists('', 'secret')
  
  def test_PersonWithSuperUserLoginCannotBeCreated(self, run=RUN_ALL_TESTS):
    """Tests one cannot create person with the "super user" special login."""
    from Products.ERP5Security.ERP5UserManager import SUPER_USER
    self.assertRaises(RuntimeError, self._makePerson, reference=SUPER_USER)
  
  def test_PersonWithSuperUserLogin(self, run=RUN_ALL_TESTS):
    """Tests one cannot use the "super user" special login."""
    from Products.ERP5Security.ERP5UserManager import SUPER_USER
    self._assertUserDoesNotExists(SUPER_USER, '')

  def test_MultiplePersonReference(self, run=RUN_ALL_TESTS):
    """Tests that it's refused to create two Persons with same reference."""
    self._makePerson(reference='new_person')
    self.assertRaises(RuntimeError, self._makePerson, reference='new_person')

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5Security))
    return suite

