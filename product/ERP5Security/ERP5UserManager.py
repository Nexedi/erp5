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
""" Classes: ERP5UserManager
"""

from six import string_types as basestring
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.AuthEncoding import pw_validate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.PluggableAuthService import \
    _SWALLOWABLE_PLUGIN_EXCEPTIONS
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from Products.ERP5Type.Cache import CachingMethod, transactional_cached
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from ZODB.POSException import ConflictError
from DateTime import DateTime
from zLOG import LOG, PROBLEM
from Products import ERP5Security

manage_addERP5UserManagerForm = PageTemplateFile(
  'www/ERP5Security_addERP5UserManager', globals(),
  __name__='manage_addERP5UserManagerForm' )

def addERP5UserManager(dispatcher, id, title=None, REQUEST=None):
  """ Add a ERP5UserManager to a Pluggable Auth Service. """

  eum = ERP5UserManager(id, title)
  dispatcher._setObject(eum.getId(), eum)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5UserManager+added.'
      % dispatcher.absolute_url())

class _AuthenticationFailure(Exception):
  """Raised when authentication failed, to prevent caching the fact that a user
  does not exist (yet), which happens when someone try to login before the user
  account is ready (like when the indexing not finished, an assignment not open
  etc...)
  """

@transactional_cached(lambda portal, *args: args)
def getUserByLogin(portal, login, exact_match=True):
  if isinstance(login, basestring):
    login = login,
  if exact_match:
    reference_key = 'ExactMatch'
  else:
    reference_key = 'Keyword'
  if not (portal.portal_catalog.hasColumn('portal_type') and portal.portal_catalog.hasColumn('reference')):
    raise RuntimeError('Catalog does not have column information. Make sure RDB is working and disk is not full.')
  result = portal.portal_catalog.unrestrictedSearchResults(
    select_list=('reference', ),
    portal_type="Person",
    reference=dict(query=login, key=reference_key))
  # XXX: Here, we filter catalog result list ALTHOUGH we did pass
  # parameters to unrestrictedSearchResults to restrict result set.
  # This is done because the following values can match person with
  # reference "foo":
  # "foo " because of MySQL (feature, PADSPACE collation):
  #  mysql> SELECT reference as r FROM catalog
  #      -> WHERE reference="foo      ";
  #  +-----+
  #  | r   |
  #  +-----+
  #  | foo |
  #  +-----+
  #  1 row in set (0.01 sec)
  # "bar OR foo" because of ZSQLCatalog tokenizing searched strings
  #  by default (feature).
  return [x.getObject() for x in result if not exact_match
                                           or x['reference'] in login]

@transactional_cached(lambda portal, *args: args)
def getValidAssignmentList(user):
  """Returns list of valid assignments."""
  assignment_list = [x for x in user.contentValues(portal_type="Assignment") if x.getValidationState() == "open"]
  valid_assignment_list = []
  # check dates if exist
  login_date = DateTime()
  for assignment in assignment_list:
    if assignment.getStartDate() is not None and \
           assignment.getStartDate() > login_date:
      continue
    if assignment.getStopDate() is not None and \
           assignment.getStopDate() < login_date:
      continue
    valid_assignment_list.append(assignment)
  return valid_assignment_list

