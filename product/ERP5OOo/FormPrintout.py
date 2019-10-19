# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi KK and Contributors. All Rights Reserved.
#                    Tatuya Kamada <tatuya@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301,
# USA.
##############################################################################
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import PropertySheet, Permissions
from Products.ERP5Form.ListBox import ListBox
from Products.ERP5Form.FormBox import FormBox
from Products.ERP5Form.ReportBox import ReportBox
from Products.ERP5Form.ImageField import ImageField
from Products.ERP5OOo.OOoUtils import OOoBuilder
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Acquisition import Implicit, aq_base
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, Persistent
from AccessControl import ClassSecurityInfo
from OFS.role import RoleManager
from OFS.SimpleItem import Item
from OFS.PropertyManager import PropertyManager
from urllib import quote, quote_plus
from copy import deepcopy
from lxml import etree
from zLOG import LOG, DEBUG, INFO, WARNING
from mimetypes import guess_extension
from DateTime import DateTime
from decimal import Decimal
from xml.sax.saxutils import escape
import re

try:
  from webdav.Lockable import ResourceLockedError
  SUPPORTS_WEBDAV_LOCKS = 1
except ImportError:
  SUPPORTS_WEBDAV_LOCKS = 0


DRAW_URI = 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0'
TEXT_URI = 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
XLINK_URI = 'http://www.w3.org/1999/xlink'
SVG_URI = 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'
TABLE_URI = 'urn:oasis:names:tc:opendocument:xmlns:table:1.0'
OFFICE_URI = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
STYLE_URI = 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'


NSMAP = {
          'draw': DRAW_URI,
          'text': TEXT_URI,
          'xlink': XLINK_URI,
          'svg': SVG_URI,
          'table': TABLE_URI,
          'office': OFFICE_URI,
          'style': STYLE_URI,
        }


# Constructors
manage_addFormPrintout = DTMLFile("dtml/FormPrintout_add", globals())

def addFormPrintout(self, id, title="", form_name='', template='',
                    REQUEST=None, filename='object/title_or_id'):
  """Add form printout to folder.

  Keyword arguments:
  id     -- the id of the new form printout to add
  title  -- the title of the form printout to add
  form_name -- the name of a form which contains data to printout
  template -- the name of a template which describes printout layout
  """
  # add actual object
  id = self._setObject(id, FormPrintout(id, title, form_name, template, filename))
  # respond to the add_and_edit button if necessary
  add_and_edit(self, id, REQUEST)
  return ''

