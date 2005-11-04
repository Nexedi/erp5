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
