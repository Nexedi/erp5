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
    except:
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
    content_type = 'application/pdf'

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
      args = extra_context.get('options', None)      
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
        request.RESPONSE.setHeader('Content-Disposition','inline;filename=%s.pdf' % self.id)

      return pdf

    #def _exec(self, bound_names, args, kw):
    #    pt = getattr(self,self.pt)
    #    return pt._exec(self, bound_names, args, kw)

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
from Products.CMFReportTool.ReportTool import ReportTool
try:
  from Products.CMFReportTool.ReportTool import ZODBResourceHandler
  HAS_ZODB_RESOURCE_HANDLER=1
except ImportError:
  from Products.CMFReportTool.ReportTool import ZODBHandler, ResourceHandler
  HAS_ZODB_RESOURCE_HANDLER=0

from Products.CMFReportTool.RenderPDF.Parser import TemplateParser,DocumentParser
from Products.PageTemplates.Expressions import restrictedTraverse
from StringIO import StringIO
import xml.dom.minidom
import urllib,os.path


if HAS_ZODB_RESOURCE_HANDLER:
  class ERP5ResourceHandler(ZODBResourceHandler):
    ''' Wrapper for ZODB Resources and files'''

    def handleZODB(self,path):

      path = path.split('/')
      obj = restrictedTraverse(self.context,path,getSecurityManager())

      # check type and e.g. call object if script ...
      if callable(obj):
        try:
          obj = obj()
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
      obj = restrictedTraverse(self.context,path,getSecurityManager())

      # check type and e.g. call object if script ...
      if callable(obj):
        try:
          obj = obj()
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



class ERP5ReportTool(ReportTool):

  def renderPDF(self, templatename, document_xml, *args, **kwargs):
    """
      Render document using template
    """

    context = kwargs.get('context',None)
    if context is None:
      context = self

    encoding = kwargs.get('encoding') or 'iso-8859-1'
    rhandler = ERP5ResourceHandler(context, getattr(self, 'resourcePath', None))

    #template = self._v_templatecache.get(templatename,None)
    #if not template:
    if 1:
      template_xml = getattr(context, templatename)(*args, **kwargs)
      if type(template_xml) is not type(u'a'):
        template_xml = unicode(template_xml,encoding=encoding)
      template_xml = template_xml.encode('utf-8')
      template_dom = xml.dom.minidom.parseString(template_xml)
      template = TemplateParser(template_dom,encoding,resourceHandler=rhandler)()
      #self._v_templatecache[templatename] = template

    document_dom = xml.dom.minidom.parseString(document_xml)
    document = DocumentParser(document_dom,encoding,resourceHandler=rhandler)

    buf = StringIO()
    document(template,buf)
    buf.seek(0)
    return buf.read()


ReportTool.renderPDF = ERP5ReportTool.renderPDF
