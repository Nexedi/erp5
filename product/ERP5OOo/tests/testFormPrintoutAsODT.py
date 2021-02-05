# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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
from unittest import skip
from Products.ERP5OOo.tests.TestFormPrintoutMixin import TestFormPrintoutMixin
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.MimetypesRegistry.mime_types.magic import guessMime
from Products.ERP5OOo.OOoUtils import OOoBuilder
from Products.ERP5OOo.tests.utils import Validator
from Products.ERP5Type.tests.utils import FileUpload
from DateTime import DateTime
from lxml import etree
import os

class TestFormPrintoutAsODT(TestFormPrintoutMixin):

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "FormPrintout"

  def afterSetUp(self):
    self.login()
    # XML validator
    v12schema_url = os.path.join(os.path.dirname(__file__),
                                 'OpenDocument-v1.2-os-schema.rng')
    self.validator = Validator(schema_url=v12schema_url)

    foo_file_path = os.path.join(os.path.dirname(__file__),
                                'test_document',
                                'Foo_001.odt')
    foo2_file_path = os.path.join(os.path.dirname(__file__),
                                  'test_document',
                                  'Foo_002.odt')
    foo3_file_path = os.path.join(os.path.dirname(__file__),
                                  'test_document',
                                  'Foo_003.odt')
    foo4_file_path = os.path.join(os.path.dirname(__file__),
                                  'test_document',
                                  'Foo_004.odt')
    foo5_file_path = os.path.join(os.path.dirname(__file__),
                                  'test_document',
                                  'Foo_005.odt')
    variable_file_path = os.path.join(os.path.dirname(__file__),
                                  'test_document',
                                  'Foo_001_with_variable.odt')
    foo_file = open(foo_file_path, 'rb')
    foo2_file = open(foo2_file_path, 'rb')
    foo3_file = open(foo3_file_path, 'rb')
    foo4_file = open(foo4_file_path, 'rb')
    foo5_file = open(foo5_file_path, 'rb')
    variable_file_object = open(variable_file_path, 'rb')
    custom = self.portal.portal_skins.custom
    addStyleSheet = custom.manage_addProduct['OFSP'].manage_addFile
    if custom._getOb('Foo_getODTStyleSheet', None) is None:
      addStyleSheet(id='Foo_getODTStyleSheet', file=foo_file, title='',
                    content_type = 'application/vnd.oasis.opendocument.text')
    if custom._getOb('Foo2_getODTStyleSheet', None) is None:
      addStyleSheet(id='Foo2_getODTStyleSheet', file=foo2_file, title='',
                    content_type = 'application/vnd.oasis.opendocument.text')
    if custom._getOb('Foo3_getODTStyleSheet', None) is None:
      addStyleSheet(id='Foo3_getODTStyleSheet', file=foo3_file, title='',
                    content_type = 'application/vnd.oasis.opendocument.text')
    if custom._getOb('Foo4_getODTStyleSheet', None) is None:
      addStyleSheet(id='Foo4_getODTStyleSheet', file=foo4_file, title='',
                    content_type = 'application/vnd.oasis.opendocument.text')
    if custom._getOb('Foo5_getODTStyleSheet', None) is None:
      addStyleSheet(id='Foo5_getODTStyleSheet', file=foo5_file, title='',
                    content_type = 'application/vnd.oasis.opendocument.text')
    if custom._getOb('Foo_getVariableODTStyleSheet', None) is None:
      addStyleSheet(id='Foo_getVariableODTStyleSheet',
                    file=variable_file_object, title='',
                    content_type='application/vnd.oasis.opendocument.text')
    erp5OOo = custom.manage_addProduct['ERP5OOo']

    if custom._getOb('Foo_viewAsPrintout', None) is None:
      erp5OOo.addFormPrintout(id='Foo_viewAsPrintout', title='',
                              form_name='Foo_view', template='Foo_getODTStyleSheet')
    if custom._getOb('FooReport_viewAsPrintout', None) is None:
      erp5OOo.addFormPrintout(id='FooReport_viewAsPrintout',
                              title='')
    if custom._getOb('Foo5_viewAsPrintout', None) is None:
      erp5OOo.addFormPrintout(id='Foo5_viewAsPrintout', title='',
                              form_name='Foo_view', template='Foo5_getODTStyleSheet')

    ## append 'test1' data to a listbox
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    if test1._getOb("foo_1", None) is None:
      test1.newContent("foo_1", portal_type='Foo Line')
    if test1._getOb("foo_2", None) is None:
      test1.newContent("foo_2", portal_type='Foo Line')
    self.tic()

  def test_01_Paragraph(self):
    """
    mapping a field to a paragraph
    """
    portal = self.getPortal()
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    test1.setTitle('Foo title!')
    self.tic()

    # test target
    foo_printout = portal.foo_module.test1.Foo_viewAsPrintout
    self._validate(self.getODFDocumentFromPrintout(foo_printout))

    request = self.app.REQUEST
    # 1. Normal case: "my_title" field to the "my_title" reference in the ODF document
    self.portal.changeSkin('ODT')
    odf_document = foo_printout.index_html(REQUEST=request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Foo title!") > 0)
    self.assertEqual(request.RESPONSE.getHeader('content-type'),
                     'application/vnd.oasis.opendocument.text')
    self.assertEqual(request.RESPONSE.getHeader('content-disposition'),
                     'inline;filename="Foo_viewAsPrintout.odt"')
    self._validate(odf_document)
    pdf_document = foo_printout.index_html(REQUEST=request, format='pdf')
    self.assertEqual(request.RESPONSE.getHeader('content-type'),
                     'application/pdf')
    self.assertEqual(request.RESPONSE.getHeader('content-disposition'),
                     'attachment;filename="Foo_viewAsPrintout.pdf"')

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
    self.assertRaises(ValueError, foo_printout.index_html, request)
    # put back
    foo_printout.template = tmp_template

    # 5. Normal case: just call a FormPrintout object
    request.RESPONSE.setHeader('Content-Type', 'text/html')
    test1.setTitle("call!")
    odf_document = foo_printout(request, batch_mode=True) # call
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("call!") > 0)
    self.assertEqual(request.RESPONSE.getHeader('content-type'), 'text/html')
    self._validate(odf_document)

    # 5. Normal case: utf-8 string
    test1.setTitle("Français")
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français") > 0)
    self._validate(odf_document)

    # 6. Normal case: unicode string
    test1.setTitle(u'Français test2')
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français test2") > 0)
    self._validate(odf_document)

    # 7. Change Filename of downloadable file
    reference = 'My Reference'
    test1.setReference(reference)
    foo_printout.filename = 'here/getReference'
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertEqual(request.RESPONSE.getHeader('content-disposition'),
                     'inline;filename="%s.odt"' % reference)
    test1.setReference(None)

  def test_01_Paragraph_07_LinesField(self):
    """test LinesField into multi line"""
    foo_printout = self.portal.foo_module.test1.Foo_viewAsPrintout
    foo_form = self.portal.foo_module.test1.Foo_view
    if foo_form._getOb("week", None) is None:
      foo_form.manage_addField('week', 'week', 'LinesField')
    week = foo_form.week
    week.values['default'] = ['line1', 'line2']

    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    #test_output = open("/tmp/test_01_Paragraph_07_LinesField.odf", "w")
    #test_output.write(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    content_tree = etree.XML(content_xml)
    span_list = content_tree.xpath('//text:reference-mark-start[@text:name="week"]/following-sibling::text:span',
                                   namespaces=content_tree.nsmap)
    if span_list:
      self.assertEqual(1, len(span_list))
      span = span_list[0]
      self.assertEqual('line1', span.text)
      self.assertEqual('line2', span[0].tail)
    else:
      reference_mark_node = content_tree.xpath('//text:reference-mark-start[@text:name="week"][1]',
                                               namespaces=content_tree.nsmap)[0]
      self.assertEqual('line1', reference_mark_node.tail)
      self.assertEqual('line2', reference_mark_node.getnext().tail)
    self._validate(odf_document)

  def test_01_Paragraph_08_Field_Format(self):
    """test a field with format"""
    foo_printout = self.portal.foo_module.test1.Foo_viewAsPrintout
    foo_form = self.portal.foo_module.test1.Foo_view
    if foo_form._getOb("number", None) is None:
      foo_form.manage_addField('number', 'number', 'FloatField')
    number = foo_form.number
    number.values['default'] = '543210'
    # set a float field format
    number.values['input_style'] = '-1 234.5'
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    #test_output = open("/tmp/test_01_Paragraph_08_Filed_Format.odf", "w")
    #test_output.write(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    content = etree.XML(content_xml)
    self.assertTrue(content.xpath('//text:p[text() = "543 210.0"]', namespaces=content.nsmap))
    self._validate(odf_document)

    # change format
    number.values['input_style'] = '-1234.5'
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    content = etree.XML(content_xml)
    self.assertTrue(content.xpath('//text:p = "543210.0"', namespaces=content.nsmap))

    self._validate(odf_document)

  def test_01_Paragraph_09_RangeReferenceWithSpan(self):
    """test range reference and span setting"""
    foo_printout = self.portal.foo_module.test1.Foo_viewAsPrintout
    foo_form = self.portal.foo_module.test1.Foo_view
    if foo_form._getOb("my_test_title", None) is None:
      foo_form.manage_addField('my_test_title', 'test title', 'StringField')
    test_title = foo_form.my_test_title
    test_title.values['default'] = 'ZZZ test here ZZZ'

    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    #test_output = open("/tmp/test_01_Paragraph_09_RangeReferenceWithSpan.odf", "w")
    #test_output.write(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("ZZZ test here ZZZ") > 0)
    self.assertTrue(content_xml.find("test title") < 0)
    self._validate(odf_document)

  def test_02_Table_01_Normal(self):
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
    self.assertTrue('Set Successfully' in message)
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

  def test_02_Table_02_SmallerThanListboxColumns(self):
    """2. Irregular case: listbox columns count smaller than table columns count"""
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
    self.assertTrue('Set Successfully' in message)
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

  def test_02_Table_03_ListboxColumnsLargerThanTable(self):
    """3. Irregular case: listbox columns count larger than table columns count"""
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
    self.assertTrue('Set Successfully' in message)
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

  def test_02_Table_04_ListboxHasNotStat(self):
    """4. Irregular case: listbox has not a stat line, but table has a stat line"""
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
    self.assertTrue('Set Successfully' in message)
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

  def test_02_Table_05_NormalSameLayout(self):
    """5. Normal case: the listobx and the ODF table are same layout

    * Test Data Format:

     ODF table named 'listbox2'
     +-------------------------------+
     |  A    |   B   |   C   |   D   |
     |-------+-------+-------+-------|
     |       |       |       |       |
     +-------+-------+-------+-------+
    """
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
    self.assertTrue('Set Successfully' in message)
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
    content_tree = etree.XML(content_xml)
    #Check that foo_1 is inside table, with the same style
    xpath_style_name_expression = '//table:table[@table:name="listbox2"]/table:table-row/table:table-cell/text:p[starts-with(@text:style-name, "P")]'
    element_list = content_tree.xpath(xpath_style_name_expression, namespaces=content_tree.nsmap)
    self.assertEqual(len(element_list), 2)
    self.assertEqual(element_list[0].get('{%s}style-name' % content_tree.nsmap['text']),
                     element_list[1].get('{%s}style-name' % content_tree.nsmap['text']))
    self.assertEqual(['foo_1', 'foo_2'], [x.text for x in element_list])
    #Check that each listbox values are inside ODT table cells
    xpath_result_expression = '//table:table[@table:name="listbox2"]/table:table-row/table:table-cell/text:p/text()'
    self.assertEqual(['foo_1', 'foo_title_5', '0.0', 'foo_2', 'foo_2', '0.0', '1234.5'], content_tree.xpath(xpath_result_expression, namespaces=content_tree.nsmap))
    self.assertFalse(content_xml.find("foo_title_4") > 0)
    self._validate(odf_document)

    # put back the field name
    foo_form.manage_renameObject('listbox2', 'listbox', REQUEST=request)

  def test_02_Table_06_TableDoesNotHaveAHeader(self):
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
    self.assertTrue('Set Successfully' in message)
    listboxline_list = listbox3.get_value('default', render_format = 'list',
                                         REQUEST = request)
    self.assertEqual(len(listboxline_list), 4)
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_6")

    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_06_Table.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_title_5") > 0)
    self.assertTrue(content_xml.find("foo_title_6") > 0)
    self._validate(odf_document)

    # put back the field name
    foo_form.manage_renameObject('listbox3', 'listbox', REQUEST=request)

  def test_02_Table_07_CellFormat(self):
    """7. Normal case: make sure that it is enable to use ODF cell format setting in FormPrintout"""
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST
    request['here'] = test1

    test1.foo_1.setTitle('foo_title_7')
    test1.foo_1.setStartDate(DateTime(2009,4,20))
    message = listbox.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.assertTrue('Set Successfully' in message)
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

  def test_02_Table_08_Nodata(self):
    """8. Normal case: list box has no data"""
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
    self.assertTrue('Set Successfully' in message)
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

  def test_02_Table_09_StyleSetting(self):
    """ 9. Normal case: setting the style of the row.

     * Test Data format:
     The table listbox4 has six rows which contains the reference of the row.
    """
    # test target
    test1 = self.portal.foo_module.test1
    foo_printout = test1.Foo_viewAsPrintout
    foo_form = test1.Foo_view
    listbox = foo_form.listbox
    request = self.app.REQUEST
    request['here'] = test1

    for i in xrange(3, 7):
      foo_id = "foo_%s" % i
      if test1._getOb(foo_id, None) is None:
        test1.newContent(foo_id, portal_type='Foo Line')

    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'Foo_getRowCssList',
      '*args,**kw',
