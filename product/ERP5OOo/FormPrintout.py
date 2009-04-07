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

from Acquisition import Implicit
from Globals import InitializeClass, DTMLFile, Persistent, get_request
from AccessControl import ClassSecurityInfo
from AccessControl.Role import RoleManager
from OFS.SimpleItem import Item, SimpleItem
from urllib import quote
from copy import deepcopy
from lxml import etree
from zLOG import LOG, DEBUG, INFO, WARNING
from mimetypes import guess_extension

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
  And the functions only supports paragraphs and tables.
  
  Fields <-> Paragraphs:      supported
  ListBox <-> Table:          supported
  Report Section <-> Tables:  experimentally supported
  FormBox <-> Frame:          experimentally supported
  Photo <-> Image:            not supported yet
  Style group <-> styles.xml: supported
  Meta group <-> meta.xml:    not supported yet
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

  security.declareProtected('View management screens', 'index_html')
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
    extra_context = dict( container=container,
                          printout_template=printout_template,
                          report_method=report_method,
                          form=form,
                          here=obj )
    # set property to aquisition
    content_type = printout_template.content_type
    self.strategy = self._create_strategy(content_type)
    printout = self.strategy.render(extra_context=extra_context)
    REQUEST.RESPONSE.setHeader('Content-Type','%s; charset=utf-8' % content_type)
    REQUEST.RESPONSE.setHeader('Content-disposition',
                               'inline;filename="%s%s"' % (self.title_or_id(), guess_extension(content_type)))
    return printout
 
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

  def _create_strategy(slef, content_type=''):
    if guess_extension(content_type) == '.odt':
      return ODTStrategy()
    raise ValueError, 'Do not support the template type:%s' % content_type

InitializeClass(FormPrintout)


NAME_SPACE_DICT = {'draw':'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
                   'table':'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
                   'text':'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                   'office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
                   'xlink':'http://www.w3.org/1999/xlink'}

