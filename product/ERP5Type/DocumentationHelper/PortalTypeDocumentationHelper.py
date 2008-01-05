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

class PortalTypeDocumentationHelper(DocumentationHelper):
  """
    Provides access to all documentation information
    of a portal type. Accessors and methods are documented
    by generating a temporary instance which provides
    an access to the property holder and allows
    reusing PortalTypeInstanceDocumentationHelper
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
    return "Portal Type"

  security.declareProtected( Permissions.AccessContentsInformation, 'getSectionList' )
  def getSectionList(self):
    """
    Returns a list of documentation sections
    """
    return map(lambda x: x.__of__(self), [
      DocumentationSection(
        id='action',
        title='Actions',
        class_name='ActionDocumentationHelper',
        uri_list=self.getActionURIList(),
      ),
      DocumentationSection(
        id='local_role',
        title='Local Role Definitions',
        class_name='LocalRoleDefinitionDocumentationHelper',
        uri_list=self.getDCWorkflowURIList(),
      ),
      # XXX - add here all sections of a portal type instance
    ])

  # Specific methods
  security.declareProtected( Permissions.AccessContentsInformation, 'getDescription' )
  def getDescription(self):
    """
    Returns the title of the documentation helper
    """
    raise NotImplemented


InitializeClass(PortalTypeDocumentationHelper)
