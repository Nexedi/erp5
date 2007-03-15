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

from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _setCacheHeaders
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Document import Document
from Products.ERP5Type.WebDAVSupport import TextContent

class TextDocument(Document, TextContent):
    """
        A Document contains text which can be formatted using
        *Structured Text* or *HTML*. Text can be automatically translated
        through the use of 'message catalogs'.

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

        Subcontent: documents may include subcontent (files, images, etc.)
        so that publication of rich content can be path independent.
    """

    meta_type = 'ERP5 Text Document'
    portal_type = 'Text Document'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    isDocument = 1

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
                      , PropertySheet.TextDocument
                      )

    # Declarative interfaces
    __implements__ = ()

    # Explicit inheritance
    security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
    PUT = TextContent.PUT # We have a security issue here with Zope < 2.8

    security.declareProtected(Permissions.View, 'manage_FTPget')
    manage_FTPget = TextContent.manage_FTPget

    # File handling
    security.declarePrivate( '_edit' )
    def _edit(self, **kw):
      """\
        This is used to edit files which contain HTML content.
      """
      if kw.has_key('file'):
        file = kw.get('file')
        text_content = file.read()
        headers, body, format = self.handleText(text=text_content)
        kw.setdefault('text_format', format)
        kw.setdefault('text_content', text_content)
        del kw['file']
      Document._edit(self, **kw)

    security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
    edit = WorkflowMethod( _edit )
    
    # Default Display
    security.declareProtected(Permissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE, format=None, **kw):
      """
        Unlike for images and files, we want to provide
        in the case of HTML a nice standard display with
        all the layout of a Web Site. If no format is provided,
        the default rendering will use the standard ERP5 machinery.
        By providing a format parameter, it is possible to
        convert the text content into various formats.
      """
      if format is None:
        # The default is to use ERP5 Forms to render the page
        return self.view()
      # Accelerate rendering in Web mode
      _setCacheHeaders(self, {'format' : format})
      # Return the raw content
      if format == 'raw':
        return self.getTextContent()
      mime_type = getToolByName(self, 'mimetypes_registry').lookupExtension('name.%s' % format)
      return getToolByName(self, 'portal_transforms').convertTo(mime_type,
                           self.getTextContent(), object=self, mimetype=self.getTextFormat())

    def __call__(self):
      _setCacheHeaders(self, {})
      return Document.__call__(self)

    ### Content indexing methods
    security.declareProtected(Permissions.View, 'getSearchableText')
    def getSearchableText(self, md=None):
        """\
        Used by the catalog for basic full text indexing
        We should try to do some kind of file conversion here so that getTextContent
        returns something more readable.
        """
        searchable_text = "%s %s %s %s %s" %  (self.getTitle(), self.getShortTitle(),
                                               self.getDescription(),
                                               self.getId(), self.getTextContent())
        return searchable_text

    # Compatibility with CMF Catalog / CPS sites
    SearchableText = getSearchableText # XXX-JPS - Here wa have a security issue - ask seb what to do