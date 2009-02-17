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
from DocumentationHelper import DocumentationHelper, getCallableSignatureString
from Products.ERP5Type import Permissions

class AccessorMethodDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about an accessor
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
  def getTitle(self):
    """
    """
    obj = self.getDocumentedObject()
    if obj is not None:
      return obj.__name__

  security.declareProtected(Permissions.AccessContentsInformation, 'getDescription')
  def getDescription(self):
    """
    """
    obj = self.getDocumentedObject()
    if obj is not None:
      return obj.__doc__

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Accessor Method"

  security.declareProtected(Permissions.AccessContentsInformation, 'getArgCount')
  def getArgCount(self):
    """
    Returns the number of args of the accessor
    """
    obj = self.getDocumentedObject()
    if obj is not None:
      return obj.func_code.co_argcount

  security.declareProtected(Permissions.AccessContentsInformation, 'getVarNames')
  def getVarNames(self):
    """
    Returns the list of args of the accessor
    """
    obj = self.getDocumentedObject()
    if obj is not None:
      return obj.func_code.co_varnames

  security.declareProtected(Permissions.AccessContentsInformation, 'getDefinition')
  def getDefinition(self):
    """
    Returns the definition of the accessor_method with the name and arguments
    """
    obj = self.getDocumentedObject()
    if obj is not None:
      return getCallableSignatureString(obj)


InitializeClass(AccessorMethodDocumentationHelper)