r"""
line_index = kw['list_index']
line_number = line_index + 1
for n in xrange(6, 0, -1):
  if line_number % n is 0:
    return "line" + str(n)
"""
      )

    foo_form.manage_renameObject('listbox', 'listbox4', REQUEST=request)
    listbox4 = foo_form.listbox4
    test1.foo_1.setTitle('foo_title_9')
    message = listbox4.ListBox_setPropertyList(
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_row_css_method = 'Foo_getRowCssList',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity',)
    self.assertTrue('Set Successfully' in message)
    listboxline_list = listbox4.get_value('default', render_format = 'list',
                                          REQUEST = request)
    self.assertEqual(len(listboxline_list), 7)
    self.assertTrue(listboxline_list[1].getColumnProperty('title') == "foo_title_9")

    ## test
    odf_document = foo_printout.index_html(REQUEST=request)
    #test_output = open("/tmp/test_02_Table_09_StyleSetting.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("foo_title_9") > 0)

    content = etree.XML(content_xml)
    table_row_xpath = '//table:table[@table:name="listbox4"]/table:table-row'
    table_row_list = content.xpath(table_row_xpath, namespaces=content.nsmap)
    self.assertEqual(len(table_row_list), 6)

    line2 = table_row_list[1]
    line2_cell_list = line2.xpath('table:table-cell', namespaces=content.nsmap)
    self.assertEqual(len(line2_cell_list), 2)
    line2_cell2 = line2_cell_list[1]
    span_attribute_name = '{%s}number-columns-spanned' % content.nsmap['table']
    line2_cell2_span = line2_cell2.attrib[span_attribute_name]
    self.assertEqual(line2_cell2_span, "2")

    line3 = table_row_list[2]
    line3_cell_list = line3.xpath('table:table-cell', namespaces=content.nsmap)
    self.assertEqual(len(line3_cell_list), 1)
    line3_cell1 = line3_cell_list[0]
    line3_cell1_span = line3_cell1.attrib[span_attribute_name]
    self.assertEqual(line3_cell1_span, "3")

    line5 = table_row_list[4]
    line5_cell_list = line5.xpath('table:table-cell', namespaces=content.nsmap)
    self.assertEqual(len(line5_cell_list), 2)
    line5_cell1 = line5_cell_list[0]
    line5_cell1_span = line5_cell1.attrib[span_attribute_name]
    self.assertEqual(line5_cell1_span, "2")

    self._validate(odf_document)

    # put back the field name
    foo_form.manage_renameObject('listbox4', 'listbox', REQUEST=request)
    # delete the test objects
    test1.manage_delObjects(['foo_3','foo_4','foo_5','foo_6'])

  def _test_03_Frame(self):
    """
    Frame not tested yet
    """

  def test_04_Iteration(self):
    """
    Iteration using ERP5Report ReportSection test
    """
    # create test target
    custom = self.portal.portal_skins.custom
    erp5form = custom.manage_addProduct['ERP5Form']
    erp5form.addERP5Report(id='FooReport_view', title='Foo Report')
    foo_report_view = custom.FooReport_view
    foo_report_view.report_method = 'FooReport_getReportSectionList'

    erp5form.addERP5Form(id='Foo2_view', title='Foo2')
    foo2_view = custom.Foo2_view
    foo2_view.manage_addField('listbox_report', 'listbox report', 'ListBox')
    listbox = foo2_view.listbox_report

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
      field_selection_name = 'listbox_report_selection',
      field_portal_types = 'Foo Line | Foo Line',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.assertTrue('Set Successfully' in message)
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
from Products.ERP5Form.Report import ReportSection

r1 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo2_view',
                   selection_name='listbox_report_selection',
                   selection_params={'title':'foo_04_Iteration_1'})
