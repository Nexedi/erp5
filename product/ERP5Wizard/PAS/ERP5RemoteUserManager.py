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
""" Classes: ERP5RemoteUserManager
"""

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager,\
    setSecurityManager, newSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin, \
                                                             IUserEnumerationPlugin
from Products.ERP5Type.Cache import CachingMethod
from DateTime import DateTime
from Products.ERP5Security.ERP5UserManager import ERP5UserManager, SUPER_USER, _AuthenticationFailure

from BTrees.OOBTree import OOBTree
from zLOG import LOG, INFO, WARNING
import socket
from AccessControl.AuthEncoding import pw_validate, pw_encrypt

manage_addERP5RemoteUserManagerForm = PageTemplateFile(
    '../dtml/ERP5Security_addERP5RemoteUserManager', globals(),
    __name__='manage_addERP5RemoteUserManagerForm' )

def addERP5RemoteUserManager(dispatcher, id, title=None, REQUEST=None):
    """ Add a ERP5UserManager to a Pluggable Auth Service. """

    eum = ERP5RemoteUserManager(id, title)
    dispatcher._setObject(eum.getId(), eum)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'ERP5RemoteUserManager+added.'
                            % dispatcher.absolute_url())


class ERP5RemoteUserManager(ERP5UserManager):
    """ PAS plugin for managing users in remote ERP5 instance
    """

    meta_type = 'ERP5 Remote User Manager'
    security = ClassSecurityInfo()
    remote_authentication_cache = None

    def _doRemoteAuthentication(self, login, password):
        # Do remote authentication with local ZODB caching
        # Thanks to this it is possible to login to instance, even
        # if master authentication server is down
        #
        # socket.sslerror and socket.error are assumed as acceptable ones
        # and invoke authentication against locally available cache of
        # users
        #
        # any other error is assumed as fatal and results in disallowing
        # authentication and clearing local cache
        if self.remote_authentication_cache is None:
            self.remote_authentication_cache = OOBTree()
        portal = self.getPortalObject()
        encrypted_password = pw_encrypt(password)
        callRemoteProxyMethod = portal.portal_wizard.callRemoteProxyMethod
        erp5_uid = portal.ERP5Site_getExpressInstanceUid()
        try:
            # XXX: This mix of passed parameters is based on
            # WizardTool_authenticateCredentials. As current implementation
            # shall be bug-to-bug compatible with previous one, kept such
            # behaviour
            result = int(callRemoteProxyMethod(
                       'Base_authenticateCredentialsFromExpressInstance',
                       use_cache = 0,
                       ignore_exceptions = 0,
                       **{'login': login,
                          'password': password,
                          'erp5_uid': erp5_uid}))
        except socket.error:
            # issue with socket, read from "ZODB cache"
            LOG('ERP5RemoteUserManager', INFO, 'Socket issue with server, '
              'used local cache', error=True)
            stored_encrypted_password = self.remote_authentication_cache.get(
               login, None)
            result = int(stored_encrypted_password is not None and pw_validate(
              stored_encrypted_password, password))
        except: # XXX: It would be better to do except Exception, but
                # to-be-bug compatible with WizardTool_authenticateCredentials
                # is better to catch the same way
            # any other issue, work like WizardTool_authenticateCredentials
            # XXX: To be fine tuned
            LOG('ERP5RemoteUserManager', WARNING, 'Not supported exception '
              'assuming that authentication failed', error=True)
            result = 0
            # clear local cache
            if login in self.remote_authentication_cache:
                del self.remote_authentication_cache[login]
        else:
            # update ZODB cache
            if result == 1:
                # successfully logged in
                stored_encrypted_password = self.remote_authentication_cache\
                    .get(login, None)
                if stored_encrypted_password is None or \
                   not pw_validate(stored_encrypted_password, password):
                    # not yet in cache or changed on server
                    self.remote_authentication_cache[login] = encrypted_password
            else:
                # wrong login, so clear local cache
                if login in self.remote_authentication_cache:
                    del self.remote_authentication_cache[login]
        return result

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
              raise _AuthenticationFailure()

            user = user_list[0]

            sm = getSecurityManager()
            if sm.getUser().getId() != SUPER_USER:
              newSecurityManager(self, self.getUser(SUPER_USER))
            try:
              # get assignment
              assignment_list = [x for x in user.contentValues(portal_type="Assignment") \
                                   if x.getValidationState() == "open"]
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

              # validate to remote ERP5 instance
              is_authenticated = self._doRemoteAuthentication(login, password)
              if is_authenticated:
                return login, login
            finally:
              setSecurityManager(sm)

            raise _AuthenticationFailure()

        _authenticateCredentials = CachingMethod(_authenticateCredentials,
                                                 id='ERP5RemoteUserManager_authenticateCredentials',
                                                 cache_factory='erp5_content_short')
        try:
          return _authenticateCredentials(
                        login=credentials.get('login'),
                        password=credentials.get('password'),
                        path=self.getPhysicalPath())
        except _AuthenticationFailure:
          return None 

classImplements( ERP5RemoteUserManager
               , IAuthenticationPlugin
               , IUserEnumerationPlugin
               )

InitializeClass(ERP5RemoteUserManager)
