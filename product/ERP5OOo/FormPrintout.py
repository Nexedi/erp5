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
from Products.ERP5Type import PropertySheet, Permissions
from Products.ERP5Form.ListBox import ListBox 
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
  
class FormPrintout(Implicit, Persistent, RoleManager, Item):
  """Form Printout

  The Form Printout enables to create a ODF document.

  The Form Printout receives a name of a ERP5 form, and a template name.
  Using their parameters, the Form Printout genereate a ODF document,
  a form as a ODF document content, and a template as a document layout.

  WARNING: The Form Printout currently supports only ODT format document.
  And the functions only supports paragraphs and tables.
  
  Fields <-> Paragraphs:      supported
  ListBox <-> Table:          supported
  Report Section <-> Tables:  experimentally supported
  FormBox <-> Frame:          not supported yet
  Photo <-> Image:            not supported yet
  Style group <-> styles.xml: not supported yet
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

  def __str__(self): return self.index_html()

  def __len__(self): return 1

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
                   'office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0'}

class ODFStrategy(Implicit):
  """ODFStrategy creates a ODF Document. """
  
  def render(self, extra_context={}):
    """Render a odt document, form as a content, template as a template.

    Keyword arguments:
    extra_context -- a dictionary, guess contains
                     'here' : where it call
                     'printout_template' : the template object, tipically a OOoTemplate
                     'container' : the object which has a form printout object
                     'form' : the form as a content
    """
    here = extra_context['here']
    if here is None:
      # This is a system error
      raise ValueError, 'Can not create a ODF Document without a parent acquisition context'
    form = extra_context['form']
    if not extra_context.has_key('printout_template') or extra_context['printout_template'] is None:
      raise ValueError, 'Can not create a ODF Document without a printout template'

    odf_template = extra_context['printout_template']
    
    # First, render a OOoTemplate itself with its style
    ooo_document = None
    if hasattr(odf_template, 'pt_render'):
      ooo_document = odf_template.pt_render(here, extra_context=extra_context)
    else:
      # File object, OOoBuilder directly support a file object
      ooo_document = odf_template 

    # Create a new builder instance
    ooo_builder = OOoBuilder(ooo_document)

    # content.xml
    ooo_builder = self._replace_content_xml(ooo_builder=ooo_builder, extra_context=extra_context)
    # styles.xml and meta.xml are not supported yet
    # ooo_builder = self._replace_styles_xml(ooo_builder=ooo_builder, extra_context=extra_context)
    # ooo_builder = self._replace_meta_xml(ooo_builder=ooo_builder, extra_context=extra_context)
        
    # Update the META informations
    ooo_builder.updateManifest()

    ooo = ooo_builder.render(name=odf_template.title or odf_template.id)
    return ooo

  def _replace_content_xml(self, ooo_builder=None, extra_context=None):
    doc_xml = ooo_builder.extract('content.xml')
    # mapping ERP5Form to ODF
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)
    ordinaly_group_list = [group for group in form.get_groups() if group not in ['meta','style']]
    doc_xml = self._replace_xml_by_form(doc_xml=doc_xml,
                                        form=form,
                                        here=here,
                                        extra_context=extra_context,
                                        group_list=ordinaly_group_list)
    # mapping ERP5Report report method to ODF
    doc_xml = self._replace_xml_by_report_section(doc_xml=doc_xml,
                                                  extra_context=extra_context)

    if isinstance(doc_xml, unicode):
      doc_xml = doc_xml.encode('utf-8')
 
    # Replace content.xml in master openoffice template
    ooo_builder.replace('content.xml', doc_xml)
    return ooo_builder

  # this method not supported yet
  def _replace_styles_xml(self, ooo_builder=None, extra_context=None):
    """
    replacing styles.xml file in a ODF document
    """
    doc_xml = ooo_builder.extract('styles.xml')
    form = extra_context['form']
    here = getattr(self, 'aq_parent', None)
    doc_xml = self._replace_xml_by_form(doc_xml=doc_xml,
                                        form=form,
                                        here=here,
                                        extra_context=extra_context,
                                        group_list=['styles'])

    if isinstance(doc_xml, unicode):
      doc_xml = doc_xml.encode('utf-8')
 
    ooo_builder.replace('styles.xml', doc_xml)
    return ooo_builder

  # this method not implemented yet
  def _replace_meta_xml(self, ooo_builder=None, extra_content=None):
    """
    replacing meta.xml file in a ODF document
    """
    doc_xml = ooo_builder.extract('meta.xml')

    if isinstance(doc_xml, unicode):
      doc_xml = doc_xml.encode('utf-8')
 
    ooo_builder.replace('meta.xml', doc_xml)
    return ooo_builder

  def _replace_xml_by_form(self, doc_xml=None, form=None, here=None,
                           group_list=[], extra_context=None):
    field_list = [f for g in group_list for f in form.get_fields_in_group(g)]
    content = etree.XML(doc_xml)
    REQUEST = get_request()
    for (count,field) in enumerate(field_list):
      if isinstance(field, ListBox):
        content = self._append_table_by_listbox(content=content,
                                                listbox=field,
                                                REQUEST=REQUEST) 
      else:
        field_value = field.get_value('default')
        content = self._replace_node_via_reference(content=content,
                                                   field_id=field.id,
                                                   field_value=field_value)
    return etree.tostring(content)

  def _replace_node_via_reference(self, content=None, field_id=None, field_value=None):
    # text:reference-mark text:name="invoice-date"
    reference_xpath = '//text:reference-mark[@text:name="%s"]' % field_id
    reference_list = content.xpath(reference_xpath, namespaces=NAME_SPACE_DICT)
    if len(reference_list) > 0:
      node = reference_list[0].getparent()
      ## remove such a "bbb"
      ## <text:p>aaa<br/>bbb</text:p>
      for child in node.getchildren():
        child.tail = ''
      node.text = field_value
    return content
  
  def _replace_xml_by_report_section(self, doc_xml=None, extra_context=None):
    if not extra_context.has_key('report_method') or extra_context['report_method'] is None:
      return doc_xml
    report_method = extra_context['report_method']
    report_section_list = report_method()
    portal_object = self.getPortalObject()
    content = etree.XML(doc_xml)
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
      for field in form.get_fields():
        if field.meta_type == 'ListBox':
          content = self._append_table_by_listbox(content=content,
                                                  listbox=field,
                                                  REQUEST=request,
                                                  render_prefix=render_prefix) 
      report_item.popReport(portal_object, render_prefix = render_prefix)
   
    return etree.tostring(content)

  def _append_table_by_listbox(self,
                               content=None, 
                               listbox=None,
                               REQUEST=None,
                               render_prefix=None):
    table_id = listbox.id
    table_xpath = '//table:table[@table:name="%s"]' % table_id
    # this list should be one item list
    target_table_list = content.xpath(table_xpath, namespaces=NAME_SPACE_DICT)
    if len(target_table_list) is 0:
      return content

    target_table = target_table_list[0]
    newtable = deepcopy(target_table)
    # <table:table-header-rows>
    table_header_rows_xpath = '%s/table:table-header-rows' % table_xpath
    table_row_xpath = '%s/table:table-row' % table_xpath
    table_header_rows_list = newtable.xpath(table_header_rows_xpath,  namespaces=NAME_SPACE_DICT)
    table_row_list = newtable.xpath(table_row_xpath,  namespaces=NAME_SPACE_DICT)

    # copy row styles from ODF Document
    has_header_rows = len(table_header_rows_list) > 0
    LOG('FormPrintout has_header_rows', INFO, has_header_rows)
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
    
    # if ODF table has heder rows, does not update the header rows
    # if ODF table does not have header rows, insert the listbox title line
    is_top = True
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
      elif index > 0 and listboxline.isDataLine():
        row = deepcopy(row_middle)
        row = self._update_column_value(row, listbox_column_list)
        newtable.append(row)
      elif listboxline.isStatLine():
        row = deepcopy(row_bottom)
        row = self._update_column_stat_value(row, listbox_column_list, row_middle)
        newtable.append(row)

    # direct listbox mapping
    if render_prefix is None:
      parent_paragraph.insert(target_index, newtable)
    else:
      # report section iteration
      parent_paragraph.append(newtable)
      # TODO: it would be better append a paragraph or linebreak
      
    return content

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
      # if value is None, remaining ODF orinal text
      if value is not None:
        self._set_column_value(column, value)
      column_span = self._get_column_span_size(column)
      listbox_column_index = self._next_listbox_column_index(column_span,
                                                             listbox_column_index,
                                                             odf_column_span_list)
    return row

  def _set_column_value(self, column, value):
    if value is None:
      # to eliminate a default value, remove "office:*" attributes.
      # if remaining "office:*" attribetes, the column shows its default value,
      # such as '0.0', '$0'
      attrib = column.attrib
      for key in attrib.keys():
        if key.startswith("{%s}" % NAME_SPACE_DICT['office']):
          del attrib[key]
        value = ''
    column_value = unicode(str(value),'utf-8')
    column.text = column_value
    column_children = column.getchildren()
    if len(column_children) > 0:
      column_children[0].text = column_value
    if column_value != '':
      column.set("{%s}value" % NAME_SPACE_DICT['office'], column_value)
    
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
    span_attribute = "{%s}number-columns-spanned" % NAME_SPACE_DICT['table']
    for column in odf_cell_list:
      column_span = self._get_column_span_size(column)
      column_span_list.append(column_span)
    return column_span_list

class ODTStrategy(ODFStrategy):
  """ODTStrategy create a ODT Document from a form and a ODT template"""
  pass
