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

class DCWorkflowVariableDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a workflow variable
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Workflow Variable"

  security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultExpression')
  def getDefaultExpression(self):
    """
    Returns the Default Expression of the documentation helper
    """
    default_expr = ""
    if getattr(self.getDocumentedObject(), "default_expr", None) is not None:
      default_expr = self.getDocumentedObject().default_expr.text
    return default_expr

  security.declareProtected(Permissions.AccessContentsInformation, 'getForCatalog')
  def getForCatalog(self):
    """
    Returns 1 if variable is available in the catalog
    """
    for_catalog = 0
    variable = self.getDocumentedObject()
    if hasattr(variable, 'for_catalog'):
      for_catalog = variable.for_catalog
    if for_catalog:
      return 'Yes'
    else:
      return 'No'

  security.declareProtected(Permissions.AccessContentsInformation, 'getUpdateAlways')
  def getUpdateAlways(self):
    """
    Returns 1 if variable is available in the history
    """
    update_always = 0
    variable = self.getDocumentedObject()
    if hasattr(variable, 'update_always'):
      update_always = variable.update_always
    if update_always:
      return 'Yes'
    else:
      return 'No'


InitializeClass(DCWorkflowVariableDocumentationHelper)