r2 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo2_view',
                   selection_name='listbox_report_selection',
                   selection_params={'title':'foo_04_Iteration_2'})
report_section_list = [r1, r2]
return report_section_list
"""
      )

    # 01. normal case using Frame
    test1 = self.portal.foo_module.test1
    foo_report_printout = test1.FooReport_viewAsPrintout
    foo_report_printout.doSettings(REQUEST=None,
                                   title='',
                                   form_name='FooReport_view',
                                   template='Foo2_getODTStyleSheet')
    self._validate(self.getODFDocumentFromPrintout(foo_report_printout))
    odf_document = foo_report_printout(self.portal.REQUEST)

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

    # 02. no report section using frame
    custom.manage_delObjects(['FooReport_getReportSectionList'])
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
return []
"""
      )
    odf_document = foo_report_printout(self.portal.REQUEST)
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


  def test_04_Iteration_02_Section(self):
    """
    Iteration using ERP5Report ReportSection and ODF Section test
    """
    # create test target
    custom = self.portal.portal_skins.custom
    erp5form = custom.manage_addProduct['ERP5Form']
    erp5form.addERP5Report(id='FooReport_view', title='Foo Report')
    foo_report_view = custom.FooReport_view
    foo_report_view.report_method = 'FooReport_getReportSectionList'

    erp5form.addERP5Form(id='Foo2_view', title='Foo2')
    foo2_view = custom.Foo2_view
    foo2_view.manage_addField('listbox_report', 'listbox report', 'ListBox')
    listbox = foo2_view.listbox_report

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
      field_selection_name = 'listbox_report_selection',
      field_portal_types = 'Foo Line | Foo Line',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.assertTrue('Set Successfully' in message)
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
from Products.ERP5Form.Report import ReportSection

