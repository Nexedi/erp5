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

from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.ERP5Site import ERP5Site
from Products import ERP5Security
from Products.ERP5Type.Base import Base
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Wizard import addERP5RemoteUserManager
from Products.ERP5Wizard.Tool.WizardTool import GeneratorCall
import socket
import unittest

# portal_witch simulation
def proxyMethodHandler(self, kw):
  """Dummy proxyMethodHandler"""
  # login as super user
  newSecurityManager(self, self.getPortalObject().acl_users.getUserById(
      ERP5Security.SUPER_USER))
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

# portal_wizard patches
def raises_socket_error(self, *args, **kw):
  raise socket.error

def raises_socket_sslerror(self, *args, **kw):
  raise socket.sslerror

def raises_valueerror(self, *args, **kw):
  raise ValueError

def raises_socket_timeout(self, *args, **kw):
  raise socket.timeout

def raises_socket_gaierror(self, *args, **kw):
  raise socket.gaierror

class TestERP5RemoteUserManager(ERP5TypeTestCase):
  """Low level tests of remote logging"""
  def getBusinessTemplateList(self):
    return (
        'erp5_base',
        'erp5_web_service',
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
    self.erp5_remote_manager = getattr(acl_users, self.erp5_remote_manager_id)
    acl_users.erp5_login_users.manage_activateInterfaces([])
    self.erp5_remote_manager.manage_activateInterfaces(['IAuthenticationPlugin', 'IUserEnumerationPlugin'])
    self.commit()

  def afterSetUp(self):
    self.login = self.id()
    self.password = self.login + 'password'
    self.portal = self.getPortalObject()
    self.createDummyWitchTool()
    self.was_sso_enable = self.portal.portal_wizard.isSingleSignOnEnabled()
    self.setUpRemoteUserManager()
    self.person_module = self.portal.person_module
    acl_users = self.portal.acl_users
    # set preferences before each test, as test suite can have different
    # ip/port after being saved and then loaded
    self.setUpAuthenticationServerPreferences()
    self.tic()

  def beforeTearDown(self):
    """Clear everything"""
    self.portal.acl_users.manage_delObjects(self.erp5_remote_manager_id)
    self.portal.deleteContent('portal_witch')
    self.removeAuthenticationServerPreferences()
    self.tic()

  def removeAuthenticationServerPreferences(self):
    portal_preferences = self.portal.portal_preferences
    if self.system_preference_id in portal_preferences.objectIds():
      portal_preferences.deleteContent(self.system_preference_id)
    self.portal.portal_caches.clearAllCache()

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
    self.person_module.newContent(
        portal_type=self.person_portal_type,
        reference=reference, title=password)

  def checkLogin(self, expected, sent):
    """Helper to check login, clear cache later and commit transaction"""
    self.assertEqual(expected,
        self.erp5_remote_manager.authenticateCredentials(sent))
    self.portal.portal_caches.clearAllCache()

  ############################################################################
  # TESTS
  ############################################################################
  def test_correct_login(self):
    """Checks typical login scenario"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)

  def test_incorrect_login(self):
    """Checks that incorrect login does not work"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': 'another_password'}
    self.checkLogin(None, kw)

  def test_incorrect_login_in_case_of_no_connection(self):
    """Checks that in case if there is no authentication server defined it is not possible to login"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.removeAuthenticationServerPreferences()
    self.tic()
    self.checkLogin(None, kw)

  def test_loggable_in_case_of_server_socket_error(self):
    """Check that in case if socket.error is raised login works from ZODB cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_socket_error
      self.assertRaises(socket.error,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.checkLogin((self.login, self.login), kw)
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_loggable_in_case_of_server_socket_sslerror(self):
    """Check that in case if socket.sslerror is raised login works from ZODB cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_socket_sslerror
      self.assertRaises(socket.sslerror,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.checkLogin((self.login, self.login), kw)
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_not_loggable_in_case_of_server_raises_anything_else(self):
    """Check that in case if non socket is raised login does not works"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_valueerror
      self.assertRaises(ValueError,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.checkLogin(None, kw)
      # assert that ZODB cache is emptied
      self.assertFalse(self.login in \
          self.erp5_remote_manager.remote_authentication_cache)
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_loggable_in_case_of_server_socket_error_with_failed_login_between(
      self):
    """Check that in case if socket.sslerror is raised login works from ZODB cache, when wrong credentials was passed"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_socket_error
      self.assertRaises(socket.error,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.checkLogin((self.login, self.login), kw)
      self.checkLogin(None, {'login':kw['login'], 'password':'wrong_password'})
      self.checkLogin((self.login, self.login), kw)
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_loggable_in_case_of_server_socket_timeout(self):
    """Check that in case if socket.timeout is raised login works from ZODB cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_socket_timeout
      self.assertRaises(socket.timeout,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.checkLogin((self.login, self.login), kw)
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_loggable_in_case_of_server_gaierror(self):
    """Check that in case if socket.gaierror is raised login works from ZODB cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_socket_gaierror
      self.assertRaises(socket.gaierror,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.checkLogin((self.login, self.login), kw)
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_loggable_in_case_of_server_gaierror_normal_cache(self):
    """Check that in case if socket.gaierror is raised login works from usual cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    expected = (self.login, self.login)
    sent = kw
    self.assertEqual(expected,
        self.erp5_remote_manager.authenticateCredentials(sent))
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_socket_gaierror
      self.assertRaises(socket.gaierror,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.assertEqual(expected,
        self.erp5_remote_manager.authenticateCredentials(sent))
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_loggable_in_case_of_server_raises_anythin_else_normal_cache(self):
    """Check that in case if non socket is raised login works from usual cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    expected = (self.login, self.login)
    sent = kw
    self.assertEqual(expected,
        self.erp5_remote_manager.authenticateCredentials(sent))
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_valueerror
      self.assertRaises(ValueError,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.assertEqual(expected,
        self.erp5_remote_manager.authenticateCredentials(sent))
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_not_loggable_in_case_of_server_gaierror_no_log_before(self):
    """Check that in case if socket.gaierror is raised login does not work in case of empty ZODB cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    # patch Wizard Tool to raise in callRemoteProxyMethod
    from Products.ERP5Wizard.Tool.WizardTool import WizardTool
    original_callRemoteProxyMethod=WizardTool.callRemoteProxyMethod
    try:
      WizardTool.callRemoteProxyMethod = raises_socket_gaierror
      self.assertRaises(socket.gaierror,
          self.portal.portal_wizard.callRemoteProxyMethod)
      self.checkLogin(None, kw)
    finally:
      WizardTool.callRemoteProxyMethod = original_callRemoteProxyMethod

  def test_wrong_login_clears_zodb_cache(self):
    """Check that wrong login attempt clears ZODB cache"""
    self.createPerson(self.login, self.password)
    self.tic()
    kw = {'login':self.login, 'password': self.password}
    self.checkLogin((self.login, self.login), kw)
    self.assertTrue(self.login in \
        self.erp5_remote_manager.remote_authentication_cache)
    self.checkLogin(None, {'login':kw['login'], 'password':'wrong_password'})
    self.assertFalse(self.login in \
        self.erp5_remote_manager.remote_authentication_cache)

  def test_is_single_sign_on_enable(self):
    """ Check if isSingleSignOn is Enabled """
    self.assertTrue(self.portal.portal_wizard.isSingleSignOnEnabled())
    # Make sure single_sign_on_enable was not enabled before
    # start the setup was made.
    self.assertFalse(self.was_sso_enable)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5RemoteUserManager))
  return suite
