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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager,\
    setSecurityManager, newSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.PluggableAuthService import \
    _SWALLOWABLE_PLUGIN_EXCEPTIONS
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from Products.ERP5Type.Cache import CachingMethod
from ZODB.POSException import ConflictError
import sys

from zLOG import LOG, PROBLEM

try :
  from AccessControl.AuthEncoding import pw_validate
except ImportError:
  pw_validate = lambda reference, attempt: reference == attempt

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
        # Forbidden the usage of the super user.
        if credentials.get('login') == SUPER_USER:
          return None

        def _authenticateCredentials(login, password, path):
            if not login or not password:
                return None

            user_list = self.getUserByLogin(login)

            if not user_list:
                return None

            user = user_list[0]

            sm = getSecurityManager()
            if sm.getUser() != SUPER_USER:
              newSecurityManager(self, self.getUser(SUPER_USER))
            try:
              if pw_validate(user.getPassword(), password) and\
                  user.getCareerRole() == 'internal':
                return login, login # use same for user_id and login
            finally:
              setSecurityManager(sm)

            return None

        _authenticateCredentials = CachingMethod(_authenticateCredentials,
                                                 id='ERP5UserManager_authenticateCredentials',
                                                 cache_factory='erp5_core_short')
        return _authenticateCredentials(
                      login=credentials.get('login'),
                      password=credentials.get('password'),
                      path=self.getPhysicalPath())

    #
    #   IUserEnumerationPlugin implementation
    #
    security.declarePrivate( 'enumerateUsers' )
    def enumerateUsers(self, id=None, login=None, exact_match=False,
                       sort_by=None, max_results=None, **kw):
        """ See IUserEnumerationPlugin.
        """
        def _enumerateUsers(id_tuple, exact_match, path):
            user_info = []
            plugin_id = self.getId()

            id_list = []
            for id in id_tuple:
              if SUPER_USER == id:
                info = { 'id' : SUPER_USER
                        , 'login' : SUPER_USER
                        , 'pluginid' : plugin_id
                        }
                user_info.append(info)
              else:
                if exact_match:
                  id_list.append(id)
                else:
                  id_list.append('%%%s%%' % id)

            if id_list:
              for user in self.getUserByLogin(tuple(id_list)):
                  info = { 'id' : user.getReference()
                         , 'login' : user.getReference()
                         , 'pluginid' : plugin_id
                         }

                  user_info.append(info)

            return tuple(user_info)

        _enumerateUsers = CachingMethod(_enumerateUsers,
                                        id='ERP5UserManager_enumerateUsers',
                                        cache_factory='erp5_core_short')

        if id is None:
          id = login
        if isinstance(id, str):
          id = (id,)
        if isinstance(id, list):
          id = tuple(id)
        return _enumerateUsers(id_tuple=id,
                               exact_match=exact_match,
                               path=self.getPhysicalPath())

    def getUserByLogin(self, login):
        # Search the Catalog for login and return a list of person objects
        # login can be a string or a list of strings
        # (no docstring to prevent publishing)
        if not login:
          return []
        # because we aren't logged in, we have to create our own
        # SecurityManager to be able to access the Catalog
        sm = getSecurityManager()
        if sm.getUser() != SUPER_USER:
          newSecurityManager(self, self.getUser(SUPER_USER))

        try:
          try:
            result = self.getPortalObject().portal_catalog(
                                    portal_type="Person", reference=login)
          except ConflictError:
            raise
          except:
            LOG('ERP5Security', PROBLEM, 'getUserByLogin failed', error=sys.exc_info())
            # Here we must raise an exception to prevent calers from caching
            # a result of a degraded situation.
            # The kind of exception does not matter as long as it's catched by
            # PAS and causes a lookup using another plugin or user folder.
            # As PAS does not define explicitely such exception, we must use
            # the _SWALLOWABLE_PLUGIN_EXCEPTIONS list.
            raise _SWALLOWABLE_PLUGIN_EXCEPTIONS[0]
        finally:
          setSecurityManager(sm)
        return [item.getObject() for item in result]

classImplements( ERP5UserManager
               , IAuthenticationPlugin
               , IUserEnumerationPlugin
               )

InitializeClass(ERP5UserManager)
