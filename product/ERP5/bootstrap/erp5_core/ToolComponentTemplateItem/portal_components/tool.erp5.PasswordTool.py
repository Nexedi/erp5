# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import uuid

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, get_request
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from zLOG import LOG, INFO
from DateTime import DateTime
from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Globals import PersistentMapping
from BTrees.OOBTree import OOBTree
from six.moves.urllib.parse import urlencode

redirect_path = '/login_form'
def redirect(REQUEST, site_url, message):
  if REQUEST is not None and getattr(REQUEST.RESPONSE, 'redirect', None) is not None:
    parameter = urlencode({'portal_status_message': message})
    ret_url = '%s%s?%s' % (site_url, redirect_path, parameter)
    return REQUEST.RESPONSE.redirect( ret_url )
  else:
    return message

class PasswordTool(BaseTool):
  """
    PasswordTool is used to allow a user to change its password
  """
  title = 'Passwords'
  id = 'portal_password'
  meta_type = 'ERP5 Password Tool'
  portal_type = 'Password Tool'
  allowed_types = ()

  # Declarative Security
  security = ClassSecurityInfo()

  _expiration_day = 1

  def __init__(self, id=None): # pylint: disable=redefined-builtin
    super(PasswordTool, self).__init__(id)
    self._password_request_dict = OOBTree()

  security.declareProtected('Manage users', 'getResetPasswordKey')
  def getResetPasswordKey(self, user_login, expiration_date=None):
    if expiration_date is None:
      # generate expiration date
      expiration_date = DateTime() + self._expiration_day

    # generate a random string
    key = uuid.uuid4().hex
    if isinstance(self._password_request_dict, PersistentMapping):
      LOG('ERP5.PasswordTool', INFO, 'Migrating password_request_dict to'
                                     ' OOBTree')
      self._password_request_dict = OOBTree(self._password_request_dict)

    # register request
    self._password_request_dict[key] = (user_login, expiration_date)
    return key

  security.declareProtected('Manage users', 'getResetPasswordUrl')
  def getResetPasswordUrl(self, user_login=None, key=None, site_url=None):
    if user_login is not None:
      # XXX Backward compatibility
      key = self.getResetPasswordKey(user_login)

    parameter = urlencode(dict(reset_key=key))
    method = self._getTypeBasedMethod("getSiteUrl")
    if method is not None:
      base_url = method()
    else:
      base_url = "%s/portal_password/PasswordTool_viewResetPassword" % (
        site_url,)
    url = "%s?%s" %(base_url, parameter)
    return url

  def _getExpirationDateForKey(self, key=None):
    return self._password_request_dict[key][1]

  security.declarePublic('mailPasswordResetRequest')
  def mailPasswordResetRequest(self, user_login=None, REQUEST=None,
                               notification_message=None, sender=None,
                               store_as_event=False,
                               expiration_date=None,
                               substitution_method_parameter_dict=None,
                               batch=False):
    """
    Create a random string and expiration date for request
    Parameters:
    user_login -- Reference of the user to send password reset link
    REQUEST -- Request object
    notification_message -- Notification Message Document used to build the email.
                            As default, a standard text will be used.
    sender -- Sender (Person or Organisation) of the email.
            As default, the default email address will be used
    store_as_event -- whenever CRM is available, store
                        notifications as events
    expiration_date -- If not set, expiration date is current date + 1 day.
    substitution_method_parameter_dict -- additional substitution dict for
                                          creating an email.
    """
    error_encountered = False
    msg = translateString("An email has been sent to you.")
    if REQUEST is None:
      REQUEST = get_request()

    if user_login is None:
      user_login = REQUEST["user_login"]

    site_url = self.getPortalObject().absolute_url()
    if REQUEST and 'came_from' in REQUEST:
      site_url = REQUEST.came_from

    error_encountered = False
    # check user exists, and have an email
    user_path_set = {x['path'] for x in self.getPortalObject().acl_users.searchUsers(
      login=user_login,
      exact_match=True,
    ) if 'path' in x}
    if len(user_path_set) == 0:
      error_encountered = True
      LOG(
        'ERP5.PasswordTool', INFO,
        "User {user} does not exist.".format(user=user_login)
      )
    else:
      # We use checked_permission to prevent errors when trying to acquire
      # email from organisation
      user_path, = user_path_set
      user_value = self.getPortalObject().unrestrictedTraverse(
        user_path)
      email_value = user_value.getDefaultEmailValue(
        checked_permission='Access content information')
      if email_value is None or not email_value.asText():
        error_encountered = True
        LOG(
          'ERP5.PasswordTool', INFO,
          "User {user} does not have an email address".format(user=user_login)
        )
      elif email_value.getValidationState() != "reachable":
        error_encountered = True
        LOG(
          'ERP5.PasswordTool', INFO,
          "User {user} does not have a valid email address".format(user=user_login)
        )
    if error_encountered:
      if batch:
        raise RuntimeError(msg)
      else:
        return redirect(REQUEST, site_url, msg)

    key = self.getResetPasswordKey(user_login=user_login,
                                   expiration_date=expiration_date)
    url = self.getResetPasswordUrl(key=key, site_url=site_url)

    # send mail
    message_dict = {'instance_name':self.getPortalObject().getTitle(),
                    'reset_password_link':url,
                    'expiration_date':self._getExpirationDateForKey(key)}
    if substitution_method_parameter_dict is not None:
      message_dict.update(substitution_method_parameter_dict)

    if notification_message is None:
      subject = translateString("[${instance_name}] Reset of your password",
          mapping={'instance_name': self.getPortalObject().getTitle()})
      subject = subject.translate()
      message = translateString("\nYou requested to reset your ${instance_name}"\
                " account password.\n\n" \
                "Please copy and paste the following link into your browser: \n"\
                "${reset_password_link}\n\n" \
                "Please note that this link will be valid only one time, until "\
                "${expiration_date}.\n" \
                "After this date, or after having used this link, you will have to make " \
                "a new request\n\n" \
                "Thank you",
                mapping=message_dict)
      message = message.translate()
      event_keyword_argument_dict={}
      message_text_format = 'text/plain'
    else:
      message_text_format = notification_message.getContentType()
      subject = notification_message.getTitle()
      if message_text_format == "text/html":
        message = notification_message.asEntireHTML(substitution_method_parameter_dict=message_dict)
      else:
        message = notification_message.asText(substitution_method_parameter_dict=message_dict)
      event_keyword_argument_dict={
        'resource':notification_message.getSpecialise(),
        'language':notification_message.getLanguage(),
      }

    self.getPortalObject().portal_notifications.sendMessage(sender=sender, recipient=[user_value,],
                                                            subject=subject, message=message,
                                                            store_as_event=store_as_event,
                                                            message_text_format=message_text_format,
                                                            event_keyword_argument_dict=event_keyword_argument_dict)
    if not batch:
      return redirect(REQUEST, site_url,
                      translateString("An email has been sent to you."))

  security.declareProtected(Permissions.ModifyPortalContent, 'removeExpiredRequests')
  def removeExpiredRequests(self):
    """
    Browse dict and remove expired request
    """
    current_date = DateTime()
    password_request_dict = self._password_request_dict
    for key, (_, date) in password_request_dict.items():
      if date < current_date:
        del password_request_dict[key]

  security.declarePublic('analyzePassword')
  def analyzePassword(self, password, password_key):
    """Analyze password validity in the context of the login.

    Returns a list of messages as returned by IEncryptedPassword.analyzePassword
    """
    portal = self.getPortalObject()
    if not portal.portal_preferences.isAuthenticationPolicyEnabled():
      return []
    try:
      register_user_login, _ = self._password_request_dict[password_key]
    except KeyError:
      return []
    user_dict_list = portal.acl_users.searchUsers(
      login=register_user_login,
      exact_match=True,
    )
    if user_dict_list:
      user_dict, = user_dict_list
      login_dict, = user_dict['login_list']
      login = portal.unrestrictedTraverse(login_dict['path'])
      return login.analyzePassword(password)
    return []

  security.declarePublic('changeUserPassword')
  def changeUserPassword(self, password, password_key, password_confirm=None,
                         user_login=None, REQUEST=None, **kw):
    """
    Reset the password for a given login
    """
    # BBB: password_confirm: unused argument
    def error(message):
      # BBB: should "raise Redirect" instead of just returning, simplifying
      #      calling code and making mistakes more difficult
      # BBB: should probably not translate message when REQUEST is None
      message = translateString(message)
      return redirect(REQUEST, site_url, message)

    if REQUEST is None:
      REQUEST = get_request()
    if self.getWebSiteValue():
      site_url = self.getWebSiteValue().absolute_url()
    elif REQUEST and 'came_from' in REQUEST:
      site_url = REQUEST.came_from
    else:
      site_url = self.getPortalObject().absolute_url()
    try:
      register_user_login, expiration_date = self._password_request_dict[
        password_key]
    except (KeyError, TypeError):
      # XXX: incorrect grammar and not descriptive enough
      return error('Key not known. Please ask reset password.')
    if user_login is not None and register_user_login != user_login:
      # XXX: not descriptive enough
      return error("Bad login provided.")
    if DateTime() > expiration_date:
      return error("Date has expired.")
    del self._password_request_dict[password_key]
    portal = self.getPortalObject()
    user_dict, = [x for x in portal.acl_users.searchUsers(
      login=register_user_login,
      exact_match=True,) if 'login_list' in x]

    login_dict, = user_dict['login_list']
    login = portal.unrestrictedTraverse(login_dict['path'])
    login.setPassword(password) # this will raise if password does not match policy
    return redirect(REQUEST, site_url,
                    translateString("Password changed."))

InitializeClass(PasswordTool)
