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
from AccessControl.SecurityManagement import newSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
from Products.ERP5Type.Cache import CachingMethod

from zLOG import LOG

manage_addERP5UserManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5UserManager', globals(), __name__='manage_addERP5UserManagerForm' )

def addERP5UserManager(dispatcher, id, title=None, REQUEST=None):
    """ Add a ERP5UserManagern to a Pluggable Auth Service. """

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
        def _authenticateCredentials(login, password, path):
            if login is None or password is None:
                return None
            
            user_list = self.getUserByLogin(login)
            
            if not user_list:
                return None
            
            user = user_list[0]
            
            if user.getPassword() == password:
                LOG('authenticateCredentials', 0, user.getId())
                return user.getId(), login
            
            return None
        
        _authenticateCredentials = CachingMethod(_authenticateCredentials, id='ERP5UserManager_authenticateCredentials')
        return _authenticateCredentials(login=credentials.get('login'), password=credentials.get('password'), path=self.getPhysicalPath())
            
    #
    #   IUserEnumerationPlugin implementation
    #
    security.declarePrivate( 'enumerateUsers' )
    def enumerateUsers(self, id=None, login=None, exact_match=False, sort_by=None, max_results=None, **kw):
        """ See IUserEnumerationPlugin.
        """    
        def _enumerateUsers(t_id, path):
            user_info = []
            user_objects = []
            plugin_id = self.getId()
                        
            if isinstance(t_id, str):
                t_id = (t_id,)
                            
            if t_id:
                person_module = self.person
                for user_name in t_id:
                    user = getattr(person_module, user_name, None)
                    if user:
                        user_objects.append(user)
                                        
            elif login:
                user_objects.extend(self.getUserByLogin(login))
            
            for user in user_objects:
                LOG('enumerateUsers', 0, user.getId())
                info = { 'id' : user.getId()
                       , 'login' : user.getReference()
                       , 'pluginid' : plugin_id
                       } 
                       
                user_info.append(info)
                                
            return tuple(user_info)
        
        _enumerateUsers = CachingMethod(_enumerateUsers, id='ERP5UserManager_enumerateUsers')
        
        if isinstance(id, list):
            id = tuple(id)
        return _enumerateUsers(t_id=id, path=self.getPhysicalPath())

    def getUserByLogin(self, login):
        """ 
        Search the Catalog for login and return a list of person objects
        login can be a string list or a list of strings
        """       
        # because we aren't logged in, we have to create our own
        # SecurityManager to be able to access the Catalog
        newSecurityManager(self, self.getPortalObject().portal_catalog.getOwner())
        
        result = self.getPortalObject().portal_catalog(portal_type="Person", reference=login)
        
        return [item.getObject() for item in result]
    
classImplements( ERP5UserManager
               , IAuthenticationPlugin
               , IUserEnumerationPlugin
               )

InitializeClass(ERP5UserManager)
