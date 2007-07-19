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
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.CMFCore.DirectoryView import registerFileExtension, registerMetaType
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ERP5Type import PropertySheet
from urllib import quote
from Globals import InitializeClass, DTMLFile, get_request
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

  # Declarative Security
  security = ClassSecurityInfo()

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem)

  # Constructors
  constructors =   (manage_addOOoTemplate, addOOoTemplate)

  # Default Attributes
  ooo_stylesheet = 'Base_getODTStyleSheet'

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

  def __init__(self,*args,**kw):
    ZopePageTemplate.__init__(self,*args,**kw)
    # we store the attachments of the uploaded document
    self.OLE_documents_zipstring = None

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
      file = builder.prepareContentXml()

    return ZopePageTemplate.pt_upload(self, REQUEST, file)

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

  def _resolvePath(self, path):
    return self.getPortalObject().unrestrictedTraverse(path)

  def renderIncludes(self, here, text, sub_document=None):
    attached_files_dict = {}
    arguments_re = re.compile('(\w+)\s*=\s*"(.*?)"\s*',re.DOTALL)

    def getLengthInfos( opts_dict, opts_names ):
      ret = []
      for opt_name in opts_names:
        try:
          val = opts_dict[opt_name]
          if val.endswith('cm'):
            val = val[:-2]
          val = float( val )
        except (ValueError, KeyError):
          val = None
        ret.append(val)
      return ret

    def replaceIncludes(match):
      options_dict = dict( style="fr1", x="0cm", y="0cm" )
      options_dict.update( dict(arguments_re.findall( match.group(1) )) )
      document = self._resolvePath( options_dict['path'] )
      #document_text = document.read()
      document_text = ZopePageTemplate.pt_render(document) # extra_context is missing

      if 'type' not in options_dict:
        options_dict['type'] = document.content_type
      else: # type passed in short form as an attribute
        options_dict['type'] = self._OOo_content_type_root + options_dict['type']

      w, h, x, y = getLengthInfos( options_dict , ('width', 'height', 'x', 'y') )
      # Set defaults
      if w is None:
        w = 10.0
      if h is None:
        h = 10.0
      if  x is None:
        x = 0.0
      if  y is None:
        y = 0.0

      actual_idx = self.document_counter.next()
      dir_name = '%s%d'%(self._OLE_directory_prefix,actual_idx)

      if sub_document: # sub-document means sub-directory
        dir_name = sub_document + '/' + dir_name

      try:
        ooo_stylesheet = getattr(here, document.ooo_stylesheet)
        # If style is dynamic, call it
        try:
          ooo_stylesheet = ooo_stylesheet()
        except AttributeError:
          pass
        temp_builder = OOoBuilder(ooo_stylesheet)
        stylesheet = temp_builder.extract('styles.xml')
      except AttributeError:
        stylesheet = None

      sub_attached_files_dict = {}
      if 'office:include' in document_text: # small optimisation to avoid recursion if possible
        (document_text, sub_attached_files_dict ) = self.renderIncludes(document_text, dir_name)

      # View*    = writer
      # Visible* = calc
      settings_text = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE office:document-settings PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">
