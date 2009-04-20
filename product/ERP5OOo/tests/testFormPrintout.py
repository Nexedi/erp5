##############################################################################
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Nexedi KK and Contributors. All Rights Reserved.
#                    Tatuya Kamada <tatuya@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301,
# USA.
#
##############################################################################

import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5OOo.OOoUtils import OOoBuilder
from Products.ERP5OOo.tests.utils import Validator
from zLOG import LOG , INFO
from lxml import etree
import os

class TestFormPrintout(ERP5TypeTestCase):
  run_all_test = 1

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "FormPrintout"

  def getBusinessTemplateList(self):
    return ('erp5_ui_test', 'erp5_odt_style')

  def afterSetUp(self):
    self.login()
    foo_file_path = os.path.join(os.path.dirname(__file__),
                                'test_document',
                                'Foo_001.odt')
    foo2_file_path = os.path.join(os.path.dirname(__file__),
                                  'test_document',
                                  'Foo_002.odt')   
    foo_file = open(foo_file_path, 'rb')
    foo2_file = open(foo2_file_path, 'rb')
    custom = self.portal.portal_skins.custom
    addStyleSheet = custom.manage_addProduct['OFSP'].manage_addFile
    if custom._getOb('Foo_getODTStyleSheet', None) is None:
      addStyleSheet(id='Foo_getODTStyleSheet', file=foo_file, title='',
                    precondition='', content_type = 'application/vnd.oasis.opendocument.text')
    if custom._getOb('Foo2_getODTStyleSheet', None) is None:
      addStyleSheet(id='Foo2_getODTStyleSheet', file=foo2_file, title='',
                    precondition='', content_type = 'application/vnd.oasis.opendocument.text')   
    erp5OOo = custom.manage_addProduct['ERP5OOo']
    addOOoTemplate = erp5OOo.addOOoTemplate
    if custom._getOb('Foo_viewAsOdt', None) is None:
      addOOoTemplate(id='Foo_viewAsOdt', title='')
    request = self.app.REQUEST
    Foo_viewAsOdt = custom.Foo_viewAsOdt
    Foo_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                             ooo_stylesheet='Foo_getODTStyleSheet')
    #Foo_viewAsOdt.pt_upload(request, file=foo_file)
    #render_result = Foo_viewAsOdt(REQUEST=request)
    builder = OOoBuilder(foo_file)
    content = builder.extract('content.xml')
    Foo_viewAsOdt.pt_edit(content, content_type='application/vnd.oasis.opendocument.text')
    if custom._getOb('Foo_viewAsPrintout', None) is None:
      erp5OOo.addFormPrintout(id='Foo_viewAsPrintout', title='',
                              form_name='Foo_view', template='Foo_getODTStyleSheet')
    if custom._getOb('FooReport_viewAsPrintout', None) is None:
      erp5OOo.addFormPrintout(id='FooReport_viewAsPrintout',
                              title='')

    ## append 'test1' data to a listbox
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    if test1._getOb("foo_1", None) is None:
      test1.newContent("foo_1", portal_type='Foo Line')
    if test1._getOb("foo_2", None) is None:
      test1.newContent("foo_2", portal_type='Foo Line')
    get_transaction().commit()
    self.tic()

    # XML validator
    v12schema_url = os.path.join(os.path.dirname(__file__),
                                 'OpenDocument-schema-v1.2-draft9.rng') 
    self.validator = Validator(schema_url=v12schema_url)
    
  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('tatuya', '', ['Manager'], [])
    user = uf.getUserById('tatuya').__of__(uf)
    newSecurityManager(None, user)

  def _validate(self, odf_file_data):
    error_list = self.validator.validate(odf_file_data)
    if error_list:
      self.fail(''.join(error_list))

  def test_01_Paragraph(self, run=run_all_test):
    """
    mapping a field to a paragraph
    """
    if not run: return
    
    portal = self.getPortal()
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    test1.setTitle('Foo title!')
    get_transaction().commit()
    self.tic()

    # test target
    foo_printout = portal.foo_module.test1.Foo_viewAsPrintout

    request = self.app.REQUEST
    # 1. Normal case: "my_title" field to the "my_title" reference in the ODF document
    self.portal.changeSkin('ODT')
    odf_document = foo_printout.index_html(REQUEST=request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Foo title!") > 0)
    self.assertEqual(request.RESPONSE.getHeader('content-type'),
                     'application/vnd.oasis.opendocument.text; charset=utf-8')
    self.assertEqual(request.RESPONSE.getHeader('content-disposition'),
                     'inline;filename="Foo_viewAsPrintout.odt"')
    self._validate(odf_document)
    
    # 2. Normal case: change the field value and check again the ODF document
    test1.setTitle("Changed Title!")
    #foo_form.my_title.set_value('default', "Changed Title!")
    odf_document = foo_printout.index_html(REQUEST=request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Changed Title!") > 0)
    self._validate(odf_document)
    
    # 3. False case: change the field name 
    test1.setTitle("you cannot find")
    # rename id 'my_title' to 'xxx_title', then does not match in the ODF document
    foo_form = portal.foo_module.test1.Foo_view
    foo_form.manage_renameObject('my_title', 'xxx_title', REQUEST=request)
    odf_document = foo_printout.index_html(REQUEST=request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("you cannot find") > 0)
    self._validate(odf_document)
    # put back
    foo_form.manage_renameObject('xxx_title', 'my_title', REQUEST=request)

    ## 4. False case: does not set a ODF template
    self.assertTrue(foo_printout.template == 'Foo_getODTStyleSheet')
    tmp_template = foo_printout.template 
    foo_printout.template = None
    # template == None, causes a ValueError 
    try: 
      foo_printout.index_html(REQUEST=request)
    except ValueError, e:
      # e -> 'Can not create a ODF Document without a odf_template'
      self.assertTrue(True)

    # put back
    foo_printout.template = tmp_template
    
    # 5. Normal case: just call a FormPrintout object
    request.RESPONSE.setHeader('Content-Type', 'text/html')
    test1.setTitle("call!")
    odf_document = foo_printout() # call
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("call!") > 0)
    # when just call FormPrintout, it does not change content-type
    self.assertEqual(request.RESPONSE.getHeader('content-type'), 'text/html')
    self._validate(odf_document)
    
    # 5. Normal case: utf-8 string
    test1.setTitle("Français")
    odf_document = foo_printout() 
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français") > 0)
    self._validate(odf_document)
    
    # 6. Normal case: unicode string
    test1.setTitle(u'Français test2')
    odf_document = foo_printout() 
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français test2") > 0)
    self._validate(odf_document)
        
  def test_02_Table_01_Normal(self, run=run_all_test):
    """To test listbox and ODF table mapping
    
     * Test Data Format
    
     ODF table named 'listbox':
     +------------------------------+
     |  ID | Title | Quantity |Date |
     |-----+-------+----------+-----|
     |     |       |          |     |
     |-----+-------+----------+-----|
     |   Total     |          |     |
     +------------------------------+
    """
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1
    
    # 1. Normal Case: ODF table last row is stat line
    test1.foo_1.setTitle('foo_title_1')
    message = listbox.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.failUnless('Set Successfully' in message)
    listboxline_list = listbox.get_value('default', render_format = 'list',
                                         REQUEST = request)
    self.assertEqual(len(listboxline_list), 4)
    self.assertTrue(listboxline_list[0].isTitleLine())
    self.assertTrue(listboxline_list[1].isDataLine())
    self.assertTrue(listboxline_list[2].isDataLine())
    self.assertTrue(listboxline_list[3].isStatLine())
    column_list = listboxline_list[0].getColumnPropertyList()
    self.assertEqual(len(column_list), 4)
    self.assertTrue(listboxline_list[1].getColumnProperty('id') == "foo_1")
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_1")
    
    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_01_Table.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("foo_title_1") > 0)
    self._validate(odf_document)
    
  def test_02_Table_02_SmallerThanListboxColumns(self, run=run_all_test):
    """2. Irregular case: listbox columns count smaller than table columns count"""
    if not run: return 
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1

    test1.foo_1.setTitle('foo_title_2')
    message = listbox.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity',)
    self.failUnless('Set Successfully' in message)
    self.assertEqual(listbox.get_value('columns'),
                     [('id', 'ID'), ('title', 'Title'), ('quantity', 'Quantity')])
    listboxline_list = listbox.get_value('default', render_format = 'list',
                                         REQUEST = request)
    self.assertEqual(len(listboxline_list), 4)
    self.assertTrue(listboxline_list[0].isTitleLine())
    self.assertTrue(listboxline_list[1].isDataLine())
    self.assertTrue(listboxline_list[2].isDataLine())
    self.assertTrue(listboxline_list[3].isStatLine())
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_2")
    
    column_list = listboxline_list[0].getColumnPropertyList()
    self.assertEqual(len(column_list), 3)

    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_02_Table.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_title_1") > 0)
    self.assertTrue(content_xml.find("foo_title_2") > 0)
    self._validate(odf_document)

  def test_02_Table_03_ListboxColumnsLargerThanTable(self, run=run_all_test):
    """3. Irregular case: listbox columns count larger than table columns count"""
    if not run: return 
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1

    test1.foo_1.setTitle('foo_title_3')
    message = listbox.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\n'
                      'start_date|Date\nstatus|Status',)
    self.failUnless('Set Successfully' in message)
    listboxline_list = listbox.get_value('default', render_format = 'list',
                                         REQUEST = request)
    self.assertEqual(len(listboxline_list), 4)
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_3")
    
    column_list = listboxline_list[0].getColumnPropertyList()
    self.assertEqual(len(column_list), 5)
    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_03_Table.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_title_2") > 0)
    self.assertTrue(content_xml.find("foo_title_3") > 0)
    self._validate(odf_document)
    
  def test_02_Table_04_ListboxHasNotStat(self, run=run_all_test):
    """4. Irregular case: listbox has not a stat line, but table has a stat line"""
    if not run: return 
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1

    test1.foo_1.setTitle('foo_title_4')
    test1.foo_1.setStartDate('2009-01-01')
    message = listbox.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = '',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.failUnless('Set Successfully' in message)
    listboxline_list = listbox.get_value('default', render_format = 'list',
                                         REQUEST = request)
    for line in listboxline_list:
      self.assertEqual(line.isStatLine(), False)
    self.assertEqual(len(listboxline_list), 3)
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_4")

    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_04_Table.odf", "w")
    #test_output.write(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(odf_document is not None)
    self.assertFalse(content_xml.find("foo_title_3") > 0)
    self.assertTrue(content_xml.find("foo_title_4") > 0)

    content = etree.XML(content_xml)
    table_row_xpath = '//table:table[@table:name="listbox"]/table:table-row'
    odf_table_rows = content.xpath(table_row_xpath, namespaces=content.nsmap)
    self.assertEqual(len(odf_table_rows), 2)
    # to test copying ODF table cell styles 
    first_row = odf_table_rows[0]
    first_row_columns = first_row.getchildren()
    last_row = odf_table_rows[-1]
    last_row_columns = last_row.getchildren()
    span_attribute = "{%s}number-columns-spanned" % content.nsmap['table']
    self.assertFalse(first_row_columns[0].attrib.has_key(span_attribute))
    self.assertEqual(int(last_row_columns[0].attrib[span_attribute]), 2)
    self._validate(odf_document)
    
  def test_02_Table_05_NormalSameLayout(self, run=run_all_test):
    """5. Normal case: the listobx and the ODF table are same layout

    * Test Data Format:
    
     ODF table named 'listbox2'
     +-------------------------------+
     |  A    |   B   |   C   |   D   |
     |-------+-------+-------+-------|
     |       |       |       |       |
     +-------+-------+-------+-------+
    """
    if not run: return

    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1

    foo_form.manage_renameObject('listbox', 'listbox2', REQUEST=request)
    listbox2 = foo_form.listbox2
    test1.foo_1.setTitle('foo_title_5')
    message = listbox2.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.failUnless('Set Successfully' in message)
    listboxline_list = listbox2.get_value('default', render_format = 'list',
                                         REQUEST = request)
    self.assertEqual(len(listboxline_list), 4)
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_5")

    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_05_Table.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_title_4") > 0)
    self.assertTrue(content_xml.find("foo_title_5") > 0)
    self._validate(odf_document)
    
    # put back the field name
    foo_form.manage_renameObject('listbox2', 'listbox', REQUEST=request)

    
  def test_02_Table_06_TableDoesNotHaveAHeader(self, run=run_all_test):
    """6. Normal case: ODF table does not have a header
     * Test Data format:
    
     ODF table named 'listbox3'
     the table listbox3 has not table header.
     first row is a table content, too.
     +-------------------------------+
     |  1    |   2   |   3   |   4   |
     |-------+-------+-------+-------|
     |       |       |       |       |
     +-------+-------+-------+-------+
    """
    if not run: return 
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1

    foo_form.manage_renameObject('listbox', 'listbox3', REQUEST=request)
    listbox3 = foo_form.listbox3
    test1.foo_1.setTitle('foo_title_6')
    message = listbox3.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.failUnless('Set Successfully' in message)
    listboxline_list = listbox3.get_value('default', render_format = 'list',
                                         REQUEST = request)
    self.assertEqual(len(listboxline_list), 4)
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_6")
    
    odf_document = foo_printout.index_html(REQUEST=request)
    test_output = open("/tmp/test_02_06_Table.odf", "w")
    test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_title_5") > 0)
    self.assertTrue(content_xml.find("foo_title_6") > 0)
    self._validate(odf_document)
    
    # put back the field name
    foo_form.manage_renameObject('listbox3', 'listbox', REQUEST=request)

  def test_02_Table_07_CellFormat(self, run=run_all_test):
    """7. Normal case: cell format cetting"""
    if not run: return 
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1

    test1.foo_1.setTitle('foo_title_7')
    test1.foo_1.setStartDate('2009-04-20')
    message = listbox.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.failUnless('Set Successfully' in message)
    listboxline_list = listbox.get_value('default', render_format = 'list',
                                         REQUEST = request)
    self.assertEqual(len(listboxline_list), 4)
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_7")
      
    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_07_Table.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_title_6") > 0)
    self.assertTrue(content_xml.find("foo_title_7") > 0)

    content = etree.XML(content_xml)
    table_row_xpath = '//table:table[@table:name="listbox"]/table:table-row'
    odf_table_rows = content.xpath(table_row_xpath, namespaces=content.nsmap)
    self.assertEqual(len(odf_table_rows), 3)
    # to test ODF table cell number format
    first_row = odf_table_rows[0]
    first_row_columns = first_row.getchildren()
    date_column = first_row_columns[3]
    date_value_attrib = "{%s}date-value" % content.nsmap['office']
    self.assertTrue(date_column.attrib.has_key(date_value_attrib))
    self.assertEqual(date_column.attrib[date_value_attrib], '2009-04-20')
    self._validate(odf_document)

  def test_02_Table_08_Nodata(self, run=run_all_test):
    """7. Normal case: list box has no data"""
    if not run: return 
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST 
    request['here'] = test1

    test1.foo_1.setTitle('foo_title_8')
    message = listbox.ListBox_setPropertyList(
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.failUnless('Set Successfully' in message)
    listboxline_list = listbox.get_value('default', render_format = 'list',
                                         REQUEST = request)
    # title line only
    self.assertEqual(len(listboxline_list), 1)
      
    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_08_Table.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")

    content = etree.XML(content_xml)
    table_row_xpath = '//table:table[@table:name="listbox"]/table:table-row'
    odf_table_rows = content.xpath(table_row_xpath, namespaces=content.nsmap)
    # no rows
    self.assertEqual(len(odf_table_rows), 0)
    self._validate(odf_document)
    
  def _test_03_Frame(self, run=run_all_test):
    """
    Frame not supported yet
    """
    pass

  def test_04_Iteration(self, run=run_all_test):
    """
    Iteration using ERP5Report ReportSection test
    """
    custom = self.portal.portal_skins.custom
    erp5form = custom.manage_addProduct['ERP5Form']
    erp5form.addERP5Report(id='FooReport_view', title='Foo Report')
    foo_report_view = custom.FooReport_view
    foo_report_view.report_method = 'FooReport_getReportSectionList'

    erp5form.addERP5Form(id='Foo2_view', title='Foo2')
    foo2_view = custom.Foo2_view
    # Attention: Report.py popReport, pushReport
    # only accepts named 'listbox' Listbox
    foo2_view.manage_addField('listbox', 'listbox', 'ListBox')
    listbox = foo2_view.listbox

    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getFooList',
      'title,**kw',
r"""
foo_list = context.objectValues(portal_type='Foo Line')
for foo in foo_list:
  foo.setTitle(title)
return foo_list
"""
      )
    message = listbox.ListBox_setPropertyList(
      field_list_method = 'FooReport_getFooList',
      field_portal_types = 'Foo Line | Foo Line',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.failUnless('Set Successfully' in message)
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
from Products.ERP5Form.Report import ReportSection

r1 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo2_view',
                   selection_params={'title':'foo_04_Iteration_1'})
