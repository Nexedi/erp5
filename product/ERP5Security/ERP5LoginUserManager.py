##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from functools import partial
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.AuthEncoding import pw_validate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from DateTime import DateTime

# This user is used to bypass all security checks.
SUPER_USER = '__erp5security-=__'

manage_addERP5LoginUserManagerForm = PageTemplateFile(
  'www/ERP5Security_addERP5LoginUserManager', globals(),
  __name__='manage_addERP5LoginUserManagerForm' )

def addERP5LoginUserManager(dispatcher, id, title=None, RESPONSE=None):
  """ Add a ERP5LoginUserManager to a Pluggable Auth Service. """
  eum = ERP5LoginUserManager(id, title)
  dispatcher._setObject(eum.getId(), eum)
  if RESPONSE is not None:
    RESPONSE.redirect(eum.absolute_url() + '/manage_main')

class ERP5LoginUserManager(BasePlugin):
  """ PAS plugin for managing users in ERP5
  """
  meta_type = 'ERP5 Login User Manager'
  login_portal_type = 'ERP5 Login'
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    self._id = self.id = id
    self.title = title

  #
  #   IAuthenticationPlugin implementation
  #
  security.declarePrivate('authenticateCredentials')
  def authenticateCredentials(self, credentials):
    login_portal_type = credentials.get(
      'login_portal_type',
      self.login_portal_type,
    )
    if 'external_login' in credentials:
      # External plugin: extractor plugin can validate credential validity.
      # Our job is to locate the actual user and check related documents
      # (assignments...).
      check_password = False
      login_value = self._getLoginValueFromLogin(
        credentials.get('external_login'),
        login_portal_type=login_portal_type,
      )
    elif 'login_relative_url' in credentials:
      # Path-based login: extractor plugin can validate credential validity and
      # directly locate the login document. Our job is to check related
      # documents (assignments...).
      check_password = False
      login_value = self.getPortalObject().unrestrictedTraverse(
        credentials.get("login_relative_url"),
      )
    else:
      # Traditional login: find login document from credentials, check password
      # and check related documents (assignments...).
      check_password = True
      login_value = self._getLoginValueFromLogin(
        credentials.get('login'),
        login_portal_type=login_portal_type,
      )
    if login_value is None:
      return
    user_value = login_value.getParentValue()
    if user_value.getValidationState() == 'deleted':
      return
    now = DateTime()
    for assignment in user_value.contentValues(portal_type="Assignment"):
      if assignment.getValidationState() == "open" and (
        not assignment.hasStartDate() or assignment.getStartDate() <= now
      ) and (
        not assignment.hasStopDate() or assignment.getStopDate() >= now
      ):
        break
    else:
      return
    is_authentication_policy_enabled = self.getPortalObject().portal_preferences.isAuthenticationPolicyEnabled()
    if check_password:
      password = credentials.get('password')
      if not password or not pw_validate(
        login_value.getPassword(),
        password,
      ):
        if is_authentication_policy_enabled:
          login_value.notifyLoginFailure()
      return
    if is_authentication_policy_enabled:
      if login_value.isPasswordExpired():
        login_value.notifyPasswordExpire()
        return
      if login_value.isLoginBlocked():
        return
    return (user_value.getReference(), login_value.getReference())

  def _getLoginValueFromLogin(self, login, login_portal_type=None):
    # Forbidden the usage of the super user.
    if login == SUPER_USER:
      return None
    user_list = self.enumerateUsers(
      login=login,
      exact_match=True,
      login_portal_type=login_portal_type,
    )
    if not user_list:
      return
    single_user, = user_list
    single_login, = single_user['login_list']
    return self.getPortalObject().unrestrictedTraverse(
      single_login['path'],
    )

  #
  #   IUserEnumerationPlugin implementation
  #
  security.declarePrivate('enumerateUsers')
  def enumerateUsers(self, id=None, login=None, exact_match=False,
             sort_by=None, max_results=None, login_portal_type=None, **kw):
    """ See IUserEnumerationPlugin.
    """
    unrestrictedSearchResults = self.getPortalObject(
      ).portal_catalog.unrestrictedSearchResults
    searchUser = lambda **kw: unrestrictedSearchResults(
      select_list=('reference', ),
      portal_type='Person',
      **kw
    ).dictionaries()
    searchLogin = lambda **kw: unrestrictedSearchResults(
      select_list=('parent_uid', 'reference'),
      validation_state='validated',
      **kw
    ).dictionaries()
    if login_portal_type is not None:
      searchLogin = partial(searchLogin, portal_type=login_portal_type)
    if login is None:
      # Only search by id if login is not given. Same logic as in
      # PluggableAuthService.searchUsers.
      if isinstance(id, str):
        id = (id, )
      id_list = []
      has_super_user = False
      for user_id in id:
        if user_id == SUPER_USER:
          has_super_user = True
        elif user_id:
          id_list.append(user_id)
      if id_list:
        if exact_match:
          requested = set(id_list).__contains__
        else:
          requested = lambda x: True
        user_list = [
          x for x in searchUser(
            reference={
              'query': id_list,
              'key': 'ExactMatch' if exact_match else 'Keyword',
            },
            limit=max_results,
          )
          if requested(x['reference'])
        ]
      else:
        user_list = []
      login_dict = {}
      if user_list:
        for login in searchLogin(parent_uid=[x['uid'] for x in user_list]):
          login_dict.setdefault(login['parent_uid'], []).append(login)
      if has_super_user:
        user_list.append({'uid': None, 'reference': SUPER_USER})
        login_dict[None] = [{
          'reference': SUPER_USER,
          'path': None,
          'uid': None,
        }]
    else:
      if isinstance(login, str):
        login = (login, )
      login_dict = {}
      if exact_match:
        requested = set(login).__contains__
      else:
        requested = lambda x: True
      if login:
        for login in searchLogin(
          reference={
            'query': login,
            'key': 'ExactMatch' if exact_match else 'Keyword',
          },
          limit=max_results,
        ):
          if requested(login['reference']):
            login_dict.setdefault(login['parent_uid'], []).append(login)
      if login_dict:
        user_list = searchUser(uid=list(login_dict))
      else:
        user_list = []
    plugin_id = self.getId()
    return tuple([
      {
        'id': user['reference'],
        # Note: PAS forbids us from returning more than one entry per given id,
        # so take any available login.
        'login': login_dict.get(user['uid'], [None])[0]['reference'],
        'pluginid': plugin_id,

        # Extra properties, specific to ERP5
        'path': user['path'],
        'login_list': [
          {
            'reference': login['reference'],
            'path': login['path'],
            'uid': login['uid'],
          }
          for login in login_dict.get(user['uid'], [])
        ],
      }
      for user in user_list
    ])

classImplements(ERP5LoginUserManager, IAuthenticationPlugin, IUserEnumerationPlugin)
InitializeClass(ERP5LoginUserManager)
