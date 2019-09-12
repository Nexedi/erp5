##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#                  Fabien Morin <fabien@nexedi.com>
#                  Mohamadou Mbengue <mmbengue@gmail.com>
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
""" Classes: ERP5GroupManager
"""

from Products.ERP5Type.Globals import InitializeClass
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
from Products.ERP5Security.ERP5UserManager import ERP5UserManager
from ZODB.POSException import ConflictError
from DateTime import DateTime
from zLOG import LOG, PROBLEM
from AccessControl.AuthEncoding import pw_validate

# This user is used to bypass all security checks.
SUPER_USER = '__erp5security-=__'

manage_addEGOVUserManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5UserManager', globals(),
    __name__='manage_addERP5UserManagerForm' )


def addEGOVUserManager(dispatcher, id, title=None, REQUEST=None):
  """ Add a EGOVUserManager to a Pluggable Auth Service. """
  eum = EGOVUserManager(id, title)
  dispatcher._setObject(eum.getId(), eum)
  if REQUEST is not None:
      REQUEST['RESPONSE'].redirect(
                              '%s/manage_workspace'
                              '?manage_tabs_message='
                              'EGOVUserManager+added.'
                          % dispatcher.absolute_url())

class EGOVUserManager(ERP5UserManager):
    """ PAS plugin for managing users in ERP5
        this plugin permit to login with evry portal_type
        So it's possible to login with organisation
    """

    meta_type = 'EGOV User Manager'

    security = ClassSecurityInfo()

    portal_type_list = ('Person',)

    _properties = BasePlugin._properties + (
       {'label' : 'Portal Type List (Experimental)',
         'type' : 'lines',
         'id'   : 'portal_type_list',
         'mode' : 'w',
       },
       )

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

            user_list = self.getUserByLogin((login,))

            if not user_list:
                return None

            user = user_list[0]
            user_portal_type = user.getPortalType()

            sm = getSecurityManager()
            if sm.getUser().getId() != SUPER_USER:
              newSecurityManager(self, self.getUser(SUPER_USER))

            # search for assignment only on person entity
            if user_portal_type == 'Person':
              try:
                # get assignment
                assignment_list = [x for x in \
                    user.contentValues(portal_type="Assignment") if \
                    x.getValidationState() == "open"]
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

                if pw_validate(user.getPassword(), password) and \
                       len(valid_assignment_list): #user.getCareerRole() == 'internal':
                  return login, login # use same for user_id and login
              finally:
                setSecurityManager(sm)
            else:
              if pw_validate(user.getPassword(), password):
                return login, login # use same for user_id and login

            return None

        _authenticateCredentials = CachingMethod(_authenticateCredentials,
                                 id='ERP5UserManager_authenticateCredentials',
                                 cache_factory='erp5_content_short')
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
              for user in self.getUserByLogin(tuple(id_list), exact_match=exact_match):
                  info = { 'id' : user.getReference()
                         , 'login' : user.getReference()
                         , 'pluginid' : plugin_id
                         }

                  user_info.append(info)

            return tuple(user_info)

        _enumerateUsers = CachingMethod(_enumerateUsers,
                                        id='ERP5UserManager_enumerateUsers',
                                        cache_factory='erp5_content_short')

        if id is None:
          id = login
        if isinstance(id, list):
          id = tuple(id)
        elif not isinstance(id, tuple):
          id = (id,)
        return _enumerateUsers(id_tuple=id,
                               exact_match=exact_match,
                               path=self.getPhysicalPath())

    def getUserByLogin(self, login, exact_match=True):
        # Search the Catalog for login and return a list of person objects
        # login can be a string or a list of strings
        # (no docstring to prevent publishing)
        if not login:
          return []

        portal = self.getPortalObject()

        def _getUserByLogin(login, exact_match):
          # because we aren't logged in, we have to create our own
          # SecurityManager to be able to access the Catalog
          sm = getSecurityManager()
          if sm.getUser().getId() != SUPER_USER:
            newSecurityManager(self, self.getUser(SUPER_USER))
          try:
            result = portal.portal_catalog.unrestrictedSearchResults(
                            select_list=['reference'],
                            portal_type=self.portal_type_list, reference=login)
            if len(result) != 1: # we won't proceed with groups
              if len(result) > 1: # configuration is screwed
                raise ConsistencyError('There is more than one Person whose'
                    ' login is %s : %s' % (user_name,
                    repr([r.getObject() for r in catalog_result])))
              else: # no person is linked to this user login
                # this permit to get the module of the application
                # the goal is to work with anonymous applications, even if
                # they are not reindexed
                module_id = self.REQUEST.get('anonymous_module', None)
                if module_id:
                  module =  getattr(portal, module_id, None)
                  if module is not None:
                    result = module._getOb(login[0], None)
                    if result is not None:
                      return [result.getPath(),]
                    else:
                      return []
                else:
                  return []
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
          finally:
            setSecurityManager(sm)
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
          # " foo", "foo " and other padding variations because of
          # ZSQLCatalog (feature ?):
          #  (Pdb) print portal.portal_catalog.unrestrictedSearchResults(\
          #              portal_type="Person", reference='  foo  ', src__=1)
          #  SELECT DISTINCT
          #     catalog.path,   catalog.uid
          #  FROM
          #     catalog AS catalog
          #  WHERE
          #    1 = 1
          #    AND (((((catalog.portal_type = 'Person'))))) AND (((((catalog.reference = 'foo')))))
          #  LIMIT 1000
          # "bar OR foo" because of ZSQLCatalog tokenizing searched sgtrings
          # by default (feature).
          return [x.path for x in result if (not exact_match) or x['reference'] in login]
        _getUserByLogin = CachingMethod(_getUserByLogin,
                                        id='ERP5UserManager_getUserByLogin',
                                        cache_factory='erp5_content_short')
        result = _getUserByLogin(login, exact_match)
        return [portal.unrestrictedTraverse(x) for x in result]

classImplements( EGOVUserManager
               , IAuthenticationPlugin
               , IUserEnumerationPlugin
               )

InitializeClass(EGOVUserManager)