class ODFStrategy(Implicit):
  """ODFStrategy creates a ODF Document. """
  
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

    # content.xml
    ooo_builder = self._replace_content_xml(ooo_builder=ooo_builder, extra_context=extra_context)
    # styles.xml
    ooo_builder = self._replace_styles_xml(ooo_builder=ooo_builder, extra_context=extra_context)
    # meta.xml is not supported yet
    # ooo_builder = self._replace_meta_xml(ooo_builder=ooo_builder, extra_context=extra_context)
        
    # Update the META informations
    ooo_builder.updateManifest()

    ooo = ooo_builder.render(name=odf_template.title or odf_template.id)
    return ooo

  def _replace_content_xml(self, ooo_builder=None, extra_context=None):
    content_xml = ooo_builder.extract('content.xml')
    # mapping ERP5Form to ODF
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)

    content_element_tree = etree.XML(content_xml)
    content_element_tree = self._replace_xml_by_form(element_tree=content_element_tree,
                                                     form=form,
                                                     here=here,
                                                     extra_context=extra_context)
    # mapping ERP5Report report method to ODF
    content_element_tree = self._replace_xml_by_report_section(element_tree=content_element_tree,
                                                               extra_context=extra_context)
    content_xml = etree.tostring(content_element_tree)
    if isinstance(content_xml, unicode):
      content_xml = content_xml.encode('utf-8')
 
    # Replace content.xml in master openoffice template
    ooo_builder.replace('content.xml', content_xml)
    return ooo_builder

  # this method not supported yet
  def _replace_styles_xml(self, ooo_builder=None, extra_context=None):
    """
    replacing styles.xml file in a ODF document
    """
    styles_xml = ooo_builder.extract('styles.xml')
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)
    styles_element_tree = etree.XML(styles_xml)
    styles_element_tree = self._replace_xml_by_form(element_tree=styles_element_tree,
                                                    form=form,
                                                    here=here,
                                                    extra_context=extra_context)
    styles_xml = etree.tostring(styles_element_tree)
    if isinstance(styles_xml, unicode):
      styles_xml = styles_xml.encode('utf-8')
 
    ooo_builder.replace('styles.xml', styles_xml)
    return ooo_builder

  # this method not implemented yet
  def _replace_meta_xml(self, ooo_builder=None, extra_content=None):
    """
    replacing meta.xml file in a ODF document
    """
    meta_xml = ooo_builder.extract('meta.xml')

    if isinstance(doc_xml, unicode):
      meta_xml = meta_xml.encode('utf-8')
 
    ooo_builder.replace('meta.xml', meta_xml)
    return ooo_builder

  def _replace_xml_by_form(self, element_tree=None, form=None, here=None,
                           extra_context=None, render_prefix=None):
    field_list = form.get_fields() 
    REQUEST = get_request()
    for (count, field) in enumerate(field_list):
      if isinstance(field, ListBox):
        element_tree = self._append_table_by_listbox(element_tree=element_tree,
                                                     listbox=field,
                                                     REQUEST=REQUEST,
                                                     render_prefix=render_prefix)
      elif isinstance(field, FormBox):
        sub_form = getattr(here, field.get_value('formbox_target_id'))
        content = self._replace_xml_by_formbox(element_tree=element_tree,
                                               field_id=field.id,
                                               form = sub_form,
                                               REQUEST=REQUEST)
      #elif isinstance(field, ImageField):
      #  element_tree = self._replace_xml_by_image_field(element_tree=element_tree,
      #                                                 image_field=field)
      else:
        element_tree = self._replace_node_via_reference(element_tree=element_tree,
                                                        field=field)
    return element_tree
  
  def _replace_node_via_reference(self, element_tree=None, field=None):
    field_id = field.id
    field_value = field.get_value('default')
    # text:reference-mark text:name="invoice-date"
    reference_xpath = '//text:reference-mark[@text:name="%s"]' % field_id
    reference_list = element_tree.xpath(reference_xpath, namespaces=NAME_SPACE_DICT)
    if len(reference_list) > 0:
      node = reference_list[0].getparent()
      # remove such a "bbb": <text:p>aaa<br/>bbb</text:p>
      for child in node.getchildren():
        child.tail = ''
      node.text = field_value
    return element_tree
  
  def _replace_xml_by_report_section(self, element_tree=None, extra_context=None):
    if not extra_context.has_key('report_method') or extra_context['report_method'] is None:
      return element_tree
    report_method = extra_context['report_method']
    report_section_list = report_method()
    portal_object = self.getPortalObject()
    REQUEST = get_request()
    request = extra_context.get('REQUEST', REQUEST)
    render_prefix = None
    for (index, report_item) in enumerate(report_section_list):
      if index > 0:
        render_prefix = 'x%s' % index
      report_item.pushReport(portal_object, render_prefix = render_prefix)
      here = report_item.getObject(portal_object)
      form_id = report_item.getFormId()
      form = getattr(here, form_id)
      element_tree = self._replace_xml_by_form(element_tree=element_tree,
                                               form=form,
                                               here=here,
                                               extra_context=extra_context,
                                               render_prefix=render_prefix)
      report_item.popReport(portal_object, render_prefix = render_prefix)
    return element_tree

  def _replace_xml_by_formbox(self, element_tree=None, field_id=None, form=None, REQUEST=None):
    draw_xpath = '//draw:frame[@draw:name="%s"]/draw:text-box/*' % field_id
    text_list = element_tree.xpath(draw_xpath, namespaces=NAME_SPACE_DICT)
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

  def _replace_xml_by_image_field(self, element_tree=None, image_field=None):
    alt = image_field.get_value('description') or image_field.get_value('title')
    image_xpath = '//draw:frame[@draw:name="%s"]/*' % image_field.id
    image_list = element_tree.xpath(image_xpath, namespaces=NAME_SPACE_DICT)
    if len(image_list) > 0:
      image_list[0].set("{%s}href" % NAME_SPACE_DICT['xlink'], image_field.absolute_url())
    
    return element_tree

  def _append_table_by_listbox(self,
                               element_tree=None, 
                               listbox=None,
                               REQUEST=None,
                               render_prefix=None):
    table_id = listbox.id
    table_xpath = '//table:table[@table:name="%s"]' % table_id
    # this list should be one item list
    target_table_list = element_tree.xpath(table_xpath, namespaces=NAME_SPACE_DICT)
    if len(target_table_list) is 0:
      return element_tree

    target_table = target_table_list[0]
    newtable = deepcopy(target_table)

    table_header_rows_xpath = '%s/table:table-header-rows' % table_xpath
    table_row_xpath = '%s/table:table-row' % table_xpath
    table_header_rows_list = newtable.xpath(table_header_rows_xpath,  namespaces=NAME_SPACE_DICT)
    table_row_list = newtable.xpath(table_row_xpath,  namespaces=NAME_SPACE_DICT)

    # copy row styles from ODF Document
    has_header_rows = len(table_header_rows_list) > 0
    (row_top, row_middle, row_bottom) = self._copy_row_style(table_row_list,
                                                             has_header_rows=has_header_rows)

    # clear original table 
    parent_paragraph = target_table.getparent()
    target_index = parent_paragraph.index(target_table)
    # 'render_prefix is None' means it is the first table of iteration
    if render_prefix is None:
      parent_paragraph.remove(target_table)
    # clear rows 
    for table_row in table_row_list:
      newtable.remove(table_row)

    listboxline_list = listbox.get_value('default',
                                         render_format='list',
                                         REQUEST=REQUEST, 
                                         render_prefix=render_prefix)
    
    # if ODF table has header rows, does not update the header rows
    # if does not have header rows, insert the listbox title line
    is_top = True
    last_index = len(listboxline_list) - 1
    for (index, listboxline) in enumerate(listboxline_list):
      listbox_column_list = listboxline.getColumnItemList()
      if listboxline.isTitleLine() and not has_header_rows:
        row = deepcopy(row_top)
        row = self._update_column_value(row, listbox_column_list)
        newtable.append(row)
        is_top = False       
      elif listboxline.isDataLine() and is_top:
        row = deepcopy(row_top)
        row = self._update_column_value(row, listbox_column_list)
        newtable.append(row)
        is_top = False
      elif listboxline.isStatLine() or index is last_index:
        row = deepcopy(row_bottom)
        row = self._update_column_stat_value(row, listbox_column_list, row_middle)
        newtable.append(row)
      elif index > 0 and listboxline.isDataLine():
        row = deepcopy(row_middle)
        row = self._update_column_value(row, listbox_column_list)
        newtable.append(row)

    # direct listbox mapping
    if render_prefix is None:
      parent_paragraph.insert(target_index, newtable)
    else:
      # report section iteration
      parent_paragraph.append(newtable)
      
    return element_tree

  def _copy_row_style(self, table_row_list=[], has_header_rows=False):
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
  
  def _update_column_value(self, row=None, listbox_column_list=[]):
    odf_cell_list = row.findall("{%s}table-cell" % NAME_SPACE_DICT['table'])
    odf_cell_list_size = len(odf_cell_list)
    listbox_column_size = len(listbox_column_list)
    for (column_index, column) in enumerate(odf_cell_list):
      if column_index >= listbox_column_size:
        break
      value = listbox_column_list[column_index][1]
      self._set_column_value(column, value)
    return row

  def _update_column_stat_value(self, row=None, listbox_column_list=[], row_middle=None):
    """stat line is capable of column span setting"""
    if row_middle is None:
      return row
    odf_cell_list = row.findall("{%s}table-cell" % NAME_SPACE_DICT['table'])
    odf_column_span_list = self._get_odf_column_span_list(row_middle)
    listbox_column_size = len(listbox_column_list)
    listbox_column_index = 0
    for (column_index, column) in enumerate(odf_cell_list):
      if listbox_column_index >= listbox_column_size:
        break
      value = listbox_column_list[listbox_column_index][1]
      self._set_column_value(column, value)
      column_span = self._get_column_span_size(column)
      listbox_column_index = self._next_listbox_column_index(column_span,
                                                             listbox_column_index,
                                                             odf_column_span_list)
    return row

  def _set_column_value(self, column, value):
    # if the value is a DefaultValue, uses the ODF template value
    if isinstance(value, DefaultValue) or value == DefaultValue:
      return
    self._clear_column_value(column)
    if value is None:
      value = ''
      self._remove_column_value(column)
    column_value = unicode(str(value),'utf-8')
    column.text = column_value
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
      value_attribute = self._get_column_value_attribute(column)
      if value_attribute is not None:
        column.set(value_attribute, column_value)

  def _remove_column_value(self, column):
    # to eliminate a default value, remove "office:*" attributes.
    # if remaining these attribetes, the column shows its default value,
    # such as '0.0', '$0'
    attrib = column.attrib
    for key in attrib.keys():
      if key.startswith("{%s}" % NAME_SPACE_DICT['office']):
        del attrib[key]
    column_children = column.getchildren()
    for child in column_children:
      column.remove(child)

  def _clear_column_value(self, column):
    attrib = column.attrib
    for key in attrib.keys():
      value_attribute = self._get_column_value_attribute(column)
      if value_attribute is not None:
        column.set(value_attribute, '')
    column_children = column.getchildren()
    for child in column_children:
      child.text = ''

  def _get_column_value_attribute(self, column):
    attrib = column.attrib
    for key in attrib.keys():
      if key.endswith("value"):
        return key
    return None
           
  def _get_column_span_size(self, column=None):
    span_attribute = "{%s}number-columns-spanned" % NAME_SPACE_DICT['table']
    column_span = 1
    if column.attrib.has_key(span_attribute):
      column_span = int(column.attrib[span_attribute])
    return column_span
  
  def _next_listbox_column_index(self, span=0, current_index=0, column_span_list=[]):
    hops = 0
    index = current_index
    while hops < span:
      column_span = column_span_list[index]
      hops += column_span
      index += 1
    return index
  
  def _get_odf_column_span_list(self, row_middle=None):
    if row_middle is None:
      return []
    odf_cell_list = row_middle.findall("{%s}table-cell" % NAME_SPACE_DICT['table'])
    column_span_list = []
    for column in odf_cell_list:
      column_span = self._get_column_span_size(column)
      column_span_list.append(column_span)
    return column_span_list

class ODTStrategy(ODFStrategy):
  """ODTStrategy create a ODT Document from a form and a ODT template"""
  pass

class DefaultValue:
  """The DefaultValue is the marker object which indicate that using template value

  Python Script Example: 'number' column uses ODF table cell value

  from Products.PythonScripts.standard import Object
  from Products.ERP5OOo.FormPrintout import DefaultValue

  return [ Object(number=DefaultValue(),
                  total_price=context.getTotalPrice())]
  """
  pass

InitializeClass(DefaultValue)
allow_class(DefaultValue)
