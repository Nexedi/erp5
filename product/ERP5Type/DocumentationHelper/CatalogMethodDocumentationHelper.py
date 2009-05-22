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
from ZSQLMethodDocumentationHelper import ZSQLMethodDocumentationHelper
from Products.ERP5Type import Permissions

class CatalogMethodDocumentationHelper(ZSQLMethodDocumentationHelper):
  """
    Provides documentation about a catalog method
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Catalog Method"

  security.declareProtected(Permissions.AccessContentsInformation, 'getConnectionId')
  def getConnectionId(self):
    """
    Returns the title of the documentation helper
    """
    return getattr(self.getDocumentedObject(), 'connection_id')

  security.declareProtected(Permissions.AccessContentsInformation, 'getArgumentList')
  def getArgumentList(self):
    """
    Returns the arguments of the documentation helper
    """
    keys = []
    arg = getattr(self.getDocumentedObject(), '_arg', None)
    if arg is not None:
      keys = getattr(arg, '_keys', [])
    return keys

  security.declareProtected(Permissions.AccessContentsInformation, 'getCatalog')
  def getCatalog(self):
    """
    Returns the catalog name of the documentation helper
    """
    catalog = ''
    parent = getattr(self.getDocumentedObject(), 'aq_parent', None)
    if parent is not None:
      catalog = getattr(parent, '__name__')
    return catalog

InitializeClass(CatalogMethodDocumentationHelper)
