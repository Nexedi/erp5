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

from types import StringType
from mimetypes import guess_extension
from zLOG import LOG , INFO
from zLOG import PROBLEM
from OFS.Image import File
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from TAL.TALInterpreter import FasterStringIO
from Products.ERP5Type import PropertySheet
from urllib import quote
from Globals import InitializeClass, DTMLFile, get_request
from Globals import DevelopmentMode
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from OOoUtils import OOoBuilder
from zipfile import ZipFile, ZIP_DEFLATED
try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO
import re
import itertools

try:
  from webdav.Lockable import ResourceLockedError
  from webdav.WriteLockInterface import WriteLockInterface
  SUPPORTS_WEBDAV_LOCKS = 1
except ImportError:
  SUPPORTS_WEBDAV_LOCKS = 0

from Products.ERP5.Document.Document import ConversionError
import Products.ERP5Type.Document

try:
  from libxml2 import parseDoc
except ImportError:
  LOG('OOoUtils', INFO, "Can't import libxml2.parseDoc")
  class parseDoc:
    def __init__(self, *args, **kw):
      raise ImportError, "Sorry, it was not possible to import libxml2 library, python2.4-libxml2 is not installed"

# Constructors
manage_addOOoTemplate = DTMLFile("dtml/OOoTemplate_add", globals())

def addOOoTemplate(self, id, title="", xml_file_id="content.xml", REQUEST=None):
  """Add OOo template to folder.

  id     -- the id of the new OOo template to add
  title  -- the title of the OOo to add
  xml_file_id -- The Id of edited xml file
  Result -- empty string
  """
  # add actual object
  id = self._setObject(id, OOoTemplate(id, title, xml_file_id))
  if REQUEST is not None:
    file = REQUEST.form.get('file')
    if file.filename:
      # Get the template in the associated context and upload the file
      getattr(self,id).pt_upload(REQUEST, file)
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

class OOoTemplateStringIO(FasterStringIO):
  def write(self, s):
    if type(s) == unicode:
      s = s.encode('utf-8')
    FasterStringIO.write(self, s)