def add_and_edit(self, id, REQUEST):
  """Helper method to point to the object's management screen if
  'Add and Edit' button is pressed.

  Keyword arguments:
  id -- the id of the object we just added
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

class FormPrintout(Implicit, Persistent, RoleManager, Item, PropertyManager):
  """Form Printout

  FormPrintout is one of a reporting system in ERP5.
  It enables to create a Printout, using an Open Document Format(ODF)
  document as its design, an ERP5Form as its contents.

  The functions status:

  Fields -> Paragraphs:      supported
  ListBox -> Table:          supported
  Report Section
      -> Frames or Sections: supported
  FormBox -> Frame:          experimentally supported
  ImageField -> Photo:       supported
  styles.xml:                supported
  meta.xml:                  not supported yet
  """

  meta_type = "ERP5 Form Printout"
  icon = "www/form_printout_icon.png"

  # Declarative Security
  security = ClassSecurityInfo()

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem)

  _properties = ( {'id': 'template',
                   'type': 'string',
                   'mode': 'w'},
                  {'id': 'form_name',
                   'type': 'string',
                   'mode': 'w'},
                  {'id': 'filename',
                   'type': 'tales',
                   'mode': 'w',},)
  # Constructors
  constructors =   (manage_addFormPrintout, addFormPrintout)

  # Tabs in ZMI
  manage_options = ((
    {'label':'Edit', 'action':'manage_editFormPrintout'},
    {'label':'View', 'action': '' }, ) + Item.manage_options)

  security.declareProtected('View management screens', 'manage_editFormPrintout')
  manage_editFormPrintout = PageTemplateFile('www/FormPrintout_manageEdit', globals(),
                                             __name__='manage_editFormPrintout')
  manage_editFormPrintout._owner = None

  # alias definition to do 'add_and_edit'
  security.declareProtected('View management screens', 'manage_main')
  manage_main = manage_editFormPrintout

  # default attributes
  template = None
  form_name = None
  filename = 'object/title_or_id'

  def __init__(self, id, title='', form_name='', template='',
               filename='object/title_or_id'):
    """Initialize id, title, form_name, template.

    Keyword arguments:
    id -- the id of a form printout
    title -- the title of a form printout
    form_name -- the name of a form which as a document content
    template -- the name of a template which as a document layout
    filename -- Tales expression which return the filename of
    downloadable file.
    """
    self.id = id
    self.title = title
    self.form_name = form_name
    self.template = template
    self.filename = filename

  security.declareProtected(Permissions.AccessContentsInformation, 'SearchableText')
  def SearchableText(self):
    return ' '.join((self.id, self.title, self.form_name, self.template, self.filename))

  security.declareProtected('View', 'index_html')
  def index_html(self, REQUEST, RESPONSE=None, template_relative_url=None,
                 format=None, batch_mode=False):
    """Render and view a printout document.

    format: conversion format requested by User.
            take precedence of format in REQUEST
    batch_mode: if True then avoid overriding response headers.
    """

    obj = getattr(self, 'aq_parent', None)
    if obj is not None:
      container = obj.aq_inner.aq_parent
      if not _checkPermission(Permissions.View, obj):
        raise AccessControl_Unauthorized('This document is not authorized for view.')
      else:
        container = None
    form = getattr(obj, self.form_name)
    if template_relative_url:
      printout_template = obj.getPortalObject().\
                                      restrictedTraverse(template_relative_url)
    elif self.template:
      printout_template = getattr(obj, self.template)
    else:
      raise ValueError, 'Can not create a ODF Document without a printout template'

    report_method = None
    if hasattr(form, 'report_method'):
      report_method = getattr(obj, form.report_method)
    extra_context = dict(container=container,
                         printout_template=printout_template,
                         report_method=report_method,
                         form=form,
                         here=obj)
    # Never set value when rendering! If you do, then every time
    # writing occur and it creates conflict error which kill ERP5
    # scalability! To get acquisition, you just have to call __of__.
    # Also frequent writing make data.fs very huge so quickly.
    content_type = printout_template.content_type
    strategy = self._createStrategy(content_type).__of__(self)
    printout = strategy.render(extra_context=extra_context)
    return self._oooConvertByFormat(printout, content_type,
                                    extra_context, REQUEST,
                                    format, batch_mode)

  security.declareProtected('View', '__call__')
  __call__ = index_html

  security.declareProtected('Manage properties', 'doSettings')
  def doSettings(self, REQUEST, title='', form_name='', template='', filename='object/title_or_id'):
    """Change title, form_name, template, filename."""
    if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
      raise ResourceLockedError, "File is locked via WebDAV"
    self.form_name = form_name
    self.template = template
    self.title = title
    self.filename = filename
    message = "Saved changes."
    if getattr(self, '_v_warnings', None):
      message = ("<strong>Warning:</strong> <i>%s</i>"
                % '<br>'.join(self._v_warnings))
    return self.manage_editFormPrintout(manage_tabs_message=message)

  def _createStrategy(slef, content_type=''):
    if guess_extension(content_type) == '.odt':
      return ODTStrategy()
    if guess_extension(content_type) == '.odg':
      return ODGStrategy()
    raise ValueError, 'Template type: %s is not supported' % content_type

  def _oooConvertByFormat(self, printout, content_type, extra_context,
                          REQUEST, format, batch_mode):
    """
    Convert the ODF document into the given format.

    Keyword arguments:
    printout -- ODF document
    content_type -- the content type of the printout
    extra_context -- extra_context including a format
    REQUEST -- Request object
    format -- requested output format
    batch_mode -- Disable headers overriding
    """
    if REQUEST is not None and not format:
      format = REQUEST.get('format', None)
    filename = self.getProperty('filename')
    # Call refresh through cloudooo
    # XXX This is a temporary implementation:
    # Calling a webservice must be done through a WebServiceMethod
    # and a WebServiceConnection
    from Products.ERP5.Document.Document import DocumentConversionServerProxy, enc, dec
    server_proxy = DocumentConversionServerProxy(self)
    extension = guess_extension(content_type).strip('.')
    printout = dec(server_proxy.convertFile(enc(printout),
                                        extension, # source_format
                                        extension, # destination_format
                                        False, # zip
                                        True)) # refresh
    # End of temporary implementation
    if not format:
      if REQUEST is not None and not batch_mode:
        REQUEST.RESPONSE.setHeader('Content-Length', len(printout))
        REQUEST.RESPONSE.setHeader('Content-Type','%s' % content_type)
        REQUEST.RESPONSE.setHeader('Content-disposition',
                                   'inline;filename="%s%s"' % \
                                     (filename, guess_extension(content_type) or ''))
      return printout
    from Products.ERP5Type.Document import newTempOOoDocument
    tmp_ooo = newTempOOoDocument(self, self.title_or_id())
    tmp_ooo.edit(data=printout,
                 base_data=printout,
                 filename=self.title_or_id(),
                 content_type=content_type,
                 base_content_type=content_type)
    mime, data = tmp_ooo.convert(format)
    if REQUEST is not None and not batch_mode:
      REQUEST.RESPONSE.setHeader('Content-Length', len(data))
      REQUEST.RESPONSE.setHeader('Content-type', mime)
      REQUEST.RESPONSE.setHeader('Content-disposition',
          'attachment;filename="%s.%s"' % (filename, format))
    return str(data)

InitializeClass(FormPrintout)

class ODFStrategy(Implicit):
  """ODFStrategy creates a ODF Document. """

  odf_existent_name_list = []

  def render(self, extra_context={}):
    """Render a odf document, form as a content, template as a template.

    Keyword arguments:
    extra_context -- a dictionary, expected:
      'here' : where it call
      'printout_template' : the template object, tipically a OOoTemplate
      'container' : the object which has a form printout object
      'form' : the form as a content
    """
    here = extra_context['here']
    if here is None:
      raise ValueError, 'Can not create a ODF Document without a parent acquisition context'
    form = extra_context['form']
    if not extra_context.has_key('printout_template') or \
        extra_context['printout_template'] is None:
      raise ValueError, 'Can not create a ODF Document without a printout template'

    odf_template = extra_context['printout_template']

    # First, render the Template if it has a pt_render method
    ooo_document = None
    if hasattr(odf_template, 'pt_render'):
      ooo_document = odf_template.pt_render(here, extra_context=extra_context)
    else:
      # File object can be a template
      ooo_document = odf_template

    # Create a new builder instance
    ooo_builder = OOoBuilder(ooo_document)
    self.odf_existent_name_list = ooo_builder.getNameList()

    # content.xml
    self._replaceContentXml(ooo_builder, extra_context)
    # styles.xml
    self._replaceStylesXml(ooo_builder, extra_context)
    # meta.xml is not supported yet
    # ooo_builder = self._replaceMetaXml(ooo_builder=ooo_builder, extra_context=extra_context)

    # Update the META information
    ooo_builder.updateManifest()

    ooo = ooo_builder.render()
    return ooo

  def _replaceContentXml(self, ooo_builder, extra_context):
    """
    Replace the content.xml in an ODF document using an ERP5Form data.
    """
    content_xml = ooo_builder.extract('content.xml')
    # mapping ERP5Form to ODF
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)

    content_element_tree = etree.XML(content_xml)
    self._replaceXmlByForm(content_element_tree, form, here, extra_context,
                           ooo_builder)
    # mapping ERP5Report report method to ODF
    report_method=extra_context.get('report_method')
    base_name = getattr(report_method, '__name__', None)
    self._replaceXmlByReportSection(content_element_tree, extra_context,
                                    report_method, base_name, ooo_builder)

    content_xml = etree.tostring(content_element_tree, encoding='utf-8')
    # Replace content.xml in master openoffice template
    ooo_builder.replace('content.xml', content_xml)

  # this method not supported yet
  def _replaceStylesXml(self, ooo_builder, extra_context):
    """
    Replace the styles.xml file in an ODF document.
    """
    styles_xml = ooo_builder.extract('styles.xml')
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)
    styles_element_tree = etree.XML(styles_xml)
    self._replaceXmlByForm(styles_element_tree, form, here, extra_context,
                           ooo_builder)
    styles_xml = etree.tostring(styles_element_tree, encoding='utf-8')

    ooo_builder.replace('styles.xml', styles_xml)

  # this method not implemented yet
  def _replaceMetaXml(self, ooo_builder, extra_context):
    """
    Replace meta.xml file in an ODF document.
    """
    return ooo_builder

  def _replaceXmlByForm(self, element_tree, form, here, extra_context,
                        ooo_builder, iteration_index=0):
    """
    Replace an element_tree object using an ERP5 form.

    Keyword arguments:
    element_tree -- the element_tree of a XML file in an ODF document.
    form -- an ERP5 form
    here -- called context
    extra_context -- extra_context
    ooo_builder -- the OOoBuilder object which have an ODF document.
    iteration_index -- the index which is used when iterating the group of items using ReportSection.

    Need to be overloaded in OD?Strategy Class
    """
    raise NotImplementedError

  def _replaceXmlByReportSection(self, element_tree, extra_context, report_method,
                                 base_name, ooo_builder):
    """
    Replace xml using ERP5Report ReportSection.
    Keyword arguments:
    element_tree -- the element tree object which have an xml document in an ODF document.
    extra_context -- the extra context
    report_method -- the report method object which is used in an ReportBox
    base_name -- the name of a ReportBox field which is used to specify the target
    ooo_builder -- the OOo Builder object which has ODF document.
    """
    if report_method is None:
      return
    report_section_list = report_method()
    portal_object = self.getPortalObject()

    target_tuple = self._pickUpTargetSection(base_name=base_name,
                                             report_section_list=report_section_list,
                                             element_tree=element_tree)
    if target_tuple is None:
      return
    target_xpath, original_target = target_tuple
    office_body = original_target.getparent()
    target_index = office_body.index(original_target)
    temporary_element_tree = deepcopy(original_target)
    for (index, report_item) in enumerate(report_section_list):
      report_item.pushReport(portal_object, render_prefix=None)
      here = report_item.getObject(portal_object)
      form_id = report_item.getFormId()
      form = getattr(here, form_id)

      target_element_tree = deepcopy(temporary_element_tree)
      # remove original target in the ODF template
      if index == 0:
        office_body.remove(original_target)
      else:
        self._setUniqueElementName(base_name=base_name,
                                   iteration_index=index,
                                   xpath=target_xpath,
                                   element_tree=target_element_tree)

      self._replaceXmlByForm(target_element_tree, form, here, extra_context,
                             ooo_builder, iteration_index=index)
      office_body.insert(target_index, target_element_tree)
      target_index += 1
      report_item.popReport(portal_object, render_prefix=None)

  def _pickUpTargetSection(self, base_name='', report_section_list=[], element_tree=None):
    """pick up a ODF target object to iterate ReportSection
    base_name -- the target name to replace in an ODF document
    report_section_list -- ERP5Form ReportSection List which was created by a report method
    element_tree -- XML ElementTree object
    """
    frame_xpath = '//draw:frame[@draw:name="%s"]' % base_name
    frame_list = element_tree.xpath(frame_xpath, namespaces=element_tree.nsmap)
    # <text:section text:style-name="Sect2" text:name="Section2">
    section_xpath = '//text:section[@text:name="%s"]' % base_name
    section_list = element_tree.xpath(section_xpath, namespaces=element_tree.nsmap)
    if not frame_list and not section_list:
      return

    office_body = None
    original_target = None
    target_xpath = ''
    if frame_list:
      frame = frame_list[0]
      original_target = frame.getparent()
      target_xpath = frame_xpath
    elif section_list:
      original_target = section_list[0]
      target_xpath = section_xpath
    office_body = original_target.getparent()
    # remove if no report section
    if not report_section_list:
      office_body.remove(original_target)
      return

    return (target_xpath, original_target)

  def _setUniqueElementName(self, base_name='', iteration_index=0, xpath='', element_tree=None):
    """create a unique element name and set it to the element tree

    Keyword arguments:
    base_name -- the base name of the element
    iteration_index -- iteration index
    xpath -- xpath expression which was used to search the element
    element_tree -- element tree
    """
    if iteration_index == 0:
      return
    def getNameAttribute(target_element):
      attrib = target_element.attrib
      for key in attrib.keys():
        if key.endswith("}name"):
          return key
      return None
    odf_element_name =  "%s_%s" % (base_name, iteration_index)
    result_list = element_tree.xpath(xpath, namespaces=element_tree.nsmap)
    if not result_list:
      return
    target_element = result_list[0]
    name_attribute = getNameAttribute(target_element)
    if name_attribute:
      target_element.set(name_attribute, odf_element_name)

  def _replaceXmlByFormbox(self, element_tree, field, form, extra_context,
                           ooo_builder, iteration_index=0):
    """
    Replace an ODF frame using an ERP5Form form box field.

    Note: This method is incompleted yet. This function is intended to
    make an frame hide/show. But it has not such a feature currently.
    """
    field_id = field.id
    enabled = field.get_value('enabled')
    draw_xpath = '//draw:frame[@draw:name="%s"]/draw:text-box/*' % field_id
    text_list = element_tree.xpath(draw_xpath, namespaces=element_tree.nsmap)
    if not text_list:
      return
    target_element = text_list[0]
    frame_paragraph = target_element.getparent()
    office_body = frame_paragraph.getparent()
    if not enabled:
      office_body.remove(frame_paragraph)
      return
    # set when using report section
    self._setUniqueElementName(field_id, iteration_index, draw_xpath, element_tree)
    self._replaceXmlByForm(frame_paragraph, form, extra_context['here'], extra_context,
                           ooo_builder, iteration_index=iteration_index)

  def _replaceXmlByImageField(self, element_tree, image_field, ooo_builder, iteration_index=0):
    """
    Replace an ODF draw:frame using an ERP5Form image field.
    """
    alt = image_field.get_value('description') or image_field.get_value('title')
    image_xpath = '//draw:frame[@draw:name="%s"]/*' % image_field.id
    image_list = element_tree.xpath(image_xpath, namespaces=element_tree.nsmap)
    if not image_list:
      return
    path = image_field.get_value('default')
    image_node = image_list[0]
    image_frame = image_node.getparent()
    if path is not None:
      path = path.encode()
    picture = self.getPortalObject().restrictedTraverse(path)
    picture_data = getattr(aq_base(picture), 'data', None)
    if picture_data is None:
      image_frame = image_node.getparent()
      image_frame.remove(image_node)
      return
    picture_type = picture.getContentType()
    picture_path = self._createOdfUniqueFileName(path=path, picture_type=picture_type)
    ooo_builder.addFileEntry(picture_path, media_type=picture_type, content=picture_data)
    width, height = self._getPictureSize(picture, image_frame)
    image_node.set('{%s}href' % XLINK_URI, picture_path)
    image_frame.set('{%s}width' % SVG_URI, str(width))
    image_frame.set('{%s}height' % SVG_URI, str(height))
    # set when using report section
    self._setUniqueElementName(image_field.id, iteration_index, image_xpath, element_tree)

  def _createOdfUniqueFileName(self, path='', picture_type=''):
    extension = guess_extension(picture_type)
    # here, it's needed to use quote_plus to escape '/' caracters to make valid
    # paths in the odf archive.
    picture_path = 'Pictures/%s%s' % (quote_plus(path), extension)
    if picture_path not in self.odf_existent_name_list:
      return picture_path
    number = 0
    while True:
      picture_path = 'Pictures/%s_%s%s' % (quote_plus(path), number, extension)
      if picture_path not in self.odf_existent_name_list:
        return picture_path
      number += 1

  # XXX this method should not be used anymore. This should be made by the
  # render_od*
  def _getPictureSize(self, picture=None, draw_frame_node=None):
    if picture is None or draw_frame_node is None:
      return ('0cm', '0cm')
    svg_width = draw_frame_node.attrib.get('{%s}width' % SVG_URI)
    svg_height = draw_frame_node.attrib.get('{%s}height' % SVG_URI)
    if svg_width is None or svg_height is None:
      return ('0cm', '0cm')
    # if not match causes exception
    width_tuple = re.match("(\d[\d\.]*)(.*)", svg_width).groups()
    height_tuple = re.match("(\d[\d\.]*)(.*)", svg_height).groups()
    unit = width_tuple[1]
    w = Decimal(width_tuple[0])
    h = Decimal(height_tuple[0])
    aspect_ratio = 1
    try: # try image properties
      aspect_ratio = Decimal(picture.width) / Decimal(picture.height)
    except (TypeError, ZeroDivisionError):
      try: # try ERP5.Document.Image API
        height = Decimal(picture.getHeight())
        if height:
          aspect_ratio = Decimal(picture.getWidth()) / height
      except AttributeError: # fallback to Photo API
        height = float(picture.height())
        if height:
          aspect_ratio = Decimal(picture.width()) / height
    resize_w = h * aspect_ratio
    resize_h = w / aspect_ratio
    if resize_w < w:
      w = resize_w
    elif resize_h < h:
      h = resize_h
    return (str(w) + unit, str(h) + unit)


  def _appendTableByListbox(self, element_tree, listbox, REQUEST, iteration_index=0):
    """
    Append a ODF table using an ERP5 Form listbox.
    """
    table_id = listbox.id
    table_xpath = '//table:table[@table:name="%s"]' % table_id
    # this list should be one item list
    target_table_list = element_tree.xpath(table_xpath, namespaces=element_tree.nsmap)
    if not target_table_list:
      return element_tree

    target_table = target_table_list[0]
    newtable = deepcopy(target_table)

    table_header_rows_xpath = '%s/table:table-header-rows' % table_xpath
    table_row_xpath = '%s/table:table-row' % table_xpath
    table_header_rows_list = newtable.xpath(table_header_rows_xpath,  namespaces=element_tree.nsmap)
    table_row_list = newtable.xpath(table_row_xpath, namespaces=element_tree.nsmap)

    # copy row styles from ODF Document
    has_header_rows = len(table_header_rows_list) > 0
    (row_top, row_middle, row_bottom) = self._copyRowStyle(table_row_list,
                                                           has_header_rows=has_header_rows)
    # create style-name and table-row dictionary if a reference name is set
    style_name_row_dictionary = self._createStyleNameRowDictionary(table_row_list)
    # clear original table
    parent_paragraph = target_table.getparent()
    # clear rows
    [newtable.remove(table_row) for table_row in table_row_list]

    listboxline_list = listbox.get_value('default',
                                         render_format='list',
                                         REQUEST=REQUEST,
                                         render_prefix=None)
    # if ODF table has header rows, does not update the header rows
    # if does not have header rows, insert the listbox title line
    is_top = True
    last_index = len(listboxline_list) - 1
    for (index, listboxline) in enumerate(listboxline_list):
      listbox_column_list = listboxline.getColumnItemList()
      row_style_name = listboxline.getRowCSSClassName()
      if listboxline.isTitleLine() and not has_header_rows:
        row = deepcopy(row_top)
        self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)
        is_top = False
      elif listboxline.isDataLine() and is_top:
        row = deepcopy(style_name_row_dictionary.get(row_style_name, row_top))
        self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)
        is_top = False
      elif listboxline.isStatLine() or (index is last_index and listboxline.isDataLine()):
        row = deepcopy(style_name_row_dictionary.get(row_style_name, row_bottom))
        self._updateColumnStatValue(row, listbox_column_list, row_middle)
        newtable.append(row)
      elif index > 0 and listboxline.isDataLine():
        row = deepcopy(style_name_row_dictionary.get(row_style_name, row_middle))
        self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)

    self._setUniqueElementName(table_id, iteration_index, table_xpath, newtable)
    parent_paragraph.replace(target_table, newtable)

  def _copyRowStyle(self, table_row_list=None, has_header_rows=False):
    """
    Copy ODF table row styles.
    """
    if table_row_list is None:
      table_row_list = []
    def removeOfficeAttribute(row):
      if row is None or has_header_rows: return
      odf_cell_list = row.findall("{%s}table-cell" % TABLE_URI)
      for odf_cell in odf_cell_list:
        self._removeColumnValue(odf_cell)

    row_top = None
    row_middle = None
    row_bottom = None
    len_table_row_list = len(table_row_list)
    if len_table_row_list == 1:
      row_top = deepcopy(table_row_list[0])
      row_middle = deepcopy(table_row_list[0])
      row_bottom = deepcopy(table_row_list[0])
    elif len_table_row_list == 2 and has_header_rows:
      row_top = deepcopy(table_row_list[0])
      row_middle = deepcopy(table_row_list[0])
      row_bottom = deepcopy(table_row_list[-1])
    elif len_table_row_list == 2 and not has_header_rows:
      row_top = deepcopy(table_row_list[0])
      row_middle = deepcopy(table_row_list[1])
      row_bottom = deepcopy(table_row_list[-1])
    elif len_table_row_list >= 2:
      row_top = deepcopy(table_row_list[0])
      row_middle = deepcopy(table_row_list[1])
      row_bottom = deepcopy(table_row_list[-1])

    # remove office attribute if create a new header row
    removeOfficeAttribute(row_top)
    return (row_top, row_middle, row_bottom)


  def _createStyleNameRowDictionary(self, table_row_list):
    """create stylename and table row dictionary if a style name reference is set"""
    style_name_row_dictionary = {}
    for table_row in table_row_list:
      reference_element = table_row.find('.//*[@%s]' % self._name_attribute_name)
      if reference_element is not None:
        name = reference_element.attrib[self._name_attribute_name]
        style_name_row_dictionary[name] = deepcopy(table_row)
    return style_name_row_dictionary

  def _updateColumnValue(self, row, listbox_column_list):
    odf_cell_list = row.findall("{%s}table-cell" % TABLE_URI)
    odf_cell_list_size = len(odf_cell_list)
    listbox_column_size = len(listbox_column_list)
    for (column_index, column) in enumerate(odf_cell_list):
      if column_index >= listbox_column_size:
        break
      value = listbox_column_list[column_index][1]
      self._setColumnValue(column, value)

  def _updateColumnStatValue(self, row, listbox_column_list, row_middle):
    """stat line is capable of column span setting"""
    if row_middle is None:
      return
    odf_cell_list = row.findall("{%s}table-cell" % TABLE_URI)
    odf_column_span_list = self._getOdfColumnSpanList(row_middle)
    listbox_column_size = len(listbox_column_list)
    listbox_column_index = 0
    for (column_index, column) in enumerate(odf_cell_list):
      if listbox_column_index >= listbox_column_size:
        break
      value = listbox_column_list[listbox_column_index][1]
      self._setColumnValue(column, value)
      column_span = self._getColumnSpanSize(column)
      listbox_column_index = self._nextListboxColumnIndex(column_span,
                                                          listbox_column_index,
                                                          odf_column_span_list)

  def _setColumnValue(self, column, value):
    self._clearColumnValue(column)
    if value is None:
      self._removeColumnValue(column)
    column_value, table_content = self._translateValueIntoColumnContent(value, column)
    [column.remove(child) for child in column]
    if table_content is not None:
      column.append(table_content)
    value_attribute = self._getColumnValueAttribute(column)
    if value_attribute is not None and column_value is not None:
       column.set(value_attribute, column_value)

  def _translateValueIntoColumnContent(self, value, column):
    """translate a value as a table content"""
    table_content = None
    if len(column):
      table_content = deepcopy(column[0])
    # create a tempolaly etree object to generate a content paragraph
    fragment = self._valueAsOdfXmlElement(value=value, element_tree=column)
    column_value = None
    if table_content is not None:
      table_content.text = fragment.text
      for element in fragment:
        table_content.append(element)
      column_value = " ".join(table_content.itertext())
    return (column_value, table_content)

  def _valueAsOdfXmlElement(self, value=None, element_tree=None):
    """values as ODF XML element

    replacing:
      \t -> tabs
      \n -> line-breaks
      DateTime -> Y-m-d
    """
    if value is None:
      value = ''
    translated_value = str(value)
    if isinstance(value, DateTime):
      translated_value = value.strftime('%Y-%m-%d')
    translated_value = escape(translated_value)
    tab_element_str = '<text:tab xmlns:text="%s"/>' % TEXT_URI
    line_break_element_str ='<text:line-break xmlns:text="%s"/>' % TEXT_URI
    translated_value = translated_value.replace('\t', tab_element_str)
    translated_value = translated_value.replace('\r', '')
    translated_value = translated_value.replace('\n', line_break_element_str)
    translated_value = unicode(str(translated_value),'utf-8')
    # create a paragraph
    template = '<text:p xmlns:text="%s">%s</text:p>'
    fragment_element_tree = etree.XML(template % (TEXT_URI, translated_value))
    return fragment_element_tree

  def _removeColumnValue(self, column):
    # to eliminate a default value, remove "office:*" attributes.
    # if remaining these attribetes, the column shows its default value,
    # such as '0.0', '$0'
    attrib = column.attrib
    for key in attrib.keys():
      if 'office' in column.nsmap and key.startswith("{%s}" % column.nsmap['office']):
        del attrib[key]
    column.text = None
    [column.remove(child) for child in column]

  def _clearColumnValue(self, column):
    attrib = column.attrib
    for key in attrib.keys():
      value_attribute = self._getColumnValueAttribute(column)
      if value_attribute is not None:
        column.set(value_attribute, '')
    column.text = None
    for child in column:
      # clear data except style
      style_value = child.attrib.get(self._style_attribute_name)
      child.clear()
      if style_value:
        child.set(self._style_attribute_name, style_value)

  def _getColumnValueAttribute(self, column):
    attrib = column.attrib
    for key in attrib.keys():
      if key.endswith("value"):
        return key
    return None

  def _getColumnSpanSize(self, column=None):
    span_attribute = "{%s}number-columns-spanned" % TABLE_URI
    return int(column.attrib.get(span_attribute, 1))

  def _nextListboxColumnIndex(self, span=0, current_index=0, column_span_list=[]):
    hops = 0
    index = current_index
    while hops < span:
      column_span = column_span_list[index]
      hops += column_span
      index += 1
    return index

  def _getOdfColumnSpanList(self, row_middle=None):
    if row_middle is None:
      return []
    odf_cell_list = row_middle.findall("{%s}table-cell" % TABLE_URI)
    column_span_list = []
    for column in odf_cell_list:
      column_span = self._getColumnSpanSize(column)
      column_span_list.append(column_span)
    return column_span_list

  def _toUnicodeString(self, field_value = None):
    value = ''
    if isinstance(field_value, unicode):
      value = field_value
    elif field_value is not None:
      value = unicode(str(field_value), 'utf-8')
    return value

class ODTStrategy(ODFStrategy):
  """ODTStrategy create a ODT Document from a form and a ODT template"""

  _style_attribute_name = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name'
  _name_attribute_name = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}name'

  def _replaceXmlByForm(self, element_tree, form, here, extra_context,
                        ooo_builder, iteration_index=0):
    """
    Replace an element_tree object using an ERP5 form.

    Keyword arguments:
    element_tree -- the element_tree of a XML file in an ODF document.
    form -- an ERP5 form
    here -- called context
    extra_context -- extra_context
    ooo_builder -- the OOoBuilder object which have an ODF document.
    iteration_index -- the index which is used when iterating the group of items using ReportSection.
    """
    field_list = form.get_fields()
    REQUEST = here.REQUEST
    for (count, field) in enumerate(field_list):
      if isinstance(field, ListBox):
        self._appendTableByListbox(element_tree, field, REQUEST,
                                   iteration_index=iteration_index)
      elif isinstance(field, FormBox):
        if not hasattr(here, field.get_value('formbox_target_id')):
          continue
        sub_form = getattr(here, field.get_value('formbox_target_id'))
        content = self._replaceXmlByFormbox(element_tree, field, sub_form,
                                            extra_context, ooo_builder,
                                            iteration_index=iteration_index)
      elif isinstance(field, ReportBox):
         report_method = getattr(field, field.get_value('report_method'), None)
         self._replaceXmlByReportSection(element_tree, extra_context,
                                         report_method, field.id, ooo_builder)
      elif isinstance(field, ImageField):
        self._replaceXmlByImageField(element_tree, field,
                                     ooo_builder, iteration_index=iteration_index)
      else:
        self._replaceNodeViaReference(element_tree, field)

  def _replaceNodeViaReference(self, element_tree, field):
    """replace nodes (e.g. paragraphs) via ODF reference"""
    self._replaceNodeViaRangeReference(element_tree, field)
    self._replaceNodeViaPointReference(element_tree, field)
    self._replaceNodeViaFormName(element_tree, field)
    self._replaceNodeViaVariable(element_tree, field)

  def _replaceNodeViaPointReference(self, element_tree, field, iteration_index=0):
    """Replace text node via an ODF point reference.

    point reference example:
     <text:reference-mark text:name="invoice-date"/>
    """
    field_id = field.id
    reference_xpath = '//text:reference-mark[@text:name="%s"]' % field_id
    reference_list = element_tree.xpath(reference_xpath, namespaces=element_tree.nsmap)
    for target_node in reference_list:
      node_to_replace = target_node.xpath('ancestor::text:p[1]', namespaces=element_tree.nsmap)[0]
      attr_dict = {}
      style_value = node_to_replace.attrib.get(self._style_attribute_name)
      if style_value:
        attr_dict.update({self._style_attribute_name: style_value})
      new_node = field.render_odt(as_string=False, attr_dict=attr_dict)
      node_to_replace.getparent().replace(node_to_replace, new_node)
    # set when using report section
    self._setUniqueElementName(base_name=field.id,
                               iteration_index=iteration_index,
                               xpath=reference_xpath,
                               element_tree=element_tree)

  def _replaceNodeViaVariable(self, element_tree, field, iteration_index=0):
    """Replace text node via an ODF variable name.
    <text:variable-set text:name="my_title"
                    office:value-type="string">Title</text:variable-set>
    """
    field_id = field.id
    reference_xpath = '//text:variable-set[@text:name="%s"]' % field_id
    node_list = element_tree.xpath(reference_xpath,
                                   namespaces=element_tree.nsmap)
    for target_node in node_list:
      attr_dict = {}
      style_attribute_id = '{%s}data-style-name' % STYLE_URI
      style_value = target_node.attrib.get(style_attribute_id)
      if style_value:
        attr_dict.update({style_attribute_id: style_value})
      display_attribute_id = '{%s}display' % TEXT_URI
      display_value = target_node.attrib.get(display_attribute_id)
      if display_value:
        attr_dict.update({display_attribute_id: display_value})
      formula_attribute_id = '{%s}formula' % TEXT_URI
      formula_value = target_node.attrib.get(formula_attribute_id)
      if formula_value:
        attr_dict.update({formula_attribute_id: formula_value})
      name_attribute_id = '{%s}name' % TEXT_URI
      attr_dict[name_attribute_id] = target_node.get(name_attribute_id)
      value_type_attribute_id = '{%s}value-type' % OFFICE_URI
      attr_dict[value_type_attribute_id] = target_node.get(
                                                       value_type_attribute_id)
      new_node = field.render_odt_variable(as_string=False,
                                           attr_dict=attr_dict)
      target_node.getparent().replace(target_node, new_node)
    # set when using report section
    self._setUniqueElementName(base_name=field_id,
                               iteration_index=iteration_index,
                               xpath=reference_xpath,
                               element_tree=element_tree)

  def _replaceNodeViaRangeReference(self, element_tree, field, iteration_index=0):
    """Replace text node via an ODF ranged reference.

    range reference example:
    <text:reference-mark-start text:name="week"/>Monday<text:reference-mark-end text:name="week"/>
    or
    <text:reference-mark-start text:name="my_title"/>
      <text:span text:style-name="T1">title</text:span>
    <text:reference-mark-end text:name="my_title"/>

    """
    field_id = field.id
    range_reference_xpath = '//text:reference-mark-start[@text:name="%s"]' % (field_id,)
    node_to_remove_list_xpath = '//text:reference-mark-start[@text:name="%s"]/'\
                            'following-sibling::*[node()/'\
                            'following::text:reference-mark-end[@text:name="%s"]]' % (field_id, field_id)
    node_to_remove_list = element_tree.xpath(node_to_remove_list_xpath, namespaces=element_tree.nsmap)
    reference_list = element_tree.xpath(range_reference_xpath, namespaces=element_tree.nsmap)
    if not reference_list:
      return element_tree
    referenced_node = reference_list[0]
    referenced_node.tail = None
    parent_node = referenced_node.getparent()
    text_reference_position = parent_node.index(referenced_node)

    #Delete all contents between <text:reference-mark-start/> and <text:reference-mark-end/>
    #Try to fetch style-name
    attr_dict = {}
    [(attr_dict.update(target_node.attrib), parent_node.remove(target_node)) for target_node in node_to_remove_list]
    new_node = field.render_odt(local_name='span', attr_dict=attr_dict,
                                as_string=False)
    parent_node.insert(text_reference_position+1, new_node)
    # set when using report section
    self._setUniqueElementName(base_name=field.id,
                               iteration_index=iteration_index,
                               xpath=range_reference_xpath,
                               element_tree=element_tree)

  def _replaceNodeViaFormName(self, element_tree, field, iteration_index=0):
    """
    Used to replace field in ODT document like checkboxes
    """
    field_id = field.id
    reference_xpath = '//*[@form:name = "%s"]' % field_id
    # if form name space is not in the name space dict of element tree,
    # it means that there is no form in the tree. Then do nothing and return.
    if not 'form' in element_tree.nsmap:
      return
    reference_list = element_tree.xpath(reference_xpath, namespaces=element_tree.nsmap)
    for target_node in reference_list:
      attr_dict = {}
      attr_dict.update(target_node.attrib)
      new_node = field.render_odt(as_string=False, attr_dict=attr_dict)
      target_node.getparent().replace(target_node, new_node)

class ODGStrategy(ODFStrategy):
  """ODGStrategy create a ODG Document from a form and a ODG template"""

  def _recursiveGetAttributeDict(self, node, attr_dict):
    '''return a dictionnary corresponding with node attributes. Tag as key
       and a list corresponding to the atributes values by apparence order.
       Example, for a listbox, you will have something like :
       { tabe.tag: [table.attrib,],
         row.tag: [row.attrib,
                   row.attrib],
         cell.tag: [cell.attrib,
                    cell.attrib,
                    cell.attrib,
                    cell.attrib,
                    cell.attrib,
                    cell.attrib,],

    '''
    attr_dict.setdefault(node.tag, []).append(dict(node.attrib))
    for child in node:
      self._recursiveGetAttributeDict(child, attr_dict)

  def _recursiveApplyAttributeDict(self, node, attr_dict):
    '''recursively apply given attributes to node
    '''
    image_tag_name = '{%s}%s' % (DRAW_URI, 'image')
    if len(attr_dict[node.tag]):
      attribute_to_update_dict = attr_dict[node.tag].pop(0)
      # in case of images, we don't want to update image path
      # because they were calculated by render_odg
      if node.tag != image_tag_name:
        node.attrib.update(attribute_to_update_dict)
    for child in node:
      self._recursiveApplyAttributeDict(child, attr_dict)

  def _replaceXmlByForm(self, element_tree, form, here, extra_context,
                        ooo_builder, iteration_index=0):
    field_list = form.get_fields()
    for (count, field) in enumerate(field_list):
      text_xpath = '//draw:frame[@draw:name="%s"]' % field.id
      node_list = element_tree.xpath(text_xpath, namespaces=element_tree.nsmap)
      value = field.get_value('default')
      if isinstance(value, str):
        value = value.decode('utf-8')
      for target_node in node_list:
        # render the field in odg xml node format
        attr_dict = {}
        self._recursiveGetAttributeDict(target_node, attr_dict)
        new_node = field.render_odg(value=value, as_string=False, ooo_builder=ooo_builder,
            REQUEST=self.REQUEST, attr_dict=attr_dict)

        if new_node is not None:
          # replace the target node by the generated node
          target_node.getparent().replace(target_node, new_node)
        else:
          # if the render return None, remove the node
          target_node.getparent().remove(target_node)