<office:document-settings xmlns:office="http://openoffice.org/2000/office"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:config="http://openoffice.org/2001/config" office:version="1.0">
<office:settings>
<config:config-item-set config:name="view-settings">
<config:config-item config:name="ViewAreaTop" config:type="int">0</config:config-item>
<config:config-item config:name="ViewAreaLeft" config:type="int">0</config:config-item>
<config:config-item config:name="ViewAreaWidth" config:type="int">%(w)d</config:config-item>
<config:config-item config:name="ViewAreaHeight" config:type="int">%(h)d</config:config-item>
<config:config-item config:name="VisibleAreaTop" config:type="int">0</config:config-item>
<config:config-item config:name="VisibleAreaLeft" config:type="int">0</config:config-item>
<config:config-item config:name="VisibleAreaWidth" config:type="int">%(w)d</config:config-item>
<config:config-item config:name="VisibleAreaHeight" config:type="int">%(h)d</config:config-item>
</config:config-item-set>
</office:settings>
</office:document-settings>"""%dict( w=int(w*1000) , h=int(h*1000) ) # convert from 10^-2 (centimeters) to 10^-5
      attached_files_dict[dir_name] = dict(document = document_text,
              doc_type = options_dict['type'], stylesheet = stylesheet )
      attached_files_dict[dir_name+'/settings.xml'] = dict( document = settings_text,
              doc_type = 'text/xml' )
      attached_files_dict.update(sub_attached_files_dict )

      # add a paragraph with the OLE document in it
      # The dir_name is relative here, extract the last path component
      replacement = """
      <draw:object draw:style-name="%s" draw:name="ERP5IncludedObject%d"
      text:anchor-type="paragraph" svg:x="%.3fcm" svg:y="%.3fcm"
      svg:width="%.3fcm" svg:height="%.3fcm" xlink:href="#./%s
      " xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
      """%(options_dict['style'], actual_idx, x, y, w, h, dir_name.split('/')[-1])
      if not self.content_type.endswith('draw'):
        replacement = '<text:p text:style-name="Standard">'+replacement+'</text:p>'
      return replacement

    def replaceIncludesImg(match):
      options_dict = dict( x='0cm', y='0cm', style="fr1" )
      options_dict.update( dict(arguments_re.findall( match.group(1) )) )
      picture = self._resolvePath( options_dict['path'] )

      # "standard" filetype == Image or File , for ERP objects the
      # manipulations are different
      is_standard_filetype = True

      if getattr(picture, 'data', None) is None \
              or callable(picture.content_type):
        is_standard_filetype = False

      if is_standard_filetype:
        picture_data = str(picture.getData())
      else:
        picture_data = picture.Base_download()

      # fetch the content-type of the picture (generally guessed by zope)
      if 'type' not in options_dict:
        if is_standard_filetype:
          options_dict['type'] = picture.content_type
        else:
          options_dict['type'] = picture.content_type()

      if '/' not in options_dict['type']:
        options_dict['type'] = 'image/' + options_dict['type']

      w, h, maxwidth, maxheight = getLengthInfos( options_dict, ('width','height','maxwidth','maxheight') )

      try: # try image properties
        aspect_ratio = float(picture.width) / float(picture.height)
      except (TypeError, ZeroDivisionError):
        try: # try ERP5.Document.Image API
          aspect_ratio = float(picture.getWidth()) / float(picture.getHeight())
        except AttributeError: # fallback to Photo API
          aspect_ratio = float(picture.width()) / float(picture.height())
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
      pic_name = 'Pictures/picture%d.%s'%(actual_idx, options_dict['type'].split('/')[-1])

      if sub_document: # sub-document means sub-directory
        pic_name = sub_document+'/'+pic_name

      attached_files_dict[pic_name] = dict(
        document = picture_data,
        doc_type = options_dict['type']
      )
      # XXX: Pictures directory not managed (seems facultative)
      #  <manifest:file-entry manifest:media-type="" manifest:full-path="ObjBFE4F50D/Pictures/"/>
      is_legacy = ('oasis.opendocument' not in self.content_type)
      replacement = """<draw:image draw:style-name="%s" draw:name="ERP5Image%d"
      text:anchor-type="paragraph" svg:x="%s" svg:y="%s"
      svg:width="%.3fcm" svg:height="%.3fcm" xlink:href="%sPictures/%s"
      xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
      """ % (options_dict['style'], actual_idx,
             options_dict['x'], options_dict['y'],
             w, h,
             is_legacy and '#' or '',
             pic_name.split('/')[-1] )
      if not (self.content_type.endswith('draw') or
              self.content_type.endswith('presentation') or
              self.content_type.endswith('writer') or
              self.content_type.endswith('text')):
        replacement = '<text:p text:style-name="Standard">'+replacement+'</text:p>'
      return replacement

    # NOTE: (?s) at the end is for including '\n' when matching '.'
    # It's an equivalent to DOTALL option passing (but sub can't get options parameter)
    text = re.sub('<\s*office:include_img\s+(.*?)\s*/\s*>(?s)', replaceIncludesImg, text)
    text = re.sub('<\s*office:include\s+(.*?)\s*/\s*>(?s)', replaceIncludes, text)
    return (text, attached_files_dict)

  # Proxy method to PageTemplate
  def pt_render(self, source=0, extra_context={}):
    # Get request
    request = extra_context.get('REQUEST', None)
    if not request:
      request = get_request()

    # Get parent object (the one to render this template on)
    here = getattr(self, 'aq_parent', None)
    if here is None:
      # This is a system error
      raise ValueError, 'Can not render a template without a parent acquisition context'
    # Retrieve master document
    ooo_document = getattr(here, self.ooo_stylesheet)
    # If style is dynamic, call it
    try:
      ooo_document = ooo_document()
    except AttributeError:
      pass
    # Create a new builder instance
    ooo_builder = OOoBuilder(ooo_document)
    # Pass builder instance as extra_context
    extra_context['ooo_builder'] = ooo_builder
    # And render page template
    doc_xml = ZopePageTemplate.pt_render(self, source=source, extra_context=extra_context)

    # Replace the includes
    (doc_xml,attachments_dict) = self.renderIncludes(here, doc_xml)

    try:
      default_styles_text = ooo_builder.extract('styles.xml')
    except AttributeError:
      default_styles_text = None
    # Add the associated files
    for dir_name, document_dict in attachments_dict.iteritems():
      # Special case : the document is an OOo one
      if document_dict['doc_type'].startswith(self._OOo_content_type_root):
        ooo_builder.addFileEntry(full_path = dir_name,
                  media_type = document_dict['doc_type'] )
        ooo_builder.addFileEntry(full_path = dir_name+'/content.xml',
                  media_type = 'text/xml',content = document_dict['document'] )
        styles_text = default_styles_text
        if document_dict.has_key('stylesheet') and document_dict['stylesheet']:
          styles_text = document_dict['stylesheet']
        if styles_text:
          ooo_builder.addFileEntry(full_path = dir_name+'/styles.xml',
                      media_type = 'text/xml',content = styles_text )
      else: # Generic case
        ooo_builder.addFileEntry(full_path=dir_name,
                  media_type=document_dict['doc_type'], content = document_dict['document'] )

    # Get request and batch_mode
    batch_mode = extra_context.get('batch_mode', 0)

    # Debug mode
    if request.get('debug',0):
      return doc_xml

    # Replace content.xml in master openoffice template
    ooo_builder.replace('content.xml', doc_xml)

    # Old templates correction
    try:
      self.OLE_documents_zipstring
    except AttributeError:
      self.OLE_documents_zipstring = None

    # If the file has embedded OLE documents, restore it
    if self.OLE_documents_zipstring:
      additional_builder = OOoBuilder( self.OLE_documents_zipstring )
      for name in additional_builder.getNameList():
        ooo_builder.replace(name, additional_builder.extract(name) )

    # Update the META informations
    ooo_builder.updateManifest()

    # Produce final result
    ooo = ooo_builder.render(self.title or self.id)

    # Convert if necessary
    opts = extra_context.get("options", None)
    if opts is not None:
      format = opts.get('format', request.get('format', None))
      if format:
        return self._asFormat(ooo, format, request)

    # Do not send a RESPONSE if in batch_mode
    if request and not batch_mode:
      request.RESPONSE.setHeader('Content-Type','%s;; charset=utf-8' % self.content_type)
      request.RESPONSE.setHeader('Content-Length',len(ooo))
      request.RESPONSE.setHeader('Content-Disposition','inline;filename=%s' %
                                  self.title_or_id())

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

  def _asFormat(self, ooo, format, REQUEST=None):
    # now create a temp OOoDocument to convert data to pdf
    from Products.ERP5Type.Document import newTempOOoDocument
    tmp_ooo = newTempOOoDocument(self, self.title_or_id())
    tmp_ooo.edit(base_data=ooo,
                 fname=self.title_or_id(),
                 source_reference=self.title_or_id(),
                 base_content_type=self.content_type,)
    tmp_ooo.oo_data = ooo
    
    if format == 'pdf':
      # slightly different implementation
      # now convert it to pdf
      tgts = [x[1] for x in tmp_ooo.getTargetFormatItemList()
              if x[1].endswith('pdf')]
      if len(tgts) > 1:
          raise ValueError, 'multiple pdf formats found - this shouldnt happen'
      if len(tgts) == 0:
          raise ValueError, 'no pdf format found'
      fmt = tgts[0]
      mime, data = tmp_ooo.convert(fmt)
      if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-type', 'application/pdf')
        REQUEST.RESPONSE.setHeader('Content-disposition',
                       'attachment;; filename="%s.pdf"' % self.title_or_id())
      return data

    mime, data = tmp_ooo.convert(format)
    if REQUEST is not None:
      REQUEST.RESPONSE.setHeader('Content-type', mime)
      REQUEST.RESPONSE.setHeader('Content-disposition',
               'attachment;; filename="%s.%s"' % (self.title_or_id(),format))
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
