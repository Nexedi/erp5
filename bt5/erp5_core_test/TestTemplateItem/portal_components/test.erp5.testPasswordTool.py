# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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

import six
from six.moves.urllib.parse import urlparse, parse_qsl

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime


class TestPasswordTool(ERP5TypeTestCase):
  """
  Test reset of password
  """
  def getBusinessTemplateList(self):
    return ('erp5_base', )

  def getTitle(self):
    return "Password Tool"

  def afterSetUp(self):
    self.portal.email_from_address = 'site@example.invalid'
    self.portal.MailHost.reset()
    self.portal.portal_caches.clearAllCache()
    self._createUser("userA")

  def _createUser(self, base_name):
    person = self.portal.person_module.newContent(
      portal_type="Person",
      reference=base_name,
      default_email_text="{base_name}@example.invalid".format(base_name=base_name))
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='{base_name}-login'.format(base_name=base_name),
      password='{base_name}-password'.format(base_name=base_name),
    )
    login.validate()
    self.tic()

  def beforeTearDown(self):
    self.abort()
    # clear modules if necessary
    self.portal.person_module.manage_delObjects(list(self.portal.person_module.objectIds()))
    # reset password tool internal structure
    self.portal.portal_password._password_request_dict.clear()
    self.tic()

  def getUserFolder(self):
    """Returns the acl_users. """
    return self.portal.acl_users

  def _assertUserExists(self, login, password):
    """Checks that a user with login and password exists and can log in to the
    system.
    """
    from Products.PluggableAuthService.interfaces.plugins import\
                                                      IAuthenticationPlugin
    uf = self.getUserFolder()
    self.assertNotEqual(uf.getUser(login), None)
    for _, plugin in uf._getOb('plugins').listPlugins(
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

  def test_password_reset(self):
    self._assertUserExists('userA-login', 'userA-password')
    self._assertUserDoesNotExists('userA-login', 'bad')
    ret = self.portal.portal_password.mailPasswordResetRequest(
      user_login='userA-login', REQUEST=self.portal.REQUEST)

    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "An email has been sent to you."), query_string_param)
    self.assertIn(("portal_status_level", "success"), query_string_param)
    self.tic()

    (mfrom, mto, mbody), = self.portal.MailHost.getMessageList()
    self.assertEqual('Portal Administrator <site@example.invalid>', mfrom)
    self.assertEqual(['userA@example.invalid'], mto)
    reset_key, = list(six.iterkeys(self.portal.portal_password._password_request_dict))
    self.assertIn(
      ('PasswordTool_viewResetPassword?reset_key=' + reset_key),
      mbody)

    ret = self.portal.portal_password.changeUserPassword(
        user_login="userA-login",
        password="new-password",
        password_confirm="new-password",
        password_key=reset_key)
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "Password changed."), query_string_param)
    self.assertIn(("portal_status_level", "success"), query_string_param)
    self.tic()
    self._assertUserExists('userA-login', 'new-password')
    self._assertUserDoesNotExists('userA-login', 'userA-password')

    # key no longer work
    ret = self.portal.portal_password.changeUserPassword(
        user_login="userA-login",
        password="new-password",
        password_confirm="new-password",
        password_key=reset_key)
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "Key not known. Please ask reset password."), query_string_param)
    self.assertIn(("portal_status_level", "error"), query_string_param)
    self.tic()
    self._assertUserExists('userA-login', 'new-password')
    self._assertUserDoesNotExists('userA-login', 'userA-password')

  def test_password_reset_request_for_non_existing_user(self):
    ret = self.portal.portal_password.mailPasswordResetRequest(
      user_login='not exist', REQUEST=self.portal.REQUEST)
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "An email has been sent to you."), query_string_param)
    self.assertIn(("portal_status_level", "success"), query_string_param)
    self.tic()
    self.assertFalse(self.portal.MailHost.getMessageList())

  def test_password_reset_request_for_wildcard_username(self):
    ret = self.portal.portal_password.mailPasswordResetRequest(
      user_login='%', REQUEST=self.portal.REQUEST)
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "An email has been sent to you."), query_string_param)
    self.assertIn(("portal_status_level", "success"), query_string_param)
    self.tic()
    self.assertFalse(self.portal.MailHost.getMessageList())

  def test_password_reset_request_for_different_user(self):
    self._createUser('userB')
    self.portal.portal_password.mailPasswordResetRequest(
      user_login='userA-login', REQUEST=self.portal.REQUEST)
    reset_key, = list(six.iterkeys(
      self.portal.portal_password._password_request_dict))

    ret = self.portal.portal_password.changeUserPassword(
        user_login="userB-login",
        password="new-password",
        password_confirm="new-password",
        password_key=reset_key)
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "Bad login provided."), query_string_param)
    self.assertIn(("portal_status_level", "error"), query_string_param)
    self.tic()
    self._assertUserExists('userA-login', 'userA-password')
    self._assertUserExists('userB-login', 'userB-password')
    self._assertUserDoesNotExists('userB-login', 'new-password')

  def test_password_reset_unknown_key(self):
    self.portal.portal_password.mailPasswordResetRequest(
      user_login='userA-login', REQUEST=self.portal.REQUEST)
    ret = self.portal.portal_password.changeUserPassword(
        user_login="userA-login",
        password="new-password",
        password_confirm="new-password",
        password_key='wrong key')
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "Key not known. Please ask reset password."), query_string_param)
    self.assertIn(("portal_status_level", "error"), query_string_param)
    self.tic()

  def test_password_reset_date_expired(self):
    self.portal.portal_password.mailPasswordResetRequest(user_login='userA-login')
    (reset_key, (login, date)), = list(six.iteritems(
      self.portal.portal_password._password_request_dict))
    self.assertTrue(date.isFuture())
    self.portal.portal_password._password_request_dict[reset_key] = (
      login,
      DateTime() - 1
    )
    ret = self.portal.portal_password.changeUserPassword(
        user_login="userA-login",
        password="new-password",
        password_confirm="new-password",
        password_key=reset_key)
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "Date has expired."), query_string_param)
    self.assertIn(("portal_status_level", "error"), query_string_param)
    self.tic()

    self._assertUserExists('userA-login', 'userA-password')
    self._assertUserDoesNotExists('userA-login', 'new-password')

    self.portal.portal_password.removeExpiredRequests()
    self.assertFalse(list(six.iterkeys(
      self.portal.portal_password._password_request_dict)))

  def test_password_reset_password_and_confirmation_do_not_match(self):
    self.portal.portal_password.mailPasswordResetRequest(
      user_login='userA-login', REQUEST=self.portal.REQUEST)
    reset_key, = list(six.iterkeys(
      self.portal.portal_password._password_request_dict))

    ret = self.portal.portal_password.changeUserPassword(
        user_login="userA-login",
        password="new-password",
        password_confirm="wrong-password",
        password_key=reset_key)
    query_string_param = parse_qsl(urlparse(str(ret)).query)
    self.assertIn(("portal_status_message", "Password does not match the confirm password."), query_string_param)
    self.assertIn(("portal_status_level", "error"), query_string_param)

  def test_two_concurrent_password_reset(self):
    self._createUser('userB')
    self._assertUserExists('userA-login', 'userA-password')
    self._assertUserExists('userB-login', 'userB-password')

    self.assertEqual(0, len(self.portal.portal_password._password_request_dict))
    self.portal.portal_password.mailPasswordResetRequest(user_login="userA-login")
    self.assertEqual(1, len(self.portal.portal_password._password_request_dict))
    key_a = list(six.iterkeys(self.portal.portal_password._password_request_dict))[0]
    self.tic()

    self.portal.portal_password.mailPasswordResetRequest(user_login="userB-login")
    possible_key_list = \
      list(six.iterkeys(self.portal.portal_password._password_request_dict))
    self.assertEqual(2, len(possible_key_list))
    key_b = [k for k in possible_key_list if k != key_a][0]
    self.tic()

    self._assertUserExists('userA-login', 'userA-password')
    self._assertUserExists('userB-login', 'userB-password')

    self.portal.portal_password.changeUserPassword(user_login="userA-login",
                                                   password="newA",
                                                   password_confirm="newA",
                                                   password_key=key_a)
    self.tic()

    self._assertUserExists('userA-login', 'newA')
    self._assertUserExists('userB-login', 'userB-password')

    self.portal.portal_password.changeUserPassword(user_login="userB-login",
                                                   password="newB",
                                                   password_confirm="newB",
                                                   password_key=key_b)
    self.tic()

    self._assertUserExists('userA-login', 'newA')
    self._assertUserExists('userB-login', 'newB')

  def test_login_with_trailing_space(self):
    person = self.portal.person_module.newContent(portal_type="Person",
                                    reference="userZ ",
                                    default_email_text="userA@example.invalid")
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='userZ-login ',
      password='passwordZ',
    )
    login.validate()

    self.tic()

    self._assertUserExists('userZ-login ', 'passwordZ')

    self.assertEqual(0, len(self.portal.portal_password._password_request_dict))
    # No reset should be send if trailing space is not entered
    self.portal.portal_password.mailPasswordResetRequest(user_login="userZ-login")
    self.assertEqual(0, len(self.portal.portal_password._password_request_dict))
    self.portal.portal_password.mailPasswordResetRequest(user_login="userZ-login ")
    self.assertEqual(1, len(self.portal.portal_password._password_request_dict))
    key_a, = list(six.iterkeys(self.portal.portal_password._password_request_dict))
    self.tic()

    self._assertUserExists('userZ-login ', 'passwordZ')

    # Check that password is not changed if trailing space is not entered
    self.portal.portal_password.changeUserPassword(user_login="userZ-login",
                                                   password="newZ",
                                                   password_confirm="newZ",
                                                   password_key=key_a)
    self.tic()
    self._assertUserExists('userZ-login ', 'passwordZ')

    # Check that password is changed if trailing space is entered
    self.portal.portal_password.changeUserPassword(user_login="userZ-login ",
                                                   password="newZ2",
                                                   password_confirm="newZ2",
                                                   password_key=key_a)
    self.tic()
    self._assertUserExists('userZ-login ', 'newZ2')

  def test_no_email_on_person(self):
    person = self.portal.person_module.newContent(portal_type="Person",
                                    reference="user",)
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='user-login',
      password='password',
    )
    login.validate()

    self.tic()
    self.logout()
    ret = self.portal.portal_password.mailPasswordResetRequest(
                  user_login='user-login', REQUEST=self.portal.REQUEST)

    query_string_param = parse_qsl(urlparse(str(ret)).query)
    # For security reasons, the message should always be the same
    self.assertIn(("portal_status_message", "An email has been sent to you."), query_string_param)
    self.assertIn(("portal_status_level", "success"), query_string_param)

    # But no mail has been sent
    self.assertFalse(self.portal.MailHost.getMessageList())

  def test_unreachable_email_on_person(self):
    person = self.portal.person_module.newContent(
      portal_type="Person",
      reference="user",
      default_email_text="user@example.invalid",
    )
    person.getDefaultEmailValue().declareUnreachable()
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='user-login',
      password='password',
    )
    login.validate()

    self.tic()
    self.logout()
    ret = self.portal.portal_password.mailPasswordResetRequest(
                  user_login='user-login', REQUEST=self.portal.REQUEST)

    query_string_param = parse_qsl(urlparse(str(ret)).query)
    # For security reasons, the message should always be the same
    self.assertIn(("portal_status_message", "An email has been sent to you."), query_string_param)
    self.assertIn(("portal_status_level", "success"), query_string_param)

    # But no mail has been sent
    self.assertFalse(self.portal.MailHost.getMessageList())

  def test_acquired_email_on_person(self):
    organisation = self.portal.organisation_module.newContent(
                                    portal_type='Organisation',
                                    default_email_text="organisation@example.com",)
    person = self.portal.person_module.newContent(portal_type="Person",
                                    reference="user",
                                    default_career_subordination_value=organisation)
    assignment = person.newContent(portal_type='Assignment')
    assignment.open()
    login = person.newContent(
      portal_type='ERP5 Login',
      reference='user-login',
      password='password',
    )
    login.validate()

    self.tic()
    self._assertUserExists('user-login', 'password')
    self.logout()
    ret = self.portal.portal_password.mailPasswordResetRequest(
                  user_login='user-login', REQUEST=self.portal.REQUEST)

    query_string_param = parse_qsl(urlparse(str(ret)).query)
    # For security reasons, the message should always be the same
    self.assertIn(("portal_status_message", "An email has been sent to you."), query_string_param)
    self.assertIn(("portal_status_level", "success"), query_string_param)
    # But no mail has been sent
    self.assertFalse(self.portal.MailHost.getMessageList())

