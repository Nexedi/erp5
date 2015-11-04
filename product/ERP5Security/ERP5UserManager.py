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
import sys
from DateTime import DateTime
from zLOG import LOG, PROBLEM

# This user is used to bypass all security checks.
SUPER_USER = '__erp5security-=__'

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
    select_expression='reference',
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


class ERP5UserManager(BasePlugin):
  """ PAS plugin for managing users in ERP5
  """

  meta_type = 'ERP5 User Manager'
  login_portal_type = 'ERP5 Login'

  security = ClassSecurityInfo()

  def __init__(self, id, title=None):

    self._id = self.id = id
    self.title = title

  def getLoginPortalType(self):
    return self.login_portal_type

  def getPersonByReference(self, reference):
    def _getPersonRelativeUrlFromReference(reference):
      person_url = self.REQUEST.get('_login_cache', {}).get(reference)
      portal = self.getPortalObject()
      if person_url is not None:
        return person_url
      else:
        person_list = portal.portal_catalog.unrestrictedSearchResults(
          select_list=('relative_url',),
          portal_type='Person',
          reference={'query': reference, 'key': 'ExactMatch'},
          limit=2
        )
        l = len(person_list)
        if l > 1:
          raise RuntimeError, 'More than one Person have login %r' % \
            (reference,)
        elif l == 1:
          return person_list[0]['relative_url']
    _getPersonRelativeUrlFromReference = CachingMethod(
      _getPersonRelativeUrlFromReference,
      id='ERP5UserManager._getPersonRelativeUrlFromReference',
      cache_factory='erp5_content_short')
    person_relative_url = _getPersonRelativeUrlFromReference(reference)
    if person_relative_url is not None:
      return self.getPortalObject().unrestrictedTraverse(
        person_relative_url)

  def checkPersonValidity(self, person):
    if person.getValidationState() in ('deleted',):
      return False
    now = DateTime()
    for assignment in person.contentValues(portal_type="Assignment"):
      if assignment.getValidationState() != "open":
         continue
      if assignment.hasStartDate() and \
           assignment.getStartDate() > now:
         continue
      if assignment.hasStopDate() and \
           assignment.getStopDate() < now:
         continue
      return True
    return False

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
    if login == SUPER_USER:
      return None

    @UnrestrictedMethod
    def _authenticateCredentials(login, password, portal_type,
      ignore_password=False):
      if not login or not (password or ignore_password):
        return None, None

      login_object = self.getLoginObject(login, portal_type)

      if not login_object:
        raise _AuthenticationFailure(None)

      if login_object.getPortalType() == 'Person':
        # BBB
        user = login_object
      else:
        user = login_object.getParentValue()

      try:
        if self.checkPersonValidity(user) and \
            (ignore_password or self._validatePassword(login_object, password)):
          return user.getReference(), login_object.getRelativeUrl()
      finally:
        pass
      raise _AuthenticationFailure(login_object.getRelativeUrl())

    _authenticateCredentials = CachingMethod(
      _authenticateCredentials,
      id=self.__class__.__name__ + '_authenticateCredentials',
      cache_factory='erp5_content_short')
    try:
      user_reference, login_url = _authenticateCredentials(
        login=login,
        password=credentials.get('password'),
        portal_type=credentials.get('login_portal_type',
                                    self.login_portal_type),
        ignore_password=ignore_password)
    except _AuthenticationFailure, exception:
      user_reference = None
      login_url = exception.message or None

    if user_reference and '_login_cache' not in self.REQUEST:
      self.REQUEST.set('_login_cache', {})
      self.REQUEST['_login_cache'][user_reference] = login_url
    if not self.getPortalObject().portal_preferences.isAuthenticationPolicyEnabled():
      # stop here, no authentication policy enabled
      # so just return authentication check result
      if user_reference:
        return (user_reference, user_reference)
      else:
        return None

    if login_url is None:
      return None

    # authentication policy enabled, we need person object anyway
    login = self.getPortalObject().unrestrictedTraverse(login_url)

    if user_reference is None:
      # file a failed authentication attempt
      login.notifyLoginFailure()
      return None

    # check if password is expired
    if login.isPasswordExpired():
      login.notifyPasswordExpire()
      return None

    # check if login is blocked
    if login.isLoginBlocked():
      return None

    return (user_reference, user_reference)

  def _validatePassword(self, login_object, password):
    return pw_validate(login_object.getPassword(), password)

  #
  #   IUserEnumerationPlugin implementation
  #
  security.declarePrivate( 'enumerateUsers' )
  def enumerateUsers(self, id=None, login=None, exact_match=False,
             sort_by=None, max_results=None, **kw):
    """ See IUserEnumerationPlugin.
    """
    if not id:
      id = login
    if isinstance(id, str):
      id = (id,)
    if isinstance(id, list):
      id = tuple(id)

    user_info = []
    plugin_id = self.getId()

    id_list = []
    for user_id in id:
      if SUPER_USER == user_id:
        info = {'id' : SUPER_USER,
                'login' : SUPER_USER,
                'pluginid' : plugin_id,
               }
        user_info.append(info)
      else:
        id_list.append(user_id)

    if id_list:
      if exact_match:
        for reference in id_list:
          user = self.getPersonByReference(reference)
          if user is not None:
            info = {'id': reference,
                    'login' : reference,
                    'pluginid': plugin_id,
                   }
            user_info.append(info)
      else:
        for user in self.getPortalObject().portal_catalog.unrestrictedSearchResults(
          select_list=('reference',),
          portal_type='Person',
          reference={'query': id_list, 'key': 'Keyword'},
        ):
          info = {'id': user['reference'],
                  'login' : user['reference'],
                  'pluginid' : plugin_id,
                 }
          user_info.append(info)

    return tuple(user_info)

  @transactional_cached(lambda self, *args: args)
  def getLoginObject(self, login, portal_type):
    try:
      if not login:
        return
      catalog_result = self.getPortalObject().portal_catalog.unrestrictedSearchResults(
        select_expression=('portal_type', 'reference', 'validation_state'),
        portal_type=(portal_type, 'Person'),
        reference=dict(query=login, key='ExactMatch'),
        sort_on=(('portal_type',),),
      )
      for x in catalog_result:
        if x['portal_type'] != 'Person' and x['validation_state'] != 'validated':
          continue
        if x['reference'] != login:
          continue
        x = x.getObject()
        if x.objectIds(spec='ERP5 Login'):
          continue # Already migrated.
        return x
    except ConflictError:
      raise
    except:
      LOG('ERP5Security', PROBLEM, 'getLoginObject failed', error=sys.exc_info())
      # Here we must raise an exception to prevent callers from caching
      # a result of a degraded situation.
      # The kind of exception does not matter as long as it's catched by
      # PAS and causes a lookup using another plugin or user folder.
      # As PAS does not define explicitely such exception, we must use
      # the _SWALLOWABLE_PLUGIN_EXCEPTIONS list.
      raise _SWALLOWABLE_PLUGIN_EXCEPTIONS[0]

  def getUserByLogin(self, login, exact_match=True):
    # Search the Catalog for login and return a list of person objects
    # login can be a string or a list of strings
    # (no docstring to prevent publishing)
    if not login:
      return []
    if isinstance(login, list):
      login = tuple(login)
    elif not isinstance(login, tuple):
      login = str(login)
    try:
      return getUserByLogin(self.getPortalObject(), login, exact_match)
    except ConflictError:
      raise
    except:
      LOG('ERP5Security', PROBLEM, 'getUserByLogin failed', error=sys.exc_info())
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
