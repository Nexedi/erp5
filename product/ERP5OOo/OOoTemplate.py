##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.Formulator.Form import BasicForm
from Products.Formulator.Form import fields
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ERP5Type import PropertySheet

from urllib import quote
from Globals import InitializeClass, DTMLFile, get_request
from AccessControl import ClassSecurityInfo
from OOoUtils import OOoBuilder

from zLOG import LOG

try:
    from webdav.Lockable import ResourceLockedError
    from webdav.WriteLockInterface import WriteLockInterface
    SUPPORTS_WEBDAV_LOCKS = 1
except ImportError:
    SUPPORTS_WEBDAV_LOCKS = 0

# Constructors
manage_addOOoTemplate = DTMLFile("dtml/OOoTemplate_add", globals())

def addOOoTemplate(self, id, title="", REQUEST=None):
    """Add OOo template to folder.
    
    id     -- the id of the new OOo template to add
    title  -- the title of the OOo to add
    Result -- empty string
    """
    # add actual object
    id = self._setObject(id, OOoTemplate(id, title))
    # respond to the add_and_edit button if necessary
    add_and_edit(self, id, REQUEST)
    return ''

def add_and_edit(self, id, REQUEST):
    """Helper method to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except AttributeError:
        u = REQUEST['URL1']
    if REQUEST['submit'] == " Add and Edit ":
        u = "%s/%s" % (u, quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')


class OOoTemplate(ZopePageTemplate):
    """
        A page template which is able to embed and OpenOffice
        file (zip archive) and replace content.xml at render time
        with XML dynamically generated through TAL/TALES/METAL expressions

        TODO:
          - solve content type issue (text/html currently required
            to produce valude xml). TALParser (used if content type
            is application/) does not produce appropriate result.

          - upload of OOo documents must be able to extract content.xml
            from the archive, remove DTD definition and include
            CR/LF to produce a nice looking XML source.
    """
    meta_type = "ERP5 OOo Template"
    icon = "www/OOo.png"

    # Declarative Security
    security = ClassSecurityInfo()

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem)

    # Constructors
    constructors =   (manage_addOOoTemplate, addOOoTemplate)

    # Default Attributes
    ooo_stylesheet = 'default_ooo_template'

    # Default content type
    #content_type = 'application/vnd.sun.xml.writer' # Writer type by default
    content_type = 'text/html' # This is the only for now to produce valid XML

    # Management interface
    manage_options =  ( ZopePageTemplate.manage_options +
        (
          {'label':'Stylesheet Setting', 'action':'formSettings',
           'help':('ERPForm', 'pdfStylesheet.txt')},
        )
      )

    security.declareProtected('View management screens', 'formSettings')
    formSettings = PageTemplateFile('www/formSettings', globals(), __name__='formSettings')
    formSettings._owner = None

    security.declareProtected('Change Page Templates', 'doSettings')
    def doSettings(self, REQUEST, title, ooo_stylesheet):
      """
        Change title and ooo_stylesheet.
      """
      if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
        raise ResourceLockedError, "File is locked via WebDAV"
      self.ooo_stylesheet = ooo_stylesheet
      self.pt_setTitle(title)
      #REQUEST.set('text', self.read()) # May not equal 'text'!
      message = "Saved changes."
      if getattr(self, '_v_warnings', None):
        message = ("<strong>Warning:</strong> <i>%s</i>"
                  % '<br>'.join(self._v_warnings))
      return self.formSettings(manage_tabs_message=message)

    # Proxy method to PageTemplate
    def pt_render(self, source=0, extra_context={}):
      # Retrieve master document
      ooo_document = getattr(self, self.ooo_stylesheet)
      # Create a new builder instance
      ooo_builder = OOoBuilder(ooo_document)
      # Pass builder instance as extra_context
      extra_context['ooo_builder'] = ooo_builder
      # And render page template
      doc_xml = ZopePageTemplate.pt_render(self, source=source, extra_context=extra_context)

      # Get request and batch_mode
      batch_mode = extra_context.get('batch_mode', 0)
      request = extra_context.get('REQUEST', None)
      if not request:
        request = get_request()

      if request.get('debug',0):
        return doc_xml

      # Replace content.xml in master openoffice template
      ooo_builder.replace('content.xml', doc_xml)

      # Produce final result
      ooo = ooo_builder.render(self.title or self.id)

      # Do not send a RESPONSE if in batch_mode
      if request and not batch_mode:
        request.RESPONSE.setHeader('Content-Type','application/vnd.sun.xml.writer')
        #request.RESPONSE.setHeader('Content-Type',self.content_type) # content_type is set to text/html to produce acceptable result until solution found
        request.RESPONSE.setHeader('Content-Length',len(ooo))
        request.RESPONSE.setHeader('Content-Disposition','inline;filename=%s.ooo' % self.id)

      return ooo

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': 'misc_/ERP5Form/OOo.png',
                  'alt': self.meta_type, 'title': self.meta_type},)
        if not self._v_cooked:
            self._cook()
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                              'alt': 'Error',
                              'title': 'This template has an error'},)
        return icons


InitializeClass(OOoTemplate)

class FSOOoTemplate(FSPageTemplate, OOoTemplate):

    meta_type = "ERP5 Filesystem OOo Template"
    icon = "www/OOo.png"

    def __call__(self, *args, **kwargs):
      return OOoTemplate.__call__(self, *args, **kwargs)

InitializeClass(FSOOoTemplate)

registerFileExtension('ooot', FSOOoTemplate)
registerMetaType('ERP5 OOo Template', FSOOoTemplate)