class OOoTemplate(ZopePageTemplate):
  """
  A page template which is able to embed and OpenOffice
  file (zip archive) and replace content.xml at render time
  with XML dynamically generated through TAL/TALES/METAL expressions

  TODO:
    - find a way to embed TALES in OOo documents in such
      way that editing with OOo does not destroy TAL/TALES

    - add preprocessing option to handle explicit macros in
      OOo in any language. Include debugging options in this case
      (on preprocessed source rather than pure source)

    - add interface for Cache (http/RAM)
  """
  meta_type = "ERP5 OOo Template"
  icon = "www/OOo.png"

  # NOTE: 100 is just pure random starting number
  # it won't influence the code at all
  document_counter = itertools.count(100)
  # Every linked OLE document is in a directory starting with 'Obj'
  _OLE_directory_prefix  = 'Obj'
  # every OOo document have a content-type starting like this
  _OOo_content_type_root = 'application/vnd.sun.xml.'
  _ODF_content_type_root = 'application/vnd.oasis.opendocument.'

  # Declarative Security
  security = ClassSecurityInfo()

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem)

  # Constructors
  constructors =   (manage_addOOoTemplate, addOOoTemplate)

  # Default Attributes
  ooo_stylesheet = 'Base_getODTStyleSheet'
  ooo_xml_file_id = 'content.xml'

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
  formSettings = PageTemplateFile('www/formSettings', globals(),
                                  __name__='formSettings')
  formSettings._owner = None

  def __init__(self, id, title, xml_file_id='content.xml', *args,**kw):
    ZopePageTemplate.__init__(self, id, title, *args, **kw)
    # we store the attachments of the uploaded document
    self.OLE_documents_zipstring = None
    self.ooo_xml_file_id = xml_file_id
  # Every OOoTemplate uses UTF-8 or Unicode, so a special StringIO class
  # must be used, which does not care about response.
  def StringIO(self):
    return OOoTemplateStringIO()

  def pt_upload(self, REQUEST, file=''):
    """Replace the document with the text in file."""
    if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
      raise ResourceLockedError, "File is locked via WebDAV"

    if type(file) is not StringType:
      if not file: raise ValueError, 'File not specified'
      file = file.read()

    if file.startswith("PK") : # FIXME: this condition is probably not enough
      # this is a OOo zip file, extract the content
      builder = OOoBuilder(file)
      attached_files_list = [n for n in builder.getNameList()
        if n.startswith(self._OLE_directory_prefix)
        or n.startswith('Pictures')
        or n == 'META-INF/manifest.xml' ]
      # destroy a possibly pre-existing OLE document set
      if self.OLE_documents_zipstring:
        self.OLE_documents_zipstring = None
      # create a zip archive and store it
      if attached_files_list:
        memory_file = StringIO()
        try:
          zf = ZipFile(memory_file, mode='w', compression=ZIP_DEFLATED)
        except RuntimeError:
          zf = ZipFile(memory_file, mode='w')
        for attached_file in attached_files_list:
            zf.writestr(attached_file, builder.extract(attached_file) )
        zf.close()
        memory_file.seek(0)
        self.OLE_documents_zipstring = memory_file.read()
      self.content_type = builder.getMimeType()
      #get XSL stylesheet from portal_skins
      xsl_dtml = getattr(self, 'ERP5OOoTemplate_ooo2zpt', None)
      xsl_content = None
      if xsl_dtml is not None:
        xsl_content = xsl_dtml()
      file = builder.prepareContentXml(self.ooo_xml_file_id, xsl_content)
    return ZopePageTemplate.pt_upload(self, REQUEST, file)

  security.declareProtected('Change Page Templates', 'pt_edit')
  def pt_edit(self, text, content_type):
    if content_type:
      self.content_type = str(content_type)
    if hasattr(text, 'read'):
      text = text.read()
    self.write(text)

  security.declareProtected('Change Page Templates', 'doSettings')
  def doSettings(self, REQUEST, title, xml_file_id, ooo_stylesheet):
    """
      Change title, xml_file_id and ooo_stylesheet.
    """
    if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
      raise ResourceLockedError, "File is locked via WebDAV"
    self.ooo_stylesheet = ooo_stylesheet
    self.ooo_xml_file_id = xml_file_id
    self.pt_setTitle(title)
    #REQUEST.set('text', self.read()) # May not equal 'text'!
    message = "Saved changes."
    if getattr(self, '_v_warnings', None):
      message = ("<strong>Warning:</strong> <i>%s</i>"
                % '<br>'.join(self._v_warnings))
    return self.formSettings(manage_tabs_message=message)

  def _resolvePath(self, path):
    return self.getPortalObject().unrestrictedTraverse(path)

  def renderIncludes(self, here, text, extra_context, request, sub_document=None):
    attached_files_dict = {}
    arguments_re = re.compile('''(\S+?)\s*=\s*('|")(.*?)\\2\s*''',re.DOTALL)
    def getLengthInfos( opts_dict, opts_names ):
      ret = []
      for opt_name in opts_names:
        try:
          val = opts_dict.pop(opt_name)
          if val.endswith('cm'):
            val = val[:-2]
          val = float( val )
        except (ValueError, KeyError):
          val = None
        ret.append(val)
      return ret

    def replaceIncludes(path):
      # Find the page template based on the path and remove path from dict
      document = self._resolvePath(path)
      document_text = ZopePageTemplate.pt_render(document,
                                                 extra_context=extra_context)

      # Find the type of the embedded document
      document_type = document.content_type

      # Prepare a subdirectory to store embedded objects
      actual_idx = self.document_counter.next()
      dir_name = '%s%d'%(self._OLE_directory_prefix, actual_idx)

      if sub_document: # sub-document means sub-directory
        dir_name = sub_document + '/' + dir_name

      # Get the stylesheet of the embedded openoffice document
      ooo_stylesheet = document.ooo_stylesheet
      if ooo_stylesheet:
        ooo_stylesheet = getattr(here, ooo_stylesheet)
        # If ooo_stylesheet is dynamic, call it
        try:
          ooo_stylesheet = ooo_stylesheet()
        except AttributeError:
          pass
        temp_builder = OOoBuilder(ooo_stylesheet)
        stylesheet = temp_builder.extract('styles.xml')
      else:
        stylesheet = None

      # Start recursion if necessary
      sub_attached_files_dict = {}
      if 'office:include' in document_text: # small optimisation to avoid recursion if possible
        (document_text, sub_attached_files_dict ) = self.renderIncludes(document_text, dir_name, extra_context, request)

      # Attach content, style and settings if any
      attached_files_dict[dir_name] = dict(document=document_text,
                                           doc_type=document_type,
                                           stylesheet=stylesheet)

      attached_files_dict.update(sub_attached_files_dict)

      # Build the new tag
      new_path = './%s' % dir_name.split('/')[-1]
      return new_path

    def replaceIncludesImg(match):
      options_dict = { 'text:anchor-type': 'paragraph' }
      options_dict.update((x[0], x[2]) for x in arguments_re.findall(match.group(1)))
      for old_name, name, default in (('x', 'svg:x', '0cm'),
                                      ('y', 'svg:y', '0cm'),
                                      ('style', 'draw:style-name', 'fr1')):
        options_dict.setdefault(name, options_dict.pop(old_name, default))

      picture = self._resolvePath(options_dict.pop('path').encode())

      # If this is not a File, build a new file with this content
      if not isinstance(picture, File):
        tmp_picture = Products.ERP5Type.Document.newTempImage(self, 'tmp')
        tmp_picture.setData(picture())
        picture = tmp_picture

      picture_type = options_dict.pop('type', None)

      picture_data = getattr(aq_base(picture), 'data', None)
      if picture_data is None:
        picture_data = picture.Base_download()
        if picture_type is None:
          picture_type = picture.content_type()
      else:
        # "standard" filetype case (Image or File)
        picture_data = str(picture_data)
        if picture_type is None:
          picture_type = picture.getContentType()

      w, h, maxwidth, maxheight = getLengthInfos(options_dict,
                                  ('width', 'height', 'maxwidth', 'maxheight'))

      aspect_ratio = 1
      try: # try image properties
        aspect_ratio = float(picture.width) / float(picture.height)
      except (TypeError, ZeroDivisionError):
        try: # try ERP5.Document.Image API
          height = float(picture.getHeight())
          if height:
            aspect_ratio = float(picture.getWidth()) / height
        except AttributeError: # fallback to Photo API
          height = float(picture.height())
          if height:
            aspect_ratio = float(picture.width()) / height
      # fix a default value and correct the aspect
      if h is None:
        if w is None:
          w = 10.0
        h = w / aspect_ratio
      elif w is None:
        w = h * aspect_ratio
      # picture is too large
      if maxwidth and maxwidth < w:
        w = maxwidth
        h = w / aspect_ratio
      if maxheight and maxheight < h:
        h = maxheight
        w = h * aspect_ratio

      actual_idx = self.document_counter.next()
      pic_name = 'Pictures/picture%d%s' \
                 % (actual_idx, guess_extension(picture_type) or '')

      # XXX: Pictures directory not managed (seems facultative)
      #  <manifest:file-entry manifest:media-type="" manifest:full-path="ObjBFE4F50D/Pictures/"/>
      is_legacy = 'oasis.opendocument' not in self.content_type
      replacement = ('<draw:frame %s>\n<draw:image %s/></draw:frame>',
                     '<draw:image %s %s/>')[is_legacy] % (
        '''draw:name="ERP5Image%d" svg:width="%.3fcm" svg:height="%.3fcm"%s'''
        % (actual_idx, w, h,
           ''.join(' %s="%s"' % opt for opt in options_dict.iteritems())),
        '''xlink:href="%s%s" xlink:type="simple"
           xlink:show="embed" xlink:actuate="onLoad"'''
        % (is_legacy and '#' or '', pic_name))

      if sub_document: # sub-document means sub-directory
        pic_name = sub_document + '/' + pic_name

      attached_files_dict[pic_name] = dict(
        document=picture_data,
        doc_type=picture_type,
      )

      if not (self.content_type.endswith('draw') or
              self.content_type.endswith('presentation') or
              self.content_type.endswith('writer') or
              self.content_type.endswith('text')):
        replacement = '<text:p text:style-name="Standard">'+replacement+'</text:p>'
      return replacement

    xml_doc = parseDoc(text)
    draw_ns = xml_doc.getRootElement().searchNs(xml_doc, 'draw')
    xlink_ns = xml_doc.getRootElement().searchNs(xml_doc, 'xlink')
    for office_include in xml_doc.xpathEval('//*[name() = "office:include"]'):
      marshal_list = office_include.xpathEval('./marshal')
      if marshal_list:
        from xml.marshal.generic import loads
        arg_dict = loads(marshal_list[0].serialize('utf-8', 0))
        extra_context.update(arg_dict)
        request.other.update(arg_dict)
      attr_path_list = office_include.xpathEval('./@path')
      path = attr_path_list[0].content
      new_path = replaceIncludes(path)
      draw_object = xml_doc.newChild(draw_ns, 'object', None)
      draw_object.setNsProp(xlink_ns, 'href', new_path)
      draw_object.copyPropList(office_include)
      office_include.replaceNode(draw_object)
    text = xml_doc.serialize('utf-8', 0)
    xml_doc.freeDoc()
    text = re.sub('<\s*office:include_img\s+(.*?)\s*/\s*>(?s)', replaceIncludesImg, text)

    return (text, attached_files_dict)
  # Proxy method to PageTemplate
  def pt_render(self, source=0, extra_context={}):
    # Get request
    request = extra_context.get('REQUEST', self.REQUEST)
    # Get parent object (the one to render this template on)
    here = getattr(self, 'aq_parent', None)
    if here is None:
      # This is a system error
      raise ValueError, 'Can not render a template without a parent acquisition context'
    # Retrieve master document
    ooo_document = getattr(here, self.ooo_stylesheet)
    format = request.get('format')
    try:
      # If style is dynamic, call it
      if getattr(aq_base(ooo_document), '__call__', None) is not None:
        request.set('format', None)
        ooo_document = ooo_document()
    finally:
      request.set('format', format)
    # Create a new builder instance
    ooo_builder = OOoBuilder(ooo_document)
    # Pass builder instance as extra_context
    extra_context['ooo_builder'] = ooo_builder

    # And render page template
    doc_xml = ZopePageTemplate.pt_render(self, source=source,
                                         extra_context=extra_context)
    if isinstance(doc_xml, unicode):
      doc_xml = doc_xml.encode('utf-8')

    # Replace the includes
    (doc_xml,attachments_dict) = self.renderIncludes(here, doc_xml,
                                                     extra_context, request)

    try:
      default_styles_text = ooo_builder.extract('styles.xml')
    except AttributeError:
      default_styles_text = None

    # Add the associated files
    for dir_name, document_dict in attachments_dict.iteritems():
      # Special case : the document is an OOo one
      if document_dict['doc_type'].startswith(self._OOo_content_type_root) or \
         document_dict['doc_type'].startswith(self._ODF_content_type_root):
        ooo_builder.addFileEntry(full_path=dir_name,
                                 media_type=document_dict['doc_type'])
        ooo_builder.addFileEntry(full_path=dir_name + '/content.xml',
                                 media_type='text/xml', content=document_dict['document'])
        styles_text = default_styles_text
        if document_dict.has_key('stylesheet') and document_dict['stylesheet']:
          styles_text = document_dict['stylesheet']
        if styles_text:
          ooo_builder.addFileEntry(full_path=dir_name + '/styles.xml',
                                   media_type='text/xml', content=styles_text)
      else: # Generic case
        ooo_builder.addFileEntry(full_path=dir_name,
                                 media_type=document_dict['doc_type'],
                                 content=document_dict['document'])

    # Debug mode
    if request.get('debug',0):
      return doc_xml

    # Replace content.xml in master openoffice template
    ooo_builder.replace(self.ooo_xml_file_id, doc_xml)

    # Old templates correction
    try:
      self.OLE_documents_zipstring
    except AttributeError:
      self.OLE_documents_zipstring = None

    # Convert if necessary
    opts = extra_context.get("options", dict())

    # Get batch_mode
    batch_mode = opts.get('batch_mode', None)

    # If the file has embedded OLE documents, restore it
    if self.OLE_documents_zipstring:
      additional_builder = OOoBuilder( self.OLE_documents_zipstring )
      for name in additional_builder.getNameList():
        ooo_builder.replace(name, additional_builder.extract(name) )

    # Update the META informations
    ooo_builder.updateManifest()

    # Produce final result
    if batch_mode:
      ooo = ooo_builder.render()
    else:
      ooo = ooo_builder.render(name=self.title or self.id)
    
    format = opts.get('format', request.get('format', None))
    if format:
      return self._asFormat(ooo, format, request, batch_mode)

    if not format and not batch_mode:
      request.RESPONSE.setHeader('Content-Type','%s; charset=utf-8' % self.content_type)
      request.RESPONSE.setHeader('Content-disposition', 'inline;filename="%s"' % self.title_or_id())
    
    if DevelopmentMode:
      # Validate XML in development mode
      from Products.ERP5OOo.tests.utils import Validator
      err_list = Validator().validate(ooo)
      if err_list:
        LOG('ERP5OOo', PROBLEM,
            'Validation of %s failed:\n%s' % (self.getId(), ''.join(err_list)))
    
    return ooo
  
  def om_icons(self):
    """Return a list of icon URLs to be displayed by an ObjectManager"""
    icons = ({'path': 'misc_/ERP5OOo/OOo.png',
              'alt': self.meta_type, 'title': self.meta_type},)
    if not self._v_cooked:
        self._cook()
    if self._v_errors:
        icons = icons + ({'path': 'misc_/PageTemplates/exclamation.gif',
                          'alt': 'Error',
                          'title': 'This template has an error'},)
    return icons

  def _asPdf(self, ooo, REQUEST=None):
    """
    Return OOo report as pdf
    """
    return self._asFormat(ooo, 'pdf', REQUEST)

  def _asFormat(self, ooo, format, REQUEST=None, batch_mode=0):
    # Now create a temp OOoDocument to convert data to pdf
    from Products.ERP5Type.Document import newTempOOoDocument
    tmp_ooo = newTempOOoDocument(self, self.title_or_id())
    tmp_ooo.edit(base_data=ooo,
                 fname=self.title_or_id(),
                 source_reference=self.title_or_id(),
                 base_content_type=self.content_type,)
    tmp_ooo.oo_data = ooo
    if format == 'pdf' and not batch_mode:
      # Slightly different implementation
      # now convert it to pdf
      tgts = [x[1] for x in tmp_ooo.getTargetFormatItemList()
              if x[1].endswith('pdf')]
      if len(tgts) > 1:
        REQUEST.RESPONSE.setHeader('Content-type', 'text/html')
        REQUEST.RESPONSE.setHeader('Content-disposition',
            'inline;filename="%s.pdf"' % self.title_or_id())
        raise ValueError, 'multiple pdf formats found - this shouldnt happen'
      if len(tgts) == 0:
        REQUEST.RESPONSE.setHeader('Content-type', 'text/html')
        REQUEST.RESPONSE.setHeader('Content-disposition',
            'inline;filename="%s.pdf"' % self.title_or_id())
        raise ValueError, 'no pdf format found'
      fmt = tgts[0]
      mime, data = tmp_ooo.convert(fmt)
      if REQUEST is not None:
          REQUEST.RESPONSE.setHeader('Content-type', 'application/pdf')
          REQUEST.RESPONSE.setHeader('Content-disposition',
              'attachment;filename="%s.pdf"' % self.title_or_id())
      return data
    mime, data = tmp_ooo.convert(format)
    if REQUEST is not None and not batch_mode:
      REQUEST.RESPONSE.setHeader('Content-type', mime)
      REQUEST.RESPONSE.setHeader('Content-disposition',
          'attachment;filename="%s.%s"' % (self.title_or_id(),format))
        # FIXME the above lines should return zip format when html was requested
    return data

InitializeClass(OOoTemplate)

class FSOOoTemplate(FSPageTemplate, OOoTemplate):

  meta_type = "ERP5 Filesystem OOo Template"
  icon = "www/OOo.png"

  def __call__(self, *args, **kwargs):
    return OOoTemplate.__call__(self, *args, **kwargs)

InitializeClass(FSOOoTemplate)

registerFileExtension('ooot', FSOOoTemplate)
registerMetaType(OOoTemplate.meta_type, FSOOoTemplate)
