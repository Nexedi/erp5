##############################################################################
#
# Copyright (c) 2016 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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
from functools import partial
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.AuthEncoding import pw_validate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from DateTime import DateTime
from Products import ERP5Security
from AccessControl import SpecialUsers
from Shared.DC.ZRDB.DA import DatabaseError
from zLOG import LOG, ERROR

SYSTEM_USER_USER_NAME = SpecialUsers.system.getUserName()
# To prevent login thieves
SPECIAL_USER_NAME_SET = (
  ERP5Security.SUPER_USER,
  SpecialUsers.nobody.getUserName(),
  SYSTEM_USER_USER_NAME,
  # Note: adding emergency_user is pointless as its login is variable, so no
  # way to prevent another user from stealing its login.
)

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
    if not user_value.hasUserId():
      return
    if user_value.getValidationState() == 'deleted':
      return
    if user_value.getPortalType() in ('Person', ):
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
      login_password = login_value.getPassword()
      if (not password
          or login_password is None
          or not pw_validate(login_password, password)):
        if is_authentication_policy_enabled:
          login_value.notifyLoginFailure()
        return
    if is_authentication_policy_enabled:
      if login_value.isPasswordExpired():
        login_value.notifyPasswordExpire()
        return
      if login_value.isLoginBlocked():
        return
    return (user_value.getUserId(), login_value.getReference())

  def _getLoginValueFromLogin(self, login, login_portal_type=None):
    try:
      user_list = self.enumerateUsers(
        login=login,
        exact_match=True,
        login_portal_type=login_portal_type,
      )
    except DatabaseError:
      # DatabaseError gets raised when catalog is not functional. In which case
      # it should be fine to bail without any user, letting PAS continue trying
      # other plugins.
      LOG(
        repr(self),
        ERROR,
        'enumerateUsers raised, bailing',
        error=True,
      )
      user_list = []
    if not user_list:
      return
    single_user, = user_list
    single_login, = single_user['login_list']
    path = single_login['path']
    if path is None:
      return
    return self.getPortalObject().unrestrictedTraverse(path)

  #
  #   IUserEnumerationPlugin implementation
  #
  security.declarePrivate('enumerateUsers')
  def enumerateUsers(self, id=None, login=None, exact_match=False,
             sort_by=None, max_results=None, login_portal_type=None, **kw):
    """ See IUserEnumerationPlugin.
    """
    portal = self.getPortalObject()
    if login_portal_type is None:
      login_portal_type = portal.getPortalLoginTypeList()
    unrestrictedSearchResults = portal.portal_catalog.unrestrictedSearchResults
    searchUser = lambda **kw: unrestrictedSearchResults(
      select_list=('user_id', ),
      **kw
    ).dictionaries()
    searchLogin = lambda **kw: unrestrictedSearchResults(
      select_list=('parent_uid', 'reference'),
      validation_state='validated',
      **kw
    ).dictionaries()
    if login_portal_type is not None:
      searchLogin = partial(searchLogin, portal_type=login_portal_type)
    special_user_name_set = set()
    if login is None:
      # Only search by id if login is not given. Same logic as in
      # PluggableAuthService.searchUsers.
      if isinstance(id, str):
        id = (id, )
      # Short-cut "System Processes" as not being searchable by user_id.
      # This improves performance in proxy-role'd execution by avoiding an
      # sql query expected to find no user.
      id = [x for x in id or () if x != SYSTEM_USER_USER_NAME]
      if id:
        if exact_match:
          requested = set(id).__contains__
        else:
          requested = lambda x: True
        user_list = [
          x for x in searchUser(
            user_id={
              'query': id,
              'key': 'ExactMatch' if exact_match else 'Keyword',
            },
            limit=max_results,
          )
          if requested(x['user_id'])
        ]
      else:
        user_list = []
      login_dict = {}
      if user_list:
        for login in searchLogin(parent_uid=[x['uid'] for x in user_list]):
          login_dict.setdefault(login['parent_uid'], []).append(login)
    else:
      if isinstance(login, str):
        login = (login, )
      login_list = []
      for user_login in login:
        if user_login in SPECIAL_USER_NAME_SET:
          special_user_name_set.add(user_login)
        else:
          login_list.append(user_login)
          # Ignore leading or trailing space in login name
          user_login_stripped = user_login.strip()
          if user_login_stripped != user_login:
            login_list.append(user_login_stripped)
      login_dict = {}
      if exact_match:
        requested = set(login_list).__contains__
      else:
        requested = lambda x: True
      if login_list:
        for login in searchLogin(
          reference={
            'query': login_list,
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
    result = [
      {
        'id': user['user_id'],
        # Note: PAS forbids us from returning more than one entry per given id,
        # so take any available login.
        'login': login_dict.get(user['uid'], [{'reference': None}])[0]['reference'],
        'pluginid': plugin_id,

        # Extra properties, specific to ERP5
        'path': user['path'],
        'uid': user['uid'],
        'login_list': [
          {
            'reference': login['reference'],
            'path': login['path'],
            'uid': login['uid'],
          }
          for login in login_dict.get(user['uid'], [])
        ],
      }
      for user in user_list if user['user_id']
    ]
    
    tv = getTransactionalVariable()
    person = tv.get("transactional_user", None) 
    if person is not None:
      erp5_login = person.objectValues("ERP5 Login")[0]
      if (login is not None and erp5_login.getReference() == None) or \
           (id is not None and person.getUserId() == id[0]):
        result.append({
          'id': person.getUserId(),
          # Note: PAS forbids us from returning more than one entry per given id,
          # so take any available login.
          'login': erp5_login.getReference(), 
          'pluginid': plugin_id,

          # Extra properties, specific to ERP5
          'path': person.getPath(),
          'uid': person.getUid(),
          'login_list': [
            {
              'reference': erp5_login.getReference(),
              'path': erp5_login.getRelativeUrl(),
              'uid': erp5_login.getPath(),
            }
          ],
        })

    for special_user_name in special_user_name_set:
      # Note: special users are a bastard design in Zope: they are expected to
      # have a user name (aka, a login), but no id (aka, they do not exist as
      # users). This is likely done to prevent them from having any local role
      # (ownership or otherwise). In reality, they should have an id (they do
      # exist, and user ids are some internal detail where it is easy to avoid
      # such magic strings) and no login (because nobody should ever be able to
      # log in as a special user, and logins are exposed to users (duh !) and
      # hence magic values are impossible to avoid with ad-hoc code peppered
      # everywhere). To avoid such ad-hoc code, this plugin will find magic
      # users so code checking if a user login exists before allowing it to be
      # reused, preventing misleading logins from being misused.
      result.append({
        'id': special_user_name,
        'login': special_user_name,
        'pluginid': plugin_id,

        'path': None,
        'uid': None,
        'login_list': [
          {
            'reference': special_user_name,
            'path': None,
            'uid': None,
          }
        ]
      })
    return tuple(result)

  security.declarePrivate('updateUser')
  def updateUser(self, user_id, login_name):
    # Operation not supported here
    return False

  security.declarePrivate('updateEveryLoginName')
  def updateEveryLoginName(self, quit_on_first_error=True):
    # Operation not supported here
    raise NotImplementedError()


classImplements(ERP5LoginUserManager, IAuthenticationPlugin, IUserEnumerationPlugin)
InitializeClass(ERP5LoginUserManager)