r1 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo2_view',
                   selection_name='listbox_report_selection',
                   selection_params={'title':'foo_04_Iteration_1'})
r2 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo2_view',
                   selection_name='listbox_report_selection',
                   selection_params={'title':'foo_04_Iteration_2'})
report_section_list = [r1, r2]
return report_section_list
"""
       )

    # 01. normal case using ODF Section
    test1 = self.portal.foo_module.test1
    foo_report_printout = test1.FooReport_viewAsPrintout
    foo_report_printout.doSettings(REQUEST=None,
                                   title='',
                                   form_name='FooReport_view',
                                   template='Foo3_getODTStyleSheet')
    self._validate(self.getODFDocumentFromPrintout(foo_report_printout))
    odf_document = foo_report_printout(self.portal.REQUEST)

    #test_output = open("/tmp/test_04_Iteratoin_02_Section_01.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("foo_04_Iteration_1") > 0)
    content = etree.XML(content_xml)
    section_xpath = '//text:section[@text:name="FooReport_getReportSectionList"]'
    section_list = content.xpath(section_xpath, namespaces=content.nsmap)
    self.assertEqual(len(section_list), 1)
    section1_xpath = '//text:section[@text:name="FooReport_getReportSectionList_1"]'
    section1_list = content.xpath(section1_xpath, namespaces=content.nsmap)
    self.assertEqual(len(section1_list), 1)

    self._validate(odf_document)

    # 02. no report section and using ODF Section
    custom.manage_delObjects(['FooReport_getReportSectionList'])
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
return []
"""
      )
    odf_document = foo_report_printout(self.portal.REQUEST)
    #test_output = open("/tmp/test_04_Iteratoin_02_Section_02.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_04_Iteration") > 0)
    content = etree.XML(content_xml)
    section_xpath = '//text:section[@text:name="FooReport_getReportSectionList"]'
    section_list = content.xpath(section_xpath, namespaces=content.nsmap)
    # the section was removed
    self.assertEqual(len(section_list), 0)
    self._validate(odf_document)


  def test_04_Iteration_03_ReportBox_and_Section(self):
    """
    Iteration using ReportBox and ODF Section test
    """
    # create test target
    custom = self.portal.portal_skins.custom
    erp5form = custom.manage_addProduct['ERP5Form']

    erp5form.addERP5Form(id='Foo_Box_view', title='Foo Box')
    foo_box_view = custom.Foo_Box_view
    foo_box_view.manage_addField('listbox_report', 'listbox report', 'ListBox')
    listbox = foo_box_view.listbox_report

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
      field_selection_name = 'listbox_report_selection',
      field_portal_types = 'Foo Line | Foo Line',
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)
    self.assertTrue('Set Successfully' in message)

    # report box
    foo2_view = erp5form.addERP5Form(id='Foo2_view', title='Foo2 View')
    foo2_view = custom.Foo2_view
    foo2_view.manage_addField('your_report_box1', 'Your Report Box', 'ReportBox')
    your_report_box1 = foo2_view.your_report_box1
    your_report_box1._edit({'report_method':'FooReport_getReportSectionList'})

    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
