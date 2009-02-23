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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager,\
    setSecurityManager, newSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin, \
                                                             IUserEnumerationPlugin
from Products.ERP5Type.Cache import CachingMethod
from DateTime import DateTime
from Products.ERP5Security.ERP5UserManager import ERP5UserManager, SUPER_USER


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
              portal = self.getPortalObject() 
              is_authenticated = int(portal.WizardTool_authenticateCredentials(login , password))
              if is_authenticated:
                return login, login
            finally:
              setSecurityManager(sm)

            return None

        _authenticateCredentials = CachingMethod(_authenticateCredentials,
                                                 id='ERP5RemoteUserManager_authenticateCredentials',
                                                 cache_factory='erp5_content_short')
        return _authenticateCredentials(
                      login=credentials.get('login'),
                      password=credentials.get('password'),
                      path=self.getPhysicalPath())

classImplements( ERP5RemoteUserManager
               , IAuthenticationPlugin
               , IUserEnumerationPlugin
               )

InitializeClass(ERP5RemoteUserManager)
