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