class ERP5UserManager(BasePlugin):
  """ PAS plugin for managing users in ERP5
  """

  meta_type = 'ERP5 User Manager'

  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    self._id = self.id = id
    self.title = title

  #
  #   IAuthenticationPlugin implementation
  #
  security.declarePrivate( 'authenticateCredentials' )
  def authenticateCredentials(self, credentials):
    """ See IAuthenticationPlugin.

    o We expect the credentials to be those returned by
      ILoginPasswordExtractionPlugin.
    """
    login = credentials.get('login')
    ignore_password = False
    if not login:
      # fallback to support plugins using external tools to extract login
      # those are not using login/password pair, they just extract login
      # from remote system (eg. SSL certificates)
      login = credentials.get('external_login')
      ignore_password = True
    # Forbidden the usage of the super user.
    if login == ERP5Security.SUPER_USER:
      return None

    @UnrestrictedMethod
    def _authenticateCredentials(login, password, path,
      ignore_password=False):
      if not login or not (password or ignore_password):
        return None

      user_list = self.getUserByLogin(login)

      if not user_list:
        raise _AuthenticationFailure()

      user = user_list[0]

      try:

        if (ignore_password or pw_validate(user.getPassword(), password)) and \
            len(getValidAssignmentList(user)) and user  \
            .getValidationState() != 'deleted': #user.getCareerRole() == 'internal':
          return login, login # use same for user_id and login
      finally:
        pass
      raise _AuthenticationFailure()

    _authenticateCredentials = CachingMethod(
      _authenticateCredentials,
      id='ERP5UserManager_authenticateCredentials',
      cache_factory='erp5_content_short')
    try:
      authentication_result = _authenticateCredentials(
        login=login,
        password=credentials.get('password'),
        path=self.getPhysicalPath(),
        ignore_password=ignore_password)

    except _AuthenticationFailure:
      authentication_result = None

    if not self.getPortalObject().portal_preferences.isAuthenticationPolicyEnabled():
      # stop here, no authentication policy enabled
      # so just return authentication check result
      return authentication_result

    # authentication policy enabled, we need person object anyway
    user_list = self.getUserByLogin(credentials.get('login'))
    if not user_list:
      # not an ERP5 Person object
      return None
    user = user_list[0]

    if authentication_result is None:
      # file a failed authentication attempt
      user.notifyLoginFailure()
      return None

    # check if password is expired
    if user.isPasswordExpired():
      user.notifyPasswordExpire()
      return None

    # check if user account is blocked
    if user.isLoginBlocked():
      return None

    return authentication_result

  #
  #   IUserEnumerationPlugin implementation
  #
  security.declarePrivate( 'enumerateUsers' )
  def enumerateUsers(self, id=None, login=None, exact_match=False,
             sort_by=None, max_results=None, **kw):
    """ See IUserEnumerationPlugin.
    """
    # Note: this plugin totally ignores the distinction between login and id.
    if id is None:
      id = login
    if isinstance(id, str):
      id = (id,)

    unrestrictedSearchResults = self.getPortalObject(
      ).portal_catalog.unrestrictedSearchResults
    searchUser = lambda **kw: unrestrictedSearchResults(
      select_list=('reference', ),
      portal_type='Person',
      **kw
    ).dictionaries()
    # Only search by id if login is not given. Same logic as in
    # PluggableAuthService.searchUsers.
    if isinstance(id, str):
      id = (id, )
    id_list = []
    has_super_user = False
    for user_id in id:
      if user_id == ERP5Security.SUPER_USER:
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
    if has_super_user:
      user_list.append({'uid': None, 'path': None, 'reference': ERP5Security.SUPER_USER})
    plugin_id = self.getId()
    return tuple([
      {
        'id': user['reference'],
        # Note: PAS forbids us from returning more than one entry per given id,
        # so take any available login.
        'login': user['reference'],
        'pluginid': plugin_id,

        # Extra properties, specific to ERP5
        'path': user['path'],
        'uid': user['uid'],
        'login_list': user['path'] and [
          {
            'reference': user['reference'],
            'path': user['path'],
            'uid': user['uid'],
          }
        ] or [],
      }
      for user in user_list
    ])

  security.declarePrivate( 'updateUser' )
  def updateUser(self, user_id, login_name):
    # Operation not supported here
    return False

  security.declarePrivate( 'updateEveryLoginName' )
  def updateEveryLoginName(self, quit_on_first_error=True):
    # Operation not supported here
    raise NotImplementedError()

  def getUserByLogin(self, login, exact_match=True):
    # Search the Catalog for login and return a list of person objects
    # login can be a string or a list of strings
    # (no docstring to prevent publishing)
    if not login:
      return []
    if isinstance(login, list):
      login = tuple(login)
    elif not isinstance(login, (tuple, str)):
      login = login.getUserName()
    try:
      return getUserByLogin(self.getPortalObject(), login, exact_match)
    except ConflictError:
      raise
    except:
      LOG('ERP5Security', PROBLEM, 'getUserByLogin failed', error=True)
      # Here we must raise an exception to prevent callers from caching
      # a result of a degraded situation.
      # The kind of exception does not matter as long as it's catched by
      # PAS and causes a lookup using another plugin or user folder.
      # As PAS does not define explicitely such exception, we must use
      # the _SWALLOWABLE_PLUGIN_EXCEPTIONS list.
      raise _SWALLOWABLE_PLUGIN_EXCEPTIONS[0]


classImplements( ERP5UserManager
               , IAuthenticationPlugin
               , IUserEnumerationPlugin
               )

InitializeClass(ERP5UserManager)
