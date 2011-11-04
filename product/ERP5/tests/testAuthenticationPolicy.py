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

import unittest
import time
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from Products.Formulator.Errors import ValidationError
from Products.ERP5Type.Document import newTempBase
from DateTime import DateTime

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
    self.login(self.manager_username)
    kw = dict(portal_type='Person',
              reference = 'test')
    if portal.portal_catalog.getResultValue(**kw) is None:
      # add a loggable Person
      person = portal.person_module.newContent(password = 'test', 
                                               first_name = 'First',
                                               last_name = 'Last', 
                                               **kw)
      person.validate()
      assignment = person.newContent(portal_type = 'Assignment')
      assignment.open()
                                      
      # Setup auth policy
      preference = portal.portal_preferences.newContent(
                                              portal_type = 'System Preference',
                                              title = 'Authentication',
                                              preferred_max_authentication_failure = 3,
                                              preferred_authentication_failure_check_duration = 600,
                                              preferred_authentication_failure_block_duration = 600,
                                              preferred_authentication_policy_enabled = True)
      preference.enable()
      self.stepTic()

  def _clearCache(self):
    for cache_factory in [x for x in self.portal.portal_caches.getCacheFactoryList() if x!="erp5_session_cache"]:
      self.portal.portal_caches.clearCacheFactory(cache_factory)

  def _getPasswordEventList(self, person):
    return [x.getObject() for x in self.portal.portal_catalog(
                                                 portal_type = 'Password Event',
                                                 default_destination_uid = person.getUid(),
                                                 sort_on = (('creation_date', 'DESC',),))]

  def _cleanUpPerson(self, person):
    self.portal.system_event_module.manage_delObjects([x.getId() for x in self._getPasswordEventList(person)])


  def test_01_BlockLogin(self):
    """
      Test that a recataloging works for Web Site documents
    """
    portal = self.getPortal()
    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())
    
    person = portal.portal_catalog.getResultValue(portal_type = 'Person', 
                                                  reference = 'test')
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)                                                  
    # login should be allowed
    self.assertFalse(person.isLoginBlocked())
    
    # file some failures so we should detect and block account
    person.notifyLoginFailure()
    person.notifyLoginFailure()
    person.notifyLoginFailure()
    self.stepTic()

    # should be blocked
    self.assertTrue(person.isLoginBlocked())
    
    # set check back interval to actualy disable blocking
    preference.setPreferredAuthenticationFailureCheckDuration(0)
    self._clearCache()
    self.stepTic()
    time.sleep(1) # we need to give a moment
    self.assertFalse(person.isLoginBlocked())
    
    # .. and revert it back
    preference.setPreferredAuthenticationFailureCheckDuration(600)
    self._clearCache()
    self.stepTic()
    self.assertTrue(person.isLoginBlocked())
    
    # increase failures attempts
    preference.setPreferredMaxAuthenticationFailure(4)
    self._clearCache()
    self.stepTic()
    self.assertFalse(person.isLoginBlocked())
    
    # .. and revert it back
    preference.setPreferredMaxAuthenticationFailure(3)
    self._clearCache()
    self.stepTic()
    self.assertTrue(person.isLoginBlocked())
    
    # set short block interval so we can test it as well
    preference.setPreferredAuthenticationFailureBlockDuration(3)
    self._clearCache()
    self.stepTic()
    time.sleep(4)
    self.assertFalse(person.isLoginBlocked())
    
    # test multiple concurrent transactions without waiting for activities to be over
    preference.setPreferredAuthenticationFailureCheckDuration(600)
    preference.setPreferredAuthenticationFailureBlockDuration(600)    
    preference.setPreferredMaxAuthenticationFailure(3)    
    person.Person_unblockLogin()
    self._clearCache()
    self.stepTic()
    
    person.notifyLoginFailure()
    person.notifyLoginFailure()
    person.notifyLoginFailure()
    
    transaction.commit()
    self.assertTrue(person.isLoginBlocked())
    self.stepTic()
    self.assertTrue(person.isLoginBlocked())
    
    # test unblock account
    person.Person_unblockLogin()
    self.stepTic()
    self.assertFalse(person.isLoginBlocked())    
    

  def test_02_PasswordHistory(self):
    """
      Test password history.
    """
    portal = self.getPortal()
    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())
    
    person = portal.person_module.newContent(portal_type = 'Person', 
                                             reference = 'test-02')                                                  
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    self.stepTic()                                                      
                                                      
    # Check that last (X where X is set in preferences) passwords are saved.
    self.assertEqual([], self._getPasswordEventList(person))    
    preference.setPreferredNumberOfLastPasswordToCheck(10)
    self.stepTic()
    self._clearCache()
    
    person.setPassword('12345678')
    self.stepTic()
    
    # password change date should be saved as well hashed old password value
    old_password = person.getPassword()     
    self.assertSameSet([old_password], [x.getPassword() for x in self._getPasswordEventList(person)])
    
    # .. test one more time to check history of password is saved in a list
    person.setPassword('123456789')
    self.stepTic()
    old_password1 = person.getPassword()
    
    # password change date should be saved as well hashed old password value
    self.assertSameSet([old_password1, old_password], [x.getPassword() for x in self._getPasswordEventList(person)])

    # other methods (_setPassword)...
    person._setPassword('123456789-1')
    self.stepTic()
    old_password2 = person.getPassword()
    self.assertSameSet([old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(person)])

    # other methods (_forceSetPassword)...
    person._forceSetPassword('123456789-2')
    self.stepTic()
    old_password3 = person.getPassword()
    self.assertSameSet([old_password3, old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(person)]) 
    

    # other methods (setEncodedPassword)...
    person.setEncodedPassword('123456789-3')
    self.stepTic()
    old_password4 = person.getPassword()
    self.assertSameSet([old_password4, old_password3, old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(person)]) 

    # other methods (edit)...
    person.edit(password = '123456789-4')
    self.stepTic()
    old_password5 = person.getPassword()
    self.assertSameSet([old_password5, old_password4, old_password3, old_password2, old_password1, old_password], \
                     [x.getPassword() for x in self._getPasswordEventList(person)]) 


  def test_03_PasswordValidity(self):
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

    person = portal.person_module.newContent(portal_type = 'Person', 
                                             reference = 'test-03',
                                             password = 'test', 
                                             first_name = 'First',
                                             last_name = 'Last')                                                    
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    self.stepTic()
    
    # by default an empty password if nothing set in preferences is OK
    self.assertTrue(person.isPasswordValid(''))
    
    # Not long enough passwords used
    self._cleanUpPerson(person)    
    preference.setPreferredMinPasswordLength(8)
    preference.setPreferredNumberOfLastPasswordToCheck(0)    
    self.stepTic()
    self._clearCache()
    
    self.assertEqual([-1], person.analyzePassword(''))
    self.assertEqual([-1], person.analyzePassword('1234567'))   
    self.assertTrue(person.isPasswordValid('12345678'))
    
    # not changed in last x days
    self._cleanUpPerson(person)    
    preference.setPreferredMinPasswordLifetimeDuration(24)
    preference.setPreferredNumberOfLastPasswordToCheck(3)
    self.stepTic()
    self._clearCache()
    
    self.assertTrue(person.isPasswordValid('12345678'))
    person.setPassword('12345678')
    self.stepTic()
    
    # if we try to change now we should fail with any password
    self.assertSameSet([-3], person.analyzePassword('87654321'))
    self.assertSameSet([-1, -3], person.analyzePassword('short')) # multiple failures
    self.assertFalse(person.isPasswordValid('short')) # multiple failures
    self.assertRaises(ValueError, person.setPassword, '87654321')
 
    preference.setPreferredMinPasswordLifetimeDuration(0) # remove restriction
    self.stepTic()
    self._clearCache()
    self.assertTrue(person.isPasswordValid('87654321')) # it's OK to change
    
    # password not used in previous X passwords
    preference.setPreferredMinPasswordLength(None) # disable for now
    self._cleanUpPerson(person)
    self._clearCache()
    self.stepTic()
    
    person.setPassword('12345678-new')
    self.stepTic()
    
    self.assertSameSet([-4], person.analyzePassword('12345678-new')) # if we try to change now we should fail with this EXACT password
    self.assertRaises(ValueError, person.setPassword, '12345678-new')
    self.assertTrue(person.isPasswordValid('12345678_')) # it's OK with another one not used yet
    for password in ['a','b','c','d', 'e', 'f']:
      person.setPassword(password)
      self.stepTic()
 
    self.assertTrue(person.isPasswordValid('12345678-new'))
    self.assertTrue(person.isPasswordValid('a'))
    self.assertTrue(person.isPasswordValid('b'))
    # only last 3 (including current one are invalid)
    self.assertSameSet([-4], person.analyzePassword('d'))
    self.assertSameSet([-4], person.analyzePassword('e'))     
    self.assertSameSet([-4], person.analyzePassword('f'))
  
    # if we remove restricted then all password are usable
    preference.setPreferredNumberOfLastPasswordToCheck(None)
    self._clearCache()    
    self.stepTic()    
    
    self.assertTrue(person.isPasswordValid('d'))
    self.assertTrue(person.isPasswordValid('e'))
    self.assertTrue(person.isPasswordValid('f'))
    
    # if we set only last password to check
    preference.setPreferredNumberOfLastPasswordToCheck(1)
    self._clearCache()    
    self.stepTic()
    self.assertTrue(person.isPasswordValid('c'))
    self.assertTrue(person.isPasswordValid('d'))
    self.assertTrue(person.isPasswordValid('e'))
    self.assertSameSet([-4], person.analyzePassword('f'))    
       
    preference.setPreferredRegularExpressionGroupList(regular_expression_list)
    preference.setPreferredMinPasswordLength(7)
    preference.setPreferredNumberOfLastPasswordToCheck(None)
    self._cleanUpPerson(person)    
    self._clearCache() 
    self.stepTic()
    
    four_group_password_list = ['abAB#12', 'ghTK61%', '5Tyui1%','Y22GJ5iu#' ]
    three_group_password_list = ['abAB123 ', 'AB123ab', 'XY123yz', 'dufgQ7xL', 'NAfft8h5', '0LcAiWtT']
    two_group_password_list = ['XY12345', 'yuiffg1', 'abcdef##', '##$aabce']
    one_group_password_list = ['1234567', 'ABZSDFE', '##!!$$%','abzdeffgg']

    # min 4 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(4)
    self._clearCache() 
    self.stepTic()
    for password in four_group_password_list:
      self.assertTrue(person.isPasswordValid(password))
    for password in three_group_password_list+two_group_password_list + one_group_password_list:
      self.assertSameSet([-2], person.analyzePassword(password))    

    # min 3 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(3)    
    self._clearCache()
    self._cleanUpPerson(person)    
    self.stepTic()    
    for password in four_group_password_list + three_group_password_list:
      self.assertTrue(person.isPasswordValid(password))
    for password in two_group_password_list + one_group_password_list:
      self.assertSameSet([-2], person.analyzePassword(password))
    
    # min 2 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(2)
    self._clearCache()
    self.stepTic()
    for password in four_group_password_list + three_group_password_list + two_group_password_list:
      self.assertTrue(person.isPasswordValid(password))
    for password in one_group_password_list:
      self.assertSameSet([-2], person.analyzePassword(password))
      
    # min 1 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(1)
    self._clearCache()
    self.stepTic()
    for password in four_group_password_list + three_group_password_list + two_group_password_list+one_group_password_list:
      self.assertTrue(person.isPasswordValid(password))

    # not contain the full name of the user
    preference.setPrefferedForceUsernameCheckInPassword(1)
    self._clearCache()
    self.stepTic()
    self.assertSameSet([-5], person.analyzePassword('abAB#12_%s' %person.getFirstName()))
    self.assertSameSet([-5], person.analyzePassword('abAB#12_%s' %person.getLastName()))
    preference.setPrefferedForceUsernameCheckInPassword(0)
    self._clearCache()
    self.stepTic()
    self.assertTrue(person.isPasswordValid('abAB#12_%s' %person.getFirstName()))
    self.assertTrue(person.isPasswordValid('abAB#12_%s' %person.getLastName()))    

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
    self.stepTic()    
    # in this case which is basically used in new account creation only length of password matters
    self.assertSameSet([-1], temp_person.Person_analyzePassword('onlyNine1'))
    self.assertSameSet([], temp_person.Person_analyzePassword('longEnough1'))
    
    # make sure re check works on temp as well ( i.e. min 3 out of all groups)
    preference.setPreferredRegularExpressionGroupList(regular_expression_list)    
    preference.setPreferredMinPasswordLength(7)    
    preference.setPreferredMinRegularExpressionGroupNumber(3)    
    self._clearCache()
    self.stepTic()    
    for password in four_group_password_list + three_group_password_list:
      self.assertSameSet([], temp_person.Person_analyzePassword(password))
    for password in two_group_password_list + one_group_password_list:
      self.assertSameSet([-2], temp_person.Person_analyzePassword(password))
      
    # make sure peron's check on username works on temp as well (i.e. not contain the full name of the user)
    preference.setPrefferedForceUsernameCheckInPassword(1)
    self._clearCache()
    self.stepTic()
    self.assertSameSet([-5], temp_person.Person_analyzePassword('abAB#12_%s' %first_name))
    self.assertSameSet([-5], temp_person.Person_analyzePassword('abAB#12_%s' %last_name))
    
    preference.setPrefferedForceUsernameCheckInPassword(0)
    self._clearCache()
    self.stepTic()
    self.assertSameSet([], temp_person.Person_analyzePassword('abAB#12_%s' %first_name))
    self.assertSameSet([], temp_person.Person_analyzePassword('abAB#12_%s' %last_name))    
    
    # check Base_isPasswordValid is able to work in Anonymous User fashion
    # but with already create Person object (i.e. recover password case)
    preference.setPrefferedForceUsernameCheckInPassword(1)
    preference.setPreferredMinPasswordLength(7)
    preference.setPreferredMinRegularExpressionGroupNumber(3)
    preference.setPreferredNumberOfLastPasswordToCheck(1)
    self._clearCache()
    self.stepTic()    
    
    person.setPassword('used_ALREADY_1234')
    self._clearCache()
    self.stepTic()
    
    # emulate Anonymous User
    self.logout()
    request.set('field_user_login', person.getReference())     
    self.assertRaises(ValidationError,  portal.Base_isPasswordValid, 'abAB#12_%s' %person.getFirstName(), request) # contains name
    self.assertRaises(ValidationError,  portal.Base_isPasswordValid, 'abAB#12_%s' %person.getLastName(), request) # contains name
    self.assertRaises(ValidationError,  portal.Base_isPasswordValid, 'abAB#1', request) # too short
    self.assertRaises(ValidationError,  portal.Base_isPasswordValid, 'abABCDEFG', request) # too few groups
    self.assertRaises(ValidationError,  portal.Base_isPasswordValid, 'used_ALREADY_1234', request) # already used 
    self.assertEqual(1, portal.Base_isPasswordValid('abAB#12_', request))
    self.assertEqual(1, portal.Base_isPasswordValid('not_used_ALREADY_1234', request))     

  def test_04_PasswordExpire(self):
    """
      Test password expire.
    """
    portal = self.getPortal()
    request = self.app.REQUEST
    
    self.assertTrue(portal.portal_preferences.isAuthenticationPolicyEnabled())
    
    person = portal.person_module.newContent(portal_type = 'Person', 
                                             reference = 'test-04',
                                             password = 'used_ALREADY_1234')                                                    
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
                                                      
    preference.setPreferredMaxPasswordLifetimeDuration(24)
    self.stepTic()
    self._clearCache()
    self.assertFalse(person.isPasswordExpired())
    self.assertFalse(request['is_user_account_password_expired'])
    
   
    # set longer password validity interval
    preference.setPreferredMaxPasswordLifetimeDuration(4*24) # password expire in 4 days
    self.stepTic()
    self._clearCache()
    self.assertFalse(person.isPasswordExpired())
    self.assertFalse(request['is_user_account_password_expired'])
    
    # test early warning password expire notification is detected
    preference.setPreferredPasswordLifetimeExpireWarningDuration(4*24) # password expire notification appear immediately
    self.stepTic()
    self._clearCache()
    self.assertFalse(person.isPasswordExpired())
    self.assertTrue(request['is_user_account_password_expired_expire_date'])
    
    # test early warning password expire notification is detected
    preference.setPreferredPasswordLifetimeExpireWarningDuration(4*24-24) # password expire notification appear 3 days befor time
    self.stepTic()
    self._clearCache()
    self.assertFalse(person.isPasswordExpired())
    self.assertFalse(request['is_user_account_password_expired_expire_date']) 

  def test_05_HttpRequest(self):
    """
      Check HTTP responses
    """
    portal = self.getPortal()
    request = self.app.REQUEST
    person = portal.portal_catalog.getResultValue(portal_type = 'Person', 
                                                  reference = 'test')
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    person.setPassword('used_ALREADY_1234')
    self.stepTic()
                                            
    path = portal.absolute_url_path() + '/view?__ac_name=%s&__ac_password=%s'  %('test', 'used_ALREADY_1234')
    response = self.publish(path)
    self.assertTrue('Welcome to ERP5' in response.getBody())
    self.assertFalse(person.isLoginBlocked())
    
    # fail request #1
    path = portal.absolute_url_path() + '/view?__ac_name=%s&__ac_password=%s'  %('test', 'bad_test')
    response = self.publish(path)
    self.assertTrue(response.getHeader("Location").endswith("login_form"))
    self.assertFalse(person.isLoginBlocked())
    
    # fail request #2
    response = self.publish(path)
    self.assertTrue(response.getHeader("Location").endswith("login_form"))
    self.assertFalse(person.isLoginBlocked())
    
    # fail request #3    
    response = self.publish(path)
    self.assertTrue(response.getHeader("Location").endswith("login_form"))
    self.assertTrue(person.isLoginBlocked())
    
    self.stepTic()
    
    # test message that account is blocked
    self.assertTrue(person.isLoginBlocked())
    path = portal.absolute_url_path() + '/logged_in?__ac_name=%s&__ac_password=%s'  %('test', 'used_ALREADY_1234')
    response = self.publish(path)
    self.assertTrue(response.getHeader("Location").endswith("login_form?portal_status_message=Account is blocked."))
    
    # test expire password message, first unblock it
    person.Person_unblockLogin()
    preference.setPreferredMaxPasswordLifetimeDuration(0)
    self.stepTic()
    self._clearCache()
    response = self.publish(path)    
    self.assertTrue(response.getHeader("Location").endswith("login_form?portal_status_message=Password is expired."))
    self.assertTrue(person.isPasswordExpired())
    
    # test we're redirected to update password due to soon expire
    preference.setPreferredMaxPasswordLifetimeDuration(24)
    preference.setPreferredPasswordLifetimeExpireWarningDuration(24)    
    self.stepTic()
    self._clearCache()
    response = self.publish(path) 
    
    self.assertTrue('Your password will expire' in response.getHeader("Location"))
    self.assertTrue('You are advised to change it as soon as possible' in response.getHeader("Location"))
    
    # test proper login
    preference.setPreferredPasswordLifetimeExpireWarningDuration(12)    
    self.stepTic()
    self._clearCache()
    path = portal.absolute_url_path() + '/view?__ac_name=%s&__ac_password=%s'  %('test', 'used_ALREADY_1234')    
    response = self.publish(path) 
    self.assertTrue('Welcome to ERP5' in response.getBody())

  def test_06_ExpireOldAuthenticationEventList(self):
    """
      Check that expiring old Authentication Event list works.
    """
    portal = self.getPortal()
    person = portal.portal_catalog.getResultValue(portal_type = 'Person', 
                                                  reference = 'test')
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
    # file some failures so we should detect and block account
    person.notifyLoginFailure()
    person.notifyLoginFailure()
    person.notifyLoginFailure()
    self.stepTic()

    # should be blocked
    self.assertTrue(person.isLoginBlocked())
    
    # set 0 check interval
    preference.setPreferredAuthenticationFailureCheckDuration(0)
    self.stepTic()
    self._clearCache()
    
    time.sleep(1) # we need to give a moment
    self.assertFalse(person.isLoginBlocked())
    
    # expire manually old
    portal.system_event_module.SystemEventModule_expireAuthenticationEventList()
    self.stepTic()
    
    self.assertEqual(3, len(portal.portal_catalog(portal_type ="Authentication Event",
                                                 default_destination_uid = person.getUid(),    
                                                 validation_state = "expired")))
                                                


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAuthenticationPolicy))
  return suite
