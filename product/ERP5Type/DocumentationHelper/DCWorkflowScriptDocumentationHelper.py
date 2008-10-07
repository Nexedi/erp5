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
from AccessorMethodDocumentationHelper import getDefinitionString

class DCWorkflowScriptDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a workflow script
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def __init__(self, uri):
    self.uri = uri

  security.declareProtected(Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Workflow Script"

  security.declareProtected(Permissions.AccessContentsInformation, 'getId' )
  def getId(self):
    """
    Returns the id of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "__name__", "")


  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return getattr(self.getDocumentedObject(), "title", "")

  security.declareProtected(Permissions.AccessContentsInformation, 'getSectionList')
  def getSectionList(self):
    """
    Returns a list of documentation sections for workflow scripts
    """
    return []

  security.declareProtected( Permissions.AccessContentsInformation, 'getDefinition' )
  def getDefinition(self):
    """
    Returns the definition of the script with the name of the script and arguments
    """
    return getDefinitionString(self.getDocumentedObject())

  security.declareProtected( Permissions.AccessContentsInformation, 'getSourceCode' )
  def getSourceCode(self):
    """
    Returns the source code the workflow script
    """
    from zLOG import LOG, INFO
    source_code = ""
    wf_script = self.getDocumentedObject()
    source_code = wf_script.document_src()
    portal_transforms = getattr(self, 'portal_transforms', None)
    if portal_transforms is not None:
      REQUEST = getattr(self, 'REQUEST', None)
      if REQUEST is not None:
        if REQUEST.get('portal_skin', 'View' ) != 'View':
          doc_string = source_code.split('"""')
          if len(doc_string)>1:
            return doc_string[1]
          else:
            return ""
    else:
      LOG('DCWorkflowScriptDocumentationHelper', INFO,
          'Transformation Tool is not installed. No convertion of python script to html')
      return source_code
    src_mimetype='text/x-python'
    mime_type = 'text/html'
    source_html = portal_transforms.convertTo(mime_type, source_code, mimetype = src_mimetype)
    return source_html.getData()

InitializeClass(DCWorkflowScriptDocumentationHelper)
