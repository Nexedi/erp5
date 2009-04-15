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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import _checkPermission, getToolByName
from Products.PythonScripts.Utility import allow_class
from Products.ERP5Type import PropertySheet, Permissions
from Products.ERP5Form.ListBox import ListBox
from Products.ERP5Form.FormBox import FormBox
from Products.ERP5Form.ImageField import ImageField
from Products.ERP5OOo.OOoUtils import OOoBuilder

from Acquisition import Implicit, aq_base
from Globals import InitializeClass, DTMLFile, Persistent, get_request
from AccessControl import ClassSecurityInfo
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item, SimpleItem
from OFS.Image import File
from urllib import quote, quote_plus
from copy import deepcopy
from lxml import etree
from zLOG import LOG, DEBUG, INFO, WARNING
from mimetypes import guess_extension
from DateTime import DateTime
from decimal import Decimal
import re

try:
  from webdav.Lockable import ResourceLockedError
  from webdav.WriteLockInterface import WriteLockInterface
  SUPPORTS_WEBDAV_LOCKS = 1
except ImportError:
  SUPPORTS_WEBDAV_LOCKS = 0

# Constructors
manage_addFormPrintout = DTMLFile("dtml/FormPrintout_add", globals())

def addFormPrintout(self, id, title="", form_name='', template='', REQUEST=None):
  """Add form printout to folder.

  Keyword arguments:
  id     -- the id of the new form printout to add
  title  -- the title of the form printout to add
  form_name -- the name of a form which contains data to printout
  template -- the name of a template which describes printout layout
  """
  # add actual object
  id = self._setObject(id, FormPrintout(id, title, form_name, template))
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

