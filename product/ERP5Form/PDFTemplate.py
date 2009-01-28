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

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.Formulator.Form import BasicForm
from Products.Formulator.Form import fields
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ERP5Type import PropertySheet

from urllib import quote
from Globals import InitializeClass, PersistentMapping, DTMLFile, get_request
from AccessControl import Unauthorized, getSecurityManager, ClassSecurityInfo
import urllib2
from ZODB.POSException import ConflictError

from Products.ERP5Type.Utils import UpperCase

from zLOG import LOG

try:
    from webdav.Lockable import ResourceLockedError
    from webdav.WriteLockInterface import WriteLockInterface
    SUPPORTS_WEBDAV_LOCKS = 1
except ImportError:
    SUPPORTS_WEBDAV_LOCKS = 0

# Constructors
manage_addPDFTemplate = DTMLFile("dtml/PDFTemplate_add", globals())

def addPDFTemplate(self, id, title="", REQUEST=None):
    """Add form to folder.
    id     -- the id of the new form to add
    title  -- the title of the form to add
    Result -- empty string
    """
    # add actual object
    id = self._setObject(id, PDFTemplate(id, title))
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


class PDFTemplate(ZopePageTemplate):
    """
        A Formulator form with a built-in rendering parameter based
        on page templates or DTML.
    """
    meta_type = "ERP5 PDF Template"
    icon = "www/PDF.png"

    # Declarative Security
    security = ClassSecurityInfo()

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem)

    # Constructors
    constructors =   (manage_addPDFTemplate, addPDFTemplate)

    # Default Attributes
    pdf_stylesheet = 'default_pdf_template'

    # XXX The content-type should be application/pdf, but if this is used, PageTemplate uses
    # TALParser instead of HTMLTALParser. This generates a strange error due to the encoding problem.
    # Because the XML declaration must specify ISO-8859-1 but PDFTemplate itself uses UTF-8.
    # Once reportlab is fixed, we will be able to use UTF-8 in every place, then this problem will
    # disappear...
    #
    # Simply speaking, reportlab is bad.
    #content_type = 'application/pdf'
    content_type = 'text/html'

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
    def doSettings(self, REQUEST, title, pdf_stylesheet):
      """
        Change title and pdf_stylesheet.
      """
      if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
        raise ResourceLockedError, "File is locked via WebDAV"
      self.pdf_stylesheet = pdf_stylesheet
      self.pt_setTitle(title)
      #REQUEST.set('text', self.read()) # May not equal 'text'!
      message = "Saved changes."
      if getattr(self, '_v_warnings', None):
        message = ("<strong>Warning:</strong> <i>%s</i>"
                  % '<br>'.join(self._v_warnings))
      return self.formSettings(manage_tabs_message=message)

    # Proxy method to PageTemplate
    def pt_render(self, source=0, extra_context={}):
      doc_xml = ZopePageTemplate.pt_render(self, source=source, extra_context=extra_context)

      # Unmarshall arguments to __call__ API
      args = extra_context.get('options', [])
      kwargs = extra_context.copy()
      if kwargs.has_key('options'): del kwargs['options']
      if kwargs.has_key('context'): del kwargs['context']

      batch_mode = extra_context.get('batch_mode', 0)

      request = extra_context.get('REQUEST', None)
      if not request:
        request = get_request()

      if request.get('debug',0):
        return doc_xml

      report_tool = getToolByName(self, 'portal_report')
      pdf = report_tool.renderPDF(self.pdf_stylesheet, doc_xml, context=self.pt_getContext()['here'], *args, **kwargs)
      if request and not batch_mode:
        request.RESPONSE.setHeader('Content-Type','application/pdf')
        request.RESPONSE.setHeader('Content-Length',len(pdf))
        request.RESPONSE.setHeader('Content-Disposition','inline;filename=%s.pdf' % self.title_or_id())

      return pdf

    #def _exec(self, bound_names, args, kw):
    #    pt = getattr(self,self.pt)
    #    return pt._exec(self, bound_names, args, kw)

    def om_icons(self):
        """Return a list of icon URLs to be displayed by an ObjectManager"""
        icons = ({'path': 'misc_/ERP5Form/PDF.png',
                  'alt': self.meta_type, 'title': self.meta_type},)
        if not self._v_cooked:
            self._cook()
        if self._v_errors:
            icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                              'alt': 'Error',
                              'title': 'This template has an error'},)
        return icons


InitializeClass(PDFTemplate)

class FSPDFTemplate(FSPageTemplate, PDFTemplate):

    meta_type = "ERP5 Filesystem PDF Template"
    icon = "www/PDF.png"

    def __call__(self, *args, **kwargs):
      return PDFTemplate.__call__(self, *args, **kwargs)

InitializeClass(FSPDFTemplate)

registerFileExtension('pdft', FSPDFTemplate)
registerMetaType('ERP5 PDF Template', FSPDFTemplate)

