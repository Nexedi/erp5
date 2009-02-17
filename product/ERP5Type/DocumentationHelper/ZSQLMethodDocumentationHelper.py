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

class ZSQLMethodDocumentationHelper(DocumentationHelper):
  """
  Provides documentation about a Z SQL Method
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Z SQL Method"

  security.declareProtected(Permissions.AccessContentsInformation, 'getSource')
  def getSource(self):
    """
    Returns the source code of the documentation helper
    """
    from zLOG import LOG, INFO
    source_code = getattr(self.getDocumentedObject(), "src", '')
    portal_transforms = getattr(self, 'portal_transforms', None)
    if portal_transforms is not None:
      REQUEST = getattr(self, 'REQUEST', None)
      if REQUEST is not None:
        if REQUEST.get('portal_skin', 'View' ) != 'View':
          return ""
    else:
      LOG('DCWorkflowScriptDocumentationHelper', INFO,
          'Transformation Tool is not installed. No convertion of python script to html')
      return source_code
    src_mimetype='text/plain'
    mime_type = 'text/html'
    source_html = portal_transforms.convertTo(mime_type, source_code, mimetype = src_mimetype)
    return source_html.getData()

  security.declareProtected(Permissions.AccessContentsInformation, 'getConnectionId')
  def getConnectionId(self):
    """
    Returns the title of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "connection_id", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getArgumentList')
  def getArgumentList(self):
    """
    Returns the arguments of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "arguments_src", [])

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassName')
  def getClassName(self):
    """
    Returns the class name of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "class_name_", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getClassFile')
  def getClassFile(self):
    """
    Returns the class file of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "class_file_", '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getMaxRows')
  def getMaxRows(self):
    """
    Returns the  of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "max_rows_", '')

InitializeClass(ZSQLMethodDocumentationHelper)