class FormPrintout(Implicit, Persistent, RoleManager, Item):
  """Form Printout

  The Form Printout enables to create a ODF document.

  The Form Printout receives an ERP5 form name, and a template name.
  Using their parameters, the Form Printout genereate a ODF document,
  a form as a ODF document content, and a template as a document layout.

  WARNING: The Form Printout currently supports only ODT format document.

  The functions status:
  
  Fields -> Paragraphs:      supported
  ListBox -> Table:          supported
  Report Section -> Frames:  experimentally supported
  FormBox -> Frame:          experimentally supported
  ImageField -> Photo:       supported
  styles.xml:                supported
  meta.xml:                  not supported yet
  """
  
  meta_type = "ERP5 Form Printout"

  # Declarative Security
  security = ClassSecurityInfo()

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem)

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
  
  # default attributes
  template = None
  form_name = None

  def __init__(self, id, title='', form_name='', template=''):
    """Initialize id, title, form_name, template.

    Keyword arguments:
    id -- the id of a form printout
    title -- the title of a form printout
    form_name -- the name of a form which as a document content
    template -- the name of a template which as a document layout
    """
    self.id = id
    self.title = title
    self.form_name = form_name
    self.template = template

  security.declareProtected('View', 'index_html')
  def index_html(self, icon=0, preview=0, width=None, height=None, REQUEST=None):
    """Render and view a printout document."""
    
    obj = getattr(self, 'aq_parent', None)
    if obj is not None:
      container = obj.aq_inner.aq_parent
      if not _checkPermission(Permissions.View, obj):
        raise AccessControl_Unauthorized('This document is not authorized for view.')
      else:
        container = None
    form = getattr(obj, self.form_name)
    if self.template is None or self.template == '':
      raise ValueError, 'Can not create a ODF Document without a printout template'
    printout_template = getattr(obj, self.template)

    report_method = None
    if hasattr(form, 'report_method'):
      report_method = getattr(obj, form.report_method)
    extra_context = dict(container=container,
                         printout_template=printout_template,
                         report_method=report_method,
                         form=form,
                         here=obj)
    # set property to do aquisition
    content_type = printout_template.content_type
    self.strategy = self._createStrategy(content_type)
    printout = self.strategy.render(extra_context=extra_context)
    if REQUEST is not None:
      REQUEST.RESPONSE.setHeader('Content-Type','%s; charset=utf-8' % content_type)
      REQUEST.RESPONSE.setHeader('Content-disposition',
                                 'inline;filename="%s%s"' % (self.title_or_id(), guess_extension(content_type)))
    return printout

  security.declareProtected('View', '__call__')
  __call__ = index_html
                
  security.declareProtected('Manage properties', 'doSettings')
  def doSettings(self, REQUEST, title='', form_name='', template=''):
    """Change title, form_name, template."""
    if SUPPORTS_WEBDAV_LOCKS and self.wl_isLocked():
      raise ResourceLockedError, "File is locked via WebDAV"
    self.form_name = form_name
    self.template = template
    self.title = title
    message = "Saved changes."
    if getattr(self, '_v_warnings', None):
      message = ("<strong>Warning:</strong> <i>%s</i>"
                % '<br>'.join(self._v_warnings))
    return self.manage_editFormPrintout(manage_tabs_message=message)

  def _createStrategy(slef, content_type=''):
    if guess_extension(content_type) == '.odt':
      return ODTStrategy()
    raise ValueError, 'Do not support the template type:%s' % content_type

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
    if not extra_context.has_key('printout_template') or extra_context['printout_template'] is None:
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
    ooo_builder = self._replaceContentXml(ooo_builder=ooo_builder, extra_context=extra_context)
    # styles.xml
    ooo_builder = self._replaceStylesXml(ooo_builder=ooo_builder, extra_context=extra_context)
    # meta.xml is not supported yet
    # ooo_builder = self._replaceMetaXml(ooo_builder=ooo_builder, extra_context=extra_context)

    # Update the META informations
    ooo_builder.updateManifest()

    ooo = ooo_builder.render(name=odf_template.title or odf_template.id)
    return ooo

  def _replaceContentXml(self, ooo_builder=None, extra_context=None):
    content_xml = ooo_builder.extract('content.xml')
    # mapping ERP5Form to ODF
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)

    content_element_tree = etree.XML(content_xml)
    content_element_tree = self._replaceXmlByForm(element_tree=content_element_tree,
                                                  form=form,
                                                  here=here,
                                                  extra_context=extra_context,
                                                  ooo_builder=ooo_builder)
    # mapping ERP5Report report method to ODF
    content_element_tree = self._replaceXmlByReportSection(element_tree=content_element_tree,
                                                           extra_context=extra_context,
                                                           ooo_builder=ooo_builder)
    content_xml = etree.tostring(content_element_tree, encoding='utf-8')
 
    # Replace content.xml in master openoffice template
    ooo_builder.replace('content.xml', content_xml)
    return ooo_builder

  # this method not supported yet
  def _replaceStylesXml(self, ooo_builder=None, extra_context=None):
    """
    replacing styles.xml file in a ODF document
    """
    styles_xml = ooo_builder.extract('styles.xml')
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)
    styles_element_tree = etree.XML(styles_xml)
    styles_element_tree = self._replaceXmlByForm(element_tree=styles_element_tree,
                                                 form=form,
                                                 here=here,
                                                 extra_context=extra_context,
                                                 ooo_builder=ooo_builder)
    styles_xml = etree.tostring(styles_element_tree, encoding='utf-8')

    ooo_builder.replace('styles.xml', styles_xml)
    return ooo_builder

  # this method not implemented yet
  def _replaceMetaXml(self, ooo_builder=None, extra_context=None):
    """
    replacing meta.xml file in a ODF document
    """
    meta_xml = ooo_builder.extract('meta.xml')

    if isinstance(doc_xml, unicode):
      meta_xml = meta_xml.encode('utf-8')

    ooo_builder.replace('meta.xml', meta_xml)
    return ooo_builder

  def _replaceXmlByForm(self, element_tree=None, form=None, here=None,
                           extra_context=None, ooo_builder=None):
    field_list = form.get_fields() 
    REQUEST = get_request()
    for (count, field) in enumerate(field_list):
      if isinstance(field, ListBox):
        element_tree = self._appendTableByListbox(element_tree=element_tree,
                                                  listbox=field,
                                                  REQUEST=REQUEST)
      elif isinstance(field, FormBox):
        sub_form = getattr(here, field.get_value('formbox_target_id'))
        content = self._replaceXmlByFormbox(element_tree=element_tree,
                                            field_id=field.id,
                                            form = sub_form,
                                            REQUEST=REQUEST)
      elif isinstance(field, ImageField):
        element_tree = self._replaceXmlByImageField(element_tree=element_tree,
                                                    image_field=field,
                                                    ooo_builder=ooo_builder)
      else:
        element_tree = self._replaceNodeViaReference(element_tree=element_tree,
                                                     field=field)
    return element_tree

  def _replaceNodeViaReference(self, element_tree=None, field=None):
    """replace nodes (e.g. paragraphs) via ODF reference"""
    element_tree = self._replaceNodeViaRangeReference(element_tree=element_tree, field=field)
    element_tree = self._replaceNodeViaPointReference(element_tree=element_tree, field=field)
    return element_tree
  
  def _replaceNodeViaPointReference(self, element_tree=None, field=None):
    """replace via ODF point reference
    
    point reference example:
     <text:reference-mark text:name="invoice-date"/>
    """
    field_id = field.id
    field_value = field.get_value('default')
    value = self._toUnicodeString(field_value)
    # text:reference-mark text:name="invoice-date"
    reference_xpath = '//text:reference-mark[@text:name="%s"]' % field_id
    reference_list = element_tree.xpath(reference_xpath, namespaces=element_tree.nsmap)
    if len(reference_list) > 0:
      node = reference_list[0].getparent()
      # remove such a "bbb": <text:p>aaa<br/>bbb</text:p>
      for child in node.getchildren():
        child.tail = ''
      node.text = value
    return element_tree
  
  def _replaceNodeViaRangeReference(self, element_tree=None, field=None):
    """replace via ODF range reference

    range reference example:
    <text:reference-mark-start text:name="week"/>Monday<text:reference-mark-end text:name="week"/>
    """
    field_value = field.get_value('default')
    value = self._toUnicodeString(field_value)
    range_reference_xpath = '//text:reference-mark-start[@text:name="%s"]' % field.id
    reference_list = element_tree.xpath(range_reference_xpath, namespaces=element_tree.nsmap)
    if len(reference_list) is 0:
      return element_tree
    target_node = reference_list[0]
    target_node.tail = value
    for node in target_node.itersiblings():
      end_tag_name = '{%s}reference-mark-end' % element_tree.nsmap['text']
      name_attribute = '{%s}name' % element_tree.nsmap['text']
      if node.tag == end_tag_name and node.get(name_attribute) == field.id:
         break
      node.tail = ''
    return element_tree
  
  def _replaceXmlByReportSection(self, element_tree=None, extra_context=None, ooo_builder=None):
    if not extra_context.has_key('report_method') or extra_context['report_method'] is None:
      return element_tree
    report_method = extra_context['report_method']
    report_section_list = report_method()
    portal_object = self.getPortalObject()
    REQUEST = get_request()
    request = extra_context.get('REQUEST', REQUEST)
    render_prefix = None

    report_section_frame_xpath = '//draw:frame[@draw:name="%s"]' % report_method.__name__
    frame_list = element_tree.xpath(report_section_frame_xpath, namespaces=element_tree.nsmap)
    if len(frame_list) is 0:
      return element_tree
    frame = frame_list[0]
    frame_paragraph = frame.getparent()
    office_body = frame_paragraph.getparent()
    # remove if no report section
    if len(report_section_list) is 0:
      office_body.remove(frame_paragraph)
      return element_tree
    frame_paragraph_element_tree = deepcopy(frame_paragraph)
    frame_paragraph_index = office_body.index(frame_paragraph)
    temporary_element_tree = deepcopy(frame_paragraph)
    for (index, report_item) in enumerate(report_section_list):
      render_prefix = 'x%s' % index
      report_item.pushReport(portal_object, render_prefix = render_prefix)
      here = report_item.getObject(portal_object)
      form_id = report_item.getFormId()
      form = getattr(here, form_id)
      
      frame_paragraph_element_tree = deepcopy(temporary_element_tree)
      if index is 0:
        office_body.remove(frame_paragraph)
      else:
        self._setReportSectionFrameName(report_method_name=report_method.__name__,
                                        frame_paragraph_index=index,
                                        frame_paragraph_element_tree=frame_paragraph_element_tree)


      frame_paragraph_element_tree = self._replaceXmlByForm(element_tree=frame_paragraph_element_tree,
                                                            form=form,
                                                            here=here,
                                                            extra_context=extra_context,
                                                            ooo_builder=ooo_builder)
      office_body.insert(frame_paragraph_index, frame_paragraph_element_tree)
      frame_paragraph_index += 1
      report_item.popReport(portal_object, render_prefix = render_prefix)
    return element_tree

  def _setReportSectionFrameName(self,
                                 report_method_name='',
                                 frame_paragraph_index=0,
                                 frame_paragraph_element_tree=None):
    report_section_frame_name =  "%s_%s" % (report_method_name, frame_paragraph_index)
    draw_name_attribute = '{%s}name' % frame_paragraph_element_tree.nsmap['draw']
    report_section_frame = frame_paragraph_element_tree.xpath(
      'draw:frame[@draw:name="%s"]' % report_method_name,
      namespaces=frame_paragraph_element_tree.nsmap)
    if len(report_section_frame) is 0:
      return
    report_section_frame[0].set(draw_name_attribute, report_section_frame_name)
  
  def _replaceXmlByFormbox(self, element_tree=None, field_id=None, form=None, REQUEST=None):
    draw_xpath = '//draw:frame[@draw:name="%s"]/draw:text-box/*' % field_id
    text_list = element_tree.xpath(draw_xpath, namespaces=element_tree.nsmap)
    if len(text_list) == 0:
      return element_tree
    parent = text_list[0].getparent()
    parent.clear()
    # this form.__call__() possibly has a side effect,
    # so must clear the 'here' context for listBox.get_value()
    box = form(REQUEST=REQUEST);
    REQUEST.set('here', None)
    node = etree.XML(box)
    # TODO style_copy
    if node is not None:
      for child in node.getchildren():
        parent.append(child)
    return element_tree

  def _replaceXmlByImageField(self, element_tree=None, image_field=None, ooo_builder=None):
    alt = image_field.get_value('description') or image_field.get_value('title')
    image_xpath = '//draw:frame[@draw:name="%s"]/*' % image_field.id
    image_list = element_tree.xpath(image_xpath, namespaces=element_tree.nsmap)
    if len(image_list) is 0:
      return element_tree
    path = image_field.get_value('default')
    if path is not None:
      path = path.encode()
    picture = self.getPortalObject().restrictedTraverse(path)
    picture_data = getattr(aq_base(picture), 'data', None)
    picture_type = picture.getContentType()
    picture_path = self._createOdfUniqueFileName(path=path, picture_type=picture_type)
    ooo_builder.addFileEntry(picture_path, media_type=picture_type, content=picture_data)
    image_node = image_list[0]
    picture_size = self._getPictureSize(picture, image_node)
    image_node.set('{%s}href' % element_tree.nsmap['xlink'], picture_path)
    image_frame = image_node.getparent()
    image_frame.set('{%s}width' % element_tree.nsmap['svg'], picture_size[0])
    image_frame.set('{%s}height' % element_tree.nsmap['svg'], picture_size[1])
    return element_tree

  def _createOdfUniqueFileName(self, path='', picture_type=''):
    extension = guess_extension(picture_type)
    picture_path = 'Pictures/%s%s' % (quote_plus(path), extension)     
    if picture_path not in self.odf_existent_name_list:
      return picture_path
    number = 0
    while True:
      picture_path = 'Pictures/%s_%s%s' % (path, number, extension)
      if picture_path not in self.odf_existent_name_list:
        return picture_path
      number += 1

  def _getPictureSize(self, picture=None, image_node=None):
    if picture is None or image_node is None:
      return ('0cm', '0cm')
    draw_frame_node = image_node.getparent()
    svg_width = draw_frame_node.attrib.get('{%s}width' % draw_frame_node.nsmap['svg'])
    svg_height = draw_frame_node.attrib.get('{%s}height' % draw_frame_node.nsmap['svg'])
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
   
  
  def _appendTableByListbox(self,
                            element_tree=None, 
                            listbox=None,
                            REQUEST=None):
    table_id = listbox.id
    table_xpath = '//table:table[@table:name="%s"]' % table_id
    # this list should be one item list
    target_table_list = element_tree.xpath(table_xpath, namespaces=element_tree.nsmap)
    if len(target_table_list) is 0:
      return element_tree

    target_table = target_table_list[0]
    newtable = deepcopy(target_table)

    table_header_rows_xpath = '%s/table:table-header-rows' % table_xpath
    table_row_xpath = '%s/table:table-row' % table_xpath
    table_header_rows_list = newtable.xpath(table_header_rows_xpath,  namespaces=element_tree.nsmap)
    table_row_list = newtable.xpath(table_row_xpath,  namespaces=element_tree.nsmap)

    # copy row styles from ODF Document
    has_header_rows = len(table_header_rows_list) > 0
    (row_top, row_middle, row_bottom) = self._copyRowStyle(table_row_list,
                                                           has_header_rows=has_header_rows)

    # clear original table 
    parent_paragraph = target_table.getparent()
    target_index = parent_paragraph.index(target_table)
    parent_paragraph.remove(target_table)
    # clear rows 
    for table_row in table_row_list:
      newtable.remove(table_row)

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
      if listboxline.isTitleLine() and not has_header_rows:
        row = deepcopy(row_top)
        row = self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)
        is_top = False       
      elif listboxline.isDataLine() and is_top:
        row = deepcopy(row_top)
        row = self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)
        is_top = False
      elif listboxline.isStatLine() or (index is last_index and listboxline.isDataLine()):
        row = deepcopy(row_bottom)
        row = self._updateColumnStatValue(row, listbox_column_list, row_middle)
        newtable.append(row)
      elif index > 0 and listboxline.isDataLine():
        row = deepcopy(row_middle)
        row = self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)

    parent_paragraph.insert(target_index, newtable)
 
    return element_tree

  def _copyRowStyle(self, table_row_list=[], has_header_rows=False):
    row_top = None
    row_middle = None
    row_bottom = None
    if len(table_row_list) > 0:
      if len(table_row_list) is 1:
        row_top = deepcopy(table_row_list[0])
        row_middle = deepcopy(table_row_list[0])
        row_bottom = deepcopy(table_row_list[0])
      elif len(table_row_list) is 2 and has_header_rows:
        row_top = deepcopy(table_row_list[0])
        row_middle = deepcopy(table_row_list[0])
        row_bottom = deepcopy(table_row_list[-1])
      elif len(table_row_list) is 2 and not has_header_rows:
        row_top = deepcopy(table_row_list[0])
        row_middle = deepcopy(table_row_list[1])
        row_bottom = deepcopy(table_row_list[-1])
      elif len(table_row_list) >= 2:
        row_top = deepcopy(table_row_list[0])
        row_middle = deepcopy(table_row_list[1])
        row_bottom = deepcopy(table_row_list[-1])
    return (row_top, row_middle, row_bottom)

  def _updateColumnValue(self, row=None, listbox_column_list=[]):
    odf_cell_list = row.findall("{%s}table-cell" % row.nsmap['table'])
    odf_cell_list_size = len(odf_cell_list)
    listbox_column_size = len(listbox_column_list)
    for (column_index, column) in enumerate(odf_cell_list):
      if column_index >= listbox_column_size:
        break
      value = listbox_column_list[column_index][1]
      self._setColumnValue(column, value)
    return row

  def _updateColumnStatValue(self, row=None, listbox_column_list=[], row_middle=None):
    """stat line is capable of column span setting"""
    if row_middle is None:
      return row
    odf_cell_list = row.findall("{%s}table-cell" % row.nsmap['table'])
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
    return row

  def _setColumnValue(self, column, value):
    self._clearColumnValue(column)
    if value is None:
      value = ''
      self._removeColumnValue(column)
    if isinstance(value, DateTime):
      value = value.strftime('%Y-%m-%d')
    column_value = unicode(str(value),'utf-8')
    column_children = column.getchildren()
    first_child = None
    if len(column_children) > 0:
      first_child = deepcopy(column_children[0])
      first_child.text = column_value
    for child in column_children:
      column.remove(child)
    if first_child is not None:
      column.append(first_child)
    if column_value != '':
      value_attribute = self._getColumnValueAttribute(column)
      if value_attribute is not None:
        column.set(value_attribute, column_value)

  def _removeColumnValue(self, column):
    # to eliminate a default value, remove "office:*" attributes.
    # if remaining these attribetes, the column shows its default value,
    # such as '0.0', '$0'
    attrib = column.attrib
    for key in attrib.keys():
      if key.startswith("{%s}" % column.nsmap['office']):
        del attrib[key]
    column.text = ''
    column_children = column.getchildren()
    for child in column_children:
      column.remove(child)

  def _clearColumnValue(self, column):
    attrib = column.attrib
    for key in attrib.keys():
      value_attribute = self._getColumnValueAttribute(column)
      if value_attribute is not None:
        column.set(value_attribute, '')
    column.text = ''
    column_children = column.getchildren()
    for child in column_children:
      # clear data except style
      style_attribute_tuple = self._getStyleAttributeTuple(child)
      child.clear()
      if style_attribute_tuple is not None:
        child.set(style_attribute_tuple[0], style_attribute_tuple[1])

  def _getStyleAttributeTuple(self, element):
    attrib = element.attrib
    for key in attrib.keys():
      if key.endswith('style-name'):
        return (key, attrib[key])
    return None
  
  def _getColumnValueAttribute(self, column):
    attrib = column.attrib
    for key in attrib.keys():
      if key.endswith("value"):
        return key
    return None

  def _getColumnSpanSize(self, column=None):
    span_attribute = "{%s}number-columns-spanned" % column.nsmap['table']
    column_span = 1
    if column.attrib.has_key(span_attribute):
      column_span = int(column.attrib[span_attribute])
    return column_span

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
    odf_cell_list = row_middle.findall("{%s}table-cell" % row_middle.nsmap['table'])
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
  pass