# Dynamic Patch
try:
  from Products.CMFReportTool.ReportTool import ReportTool
except ImportError:
  ReportTool = None


if ReportTool:
  try:
    from Products.CMFReportTool.ReportTool import ZODBResourceHandler
    HAS_ZODB_RESOURCE_HANDLER=1
  except ImportError:
    from Products.CMFReportTool.ReportTool import ZODBHandler, ResourceHandler
    HAS_ZODB_RESOURCE_HANDLER=0

  from Products.CMFReportTool.RenderPDF.Parser import TemplateParser,DocumentParser

  try:
      # Zope 2.10 and later.
      from Products.PageTemplates.Expressions import boboAwareZopeTraverse
  except ImportError:
      # Zope 2.9 and earlier.
      boboAwareZopeTraverse = None
      from Products.PageTemplates.Expressions import restrictedTraverse

  from StringIO import StringIO
  import xml.dom.minidom
  import urllib,os.path


  if HAS_ZODB_RESOURCE_HANDLER:
    class ERP5ResourceHandler(ZODBResourceHandler):
      ''' Wrapper for ZODB Resources and files'''

      def handleZODB(self,path):

        path = path.split('/')
        if boboAwareZopeTraverse is None:
            obj = restrictedTraverse(self.context,path,getSecurityManager())
        else:
            # XXX only the request should be required, but this looks ad-hoc..
            econtext = dict(request=self.context.REQUEST)
            obj = boboAwareZopeTraverse(self.context, path, econtext)


        # check type and e.g. call object if script ...
        if callable(obj):
          try:
            obj = obj()
          except (ConflictError, RuntimeError):
            raise
          except:
            pass

        ## for OFS.Image-like objects
        if hasattr(obj,'_original'):
          obj = obj._original._data()
        elif hasattr(obj,'_data'):
          obj = obj._data
        elif hasattr(obj,'data'):
          obj = obj.data

        return StringIO(str(obj))
  else:
    class ERP5ResourceHandler(ResourceHandler):
      ''' Wrapper for ZODB Resources and files'''
      def __init__(self, context=None, resource_path=None):
          zodbhandler = ERP5ZODBHandler(context)
          self.opener = urllib2.build_opener(zodbhandler)

    class ERP5ZODBHandler(ZODBHandler):
      def zodb_open(self, req):
        path = req.get_selector()
        path = path.split('/')
        if boboAwareZopeTraverse is None:
            obj = restrictedTraverse(self.context,path,getSecurityManager())
        else:
            # XXX only the request should be required, but this looks ad-hoc..
            econtext = dict(request=self.context.REQUEST)
            obj = boboAwareZopeTraverse(self.context, path, econtext)

        # check type and e.g. call object if script ...
        if callable(obj):
          try:
            obj = obj()
          except (ConflictError, RuntimeError):
            raise
          except:
            pass

        ## for OFS.Image-like objects
        if hasattr(obj,'_original'):
          obj = obj._original._data()
        elif hasattr(obj,'_data'):
          obj = obj._data
        elif hasattr(obj,'data'):
          obj = obj.data

        return StringIO(str(obj))



  def ReportTool_renderPDF(self, templatename, document_xml, *args, **kwargs):
    """
      Render document using template
    """

    context = kwargs.get('context',None)
    if context is None:
      context = self

    encoding = kwargs.get('encoding') or 'UTF-8'
    #LOG('ReportTool_renderPDF', 0, 'encoding = %r' % encoding)
    rhandler = ERP5ResourceHandler(context, getattr(self, 'resourcePath', None))

    # if zope gives us the xml in unicode
    # we need to encode it before it can be parsed
    template_xml = getattr(context, templatename)(*args, **kwargs)
    if type(template_xml) is type(u''):
      template_xml = self._encode(template_xml, encoding)
    if type(document_xml) is type(u''):
      document_xml = self._encode(document_xml, encoding)
    #LOG('ReportTool_renderPDF', 0, 'template_xml = %r, document_xml = %r' % (template_xml, document_xml))

    # XXXXX Because reportlab does not support UTF-8, use Latin-1. What a mess.
    template_xml = unicode(template_xml,encoding).encode('iso-8859-1')
    document_xml = unicode(document_xml,encoding).encode('iso-8859-1','replace')
    encoding = 'iso-8859-1'

    # create the PDFTemplate from xml
    template_dom = xml.dom.minidom.parseString(template_xml)
    template_dom.encoding = encoding
    template = TemplateParser(template_dom,encoding,resourceHandler=rhandler)()

    # create the PDFDocment from xml
    document_dom = xml.dom.minidom.parseString(document_xml)
    document_dom.encoding = encoding
    document = DocumentParser(document_dom,encoding,resourceHandler=rhandler)

    # create the PDF itself using the document and the template
    buf = StringIO()
    document(template,buf)
    buf.seek(0)
    return buf.read()


  ReportTool.renderPDF = ReportTool_renderPDF
