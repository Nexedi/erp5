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
                person_module = self.getPortalObject()\
                                        .getDefaultModule('Person')
                for user_name in t_id:
                    user = getattr(person_module, user_name, None)
                    if user:
                        if user.getCareerRole() == 'internal':
                            user_objects.append(user)

            elif login:
                for user in self.getUserByLogin(login):
                    if user.getCareerRole() == 'internal':
                        user_objects.append(user)

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
