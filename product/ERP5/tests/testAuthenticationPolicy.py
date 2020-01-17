# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
#          Ivan Tyagov <ivan@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from functools import partial
import unittest
import urllib
from StringIO import StringIO
import time
import httplib
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.Formulator.Errors import ValidationError
from Products.ERP5Type.Document import newTempBase

class TestAuthenticationPolicy(ERP5TypeTestCase):
  """
  Test for erp5_authentication_policy business template.
  """
  manager_username = 'zope'
  manager_password = 'zope'

  credential = '%s:%s' % (manager_username, manager_password)
  def getTitle(self):
    return "TestAuthenticationPolicy"

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_web',
            'erp5_credential',
            'erp5_system_event',
            'erp5_authentication_policy',)

  def afterSetUp(self):
    portal = self.getPortal()

    uf = portal.acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    self.loginByUserName(self.manager_username)
    kw = dict(portal_type='Person',
              reference = 'test')
    if portal.portal_catalog.getResultValue(**kw) is None:
      # add a loggable Person
      person = self.createUser(
        kw['reference'],
        password='test',
        person_kw={'first_name': 'First',
                   'last_name': 'Last'},
      )
      person.validate()
      assignment = person.newContent(portal_type = 'Assignment')
      assignment.open()


    # Reset and Setup auth policy
    old_preference = portal.portal_catalog.getResultValue(
      portal_type='System Preference',
      title='Authentication')
    if old_preference is not None:
      old_preference.setTitle('disabled authentication preference')
      old_preference.disable()

    preference = portal.portal_preferences.newContent(
                                            portal_type = 'System Preference',
                                            title = 'Authentication',
                                            preferred_max_authentication_failure = 3,
                                            preferred_authentication_failure_check_duration = 600,
                                            preferred_authentication_failure_block_duration = 600,
                                            preferred_authentication_policy_enabled = True)
    preference.enable()
    self.tic()

  def _clearCache(self):
    self.portal.portal_caches.clearCache(
      cache_factory_list=('erp5_content_short', # for authentication cache
                          ))

  def _getPasswordEventList(self, login):
    return [x.getObject() for x in self.portal.portal_catalog(
                                                 portal_type = 'Password Event',
                                                 default_destination_uid = login.getUid(),
                                                 sort_on = (('creation_date', 'DESC',),))]

  def _cleanUpLogin(self, login):
    self.portal.system_event_module.manage_delObjects([x.getId() for x in self._getPasswordEventList(login)])


  def createUser(self, reference, password=None, person_kw=None):
    """
      Modified version from ERP5TypeTestCase, that does set reference as
      password when password is None.
    """
    if person_kw is None:
      person_kw = {}

    person = self.portal.person_module.newContent(portal_type='Person',
                                                  reference=reference,
                                                  **person_kw)
    login = person.newContent(portal_type='ERP5 Login',
                              reference=reference,
                              password=password)
    login.validate()
    return person

  def test_BlockLogin(self):
    """
      Test that a recataloging works for Web Site documents
    """
    portal = self.getPortal()
    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())

    person = portal.portal_catalog.getResultValue(portal_type = 'Person',
                                                  reference = 'test')
    login = person.objectValues(portal_type='ERP5 Login')[0]
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    # login should be allowed
    self.assertFalse(login.isLoginBlocked())

    # file some failures so we should detect and block account
    login.notifyLoginFailure()
    login.notifyLoginFailure()
    login.notifyLoginFailure()
    self.tic()

    # should be blocked
    self.assertTrue(login.isLoginBlocked())

    # set check back interval to actualy disable blocking
    preference.setPreferredAuthenticationFailureCheckDuration(0)
    self._clearCache()
    self.tic()
    time.sleep(1) # we need to give a moment
    self.assertFalse(login.isLoginBlocked())

    # .. and revert it back
    preference.setPreferredAuthenticationFailureCheckDuration(600)
    self._clearCache()
    self.tic()
    self.assertTrue(login.isLoginBlocked())

    # increase failures attempts
    preference.setPreferredMaxAuthenticationFailure(4)
    self._clearCache()
    self.tic()
    self.assertFalse(login.isLoginBlocked())

    # .. and revert it back
    preference.setPreferredMaxAuthenticationFailure(3)
    self._clearCache()
    self.tic()
    self.assertTrue(login.isLoginBlocked())

    # set short block interval so we can test it as well
    preference.setPreferredAuthenticationFailureBlockDuration(3)
    self._clearCache()
    self.tic()
    time.sleep(4)
    self.assertFalse(login.isLoginBlocked())

    # test multiple concurrent transactions without waiting for activities to be over
    preference.setPreferredAuthenticationFailureCheckDuration(600)
    preference.setPreferredAuthenticationFailureBlockDuration(600)
    preference.setPreferredMaxAuthenticationFailure(3)
    login.Login_unblockLogin()
    self._clearCache()
    self.tic()

    login.notifyLoginFailure()
    login.notifyLoginFailure()
    login.notifyLoginFailure()

    self.commit()
    self.assertTrue(login.isLoginBlocked())
    self.tic()
    self.assertTrue(login.isLoginBlocked())

    # test unblock account
    login.Login_unblockLogin()
    self.tic()
    self.assertFalse(login.isLoginBlocked())


  def test_PasswordHistory(self):
    """
      Test password history.
    """
    portal = self.getPortal()
    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())

    person = self.createUser('test-02')
    login = person.objectValues(portal_type='ERP5 Login')[0]
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    self.tic()

    # Check that last (X where X is set in preferences) passwords are saved.
    self.assertEqual([], self._getPasswordEventList(login))
    preference.setPreferredNumberOfLastPasswordToCheck(10)
    self.tic()
    self._clearCache()

    login.setPassword('12345678')
    self.tic()

    # password change date should be saved as well hashed old password value
    old_password = login.getPassword()
    self.assertSameSet([old_password], [x.getPassword() for x in self._getPasswordEventList(login)])

    # .. test one more time to check history of password is saved in a list
    login.setPassword('123456789')
    self.tic()
    old_password1 = login.getPassword()

    # password change date should be saved as well hashed old password value
    self.assertSameSet([old_password1, old_password], [x.getPassword() for x in self._getPasswordEventList(login)])

    # other methods (_setPassword)...
    login._setPassword('123456789-1')
    self.tic()
    old_password2 = login.getPassword()
    self.assertSameSet([old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(login)])

    # other methods (_forceSetPassword)...
    login._forceSetPassword('123456789-2')
    self.tic()
    old_password3 = login.getPassword()
    self.assertSameSet([old_password3, old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(login)])


    # other methods (setEncodedPassword)...
    login.setEncodedPassword('123456789-3')
    self.tic()
    old_password4 = login.getPassword()
    self.assertSameSet([old_password4, old_password3, old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(login)])

    # other methods (edit)...
    login.edit(password = '123456789-4')
    self.tic()
    old_password5 = login.getPassword()
    self.assertSameSet([old_password5, old_password4, old_password3, old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(login)])


  def test_PasswordValidity(self):
    """
      Test validity of a password.
    """
    portal = self.getPortal()
    request = self.app.REQUEST

    regular_expression_list = ['([a-z]+)', # english lowercase
                               '([A-Z]+)', # english uppercase
                               '([0-9]+)', # numerals (0-9)
                               '([\\\\$\\\\!\\\\#\\\\%]+)' # (!, $, #, %)
                              ]

    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())

    person = self.createUser(
        'test-03',
        password='test',
        person_kw={'first_name': 'First',
                   'last_name': 'Last'},
    )
    login = person.objectValues(portal_type='ERP5 Login')[0]
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    self.tic()

    # by default an empty password if nothing set in preferences is OK
    self.assertTrue(login.isPasswordValid(''))

    # Not long enough passwords used
    self._cleanUpLogin(login)
    preference.setPreferredMinPasswordLength(8)
    preference.setPreferredNumberOfLastPasswordToCheck(0)
    self.tic()
    self._clearCache()

    self.assertEqual(['Too short.'], [str(msg) for msg in login.analyzePassword('')])
    self.assertEqual(['Too short.'], [str(msg) for msg in login.analyzePassword('1234567')])
    self.assertTrue(login.isPasswordValid('12345678'))

    # not changed in last x days
    self._cleanUpLogin(login)
    preference.setPreferredMinPasswordLifetimeDuration(24)
    preference.setPreferredNumberOfLastPasswordToCheck(3)
    self.tic()
    self._clearCache()

    self.assertTrue(login.isPasswordValid('12345678'))
    login.setPassword('12345678')
    self.tic()

    # if we try to change now we should fail with any password
    self.assertEqual(
      ['You have changed your password too recently.'],
      [str(msg) for msg in login.analyzePassword('87654321')])
    self.assertSameSet(
      ['Too short.', 'You have changed your password too recently.'],
      [str(msg) for msg in login.analyzePassword('short')]) # multiple failures
    self.assertFalse(login.isPasswordValid('short')) # multiple failures
    self.assertRaises(ValueError, login.setPassword, '87654321')

    preference.setPreferredMinPasswordLifetimeDuration(0) # remove restriction
    self.tic()
    self._clearCache()
    self.assertTrue(login.isPasswordValid('87654321')) # it's OK to change

    # password not used in previous X passwords
    preference.setPreferredMinPasswordLength(None) # disable for now
    self._cleanUpLogin(login)
    self._clearCache()
    self.tic()

    login.setPassword('12345678-new')
    self.tic()

    # if we try to change now we should fail with this EXACT password
    self.assertEqual(
      ['You have already used this password.'],
      [str(msg) for msg in login.analyzePassword('12345678-new')])
    self.assertRaises(ValueError, login.setPassword, '12345678-new')
    self.assertTrue(login.isPasswordValid('12345678_')) # it's OK with another one not used yet
    for password in ['a','b','c','d', 'e', 'f']:
      # this sleep is not so beautiful, but mysql datetime columns has a
      # precision of one second only, and we use creation_date to order
      # "Password Event" objects. So without this sleep, the test is
      # failing randomly.
      time.sleep(1)
      login.setPassword(password)
      self.tic()
    self._clearCache()
    self.tic()

    self.assertTrue(login.isPasswordValid('12345678-new'))
    self.assertTrue(login.isPasswordValid('a'))
    self.assertTrue(login.isPasswordValid('b'))
    self.assertTrue(login.isPasswordValid('c'))
    # only last 3 (including current one are invalid)
    self.assertEqual(
      ['You have already used this password.'],
      [str(msg) for msg in login.analyzePassword('d')])
    self.assertEqual(
      ['You have already used this password.'],
      [str(msg) for msg in login.analyzePassword('e')])
    self.assertEqual(
      ['You have already used this password.'],
      [str(msg) for msg in login.analyzePassword('f')])

    # if we remove restricted then all password are usable
    preference.setPreferredNumberOfLastPasswordToCheck(None)
    self._clearCache()
    self.tic()

    self.assertTrue(login.isPasswordValid('d'))
    self.assertTrue(login.isPasswordValid('e'))
    self.assertTrue(login.isPasswordValid('f'))

    # if we set only last password to check
    preference.setPreferredNumberOfLastPasswordToCheck(1)
    self._clearCache()
    self.tic()
    self.assertTrue(login.isPasswordValid('c'))
    self.assertTrue(login.isPasswordValid('d'))
    self.assertTrue(login.isPasswordValid('e'))
    self.assertEqual(
      ['You have already used this password.'],
      [str(msg) for msg in login.analyzePassword('f')])

    preference.setPreferredRegularExpressionGroupList(regular_expression_list)
    preference.setPreferredMinPasswordLength(7)
    preference.setPreferredNumberOfLastPasswordToCheck(None)
    self._cleanUpLogin(login)
    self._clearCache()
    self.tic()

    four_group_password_list = ['abAB#12', 'ghTK61%', '5Tyui1%','Y22GJ5iu#' ]
    three_group_password_list = ['abAB123 ', 'AB123ab', 'XY123yz', 'dufgQ7xL', 'NAfft8h5', '0LcAiWtT']
    two_group_password_list = ['XY12345', 'yuiffg1', 'abcdef##', '##$aabce']
    one_group_password_list = ['1234567', 'ABZSDFE', '##!!$$%','abzdeffgg']

    # min 4 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(4)
    self._clearCache()
    self.tic()
    for password in four_group_password_list:
      self.assertTrue(login.isPasswordValid(password))
    for password in three_group_password_list+two_group_password_list + one_group_password_list:
      self.assertEqual(
        ['Not complex enough.'],
        [str(msg) for msg in login.analyzePassword(password)])

    # min 3 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(3)
    self._clearCache()
    self._cleanUpLogin(login)
    self.tic()
    for password in four_group_password_list + three_group_password_list:
      self.assertTrue(login.isPasswordValid(password))
    for password in two_group_password_list + one_group_password_list:
      self.assertEqual(
        ['Not complex enough.'],
        [str(msg) for msg in login.analyzePassword(password)])

    # min 2 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(2)
    self._clearCache()
    self.tic()
    for password in four_group_password_list + three_group_password_list + two_group_password_list:
      self.assertTrue(login.isPasswordValid(password))
    for password in one_group_password_list:
      self.assertEqual(
        ['Not complex enough.'],
        [str(msg) for msg in login.analyzePassword(password)])

    # min 1 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(1)
    self._clearCache()
    self.tic()
    for password in four_group_password_list + three_group_password_list + two_group_password_list+one_group_password_list:
      self.assertTrue(login.isPasswordValid(password))

    # not contain the full name of the user
    preference.setPrefferedForceUsernameCheckInPassword(1)
    self._clearCache()
    self.tic()
    self.assertEqual(
      ['You can not use any parts of your first and last name in password.'],
      [str(msg) for msg in person.Login_analyzePassword('abAB#12_%s' %person.getFirstName())])
    self.assertEqual(
      ['You can not use any parts of your first and last name in password.'],
      [str(msg) for msg in person.Login_analyzePassword('abAB#12_%s' %person.getLastName())])
    preference.setPrefferedForceUsernameCheckInPassword(0)
    self._clearCache()
    self.tic()
    self.assertTrue(login.isPasswordValid('abAB#12_%s' %person.getFirstName()))
    self.assertTrue(login.isPasswordValid('abAB#12_%s' %person.getLastName()))

    # check on temp objects just passworrd length( i.e. simulating a new user account creation)
    first_name = 'John'
    last_name = 'Doh'
    kw = {'title': '%s %s' %(first_name, last_name),
          'first_name': first_name,
          'last_name': last_name}
    temp_person = newTempBase(portal, kw['title'], **kw)

    preference.setPreferredMinPasswordLength(10)
    preference.setPreferredRegularExpressionGroupList(None)
    self._clearCache()
    self.tic()
    # in this case which is basically used in new account creation only length of password matters
    self.assertEqual(
      ['Too short.'],
      [str(msg) for msg in temp_person.Login_analyzePassword('onlyNine1')])
    self.assertEqual([], temp_person.Login_analyzePassword('longEnough1'))

    # make sure re check works on temp as well ( i.e. min 3 out of all groups)
    preference.setPreferredRegularExpressionGroupList(regular_expression_list)
    preference.setPreferredMinPasswordLength(7)
    preference.setPreferredMinRegularExpressionGroupNumber(3)
    self._clearCache()
    self.tic()
    for password in four_group_password_list + three_group_password_list:
      self.assertSameSet([], temp_person.Login_analyzePassword(password))
    for password in two_group_password_list + one_group_password_list:
      self.assertEqual(
        ['Not complex enough.'],
        [str(msg) for msg in temp_person.Login_analyzePassword(password)])

    # make sure peron's check on username works on temp as well (i.e. not contain the full name of the user)
    preference.setPrefferedForceUsernameCheckInPassword(1)
    self._clearCache()
    self.tic()
    self.assertEqual(
      ['You can not use any parts of your first and last name in password.'],
      [str(msg) for msg in temp_person.Login_analyzePassword('abAB#12_%s' %first_name)])
    self.assertEqual(
      ['You can not use any parts of your first and last name in password.'],
      [str(msg) for msg in temp_person.Login_analyzePassword('abAB#12_%s' %last_name)])

    preference.setPrefferedForceUsernameCheckInPassword(0)
    self._clearCache()
    self.tic()
    self.assertEqual([], temp_person.Login_analyzePassword('abAB#12_%s' %first_name))
    self.assertEqual([], temp_person.Login_analyzePassword('abAB#12_%s' %last_name))

    # check Base_isPasswordValid is able to work in Anonymous User fashion
    # but with already create Person object (i.e. recover password case)
    preference.setPrefferedForceUsernameCheckInPassword(1)
    preference.setPreferredMinPasswordLength(7)
    preference.setPreferredMinRegularExpressionGroupNumber(3)
    preference.setPreferredNumberOfLastPasswordToCheck(1)
    self._clearCache()
    self.tic()

    login.setPassword('used_ALREADY_1234')
    self._clearCache()
    self.tic()

  def test_PasswordExpire(self):
    """
      Test password expire.
    """
    portal = self.getPortal()
    request = self.app.REQUEST

    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    preference.setPreferredMaxPasswordLifetimeDuration(24)
    self.tic()
    self._clearCache()

    person = self.createUser('test-04',
                             password='used_ALREADY_1234')
    login = person.objectValues(portal_type='ERP5 Login')[0]

    self.assertFalse(login.isPasswordExpired())
    self.assertFalse(request['is_user_account_password_expired'])

    # Check password expired
    preference.setPreferredMaxPasswordLifetimeDuration(0) # password expire immediatly (just to check isExpired)
    self.tic()
    self._clearCache()
    self.assertTrue(login.isPasswordExpired())

    # set longer password validity interval
    preference.setPreferredMaxPasswordLifetimeDuration(4*24) # password expire in 4 days
    self.tic()
    self._clearCache()
    self.assertFalse(login.isPasswordExpired())
    self.assertFalse(request['is_user_account_password_expired'])

    # test early warning password expire notification is detected
    preference.setPreferredPasswordLifetimeExpireWarningDuration(4*24) # password expire notification appear immediately
    self.tic()
    self._clearCache()
    self.assertFalse(login.isPasswordExpired())
    self.assertTrue(request['is_user_account_password_expired_expire_date'])

    # test early warning password expire notification is detected
    preference.setPreferredPasswordLifetimeExpireWarningDuration(4*24-24) # password expire notification appear 3 days befor time
    self.tic()
    self._clearCache()
    self.assertFalse(login.isPasswordExpired())
    self.assertFalse(request['is_user_account_password_expired_expire_date'])

  def test_SystemRecoverExpiredPassword(self):
    """
      Test automatic system recover password
    """
    portal = self.portal
    request = self.app.REQUEST

    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    preference.setPreferredMaxPasswordLifetimeDuration(0) # password expire immediatly
    preference.setPreferredSystemRecoverExpiredPassword(True)
    self._clearCache()
    self.tic()

    person = self.createUser(self.id(), password='password')
    assignment = person.newContent(portal_type = 'Assignment')
    assignment.open()
    login = person.objectValues(portal_type='ERP5 Login')[0]

    self.tic()
    self._clearCache()
    time.sleep(1)
    self.assertTrue(login.isPasswordExpired())

    publish = partial(
      self.publish,
      portal.absolute_url_path() + '/view',
      basic=self.id() + ':password',
    )
    # User cannot login
    response = publish()
    self.assertTrue(response.getHeader("Location").endswith("login_form"))
    self.tic()

    # and a credential recovery is created automatically
    credential_recovery, = login.getDestinationDecisionRelatedValueList(
        portal_type='Credential Recovery')

    # trying to login again does not create a new credential recovery
    response = publish()
    self.tic()
    credential_recovery, = login.getDestinationDecisionRelatedValueList(
        portal_type='Credential Recovery')

  def test_HttpRequest(self):
    """
      Check HTTP responses
    """
    portal = self.getPortal()
    request = self.app.REQUEST

    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    preference.setPreferredMaxPasswordLifetimeDuration(24)
    self._clearCache()
    self.tic()

    person = self.createUser('test-05')
    assignment = person.newContent(portal_type = 'Assignment')
    assignment.open()
    login = person.objectValues(portal_type='ERP5 Login')[0]
    login.setPassword('used_ALREADY_1234')
    self.tic()

    response = self.publish(
      portal.absolute_url_path() + '/view',
      basic='test-05:used_ALREADY_1234',
    )
    self.assertTrue('Welcome to ERP5' in response.getBody())
    self.assertFalse(login.isLoginBlocked())

    publish = partial(
      self.publish,
      portal.absolute_url_path() + '/view',
      basic='test-05:bad_test',
    )
    # fail request #1
    response = publish()
    self.assertTrue(response.getHeader("Location").endswith("login_form"))
    self.assertFalse(login.isLoginBlocked())

    # fail request #2
    response = publish()
    self.assertTrue(response.getHeader("Location").endswith("login_form"))
    self.assertFalse(login.isLoginBlocked())

    # fail request #3
    response = publish()
    self.assertTrue(response.getHeader("Location").endswith("login_form"))
    self.assertTrue(login.isLoginBlocked())

    self.tic()

    # test message that account is blocked
    self.assertTrue(login.isLoginBlocked())
    publish = partial(
      self.publish,
      portal.absolute_url_path() + '/logged_in',
      basic='test-05:used_ALREADY_1234',
    )
    response = publish()
    self.assertTrue(response.getHeader("Location").endswith("login_form?portal_status_message=Account is blocked."))

    # test expire password message, first unblock it
    login.Login_unblockLogin()
    preference.setPreferredMaxPasswordLifetimeDuration(0)
    self.tic()
    self._clearCache()
    response = publish()
    self.assertTrue(response.getHeader("Location").endswith("login_form?portal_status_message=Password is expired."))
    self.assertTrue(login.isPasswordExpired())

    # test we're redirected to update password due to soon expire
    preference.setPreferredMaxPasswordLifetimeDuration(24)
    preference.setPreferredPasswordLifetimeExpireWarningDuration(24)
    self.tic()
    self._clearCache()
    response = publish()

    self.assertTrue('Your password will expire' in response.getHeader("Location"))
    self.assertTrue('You are advised to change it as soon as possible' in response.getHeader("Location"))

    # test proper login
    preference.setPreferredPasswordLifetimeExpireWarningDuration(12)
    self.tic()
    self._clearCache()
    response = self.publish(
      portal.absolute_url_path() + '/view',
      basic='test-05:used_ALREADY_1234',
    )
    self.assertTrue('Welcome to ERP5' in response.getBody())

  def test_ExpireOldAuthenticationEventList(self):
    """
      Check that expiring old Authentication Event list works.
    """
    portal = self.getPortal()
    person = self.createUser('test-06')
    login = person.objectValues(portal_type='ERP5 Login')[0]
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    # file some failures so we should detect and block account
    login.notifyLoginFailure()
    login.notifyLoginFailure()
    login.notifyLoginFailure()
    self.tic()

    # should be blocked
    self.assertTrue(login.isLoginBlocked())

    # set 0 check interval
    preference.setPreferredAuthenticationFailureCheckDuration(0)
    self.tic()
    self._clearCache()

    time.sleep(1) # we need to give a moment
    self.assertFalse(login.isLoginBlocked())

    # expire manually old
    portal.system_event_module.SystemEventModule_expireAuthenticationEventList()
    self.tic()

    self.assertEqual(3, len(portal.portal_catalog(portal_type ="Authentication Event",
                                                 default_destination_uid = login.getUid(),
                                                 validation_state = "expired")))

  def test_PasswordTool_resetPassword_checks_policy(self):
    person = self.createUser(
      self.id(),
      password='current',
      person_kw={'first_name': 'Alice'})
    person.newContent(portal_type = 'Assignment').open()
    login = person.objectValues(portal_type='ERP5 Login')[0]
    preference = self.portal.portal_catalog.getResultValue(
      portal_type='System Preference',
      title='Authentication',)
    # Here we activate the "password should contain usename" policy
    # as a way to check that password reset checks are done in the
    # context of the login
    preference.setPrefferedForceUsernameCheckInPassword(1)
    self._clearCache()
    self.tic()

    reset_key = self.portal.portal_password.getResetPasswordKey(user_login=self.id())
    ret = self.publish(
      '%s/portal_password' % self.portal.getPath(),
      stdin=StringIO(urllib.urlencode({
        'Base_callDialogMethod:method': '',
        'dialog_id': 'PasswordTool_viewResetPassword',
        'dialog_method': 'PasswordTool_changeUserPassword',
        'field_user_login': self.id(),
        'field_your_password': 'alice',
        'field_password_confirm': 'alice',
        'field_your_password_key': reset_key,
      })),
      request_method="POST",
      handle_errors=False)
    self.assertEqual(httplib.OK, ret.getStatus())
    self.assertIn(
      '<span class="error">You can not use any parts of your '
      'first and last name in password.</span>',
      ret.getBody())

    # now with a password complying to the policy
    ret = self.publish(
      '%s/portal_password' % self.portal.getPath(),
      stdin=StringIO(urllib.urlencode({
        'Base_callDialogMethod:method': '',
        'dialog_id': 'PasswordTool_viewResetPassword',
        'dialog_method': 'PasswordTool_changeUserPassword',
        'field_user_login': self.id(),
        'field_your_password': 'ok',
        'field_password_confirm': 'ok',
        'field_your_password_key': reset_key,
      })),
      request_method="POST",
      handle_errors=False)
    self.assertEqual(httplib.FOUND, ret.getStatus())
    self.assertTrue(ret.getHeader('Location').endswith(
    '/login_form?portal_status_message=Password+changed.'))

  def test_PreferenceTool_changePassword_checks_policy(self):
    person = self.createUser(self.id(), password='current')
    person.newContent(portal_type = 'Assignment').open()
    login = person.objectValues(portal_type='ERP5 Login')[0]
    preference = self.portal.portal_catalog.getResultValue(
      portal_type='System Preference',
      title='Authentication',)
    preference.setPreferredMinPasswordLength(10)
    self._clearCache()
    self.tic()

    # too short password is refused
    ret = self.publish(
      '%s/portal_preferences' % self.portal.getPath(),
      basic='%s:current' % self.id(),
      stdin=StringIO(urllib.urlencode({
        'Base_callDialogMethod:method': '',
        'dialog_id': 'PreferenceTool_viewChangePasswordDialog',
        'dialog_method': 'PreferenceTool_setNewPassword',
        'field_your_current_password': 'current',
        'field_your_new_password': 'short',
        'field_password_confirm': 'short',
      })),
      request_method="POST",
      handle_errors=False)
    self.assertEqual(httplib.OK, ret.getStatus())
    self.assertIn(
      '<span class="error">Too short.</span>',
      ret.getBody())

    # if for some reason, PreferenceTool_setNewPassword is called directly,
    # the password policy is also checked, so this cause an unhandled exception.
    self.login(person.getUserId())
    self.assertRaises(
      ValueError,
      self.portal.PreferenceTool_setNewPassword,
      current_password='current',
      new_password='short')

    # long enough password is accepted
    ret = self.publish(
      '%s/portal_preferences' % self.portal.getPath(),
      basic='%s:current' % self.id(),
      stdin=StringIO(urllib.urlencode({
        'Base_callDialogMethod:method': '',
        'dialog_id': 'PreferenceTool_viewChangePasswordDialog',
        'dialog_method': 'PreferenceTool_setNewPassword',
        'field_your_current_password': 'current',
        'field_your_new_password': 'long_enough_password',
        'field_password_confirm': 'long_enough_password',
      })),
      request_method="POST",
      handle_errors=False)
    # When password reset is succesful, user is logged out
    self.assertEqual(httplib.FOUND, ret.getStatus())
    self.assertEqual(self.portal.portal_preferences.absolute_url(),
                     ret.getHeader("Location"))

    # password is changed on the login
    self.assertTrue(login.checkPassword('long_enough_password'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAuthenticationPolicy))
  return suite
