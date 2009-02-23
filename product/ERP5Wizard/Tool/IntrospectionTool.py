##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Wizard import _dtmldir
from AccessControl.SecurityManagement import newSecurityManager, \
                                             getSecurityManager, setSecurityManager
import zLOG
from Products.ERP5Type.Cache import CachingMethod

class IntrospectionTool(BaseTool):
  """
 This tool provides both local and  remote introspection.
  """
  id = 'portal_introspections'
  title = 'Introspection Tool'

  meta_type = 'ERP5 Introspection Tool'
  portal_type = 'Introspection Tool'
  allowed_content_types = ('Anonymized Introspection Report', 'User Introspection Report', )
  
  security = ClassSecurityInfo()
  security.declareProtected(Permissions.ManagePortal, 'manage_overview')
  manage_overview = DTMLFile('explainIntrospectionTool', _dtmldir )

InitializeClass(IntrospectionTool)
