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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.backportUnittest import expectedFailure
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
                                      
      # Setup auth policy
      preference = portal.portal_preferences.newContent(
                                              portal_type = 'System Preference',
                                              title = 'Authentication',
                                              preferred_max_authentication_failure = 3,
                                              preferred_authentication_failure_check_duration = 600,
                                              preferred_authentication_failure_block_duration = 600)
      preference.enable()
      self.stepTic()

  def _clearCache(self):
    for cache_factory in [x for x in self.portal.portal_caches.getCacheFactoryList() if x!="erp5_session_cache"]:
      self.portal.portal_caches.clearCacheFactory(cache_factory)

  def _cleanUpPerson(self, person):
    # remove all traces from password changes
    person.setLastPasswordModificationDate(None)
    person.setLastChangedPasswordValueList([])


  def test_01_BlockLogin(self):
    """
      Test that a recataloging works for Web Site documents
    """
    portal = self.getPortal()
    self.assertTrue(portal.ERP5Site_isAuthenticationPolicyEnabled())
    
    person = portal.portal_catalog.getResultValue(portal_type = 'Person', 
                                                  reference = 'test')
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)                                                  
    # login should be allowed
    self.assertEqual(1, len(person.notifyLoginFailure())) # just to init structure
    self.assertFalse(person.isLoginBlocked())
    
    # file two more failures so we should detect and block account
    self.assertEqual(2, len(person.notifyLoginFailure()))
    self.assertEqual(3, len(person.notifyLoginFailure()))

    #import pdb; pdb.set_trace()
    self.assertTrue(person.isLoginBlocked())
    
    # set check back interval to actualy disable blocking
    preference.setPreferredAuthenticationFailureCheckDuration(0)
    self._clearCache()
    self.stepTic()
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

  def test_02_PasswordHistory(self):
    """
      Test password history.
    """
    portal = self.getPortal()
    self.assertTrue(portal.ERP5Site_isAuthenticationPolicyEnabled())
    
    person = portal.portal_catalog.getResultValue(portal_type = 'Person', 
                                                  reference = 'test')
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
                                                      
    # Check that last (X where X is set in preferences) passwords are saved.
    self.assertEqual(None, person.getLastPasswordModificationDate())
    self.assertEqual([], person.getLastChangedPasswordValueList())    
    preference.setPreferredNumberOfLastPasswordToCheck(10)
    self.stepTic()
    self._clearCache()
    
    before = DateTime()
    old_password = person.getPassword()
    person.setPassword('12345678')
    self.stepTic()
    
    # password change date should be saved as well hashed old password value
    self.assertTrue(person.getLastPasswordModificationDate() > before)
    self.assertEqual([old_password], person.getLastChangedPasswordValueList()) 
    
    # .. test one more time to check history of password is saved in a list
    before = DateTime()
    old_password1 = person.getPassword()
    person.setPassword('123456789')
    self.stepTic()
    
    # password change date should be saved as well hashed old password value
    self.assertTrue(person.getLastPasswordModificationDate() > before)
    self.assertEqual([old_password, old_password1], person.getLastChangedPasswordValueList())

  def test_03_PasswordValidity(self):
    """
      Test validity of a password.
    """
      
    portal = self.getPortal()
    
    regular_expression_list = ['([a-z]+)', # english lowercase
                               '([A-Z]+)', # english uppercase
                               '([0-9]+)', # numerals (0-9)
                               '([\\\\$\\\\!\\\\#\\\\%]+)' # (!, $, #, %)
                              ]
    
    self.assertTrue(portal.ERP5Site_isAuthenticationPolicyEnabled())
    
    person = portal.portal_catalog.getResultValue(portal_type = 'Person', 
                                                  reference = 'test')
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)

    # by default an empty password if nothing set in preferences is OK
    self.assertTrue(person.isPasswordValid(''))
    
    # Not long enough passwords used
    self._cleanUpPerson(person)    
    preference.setPreferredMinPasswordLength(8)
    preference.setPreferredNumberOfLastPasswordToCheck(0)    
    self.stepTic()
    self._clearCache()
    
    self.assertFalse(person.isPasswordValid(''))
    self.assertFalse(person.isPasswordValid('1234567'))   
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
    self.assertFalse(person.isPasswordValid('87654321')) # if we try to change now we should fail with any password
    
    preference.setPreferredMinPasswordLifetimeDuration(0) # remove restriction
    self.stepTic()
    self._clearCache()
    self.assertTrue(person.isPasswordValid('87654321')) # it's OK to change
    
    # password not used in previous X passwords
    preference.setPreferredMinPasswordLength(None) # disable for now
    self._cleanUpPerson(person)
    self._clearCache()    
    person.setPassword('12345678')
    self.stepTic()
    self.assertFalse(person.isPasswordValid('12345678')) # if we try to change now we should fail with this EXACT password     
    self.assertTrue(person.isPasswordValid('12345678_')) # it's OK with another one not used yet
    for password in ['a','b','c','d', 'e']:
      person.setPassword(password)
      self.stepTic()
    
    self.assertTrue(person.isPasswordValid('12345678'))
    self.assertTrue(person.isPasswordValid('a'))
    self.assertTrue(person.isPasswordValid('b'))
    # only last 3 (including current one are invalid)
    self.assertFalse(person.isPasswordValid('c'))
    self.assertFalse(person.isPasswordValid('d'))
    self.assertFalse(person.isPasswordValid('e'))
    
    # if we remove restricted then all password are usable
    preference.setPreferredNumberOfLastPasswordToCheck(None)
    self._clearCache()    
    self.stepTic()    
    
    self.assertTrue(person.isPasswordValid('c'))
    self.assertTrue(person.isPasswordValid('d'))
    self.assertTrue(person.isPasswordValid('e'))
    
    # if we set only last password to check
    preference.setPreferredNumberOfLastPasswordToCheck(1)
    self._clearCache()    
    self.stepTic()
    self.assertTrue(person.isPasswordValid('c'))
    self.assertTrue(person.isPasswordValid('d'))
    self.assertFalse(person.isPasswordValid('e'))    
    
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
      self.assertFalse(person.isPasswordValid(password))    

    # min 3 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(3)    
    self._clearCache()
    self._cleanUpPerson(person)    
    self.stepTic()    
    for password in four_group_password_list + three_group_password_list:
      self.assertTrue(person.isPasswordValid(password))
    for password in two_group_password_list + one_group_password_list:
      self.assertFalse(person.isPasswordValid(password))
    
    # min 2 out of all groups
    preference.setPreferredMinRegularExpressionGroupNumber(2)
    self._clearCache()
    self.stepTic()
    for password in four_group_password_list + three_group_password_list + two_group_password_list:
      self.assertTrue(person.isPasswordValid(password))
    for password in one_group_password_list:
      self.assertFalse(person.isPasswordValid(password))
      
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
    self.assertFalse(person.isPasswordValid('abAB#12_%s' %person.getFirstName()))
    self.assertFalse(person.isPasswordValid('abAB#12_%s' %person.getLastName()))
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
    self.assertFalse(temp_person.Person_isPasswordValid('onlyNine1'))
    self.assertTrue(temp_person.Person_isPasswordValid('longEnough1'))
    
    # make sure re check works on temp as well ( i.e. min 3 out of all groups)
    preference.setPreferredRegularExpressionGroupList(regular_expression_list)    
    preference.setPreferredMinPasswordLength(7)    
    preference.setPreferredMinRegularExpressionGroupNumber(3)    
    self._clearCache()
    self.stepTic()    
    for password in four_group_password_list + three_group_password_list:
      self.assertTrue(temp_person.Person_isPasswordValid(password))
    for password in two_group_password_list + one_group_password_list:
      self.assertFalse(temp_person.Person_isPasswordValid(password))
      
    # make sure peron's check on username works on temp as well (i.e. not contain the full name of the user)
    preference.setPrefferedForceUsernameCheckInPassword(1)
    self._clearCache()
    self.stepTic()
    self.assertFalse(temp_person.Person_isPasswordValid('abAB#12_%s' %first_name))
    self.assertFalse(temp_person.Person_isPasswordValid('abAB#12_%s' %last_name))
    
    preference.setPrefferedForceUsernameCheckInPassword(0)
    self._clearCache()
    self.stepTic()
    self.assertTrue(temp_person.Person_isPasswordValid('abAB#12_%s' %first_name))
    self.assertTrue(temp_person.Person_isPasswordValid('abAB#12_%s' %last_name))    
      

  def test_04_PasswordExpire(self):
    """
      Test password expire.
    """
    portal = self.getPortal()
    request = self.app.REQUEST
    
    self.assertTrue(portal.ERP5Site_isAuthenticationPolicyEnabled())
    
    person = portal.portal_catalog.getResultValue(portal_type = 'Person', 
                                                  reference = 'test')
    preference = portal.portal_catalog.getResultValue(portal_type = 'System Preference',
                                                      title = 'Authentication',)
                                                      
    preference.setPreferredMaxPasswordLifetimeDuration(24)
    self.stepTic()
    self._clearCache()
    self.assertFalse(person.isPasswordExpired())
    self.assertFalse(request['is_user_account_password_expired'])
    
    # set older last password modification date just for test
    now = DateTime()
    person.setLastPasswordModificationDate(now - 2)
    self.stepTic()
    self._clearCache()
    self.assertTrue(person.isPasswordExpired())
    self.assertTrue(request['is_user_account_password_expired'])    
    
    # set longer password validity interval
    person.setLastPasswordModificationDate(now)
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
    self.assertTrue(request['is_user_account_password_expired_warning_on'])
    
    # test early warning password expire notification is detected
    preference.setPreferredPasswordLifetimeExpireWarningDuration(4*24-24) # password expire notification appear 3 days befor time
    self.stepTic()
    self._clearCache()
    self.assertFalse(person.isPasswordExpired())
    #import pdb; pdb.set_trace()
    self.assertFalse(request['is_user_account_password_expired_warning_on']) 
            
    
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestAuthenticationPolicy))
  return suite
