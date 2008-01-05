
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


class BusinessTemplateDocumentationHelper(DocumentationHelper):
  """
    Provides access to all documentation information
    of a business template.
  """

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # API Implementation
  security.declareProtected( Permissions.AccessContentsInformation, 'getTitle' )
  def getTitle(self):
    """
    Returns the title of the documentation helper
    """
    return self.getDocumentedObject().getTitleOrId()

  security.declareProtected( Permissions.AccessContentsInformation, 'getType' )
  def getType(self):
    """
    Returns the type of the documentation helper
    """
    return "Business Template"

  security.declareProtected( Permissions.AccessContentsInformation, 'getSectionList' )
  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    return map(lambda x: x.__of__(self), [
      DocumentationSection(
        id='portal_type',
        title='Portal Types',
        class_name='PortalTypeDocumentationHelper',
        uri_list=self.getPortalTypeURIList(),
      ),
      DocumentationSection(
        id='workflow',
        title='Workflows',
        class_name='DCWorkflowDocumentationHelper',
        uri_list=self.getDCWorkflowURIList(),
      ),
      DocumentationSection(
        id='interaction',
        title='Interaction Workflows',
        class_name='InteractionWorkflowStateDocumentationHelper',
        uri_list=self.getInteractionWorkflowURIList(),
      ),
      DocumentationSection(
        id='skin_folder',
        title='Skin Folders',
        class_name='SkinFolderDocumentationHelper',
        uri_list=self.getSkinFolderURIList(),
      ),
    ])

  # Specific methods
  security.declareProtected( Permissions.AccessContentsInformation, 'getDescription' )
  def getDescription(self):
    """
    Returns the title of the documentation helper
    """
    raise NotImplemented


InitializeClass(BusinessTemplateDocumentationHelper)
