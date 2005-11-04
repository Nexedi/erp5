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
""" Classes: ERP5GroupManager
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
from Products.ERP5Type.Cache import CachingMethod

from zLOG import LOG

manage_addERP5GroupManagerForm = PageTemplateFile(
    'www/ERP5Security_addERP5GroupManager', globals(), __name__='manage_addERP5GroupManagerForm' )

def addERP5GroupManager( dispatcher, id, title=None, REQUEST=None ):
    """ Add a ERP5GroupManager to a Pluggable Auth Service. """

    egm = ERP5GroupManager(id, title)
    dispatcher._setObject(egm.getId(), egm)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'ERP5GroupManager+added.'
                            % dispatcher.absolute_url())

class ERP5GroupManager(BasePlugin):

    """ PAS plugin for dynamically adding Groups
    based on Assignments in ERP5
    """
    meta_type = 'ERP5 Group Manager'

    security = ClassSecurityInfo()

    def __init__(self, id, title=None):

        self._id = self.id = id
        self.title = title

    #
    #   IGroupsPlugin implementation
    #
    def getGroupsForPrincipal(self, principal, request=None):
        """ See IGroupsPlugin.
        """
        def _getGroupsForPrincipal(user_name, path):
            security_group_list = []

            # because we aren't logged in, we have to create our own
            # SecurityManager to be able to access the Catalog
            newSecurityManager(self, self.getPortalObject().getOwner())
            base_category_list = self.getPortalObject().getPortalAssignmentBaseCategoryList()

            user_name = principal.getId()

            person_module = self.getPortalObject().getDefaultModule('Person')
            person_object = getattr(person_module, user_name, None)

            # return no groups if the username is not registered in person module
            if not person_object:
                return ()

            # Fetch category values from assignment
            category_list = self.ERP5Type_getSecurityCategoryFromAssignment(base_category_list, user_name, self, '')

            # return no groups if we there are no Security Categories
            if not category_list:
                return ()

            # Get group names from category values
            for c_dict in category_list:
                security_group_list.append(self.ERP5Type_asSecurityGroupId(category_order=base_category_list, **c_dict))

            LOG('erp5_groups', 0, 'user %s is member of %s' %(user_name, str(security_group_list)))

            return tuple(security_group_list)

        _getGroupsForPrincipal = CachingMethod(_getGroupsForPrincipal, id='ERP5GroupManager_getGroupsForPrincipal')
        return _getGroupsForPrincipal(user_name=principal.getId(), path=self.getPhysicalPath())



classImplements( ERP5GroupManager
               , IGroupsPlugin
               )

InitializeClass(ERP5GroupManager)
