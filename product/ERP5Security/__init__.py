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
""" ERP5Security product initialization.
"""

from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from Products.PluggableAuthService.permissions import ManageGroups

import ERP5UserManager
import ERP5GroupManager
import ERP5RoleManager

registerMultiPlugin(ERP5UserManager.ERP5UserManager.meta_type)
registerMultiPlugin(ERP5GroupManager.ERP5GroupManager.meta_type)
registerMultiPlugin(ERP5RoleManager.ERP5RoleManager.meta_type)

def initialize(context):

    context.registerClass( ERP5UserManager.ERP5UserManager
                         , permission=ManageUsers
                         , constructors=(
                            ERP5UserManager.manage_addERP5UserManagerForm, 
                            ERP5UserManager.addERP5UserManager, )
                         , visibility=None
                         , icon='www/portal.gif'
                         )

    context.registerClass( ERP5GroupManager.ERP5GroupManager
                         , permission=ManageGroups
                         , constructors=(
                            ERP5GroupManager.manage_addERP5GroupManagerForm, 
                            ERP5GroupManager.addERP5GroupManager, )
                         , visibility=None
                         , icon='www/portal.gif'
                         )

    context.registerClass( ERP5RoleManager.ERP5RoleManager
                         , permission=ManageUsers
                         , constructors=(
                            ERP5RoleManager.manage_addERP5RoleManagerForm,
                            ERP5RoleManager.addERP5RoleManager, )
                         , visibility=None
                         , icon='www/portal.gif'
                         )
