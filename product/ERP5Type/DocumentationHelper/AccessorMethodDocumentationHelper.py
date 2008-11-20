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

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions

#return the definition string of an object representing a workflow method or a class method or an accessor
def getDefinitionString(obj=None):
  if obj is None:
    return ""
  func_code = getattr(obj, "func_code", None)
  if func_code is None:
    return ""
  fc_var_names = getattr(func_code, "co_varnames", [])
  fc = []
  for i in range(len(fc_var_names)):
    if fc_var_names[i] == 'args':
      fc.append('*args')
    elif fc_var_names[i] == 'kw':
      fc.append('**kw')
    elif fc_var_names[i].startswith('_') or \
        fc_var_names[i].startswith('Products'):
      # In case of python scripts, we have many things
      # that we do not want to display
      break
    else:
      fc.append(fc_var_names[i])
  fd = obj.func_defaults
  acc_def = obj.__name__ + ' ('
  if fd == None:
    acc_def += ', '.join(fc)
  else:
    for x in range(len(fc)):
      if (len(fc)-(x+1)<len(fd)):
        if (x == len(fc)-1):
          acc_def += " "+str(fc[x])+"='"+str(fd[x-len(fd)])+"'"
        else:
          acc_def += " "+str(fc[x])+"='"+str(fd[x-len(fd)])+"',"
      else:
        if (x == len(fc)-1):
          acc_def += " "+str(fc[x])
        else:
          acc_def += " "+str(fc[x])+","
  acc_def += ")"
  return acc_def


class AccessorMethodDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about an accessor
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, uri):
    self.uri = uri

  security.declareProtected(Permissions.AccessContentsInformation, 'getDescription')
  def getDescription(self):
    return getattr(self.getDocumentedObject(), "__doc__", "")

  security.declareProtected( Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Accessor Method"

  security.declareProtected( Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "__name__", "")

  security.declareProtected(Permissions.AccessContentsInformation, 'getSectionList')
  def getSectionList(self):
    """
    Returns a list of documentation sections for accessors
    """
    return []

  security.declareProtected( Permissions.AccessContentsInformation, 'getArgCount' )
  def getArgCount(self):
    """
    Returns the number of args of the accessor
    """
    return self.getDocumentedObject().func_code.co_argcount

  security.declareProtected( Permissions.AccessContentsInformation, 'getVarNames' )
  def getVarNames(self):
    """
    Returns the list of args of the accessor
    """
    return self.getDocumentedObject().func_code.co_varnames

  security.declareProtected( Permissions.AccessContentsInformation, 'getDefinition' )
  def getDefinition(self):
    """
    Returns the definition of the accessor_method with the name and arguments
    """
    return getDefinitionString(self.getDocumentedObject())


InitializeClass(AccessorMethodDocumentationHelper)
