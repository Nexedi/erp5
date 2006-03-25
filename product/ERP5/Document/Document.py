##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.WebDAVSupport import TextContent

class Document(XMLObject, TextContent):
    """
        A Document can contain text that can be formatted using
        *Structured Text* or *HTML*. Text can be automatically translated
        through the use of 'message catalogs'.

        A Document is a terminating leaf
        in the OFS. It can not contain anything.

        Document inherits from XMLObject and can
        be synchronized accross multiple sites.

        Version Management: the notion of version depends on the
        type of application. For example, in the case (1) of Transformation
        (BOM), all versions are considered as equal and may be kept
        indefinitely for both archive and usage purpose. In the case (2)
        of Person data, the new version replaces the previous one
        in place and is not needed for archive. In the case (3) of
        a web page, the new version replaces the previous one,
        the previous one being kept in place for archive.
    """

    meta_type = 'ERP5 Document'
    portal_type = 'Document'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Version
                      , PropertySheet.Document
                      )

    # Declarative interfaces
    __implements__ = ()

    # Patch
    PUT = TextContent.PUT

    ### Content indexing methods
    security.declareProtected(Permissions.View, 'getSearchableText')
    def getSearchableText(self, md=None):
        """\
        Used by the catalog for basic full text indexing
        We should try to do some kind of file conversion here
        """
        searchable_text = "%s %s %s %s" %  (self.getTitle(), self.getDescription(),
                                            self.getId(), self.getTextContent())
        return searchable_text

    # Compatibility with CMF Catalog / CPS sites
    SearchableText = getSearchableText
