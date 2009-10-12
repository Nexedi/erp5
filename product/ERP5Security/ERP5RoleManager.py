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
""" Classes: ERP5RoleManager
"""

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin,\
                                                    IRoleEnumerationPlugin

from ERP5UserManager import SUPER_USER

manage_addERP5RoleManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5RoleManager', globals(),
    __name__='manage_addERP5RoleManagerForm' )

def addERP5RoleManager( dispatcher, id, title=None, REQUEST=None ):
    """ Add a ERP5RoleManager to a Pluggable Auth Service. """

    erm = ERP5RoleManager(id, title)
    dispatcher._setObject(erm.getId(), erm)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'ERP5RoleManager+added.'
                            % dispatcher.absolute_url())
 
class ERP5RoleManager( BasePlugin ):

    """ PAS plugin to add 'Member' as default
    Role for every user.
    """
    meta_type = 'ERP5 Role Manager'

    security = ClassSecurityInfo()

    def __init__(self, id, title=None):

        self._id = self.id = id
        self.title = title

    #
    #   IRolesPlugin implementation
    #
    security.declarePrivate( 'getRolesForPrincipal' )
    def getRolesForPrincipal( self, principal, request=None ):
        """ See IRolesPlugin.
        We only ever return Member for every principal
        """
        if principal.getId() == SUPER_USER:
          # If this is the super user, give all the roles present in this system.
          # XXX no API to do this in PAS.
          rolemakers = self._getPAS().plugins.listPlugins( IRoleEnumerationPlugin )
          roles = []
          for rolemaker_id, rolemaker in rolemakers:
            roles.extend([role['id'] for role in rolemaker.enumerateRoles()])
          return tuple(roles)

        return ('Member',)

classImplements( ERP5RoleManager
               , IRolesPlugin
               )


InitializeClass(ERP5RoleManager)
