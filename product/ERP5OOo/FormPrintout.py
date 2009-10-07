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
from Products.ERP5Form.ImageField import ImageField
from Products.ERP5OOo.OOoUtils import OOoBuilder
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Acquisition import Implicit, aq_base
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, Persistent, get_request
from AccessControl import ClassSecurityInfo
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item
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
    return ooo_builder

  def _replaceXmlByForm(self, element_tree=None, form=None, here=None,
                           extra_context=None, ooo_builder=None, iteration_index=0):
    field_list = form.get_fields(include_disabled=1) 
    REQUEST = get_request()
    for (count, field) in enumerate(field_list):
      if isinstance(field, ListBox):
        element_tree = self._appendTableByListbox(element_tree=element_tree,
                                                  listbox=field,
                                                  REQUEST=REQUEST,
                                                  iteration_index=iteration_index)
      elif isinstance(field, FormBox):
        if not hasattr(here, field.get_value('formbox_target_id')):
          continue
        sub_form = getattr(here, field.get_value('formbox_target_id'))
        content = self._replaceXmlByFormbox(element_tree=element_tree,
                                            field=field,
                                            form=sub_form,
                                            extra_context=extra_context,
                                            ooo_builder=ooo_builder,
                                            iteration_index=iteration_index)
      elif isinstance(field, ImageField):
        element_tree = self._replaceXmlByImageField(element_tree=element_tree,
                                                    image_field=field,
                                                    ooo_builder=ooo_builder,
                                                    iteration_index=iteration_index)
      else:
        element_tree = self._replaceNodeViaReference(element_tree=element_tree,
                                                     field=field, iteration_index=iteration_index)
    return element_tree

  def _replaceNodeViaReference(self, element_tree=None, field=None, iteration_index=0):
    """replace nodes (e.g. paragraphs) via ODF reference"""
    element_tree = self._replaceNodeViaRangeReference(element_tree=element_tree, field=field)
    element_tree = self._replaceNodeViaPointReference(element_tree=element_tree, field=field)
    return element_tree
  
  def _renderField(self, field):
    # XXX It looks ugly to use render_pdf to extract text. Probably
    # it should be renamed to render_text.
    return field.render_pdf(field.get_value('default'))

  def _replaceNodeViaPointReference(self, element_tree=None, field=None, iteration_index=0):
    """replace via ODF point reference
    
    point reference example:
     <text:reference-mark text:name="invoice-date"/>
    """
    field_id = field.id
    field_value = self._renderField(field)
    value = self._toUnicodeString(field_value)
    # text:reference-mark text:name="invoice-date"
    reference_xpath = '//text:reference-mark[@text:name="%s"]' % field_id
    reference_list = element_tree.xpath(reference_xpath, namespaces=element_tree.nsmap)
    if len(reference_list) > 0:
      target_node = reference_list[0]
      paragraph_node = reference_list[0].getparent()
      parent_node = paragraph_node.getparent()
      if not isinstance(field_value, list):
        # remove such a "bbb": <text:p>aaa<text:line-break/>bbb</text:p>
        for child in paragraph_node.getchildren():
          child.tail = ''
        paragraph_node.text = value
      else:
        self._appendParagraphsWithLineList(target_node=target_node, line_list=field_value)
    # set when using report section
    self._setUniqueElementName(base_name=field.id,
                               iteration_index=iteration_index,
                               xpath=reference_xpath,
                               element_tree=element_tree)
    return element_tree
  
  def _replaceNodeViaRangeReference(self, element_tree=None, field=None, iteration_index=0):
    """replace via ODF range reference

    range reference example:
    <text:reference-mark-start text:name="week"/>Monday<text:reference-mark-end text:name="week"/>
    """
    field_value = self._renderField(field)
    value = self._toUnicodeString(field_value)
    range_reference_xpath = '//text:reference-mark-start[@text:name="%s"]' % field.id
    reference_list = element_tree.xpath(range_reference_xpath, namespaces=element_tree.nsmap)
    if len(reference_list) is 0:
      return element_tree
    target_node = reference_list[0]
    if not isinstance(field_value, list):
      target_node.tail = value
      # clear text until 'reference-mark-end'
      for node in target_node.itersiblings():
        end_tag_name = '{%s}reference-mark-end' % element_tree.nsmap['text']
        name_attribute = '{%s}name' % element_tree.nsmap['text']
        if node.tag == end_tag_name and node.get(name_attribute) == field.id:
          break
        node.tail = ''
    else:
      self._appendParagraphsWithLineList(target_node=target_node, line_list=field_value)

    # set when using report section
    self._setUniqueElementName(base_name=field.id,
                               iteration_index=iteration_index,
                               xpath=range_reference_xpath,
                               element_tree=element_tree)
    return element_tree

  def _appendParagraphsWithLineList(self, target_node=None, line_list=None):
    """create paragraphs 
    
    example:
    --
    first line
    second line
    --
    <p:text>
    first line
    </p:text>
    <p:text>
    second line
    </p:text>
    """
    paragraph_node = target_node.getparent()
    parent_node = paragraph_node.getparent()
    paragraph_list = []
    for line in line_list:
      p = deepcopy(paragraph_node)
      for child in p.getchildren():
        child.tail = ''
      value = self._toUnicodeString(line)
      p.text = value
      paragraph_list.append(p)
    paragraph_node_index = parent_node.index(paragraph_node)
    parent_node.remove(paragraph_node)
    for (index, paragraph) in enumerate(paragraph_list):
      parent_node.insert(paragraph_node_index, paragraph)
      paragraph_node_index = paragraph_node_index + 1
      
  def _replaceXmlByReportSection(self, element_tree=None, extra_context=None, ooo_builder=None):
    if not extra_context.has_key('report_method') or extra_context['report_method'] is None:
      return element_tree
    report_method = extra_context['report_method']
    report_section_list = report_method()
    portal_object = self.getPortalObject()
    REQUEST = get_request()
    request = extra_context.get('REQUEST', REQUEST)

    target_tuple = self._pickUpTargetSection(report_method_name=report_method.__name__,
                                             report_section_list=report_section_list,
                                             element_tree=element_tree)
    if target_tuple is None:
      return element_tree
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
      if index is 0:
        office_body.remove(original_target)
      else:
        self._setUniqueElementName(base_name=report_method.__name__,
                                   iteration_index=index,
                                   xpath=target_xpath,
                                   element_tree=target_element_tree)

      target_element_tree = self._replaceXmlByForm(element_tree=target_element_tree,
                                                   form=form,
                                                   here=here,
                                                   extra_context=extra_context,
                                                   ooo_builder=ooo_builder,
                                                   iteration_index=index)
      office_body.insert(target_index, target_element_tree)
      target_index += 1
      report_item.popReport(portal_object, render_prefix=None)
    return element_tree

  def _pickUpTargetSection(self, report_method_name='', report_section_list=[], element_tree=None):
    """pick up a ODF target object to iterate ReportSection

    report_method_name -- report method name
    report_section_list -- ERP5Form ReportSection List which was created by a report method
    element_tree -- XML ElementTree object
    """
    frame_xpath = '//draw:frame[@draw:name="%s"]' % report_method_name
    frame_list = element_tree.xpath(frame_xpath, namespaces=element_tree.nsmap)
    # <text:section text:style-name="Sect2" text:name="Section2">
    section_xpath = '//text:section[@text:name="%s"]' % report_method_name
    section_list = element_tree.xpath(section_xpath, namespaces=element_tree.nsmap)
    
    if len(frame_list) is 0 and len(section_list) is 0:
      return None

    office_body = None
    original_target = None
    target_xpath = ''
    if len(frame_list) > 0:
      frame = frame_list[0]
      original_target = frame.getparent()
      target_xpath = frame_xpath
    elif len(section_list) > 0:
      original_target = section_list[0]
      target_xpath = section_xpath
    office_body = original_target.getparent()
    # remove if no report section
    if len(report_section_list) is 0:
      office_body.remove(original_target)
      return None  
   
    return (target_xpath, original_target)
  
  def _setUniqueElementName(self, base_name='', iteration_index=0, xpath='', element_tree=None):
    """create a unique element name and set it to the element tree

    Keyword arguments:
    base_name -- the base name of the element
    iteration_index -- iteration index
    xpath -- xpath expression which was used to search the element
    element_tree -- element tree
    """
    if iteration_index is 0:
      return
    def getNameAttribute(target_element=None):
      if target_element is None:
        return None
      attrib = target_element.attrib
      for key in attrib.keys():
        if key.endswith("}name"):
          return key
      return None
    odf_element_name =  "%s_%s" % (base_name, iteration_index)
    result_list = element_tree.xpath(xpath, namespaces=element_tree.nsmap)
    if len(result_list) is 0:
      return
    target_element = result_list[0]
    name_attribute = getNameAttribute(target_element)
    if name_attribute is not None:
      target_element.set(name_attribute, odf_element_name)
 
  def _replaceXmlByFormbox(self,
                           element_tree=None,
                           field=None,
                           form=None,
                           extra_context=None,
                           ooo_builder=None,
                           iteration_index=0):
    field_id = field.id
    enabled = field.get_value('enabled')
    draw_xpath = '//draw:frame[@draw:name="%s"]/draw:text-box/*' % field_id
    text_list = element_tree.xpath(draw_xpath, namespaces=element_tree.nsmap)
    if len(text_list) == 0:
      return element_tree
    target_element = text_list[0]
    frame_paragraph = target_element.getparent()
    office_body = frame_paragraph.getparent()
    if not enabled:
      office_body.remove(frame_paragraph)
      return element_tree
    # set when using report section
    self._setUniqueElementName(base_name=field_id,
                               iteration_index=iteration_index,
                               xpath=draw_xpath,
                               element_tree=element_tree)
    self._replaceXmlByForm(element_tree=frame_paragraph,
                           form=form,
                           here=extra_context['here'],
                           extra_context=extra_context,
                           ooo_builder=ooo_builder,
                           iteration_index=iteration_index)
    return element_tree

  def _replaceXmlByImageField(self,
                              element_tree=None,
                              image_field=None,
                              ooo_builder=None,
                              iteration_index=0):
    alt = image_field.get_value('description') or image_field.get_value('title')
    image_xpath = '//draw:frame[@draw:name="%s"]/*' % image_field.id
    image_list = element_tree.xpath(image_xpath, namespaces=element_tree.nsmap)
    if len(image_list) is 0:
      return element_tree
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
      return element_tree
    picture_type = picture.getContentType()
    picture_path = self._createOdfUniqueFileName(path=path, picture_type=picture_type)
    ooo_builder.addFileEntry(picture_path, media_type=picture_type, content=picture_data)
    picture_size = self._getPictureSize(picture, image_node)
    image_node.set('{%s}href' % element_tree.nsmap['xlink'], picture_path)
    image_frame.set('{%s}width' % element_tree.nsmap['svg'], picture_size[0])
    image_frame.set('{%s}height' % element_tree.nsmap['svg'], picture_size[1])
    # set when using report section
    self._setUniqueElementName(base_name=image_field.id,
                               iteration_index=iteration_index,
                               xpath=image_xpath,
                               element_tree=element_tree)
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
                            REQUEST=None,
                            iteration_index=0):
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
    # create style-name and table-row dictionary if a reference name is set
    style_name_row_dictionary = self._createStyleNameRowDictionary(table_row_list)
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
      row_style_name = listboxline.getRowCSSClassName()
      if listboxline.isTitleLine() and not has_header_rows:
        row = deepcopy(row_top)
        row = self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)
        is_top = False       
      elif listboxline.isDataLine() and is_top:
        if style_name_row_dictionary.has_key(row_style_name):
          row = deepcopy(style_name_row_dictionary[row_style_name])
        else:
          row = deepcopy(row_top)
        row = self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)
        is_top = False
      elif listboxline.isStatLine() or (index is last_index and listboxline.isDataLine()):
        row = deepcopy(row_bottom)
        row = self._updateColumnStatValue(row, listbox_column_list, row_middle)
        newtable.append(row)
      elif index > 0 and listboxline.isDataLine():
        if style_name_row_dictionary.has_key(row_style_name):
          row = deepcopy(style_name_row_dictionary[row_style_name])
        else:
          row = deepcopy(row_middle)
        row = self._updateColumnValue(row, listbox_column_list)
        newtable.append(row)

    self._setUniqueElementName(base_name=table_id,
                               iteration_index=iteration_index,
                               xpath=table_xpath,
                               element_tree=newtable)
    parent_paragraph.insert(target_index, newtable)
 
    return element_tree

  def _copyRowStyle(self, table_row_list=[], has_header_rows=False):
    def removeOfficeAttribute(row):
      if row is None or has_header_rows: return
      odf_cell_list = row.findall("{%s}table-cell" % row.nsmap['table'])
      for odf_cell in odf_cell_list:
        self._removeColumnValue(odf_cell)
          
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

    # remove office attribute if create a new header row 
    removeOfficeAttribute(row_top)
    return (row_top, row_middle, row_bottom)


  def _createStyleNameRowDictionary(self, table_row_list=[]):
    """create stylename and table row dictionary if a style name reference is set"""
    style_name_row_dictionary = {}
    for table_row in table_row_list:
      reference_element = table_row.find('.//*[@{%s}name]' % table_row.nsmap['text'])
      if reference_element is not None:
        name = reference_element.attrib['{%s}name' % table_row.nsmap['text']]
        style_name_row_dictionary[name] = deepcopy(table_row)
    return style_name_row_dictionary
    
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
      self._removeColumnValue(column)
    column_value, table_content = self._translateValueIntoColumnContent(value, column)
    for child in column.getchildren():
      column.remove(child)
    if table_content is not None:
      column.append(table_content)
    value_attribute = self._getColumnValueAttribute(column)
    if value_attribute is not None and column_value is not None:
       column.set(value_attribute, column_value)

  def _translateValueIntoColumnContent(self, value, column):
    """translate a value as a table content"""
    table_content = None
    column_children = column.getchildren()
    if len(column_children) > 0:
      table_content = deepcopy(column_children[0])
    # create a tempolaly etree object to generate a content paragraph
    fragment = self._valueAsOdfXmlElement(value=value, element_tree=column)
    column_value = None
    if table_content is not None:
      table_content.text = fragment.text
      for element in fragment.getchildren():
        table_content.append(element)
      column_value = " ".join([x for x in table_content.itertext()])
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
    text_namespace = element_tree.nsmap['text']
    tab_element_str = '<text:tab xmlns:text="%s"/>' % text_namespace
    line_break_element_str ='<text:line-break xmlns:text="%s"/>' % text_namespace
    translated_value = translated_value.replace('\t', tab_element_str)
    translated_value = translated_value.replace('\r', '')
    translated_value = translated_value.replace('\n', line_break_element_str)
    translated_value = unicode(str(translated_value),'utf-8')
    # create a paragraph
    template = '<text:p xmlns:text="%s">%s</text:p>'
    fragment_element_tree = etree.XML(template % (text_namespace, translated_value))
    return fragment_element_tree
  
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
