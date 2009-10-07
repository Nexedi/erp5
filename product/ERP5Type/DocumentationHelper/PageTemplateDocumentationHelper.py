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
from Products.ERP5Type.Globals import InitializeClass
from DocumentationHelper import DocumentationHelper
from Products.ERP5Type import Permissions

class PageTemplateDocumentationHelper(DocumentationHelper):
  """
    Provides documentation about a page template
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'getType')
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Page Template"

  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceCode')
  def getSourceCode(self):
    """
    Returns the source code the script python
    """
    from zLOG import LOG, INFO
    source_code = getattr(self.getDocumentedObject(), "_text")
    portal_transforms = getattr(self, 'portal_transforms', None)
    if portal_transforms is not None:
      REQUEST = getattr(self, 'REQUEST', None)
      if REQUEST is not None:
        if REQUEST.get('portal_skin', 'View' ) != 'View':
          return source_code
    else:
      LOG('DCWorkflowScriptDocumentationHelper', INFO,
          'Transformation Tool is not installed. No convertion of python script to html')
      return source_code
    src_mimetype='text/plain'
    mime_type = 'text/html'
    source_html = portal_transforms.convertTo(mime_type, source_code, mimetype = src_mimetype)
    return source_html.getData()

InitializeClass(PageTemplateDocumentationHelper)