from Products.ERP5Form.Report import ReportSection

r1 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo_Box_view',
                   selection_name='listbox_report_selection',
                   selection_params={'title':'foo_04_Iteration_1'})
r2 = ReportSection(path=context.getPhysicalPath(),
                   form_id='Foo_Box_view',
                   selection_name='listbox_report_selection',
                   selection_params={'title':'foo_04_Iteration_2'})
report_section_list = [r1, r2]
return report_section_list
"""
       )

    # 01. normal case using ODF Section
    test1 = self.portal.foo_module.test1
    request = self.app.REQUEST
    request['here'] = test1
    foo_report_printout = test1.FooReport_viewAsPrintout
    foo_report_printout.doSettings(REQUEST=request,
                                   title='',
                                   form_name='Foo2_view',
                                   template='Foo4_getODTStyleSheet')
    self._validate(self.getODFDocumentFromPrintout(foo_report_printout))
    odf_document = foo_report_printout(self.portal.REQUEST)

    # test_output = open("/tmp/test_04_Iteratoin_03_Section_01.odf", "w")
    # test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("foo_04_Iteration_1") > 0)
    content = etree.XML(content_xml)
    section_xpath = '//text:section[@text:name="your_report_box1"]'
    section_list = content.xpath(section_xpath, namespaces=content.nsmap)
    self.assertEqual(len(section_list), 1)
    section1_xpath = '//text:section[@text:name="your_report_box1_1"]'
    section1_list = content.xpath(section1_xpath, namespaces=content.nsmap)
    self.assertEqual(len(section1_list), 1)

    self._validate(odf_document)

    # 02. no report section and using ODF Section
    custom.manage_delObjects(['FooReport_getReportSectionList'])
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'FooReport_getReportSectionList',
      '',
r"""
return []
"""
      )
    odf_document = foo_report_printout(self.portal.REQUEST)
    #test_output = open("/tmp/test_04_Iteratoin_02_Section_02.odf", "w")
    #test_output.write(odf_document)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("foo_04_Iteration") > 0)
    content = etree.XML(content_xml)
    section_xpath = '//text:section[@text:name="your_report_box1"]'
    section_list = content.xpath(section_xpath, namespaces=content.nsmap)
    # the section was removed
    self.assertEqual(len(section_list), 0)
    self._validate(odf_document)

  def _test_05_Styles(self):
    """
    styles.xml not tested yet
    """

  def _test_06_Meta(self):
    """
    meta.xml not supported yet
    """

  def test_07_Image(self):
    """
    Image mapping not tested yet
    """
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    image_path = os.path.join(parent_dir,
                              'www',
                              'form_printout_icon.png')
    file_data = FileUpload(image_path)
    image = self.portal.newContent(portal_type='Image', id='test_image')
    image.edit(file=file_data)

    foo_printout = self.portal.foo_module.test1.Foo_viewAsPrintout
    foo_form = self.portal.foo_module.test1.Foo_view
    if foo_form._getOb("my_default_image_absolute_url", None) is None:
      foo_form.manage_addField('my_default_image_absolute_url', 'logo', 'ImageField')
    my_default_image_absolute_url = foo_form.my_default_image_absolute_url
    my_default_image_absolute_url.values['default'] = image.absolute_url_path()

    # 01: Normal
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    content = etree.XML(content_xml)
    image_frame_xpath = '//draw:frame[@draw:name="my_default_image_absolute_url"]'
    image_frame_list = content.xpath(image_frame_xpath, namespaces=content.nsmap)
    self.assertTrue(len(image_frame_list) > 0)
    image_frame = image_frame_list[0]
    height = image_frame.attrib['{%s}height' % content.nsmap['svg']]
    self.assertTrue(height in ('0.838cm', '0.3299in'))
    width = image_frame.attrib['{%s}width' % content.nsmap['svg']]
    self.assertTrue(width in ('0.838cm', '0.3299in'))
    self._validate(odf_document)

    # 02: no image data
    my_default_image_absolute_url.values['default'] = ''
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    # confirming the image was removed
    self.assertTrue(content_xml.find('<draw:image xlink:href') < 0)
    self._validate(odf_document)

  def test_08_OOoConversion(self):
    """test ooo conversion"""
    foo_printout = self.portal.foo_module.test1.Foo_viewAsPrintout
    foo_form = self.portal.foo_module.test1.Foo_view
    if foo_form._getOb("my_test_title", None) is None:
      foo_form.manage_addField('my_test_title', 'test title', 'StringField')
    test_title = foo_form.my_test_title
    test_title.values['default'] = 'ZZZ test here ZZZ'

    self.portal.REQUEST.set('format', 'pdf')
    printout = foo_printout(REQUEST=self.portal.REQUEST)
    #test_output = open("/tmp/test_99_OOoConversion.pdf", "w")
    #test_output.write(printout.data)
    self.assertEqual('application/pdf', guessMime(printout))

    self.portal.REQUEST.set('format', 'doc')
    printout = foo_printout(REQUEST=self.portal.REQUEST)
    #test_output = open("/tmp/test_99_OOoConversion.doc", "w")
    #test_output.write(printout.data)
    self.assertEqual('application/msword', guessMime(printout))

  def test_09_FieldReplacement(self, validate=False):
    """test field in ODF Documents"""
    foo_printout = self.portal.foo_module.test1.Foo5_viewAsPrintout
    if validate:
      self._validate(self.getODFDocumentFromPrintout(foo_printout))
    foo_form = self.portal.foo_module.test1.Foo_view
    field_name = 'your_checkbox'
    if foo_form._getOb(field_name, None) is None:
      foo_form.manage_addField(field_name, 'CheckBox', 'CheckBoxField')
    checkbox = getattr(foo_form, field_name)

    checkbox.values['default'] = 1
    odf_document = foo_printout(self.portal.REQUEST)
    if validate:
      self._validate(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    document_tree = etree.XML(content_xml)
    node = document_tree.xpath('//form:checkbox[@form:name = "%s"]' % field_name, namespaces=document_tree.nsmap)[0]
    self.assertTrue(node.get('{%s}current-state' % document_tree.nsmap['form']))

    checkbox.values['default'] = 0
    odf_document = foo_printout(self.portal.REQUEST)
    if validate:
      self._validate(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    document_tree = etree.XML(content_xml)
    node = document_tree.xpath('//form:checkbox[@form:name = "%s"]' % field_name, namespaces=document_tree.nsmap)[0]
    self.assertFalse(node.get('{%s}current-state' % document_tree.nsmap['form']))

  @skip('Disable validation because OOo does not produce compliant'\
        ' xml, and RelaxNG status is still draft')
  def test_09_FieldReplacementWithValidation(self):
    """
    """
    return self.test_09_FieldReplacement(validate=True)

  def test_field_replacement_with_variable(self):
    """test variables replacement in ODT documents.
    """
    document = self.portal.foo_module.test1
    document.setTitle(None)
    foo_form = document.Foo_view
    field_configuration_list = (
      ('my_string', 'StringField', 'ZZZ test here ZZZ'),
      ('my_figure', 'IntegerField', 221),
      ('my_float', 'FloatField', 23.43535),
      ('my_date', 'DateTimeField', DateTime('2010-12-6 23:24:15.234 GMT+6')),
      ('my_boolean', 'CheckBoxField', False),
      )
    for field_configuration in field_configuration_list:
      field_id, klass, value = field_configuration
      if foo_form._getOb(field_id, None) is not None:
        foo_form._delObject(field_id)
      foo_form.manage_addField(field_id, field_id, klass)
      field = foo_form[field_id]
      field.values['default'] = value
    foo_printout = self.portal.foo_module.test1.Foo_viewAsPrintout
    # Use template with variable defines
    foo_printout.template = 'Foo_getVariableODTStyleSheet'
    odf_document = foo_printout(self.portal.REQUEST)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    content_tree = etree.fromstring(content_xml)
    nsmap = content_tree.nsmap
    for field_configuration in field_configuration_list:
      field_id, klass, value = field_configuration
      xpath = '//text:variable-set[@text:name = "%s"]' % field_id
      node_list = content_tree.xpath(xpath, namespaces=nsmap)
      self.assertEqual(1, len(node_list))
      node = node_list[0]
      if klass == 'StringField':
        self.assertEqual(node.get('{%s}value-type' % nsmap['office']),
                          'string')
        self.assertEqual(node.text, value)
      elif klass in ('IntegerField', 'FloatField'):
        self.assertEqual(node.get('{%s}value-type' % nsmap['office']),
                          'float')
        self.assertEqual(node.get('{%s}value' % nsmap['office']), str(value))
      elif klass == 'DateTimeField':
        self.assertEqual(node.get('{%s}value-type' % nsmap['office']), 'date')
        self.assertEqual(node.text, '06/12/2010 23:24:15')
      elif klass == 'CheckBoxField':
        self.assertEqual(node.get('{%s}value-type' % nsmap['office']),
                          'boolean')
        self.assertEqual(node.get('{%s}boolean-value' % nsmap['office']),
                          'false')
        self.assertEqual(node.text, 'FALSE')
      else:
        raise NotImplementedError

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFormPrintoutAsODT))
  return suite
