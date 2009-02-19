##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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
"""
    ERP5Wizard is a ERP5Configurator client.
"""

from Products.ERP5Type.Utils import initializeProduct, updateGlobals
import sys, Permissions

from AccessControl.Permissions import manage_users as ManageUsers
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from Products.PluggableAuthService.permissions import ManageGroups
from Products.ERP5Wizard.PAS.ERP5RemoteUserManager import \
       ERP5RemoteUserManager, manage_addERP5RemoteUserManagerForm, addERP5RemoteUserManager

this_module = sys.modules[ __name__ ]
document_classes = updateGlobals(this_module, globals(), permissions_module=Permissions)


registerMultiPlugin(ERP5RemoteUserManager.meta_type)

# Finish installation
def initialize(context):
  import Document
  from Tool import WizardTool
  # Define object classes and tools
  object_classes = ()
  portal_tools = (WizardTool.WizardTool,)
  content_classes = ()
  content_constructors = ()
  # Do initialization step
  initializeProduct(context, this_module, globals(),
                    document_module=Document,
                    document_classes=document_classes,
                    object_classes=object_classes,
                    portal_tools=portal_tools,
                    content_constructors=content_constructors,
                    content_classes=content_classes)

  # register ERP5Security plugin for Wizard
  context.registerClass( ERP5RemoteUserManager
                         , permission=ManageUsers
                         , constructors=(
                            manage_addERP5RemoteUserManagerForm,
                            addERP5RemoteUserManager, )
                         , visibility=None
                         , icon='dtml/remote_user_manager_plugin.gif'
                         )  