r2 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo2_view',
                   selection_params={'title':'foo_04_Iteration_2'})
report_section_list = [r1, r2]
return report_section_list
"""
        )
    test1 = self.portal.foo_module.test1
    foo_report_printout = test1.FooReport_viewAsPrintout
    foo_report_printout.doSettings(REQUEST=None,
                                   title='',
                                   form_name='FooReport_view',
                                   template='Foo2_getODTStyleSheet')
    odf_document = foo_report_printout()

    #test_output = open("/tmp/test_04_Iteratoin.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("foo_04_Iteration_1") > 0)
    content = etree.XML(content_xml)
    frame_xpath = '//draw:frame[@draw:name="FooReport_getReportSectionList"]'
    frame_list = content.xpath(frame_xpath, namespaces=content.nsmap)
    self.assertEqual(len(frame_list), 1)
    frame1_xpath = '//draw:frame[@draw:name="FooReport_getReportSectionList_1"]'
    frame1_list = content.xpath(frame1_xpath, namespaces=content.nsmap)
    self.assertEqual(len(frame1_list), 1)

    self._validate(odf_document)
    
    # 02. no report section
    custom.manage_delObjects(['FooReport_getReportSectionList'])
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
return []
"""
      )
    odf_document = foo_report_printout()
    #test_output = open("/tmp/test_04_02_Iteratoin.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_04_Iteration") > 0)
    content = etree.XML(content_xml)
    frame_xpath = '//draw:frame[@draw:name="FooReport_getReportSectionList"]'
    frame_list = content.xpath(frame_xpath, namespaces=content.nsmap)
    # the frame was removed
    self.assertEqual(len(frame_list), 0)
    self._validate(odf_document)
    
  def _test_05_Styles(self, run=run_all_test):
    """
    styles.xml not tested yet
    """
    pass

  def _test_06_Meta(self, run=run_all_test):
    """
    meta.xml not supported yet
    """
    pass

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFormPrintout))
  return suite
