##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions

class PortalTypeActionDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a portal type action
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Portal Type Action"

  security.declareProtected(Permissions.AccessContentsInformation, 'getPermissions')
  def getPermissions(self):
    """
    Returns the permissions of the documentation helper
    """
    permissions = getattr(self.getDocumentedObject(), "permissions")
    return ', '.join(x for x in permissions)

  security.declareProtected(Permissions.AccessContentsInformation, 'getVisible')
  def getVisible(self):
    """
    Returns the visibility of the documentation helper
    """
    TITLE =['No', 'Yes']
    return TITLE[getattr(self.getDocumentedObject(), "visible", 0)]

  security.declareProtected(Permissions.AccessContentsInformation, 'getCategory')
  def getCategory(self):
    """
    Returns the category of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "category")

InitializeClass(PortalTypeActionDocumentationHelper)
