##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Lukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Wizard import addERP5RemoteUserManager
import transaction
import unittest
from Products.ERP5Security.ERP5UserManager import SUPER_USER
from AccessControl.SecurityManagement import getSecurityManager,\
    newSecurityManager
from Products.ERP5Type.Base import Base
from Products.ERP5.ERP5Site import ERP5Site
from Products.ERP5Wizard.Tool.WizardTool import GeneratorCall

# portal_witch simulation
def proxyMethodHandler(self, kw):
  """Dummy proxyMethodHandler"""
  # login as super user
  newSecurityManager(self, self.getPortalObject().acl_users.getUserById(
      SUPER_USER))
  data = getattr(self, kw['method_id'])(**kw['method_kw'])
  response = GeneratorCall(data=data)
  return response.dump()

Base.proxyMethodHandler = proxyMethodHandler
Base.security.declarePublic('proxyMethodHandler')

def Base_authenticateCredentialsFromExpressInstance(self, **kw):
  person_list = self.portal_catalog(portal_type='Person',
    reference=kw['login'])

  if len(person_list) == 1:
    if person_list[0].getTitle() == kw['password']:
      return 1
  return 0

Base.Base_authenticateCredentialsFromExpressInstance =\
    Base_authenticateCredentialsFromExpressInstance
Base.security.declarePublic('Base_authenticateCredentialsFromExpressInstance')

# portal_wizard simulation
def ERP5Site_getExpressInstanceUid(self, **kw):
  """Dummy site it"""
  return 'dummy_site_id'

ERP5Site.ERP5Site_getExpressInstanceUid =\
    ERP5Site_getExpressInstanceUid
ERP5Site.security.declarePublic('ERP5Site_getExpressInstanceUid')


class TestERP5RemoteUserManager(ERP5TypeTestCase):
  """Low level tests of remote logging"""
  def getBusinessTemplateList(self):
    return (
        'erp5_base',
        'erp5_wizard',
        )

  base_type_portal_type = 'Base Type'
  person_portal_type = 'Person'
  system_preference_portal_type = 'System Preference'

  erp5_remote_manager_id = 'erp5_remote_user_manager'
  system_preference_id = 'TestERP5RemoteUserManager'


  def setUpRemoteUserManager(self):
    acl_users = self.portal.acl_users
    addERP5RemoteUserManager(acl_users, self.erp5_remote_manager_id)
    erp5_remote_manager = getattr(acl_users, self.erp5_remote_manager_id)
    erp5_users = getattr(acl_users, 'erp5_users')
    erp5_users.manage_activateInterfaces(['IUserEnumerationPlugin'])
    erp5_remote_manager.manage_activateInterfaces(['IAuthenticationPlugin'])
    transaction.commit()

  def afterSetUp(self):
    self.portal = self.getPortalObject()
    self.createDummyWitchTool()
    self.setUpRemoteUserManager()
    self.person_module = self.portal.person_module
    acl_users = self.portal.acl_users
    self.erp5_remote_manager = getattr(acl_users, self.erp5_remote_manager_id)
    # set preferences before each test, as test suite can have different
    # ip/port after being saved and then loaded
    self.setUpAuthenticationServerPreferences()
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    """Clear everthing"""
    self.portal.acl_users.manage_delObjects(self.erp5_remote_manager_id)
    self.portal.deleteContent('portal_witch')
    self.removeAuthenticationServerPreferences()
    self.portal.portal_caches.clearAllCache()
    transaction.commit()
    self.tic()
    self.person_module.deleteContent(list(self.person_module.objectIds()))
    transaction.commit()
    self.tic()

  def removeAuthenticationServerPreferences(self):
    portal_preferences = self.portal.portal_preferences
    if self.system_preference_id in portal_preferences.objectIds():
      portal_preferences.deleteContent(self.system_preference_id)

  def setUpAuthenticationServerPreferences(self, server_url=None,
      server_root=None):
    if server_url is None:
      server_url = self.portal.absolute_url() + '/'
    if server_root is None:
      self.getPortalId()
    portal_preferences = self.portal.portal_preferences
    # disable all existing system preferences
    system_preference = portal_preferences.newContent(
        portal_type=self.system_preference_portal_type,
        id=self.system_preference_id,
        preferred_witch_tool_server_url=server_url,
        preferred_witch_tool_server_root=server_root,
    )
    system_preference.enable()
    self.assertEqual('global', system_preference.getPreferenceState())
    # clear cache after setting preferences
    self.portal.portal_caches.clearAllCache()

  def createDummyWitchTool(self):
    if 'portal_witch' not in self.portal.objectIds():
      self.portal.newContent(id='portal_witch',
        portal_type=self.base_type_portal_type)

  def createPerson(self, reference, password):
    """Creates person with reference and password in title to simulate remote
    logging"""
    person = self.person_module.newContent(
        portal_type=self.person_portal_type,
        reference=reference, title=password)

  ############################################################################
  # TESTS
  ############################################################################
  def test_correct_login(self):
    login = 'someone'
    password = 'somepass'
    self.createPerson(login, password)
    transaction.commit()
    self.tic()
    kw = {'login':login, 'password': password}
    self.assertEqual(('someone', 'someone'),
        self.erp5_remote_manager.authenticateCredentials(kw))

  def test_incorrect_login(self):
    login = 'someone'
    password = 'somepass'
    self.createPerson(login, password)
    transaction.commit()
    self.tic()
    kw = {'login':login, 'password': 'another_password'}
    self.assertEqual(None,
        self.erp5_remote_manager.authenticateCredentials(kw))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5RemoteUserManager))
  return suite
