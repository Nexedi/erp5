##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
    ERP5Catalog provides an extended catalog based on ZSQLCatalog
    and extended local roles management
"""

# Update ERP5 Globals
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
import sys, Permissions
this_module = sys.modules[ __name__ ]
document_classes = updateGlobals(this_module, globals(),
  permissions_module=Permissions)

# Finish installation
def initialize( context ):
  # Define object classes and tools
  import ActivityTool, ActiveProcess, ActivityConnection, ActivityJoblibBackend
  object_classes = (ActiveProcess.ActiveProcess,
                    #ActivityConnection.ActivityConnection
                    )
  portal_tools = (ActivityTool.ActivityTool, )
  content_classes = ()
  content_constructors = ()
  initializeProduct(context, this_module, globals(),
                    object_classes=object_classes,
                    portal_tools=portal_tools,
                    content_constructors=content_constructors,
                    content_classes=content_classes)

  # register manually instead of using object_classes above so we can reuse
  # the ZMySQLDA icon without having to carry the gif around in our own product
  context.registerClass(
        ActivityConnection.ActivityConnection,
        permission='Add Z MySQL Database Connections', # reuse the permission
        constructors=(ActivityConnection.manage_addActivityConnectionForm,
                      ActivityConnection.manage_addActivityConnection),
  )

# This is used by a script (external method) that can be run
# to set up CMFActivity in an existing CMF Site instance.
cmfactivity_globals = globals()

from AccessControl.SecurityInfo import allow_module
allow_module('Products.CMFActivity.ActiveResult')
allow_module('Products.CMFActivity.Errors')
