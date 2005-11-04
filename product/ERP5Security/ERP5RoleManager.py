##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Klaus Wölfel <k.woelfel_AT_gmx_DOT_de>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
""" Classes: ERP5RoleManager
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin

manage_addERP5RoleManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5RoleManager', globals(), __name__='manage_addERP5RoleManagerForm' )

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

        return ('Member',)

classImplements( ERP5RoleManager
               , IRolesPlugin
               )


InitializeClass(ERP5RoleManager)
