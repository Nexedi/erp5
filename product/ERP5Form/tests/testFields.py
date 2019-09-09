# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

# TODO: Some tests from this file can be merged into Formulator

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import unittest

# Initialize ERP5Form Product to load monkey patches

from Acquisition import aq_base
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.Validator import ValidationError
from Products.Formulator.StandardFields import FloatField, StringField,\
DateTimeField, TextAreaField, CheckBoxField, ListField, LinesField, \
MultiListField, IntegerField
from Products.Formulator.MethodField import Method, BoundMethod
from Products.Formulator.TALESField import TALESMethod

from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Form.Form import ERP5Form
from Products.ERP5Form.Form import field_value_cache
from Products.ERP5Form.Form import getFieldValue
from Products.ERP5Form import ProxyField
from DateTime import DateTime

from Products.Formulator.Widget import NSMAP
ODG_XML_WRAPPING_XPATH = 'draw:text-box/text:p/text:span'

class TestRenderViewAPI(ERP5TypeTestCase):
  """For all fields and widgets, tests the signature of the render_view method.
  In particular, render_view must accept a 'REQUEST' parameter after 'value'.
  """

  def getTitle(self):
    return "{Field,Widget}.render_view"

  def test_signature(self):
    for field in FieldRegistry.get_field_classes().itervalues():
      self.assertEqual(('self', 'value', 'REQUEST', 'render_prefix'),
                        field.render_view.im_func.func_code.co_varnames)
      if field is not ProxyField.ProxyField:
        self.assertEqual(('self', 'field', 'value', 'REQUEST'),
          field.widget.render_view.im_func.func_code.co_varnames[:4], '%s %s' % (field.widget, field.widget.render_view.im_func.func_code.co_varnames[:4]))


class TestFloatField(ERP5TypeTestCase):
  """Tests Float field
  """

  def getTitle(self):
    return "Float Field"

  def afterSetUp(self):
    self.field = FloatField('test_field')
    self.widget = self.field.widget
    self.validator = self.field.validator

  def test_format_thousand_separator_point(self):
    self.field.values['input_style'] = '-1 234.5'
    self.assertEqual('1 000.0', self.widget.format_value(self.field, 1000))

  def test_format_thousand_separator_coma(self):
    self.field.values['input_style'] = '-1 234,5'
    self.assertEqual('1 000,0', self.widget.format_value(self.field, 1000))

  def test_format_thousand_separator_point_coma(self):
    self.field.values['input_style'] = '-1.234,5'
    self.assertEqual('1.000,0', self.widget.format_value(self.field, 1000))

  def test_format_thousand_separator_coma_point(self):
    self.field.values['input_style'] = '-1,234.5'
    self.assertEqual('1,000.0', self.widget.format_value(self.field, 1000))

  def test_format_thousand_separator_first_separator(self):
    # test for an edge case bug bug, ",100,000.0" was displayed (with leading coma)
    self.field.values['input_style'] = '-1,234.5'
    self.assertEqual('100,000.0', self.widget.format_value(self.field, 100000))
    self.assertEqual('-100,000.0', self.widget.format_value(self.field, -100000))

  def test_format_with_separator_and_precision0(self):
    self.field.values['input_style'] = '-1,234.5'
    self.field.values['precision'] = 0
    self.assertEqual('-1,000', self.widget.format_value(self.field, -1000.25))
    self.assertEqual('-1,000', self.widget.format_value(self.field, -1000.49))
    self.assertEqual('-1,001', self.widget.format_value(self.field, -1000.99))
    self.assertEqual('-1,001', self.widget.format_value(self.field, -1000.80))
    self.assertEqual('-1,001', self.widget.format_value(self.field, -1000.70))
    self.assertEqual('-1,001', self.widget.format_value(self.field, -1000.60))
    self.assertEqual('-1,001', self.widget.format_value(self.field, -1000.59))
    self.assertEqual('-1,001', self.widget.format_value(self.field, -1000.51))
    # this is not -1,001 (is this a specification?)
    self.assertEqual('-1,000', self.widget.format_value(self.field, -1000.50))

  def test_format_percent_style(self):
    self.field.values['input_style'] = '-12.3%'
    self.assertEqual('10.0%', self.widget.format_value(self.field, 0.1))

  def test_format_precision(self):
    self.field.values['precision'] = 0
    self.assertEqual('12', self.widget.format_value(self.field, 12.34))
    # value is rounded
    self.assertEqual('13', self.widget.format_value(self.field, 12.9))

    field_value_cache.clear() # call this before changing internal field values.
    self.field.values['precision'] = 2
    self.assertEqual('0.01', self.widget.format_value(self.field, 0.011))
    # value is rounded
    self.assertEqual('0.01', self.widget.format_value(self.field, 0.009999))
    self.assertEqual('1.00',
        self.widget.format_value(self.field, sum([0.1] * 10)))
    self.assertEqual('566.30',
        self.widget.format_value(self.field, 281.80 + 54.50 + 230.00))

  def test_format_no_precision(self):
    self.assertEqual('7.2', self.widget.format_value(self.field, 7.2))
    self.assertEqual('0.009999', self.widget.format_value(self.field, 0.009999))
    self.assertEqual('1000.0', self.widget.format_value(self.field, 1000))

  def test_render_view(self):
    self.field.values['input_style'] = '-1 234.5'
    self.field.values['precision'] = 2
    self.field.values['editable'] = 0
    self.assertEqual('1&nbsp;000.00', self.field.render(1000))

  def test_render_dict(self):
    self.field.values['input_style'] = '-1 234.5'
    self.field.values['precision'] = 4
    self.assertEqual(dict(query=0.12345,
                           format='0.0000',
                           type='float'),
                      self.field.render_dict(0.12345))
    # this also work when using , as decimal separator
    self.field.values['input_style'] = '-1.234,5'
    self.assertEqual(dict(query=0.12345,
                           format='0.0000',
                           type='float'),
                      self.field.render_dict(0.12345))

  def test_render_string_value(self):
    self.field.values['precision'] = 2
    self.field.values['editable'] = 0
    self.assertEqual('12.34', self.field.render("12.34"))
    self.assertEqual('not float', self.field.render("not float"))

  def test_percent_style_render_string_value(self):
    self.field.values['input_style'] = '-12.3%'
    self.field.values['editable'] = 0
    self.assertEqual('-12.34%', self.field.render("-0.1234"))
    self.assertEqual('not float', self.field.render("not float"))

  def test_render_big_numbers(self):
    self.field.values['precision'] = 2
    self.field.values['editable'] = 0
    self.assertEqual('10000000000000.00',
                      self.field.render(10000000000000))
    self.assertEqual('1e+20', self.field.render(1e+20))

  def test_validate_thousand_separator_point(self):
    self.field.values['input_style'] = '-1 234.5'
    self.portal.REQUEST.set('field_test_field', '1 000.0')
    self.assertEqual(1000,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))

  def test_validate_thousand_separator_coma(self):
    self.field.values['input_style'] = '-1 234,5'
    self.portal.REQUEST.set('field_test_field', '1 000,0')
    self.assertEqual(1000,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))

  def test_validate_thousand_separator_point_coma(self):
    self.field.values['input_style'] = '-1.234,5'
    self.portal.REQUEST.set('field_test_field', '1.000,0')
    self.assertEqual(1000,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))

  def test_validate_thousand_separator_coma_point(self):
    self.field.values['input_style'] = '-1,234.5'
    self.portal.REQUEST.set('field_test_field', '1,000.0')
    self.assertEqual(1000,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))

  def test_validate_percent_style(self):
    self.field.values['input_style'] = '-12.3%'
    self.portal.REQUEST.set('field_test_field', '10.0%')
    self.assertEqual(0.1,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))

  def test_validate_not_float(self):
    self.portal.REQUEST.set('field_test_field', 'not_float')
    self.assertRaises(ValidationError,
        self.validator.validate, self.field, 'field_test_field', self.portal.REQUEST)

  def test_validate_two_comma(self):
    self.field.values['input_style'] = '-1.234,5'
    self.portal.REQUEST.set('field_test_field', '1,000,0')
    self.assertRaises(ValidationError,
        self.validator.validate, self.field, 'field_test_field', self.portal.REQUEST)

  def test_validate_two_dots(self):
    self.field.values['input_style'] = '-1,234.5'
    self.portal.REQUEST.set('field_test_field', '1.000.0')
    self.assertRaises(ValidationError,
        self.validator.validate, self.field, 'field_test_field', self.portal.REQUEST)

  def test_validate_precision0(self):
    # Check the consistency among the precision and user inputs
    self.field.values['input_style'] = '-1,234.5'
    self.field.values['precision'] = 0
    self.portal.REQUEST.set('field_test_field', '1.00')
    self.assertRaises(ValidationError,
      self.validator.validate, self.field, 'field_test_field',
      self.portal.REQUEST)

  def test_validate_precision0_with_percent(self):
    # Check the precision and user inputs when the style is '%'
    self.field.values['input_style'] = '-12.5%'
    self.field.values['precision'] = 1
    self.assertEqual('12.5%', self.widget.format_value(self.field, 0.125))
    self.portal.REQUEST.set('field_test_field', '0.1255')
    self.assertRaises(ValidationError,
      self.validator.validate, self.field, 'field_test_field',
      self.portal.REQUEST)

  def test_render_odt(self):
    self.field.values['input_style'] = '-1 234.5'
    self.field.values['default'] = 1000
    self.assertEqual('1 000.0', self.field.render_odt(as_string=False).text)

  def test_render_odg(self):
    self.field.values['input_style'] = '-1 234.5'
    self.field.values['default'] = 1000
    test_value = self.field.render_odg(as_string=False)\
      .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0]
    self.assertEqual('1 000.0', test_value)

  def test_render_odt_variable(self):
    self.field.values['default'] = 1000.0
    node = self.field.render_odt_variable(as_string=False)
    self.assertEqual(node.get('{%s}value-type' % NSMAP['office']), 'float')
    self.assertEqual(node.get('{%s}value' % NSMAP['office']), str(1000.0))

  def test_fullwidth_number_conversion(self):
    self.portal.REQUEST.set('field_test_field', '１2３．４5')
    self.assertEqual(123.45,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))

  def test_fullwidth_minus_number_conversion(self):
    self.portal.REQUEST.set('field_test_field', '−１2３．４5')
    self.assertEqual(-123.45,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))


class TestIntegerField(ERP5TypeTestCase):
  """Tests integer field
  """

  def getTitle(self):
    return "Integer Field"

  def afterSetUp(self):
    self.field = IntegerField('test_field')
    self.widget = self.field.widget
    self.validator = self.field.validator

  def test_render_odt(self):
    self.field.values['default'] = 34
    self.assertEqual('34', self.field.render_odt(as_string=False).text)

  def test_render_odt_variable(self):
    value = 34
    self.field.values['default'] = value
    node = self.field.render_odt_variable(as_string=False)
    self.assertEqual(node.get('{%s}value-type' % NSMAP['office']), 'float')
    self.assertEqual(node.get('{%s}value' % NSMAP['office']), str(value))
    self.assertEqual(node.text, str(value))
    self.assertTrue('{%s}formula' % NSMAP['text'] not in node.attrib)

  def test_render_odg_view(self):
    self.field.values['default'] = 34
    test_value = self.field.render_odg(as_string=False)\
      .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0]
    self.assertEqual('34', test_value)
    test_value = self.field.render_odg(value=0, as_string=False)\
      .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0]
    self.assertEqual('0', test_value)

  def test_fullwidth_number_conversion(self):
    self.portal.REQUEST.set('field_test_field', '１２３４')
    self.assertEqual(1234,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))

  def test_fullwidth_minus_number_conversion(self):
    self.portal.REQUEST.set('field_test_field', 'ー１２３４')
    self.assertEqual(-1234,
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))


class TestStringField(ERP5TypeTestCase):
  """Tests string field
  """

  def getTitle(self):
    return "String Field"

  def afterSetUp(self):
    self.field = StringField('test_field')
    self.widget = self.field.widget

  def test_escape_html(self):
    self.field.values['editable'] = 0
    self.assertEqual('&lt;script&gt;', self.field.render("<script>"))

  def test_render_odt(self):
    self.field.values['default'] = 'Hello World! <&> &lt;&mp;&gt;'
    self.assertEqual('Hello World! <&> &lt;&mp;&gt;', self.field.render_odt(as_string=False).text)
    self.assertEqual('Hello World!', self.field.render_odt(value='Hello World!', as_string=False).text)

  def test_render_odg(self):
    self.field.values['default'] = 'Hello World! <&> &lt;&mp;&gt;'
    test_value = self.field.render_odg(as_string=False)\
      .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0]
    self.assertEqual('Hello World! <&> &lt;&mp;&gt;', test_value)
    test_value = self.field.render_odg(value='Hello World!', as_string=False)\
      .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0]
    self.assertEqual('Hello World!', test_value)

  def test_render_odt_variable(self):
    self.field.values['default'] = 'Hello World! <&> &lt;&mp;&gt;'
    node = self.field.render_odt_variable(as_string=False)
    self.assertEqual(node.get('{%s}value-type' % NSMAP['office']), 'string')
    self.assertEqual(node.text, 'Hello World! <&> &lt;&mp;&gt;')

class TestDateTimeField(ERP5TypeTestCase):
  """Tests DateTime field
  """

  def getTitle(self):
    return "DateTime Field"

  def afterSetUp(self):
    self.field = DateTimeField('test_field')
    self.widget = self.field.widget
    self.validator = self.field.validator

  def test_render_odt(self):
    self.field.values['default'] = DateTime('2010/01/01 00:00:01 UTC')
    self.assertEqual('2010/01/01   00:00',
            self.field.render_odt(as_string=False).text)

  def test_render_odg(self):
    self.field.values['default'] = DateTime('2010/01/01 00:00:01 UTC')
    self.field.render_odg(as_string=False)
    self.assertEqual('2010/01/01   00:00',
                      self.field.render_odg(as_string=False)\
             .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0])

  def test_render_odt_variable(self):
    value = DateTime(2010, 12, 06, 10, 23, 32, 'GMT+5')
    self.field.values['default'] = value
    node = self.field.render_odt_variable(as_string=False)
    self.assertEqual(node.get('{%s}value-type' % NSMAP['office']), 'date')
    self.assertEqual(node.get('{%s}date-value' % NSMAP['office']),
                      value.ISO8601())
    self.field.values['default'] = None
    node = self.field.render_odt_variable(as_string=False)
    self.assertTrue(node is not None)

  def test_fullwidth_number_conversion(self):
    self.portal.REQUEST.set('subfield_field_test_field_year', '２０１１')
    self.portal.REQUEST.set('subfield_field_test_field_month', '１２')
    self.portal.REQUEST.set('subfield_field_test_field_day', '１５')
    self.portal.REQUEST.set('subfield_field_test_field_hour', '０２')
    self.portal.REQUEST.set('subfield_field_test_field_minute', '１８')
    self.assertEqual(DateTime('2011/12/15 02:18:00'),
        self.validator.validate(self.field, 'field_test_field', self.portal.REQUEST))


class TestTextAreaField(ERP5TypeTestCase):
  """Tests TextArea field
  """

  def getTitle(self):
    return "TextArea Field"

  def afterSetUp(self):
    self.field = TextAreaField('test_field')
    self.widget = self.field.widget

  def test_render_view(self):
    self.field.values['default'] = 'My first Line\n&My Second Line\tfoo'
    self.assertEqual('<div  >My first Line<br/><br/>&amp;My Second Line\tfoo</div>',
                      self.field.render_view(value=['My first Line\n', '&My Second Line\tfoo']))
    editable_mode = self.portal.REQUEST.get('editable_mode', 1)
    self.portal.REQUEST.set('editable_mode', 0)
    try:
      self.assertEqual('<div  >My first Line<br/>&amp;My Second Line\tfoo</div>',
                        self.field.render(REQUEST=self.portal.REQUEST))
    finally:
      self.portal.REQUEST.set('editable_mode', editable_mode)

  def test_render_odt(self):
    self.field.values['default'] = 'My first Line\nMy Second Line\tfoo'
    self.assertEqual('text:line-break',
        self.field.render_odt(as_string=False)[0].xpath('name()'))
    self.assertEqual('text:tab',
        self.field.render_odt(as_string=False)[1].xpath('name()'))

  def test_render_odg(self):
    self.field.values['default'] = 'My first Line\nMy Second Line\tfoo'
    test_value = self.field.render_odg(as_string=False)\
      .xpath('%s/text:line-break' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)
    self.assertTrue(test_value)
    test_value = self.field.render_odg(as_string=False)\
      .xpath('%s/text:tab' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)
    self.assertTrue(test_value)

class TestLinesField(ERP5TypeTestCase):

  def getTitle(self):
    return "Lines Field"

  def afterSetUp(self):
    self.field = LinesField('test_field')
    self.widget = self.field.widget

  def test_render_view(self):
    self.assertEqual(self.field.render_view(value=['My first Line\n', '&My Second Line\tfoo']),
                      '<div  >My first Line<br />\n<br />\n&amp;My Second Line\tfoo</div>')

  def test_render_odt(self):
    self.field.values['default'] = ['A', 'B']
    self.assertEqual('{%(text)s}p' % NSMAP,
                      self.field.render_odt(as_string=False).tag)

  def test_render_odt_view(self):
    self.field.values['default'] = ['A', 'B']
    element = self.field.render_odt(as_string=False,
                                    REQUEST=self.portal.REQUEST)
    self.assertEqual('{%(text)s}p' % NSMAP, element.tag)
    # separated by text:line-break
    self.assertEqual('{%(text)s}line-break' % NSMAP, element[0].tag)
    self.assertEqual(['A', 'B'], [x for x in element.itertext()])


class TestCheckBoxField(ERP5TypeTestCase):
  """Tests TextArea field
  """

  def getTitle(self):
    return "CheckBox Field"

  def afterSetUp(self):
    self.field = CheckBoxField('test_field')
    self.widget = self.field.widget

  def test_render_odt(self):
    self.field.values['default'] = 1
    self.assertEqual('{%(form)s}checkbox' % NSMAP,
                      self.field.render_odt(as_string=False).tag)

  def test_render_odt_view(self):
    self.field.values['default'] = 1
    self.portal.REQUEST.set('editable_mode', 0)
    self.assertEqual('{%(text)s}p' % NSMAP,
                      self.field.render_odt(as_string=False, REQUEST=self.portal.REQUEST).tag)
    self.assertEqual('1', self.field.render_odt(as_string=False, REQUEST=self.portal.REQUEST).text)

  def test_render_odt_variable(self):
    for value in (True, False,):
      self.field.values['default'] = value
      node = self.field.render_odt_variable(as_string=False)
      self.assertEqual(node.get('{%s}value-type' % NSMAP['office']),
                            'boolean')
      self.assertEqual(node.get('{%s}boolean-value' % NSMAP['office']),
                        str(value).lower())
      self.assertEqual(node.text, str(value).upper())

  def test_render_odg_view(self):
    """Like integer field
    return 1 or 0
    """
    self.field.values['default'] = 1
    self.portal.REQUEST.set('editable_mode', 0)
    test_value = self.field.render_odg(as_string=False)\
      .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0]
    self.assertEqual('1', test_value)
    test_value = self.field.render_odg(value=0, as_string=False)\
      .xpath('%s/text()' % ODG_XML_WRAPPING_XPATH, namespaces=NSMAP)[0]
    self.assertEqual('0', test_value)

class TestListField(ERP5TypeTestCase):
  """Tests List field
  """

  def getTitle(self):
    return "List Field"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return (
      'erp5_core_proxy_field_legacy',
      'erp5_base',
    )

  def afterSetUp(self):
    self.field = ListField('test_field')
    self.widget = self.field.widget
    self.createCategories()
    self.tic()

  def createCategories(self):
    """Create some categories into gender
    """
    category_tool = self.portal.portal_categories
    if len(category_tool.gender.contentValues()) == 0 :
      category_tool.gender.newContent(portal_type='Category',
                                      id='male',
                                      title='Male',
                                      int_index=1)
      category_tool.gender.newContent(portal_type='Category',
                                      id='female',
                                      title='Female',
                                      int_index=2)

  def test_render_odt(self):
    items = [('My first Line', '1'), ('My Second Line', '2')]
    self.field.values['items'] = items
    self.field.values['default'] = '2'
    element = self.field.render_odt(as_string=False)
    self.assertEqual('{%(text)s}p' % NSMAP, element.tag)
    self.assertEqual('My Second Line', element.text)

    # values not in items are displayed with ???
    self.field.values['default'] = '3'
    element = self.field.render_odt(as_string=False)
    self.assertEqual('??? (3)', element.text)


  def test_listField_value_order(self):
    '''This test check the list field value order
    '''
    # create a form with a list_field that use gender category
    portal_skins = self.getSkinsTool()
    skin_folder = portal_skins._getOb('custom')
    skin_folder.manage_addProduct['ERP5Form'].addERP5Form(
        'Base_viewTestFieldValueOrder',
        'View')
    form = skin_folder._getOb('Base_viewTestFieldValueOrder', None)

    # The field is a proxyfield on Base_viewFieldLibrary.my_category that
    # category should be sort on int_index and translated_id
    form.manage_addField('my_gender', 'Test List Field',
        'ProxyField')
    field = getattr(form, 'my_gender')
    field.manage_edit_xmlrpc(dict(
    form_id='Base_viewFieldLibrary', field_id='my_category'))

    category_item_list = field.get_value('items')
    self.assertEqual(category_item_list,
        [['', ''], ['Male', 'male'], ['Female', 'female']])

    # try on a person to select on gender and check if the result is the same
    person_module = self.portal.getDefaultModule('Person')
    person = person_module.newContent(portal_type='Person')
    person.setGender('female')
    self.assertEqual(person.getGender(), 'female')
    self.assertEqual(person.Person_view.my_gender.get_value('items'),
        [['', ''], ['Male', 'male'], ['Female', 'female']])


class TestMultiListField(ERP5TypeTestCase):

  def afterSetUp(self):
    self.field = MultiListField('test_field')
    self.widget = self.field.widget
    self.field.values['items'] = [('A', 'a',), ('B', 'b')]
    self.field.values['default'] = ['a', 'b']

  def test_render_view(self):
    self.assertEqual('A<br />\nB', self.field.render_view(value=['a', 'b']))

  def test_render_odt(self):
    element = self.field.render_odt(as_string=False)
    self.assertEqual('{%(text)s}p' % NSMAP, element.tag)
    # separated by text:line-break
    self.assertEqual('{%(text)s}line-break' % NSMAP, element[0].tag)
    self.assertEqual(['A', 'B'], [x for x in element.itertext()])

  def test_render_odt_view(self):
    element = self.field.render_odt_view(as_string=False,
                                        value=['a', 'b'],
                                        REQUEST=self.portal.REQUEST)
    self.assertEqual('{%(text)s}p' % NSMAP, element.tag)
    # separated by text:line-break
    self.assertEqual('{%(text)s}line-break' % NSMAP, element[0].tag)
    self.assertEqual(['A', 'B'], [x for x in element.itertext()])

    # values not in items are displayed with ???
    element = self.field.render_odt_view(as_string=False,
                                        value=['other'],
                                        REQUEST=self.portal.REQUEST)
    self.assertEqual('{%(text)s}p' % NSMAP, element.tag)
    self.assertEqual('??? (other)', element.text)

class TestProxyField(ERP5TypeTestCase):

  def getTitle(self):
    return "Proxy Field"

  def afterSetUp(self):
    self.container = Folder('container').__of__(self.portal)
    self.container._setObject('Base_viewProxyFieldLibrary',
                               ERP5Form('Base_viewProxyFieldLibrary', 'Proxys'))
    self.container._setObject('Base_view',
                               ERP5Form('Base_view', 'View'))


  def addField(self, form, id, title, field_type):
    form.manage_addField(id, title, field_type)
    field = getattr(form, id)
    field._p_oid = makeDummyOid()
    return field

  def test_get_template_field(self):
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Not Title', 'ProxyField')
    self.assertEqual(None, proxy_field.getTemplateField())
    self.assertEqual(None, proxy_field.get_value('enable'))
    self.assertEqual(None, proxy_field.get_value('default'))

    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEqual(original_field, proxy_field.getTemplateField())

  def test_simple_surcharge(self):
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    self.assertEqual('Title', original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Not Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assert_(proxy_field.is_delegated('title'))
    self.assertEqual('Title', proxy_field.get_value('title'))

  def test_simple_not_surcharge(self):
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    self.assertEqual('Title', original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Proxy Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    # XXX no API for this ?
    proxy_field._surcharged_edit(dict(title='Proxy Title'), ['title'])

    self.assertFalse(proxy_field.is_delegated('title'))
    self.assertEqual('Proxy Title', proxy_field.get_value('title'))

  def test_get_value_default(self):
    # If the proxy field is named 'my_id', it will get 'id'
    # property on the context, regardless of the id of the proxified field
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    proxy_field = self.addField(self.container.Base_view,
                                'my_id', 'ID', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEqual('container', self.container.getId())
    self.assertEqual('container', proxy_field.get_value('default'))

  def test_field_tales_context(self):
    # in the TALES context, "field" will be the proxyfield, not the original
    # field.
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    original_field.manage_tales_xmlrpc(dict(title='field/getId'))
    self.assertEqual('my_title', original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_reference', 'Not Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    # 'my_reference' is the ID of the proxy field
    self.assertEqual('my_reference', proxy_field.get_value('title'))

  def test_form_tales_context(self):
    # in the TALES context, "form" will be the form containing the proxyfield,
    # not the original form (ie. the field library).
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    original_field.manage_tales_xmlrpc(dict(title='form/getId'))
    self.assertEqual('Base_viewProxyFieldLibrary',
                       original_field.get_value('title'))

    proxy_field = self.addField(self.container.Base_view,
                                'my_title', 'Title', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_title',))
    self.assertEqual('Base_view', proxy_field.get_value('title'))

  def test_get_value_cache_on_TALES_target(self):
    # If the proxy field defines its target using TALES, then no caching should
    # happen.
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'Title', 'StringField')
    other_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_other_field', 'Other', 'StringField')
    proxy_field = self.addField(self.container.Base_view,
                                'my_id', 'ID', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary'))
    proxy_field.manage_tales_xmlrpc(dict(field_id='request/field_id'))

    self.container.REQUEST.set('field_id', 'my_title')
    self.assertEqual(original_field, proxy_field.getTemplateField())
    self.assertEqual('Title', proxy_field.get_value('title'))

    self.container.REQUEST.set('field_id', 'my_other_field')
    self.assertEqual(other_field, proxy_field.getTemplateField())
    self.assertEqual('Other', proxy_field.get_value('title'))

  def test_proxy_to_date_time_field(self):
    # date time fields are specific, because they use a 'sub_form', we must
    # make sure this works as expected
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_date', 'Date', 'DateTimeField')
    original_field.manage_edit_xmlrpc(dict(required=0))
    proxy_field = self.addField(self.container.Base_view,
                                'my_date', 'Date', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_date',))
    self.assertTrue(hasattr(proxy_field, '_get_sub_form'))
    self.assertEqual(proxy_field._get_sub_form().render(),
                     original_field._get_sub_form().render())

    # we can render
    proxy_field.render()
    # and validate
    self.container.Base_view.validate_all_to_request(self.portal.REQUEST)

    # change style in the original field
    original_field.manage_edit_xmlrpc(dict(input_style='number'))
    self.assertTrue('type="number"' in original_field.render())
    self.assertTrue('type="number"' in proxy_field.render())

    # override style in the proxy field
    original_field.manage_edit_xmlrpc(dict(input_style='text'))
    proxy_field._surcharged_edit({'input_style': 'number'}, ['input_style'])
    self.assertTrue('type="text"' in original_field.render())
    self.assertTrue('type="number"' in proxy_field.render())

    # unproxify the proxy field
    self.container.Base_view.unProxifyField({'my_date': 'on'})
    unproxified_field = self.container.Base_view.my_date
    self.assertTrue('type="number"' in unproxified_field.render())

  def test_manage_edit_surcharged_xmlrpc(self):
    # manage_edit_surcharged_xmlrpc is a method to edit proxyfields
    # programmatically
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_string', 'String', 'StringField')
    proxy_field = self.addField(self.container.Base_view,
                                'my_String', '', 'ProxyField')
    proxy_field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                        field_id='my_date',))

    proxy_field.manage_edit_surcharged_xmlrpc(dict(title='Title'))
    self.assertFalse(proxy_field.is_delegated('title'))
    self.assertEqual('Title', proxy_field.get_value('title'))

    # beware that all values that are not passed in the mapping will be
    # delegated again, regardless of the old state.
    proxy_field.manage_edit_surcharged_xmlrpc({})
    self.assertTrue(proxy_field.is_delegated('title'))

  def test_same_field_id_in_proxy_field_and_template_field(self):
    """
    Test a case that if proxy field id is same as template field id.
    """
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_string', 'String', 'StringField')
    # Use different id to the template field.
    proxy_field2 = self.addField(self.container.Base_view,
                                 'my_another_string', '', 'ProxyField')
    # Use same id to the template field.
    proxy_field1 = self.addField(self.container.Base_view,
                                 'my_string', '', 'ProxyField')
    proxy_field2.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                         field_id='my_string',))
    proxy_field1.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                         field_id='my_string',))

    def make_dummy_getter(value):
      def method():
        return value
      return method

    self.container.getAnotherString = make_dummy_getter('WAAA')
    self.container.getString = make_dummy_getter('123')

    # First, call field which the id is different to the template field's.
    self.assertEqual('WAAA', proxy_field2.get_value('default'))

    # Next, call field which the id is same to the template field's.
    self.assertEqual('123', proxy_field1.get_value('default'))

  def test_dicts_cleared_on_edit(self):
    """
    Test that values and tales dicts are cleared when property is switched to
    not surcharged.
    """
    # create a field
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'OrigTitle', 'StringField')
    field = self.addField(self.container.Base_view,
                                   'my_dict_test', '', 'ProxyField')
    field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                         field_id='my_title',))
    def surcharge_edit():
      #surcharge from edit
      field._surcharged_edit(dict(title='TestTitle'), ['title'])
      self.assertTrue('title' in field.delegated_list)
      self.assertEqual(field.values['title'], 'TestTitle')
      self.assertTrue('title' not in field.tales)

    def delegate_edit():
      # delegate the field from edit view
      field._surcharged_edit(dict(title='TestTitle'), [])
      self.assertTrue('title' not in field.delegated_list)
      self.assertTrue('title' not in field.values)
      self.assertTrue('title' not in field.tales)

    def surcharge_tales():
      #surcharge from tales
      field._surcharged_tales(dict(title='string:TestTitle'), ['title'])
      self.assertTrue('title' in field.delegated_list)
      self.assertTrue(field.values['title'], 'OrigTitle')
      self.assertEqual(field.tales['title'], 'string:TestTitle')

    def delegate_tales():
      # delegate the field from tales view
      field._surcharged_tales(dict(title='string:TestTitle'), [])
      self.assertTrue('title' not in field.delegated_list)
      self.assertTrue('title' not in field.values)
      self.assertTrue('title' not in field.tales)

    surcharge_edit()
    delegate_edit()
    surcharge_edit()
    delegate_tales()
    surcharge_tales()
    delegate_edit()
    surcharge_tales()
    delegate_tales()

  def test_proxify_error_message(self):
    """
    Test that error messages can be delegated and surcharged.
    """
    # create a field
    original_field = self.addField(self.container.Base_viewProxyFieldLibrary,
                                   'my_title', 'OrigTitle', 'StringField')
    field = self.addField(self.container.Base_view,
                                   'my_dict_test', '', 'ProxyField')
    field.manage_edit_xmlrpc(dict(form_id='Base_viewProxyFieldLibrary',
                                         field_id='my_title',))
    self.assertEqual(original_field.get_error_names(),
        field.get_error_names())
    test_error = 'too_long' # arbitrary chosen among StringField error names
    test_message = 'Some Unprobable Error'
    test_message2 = 'Some Even More Unprobable Error'
    original_field.message_values[test_error] = test_message
    field.message_values[test_error] = test_message2
    # delegated (by default)
    self.assertEqual(original_field.get_error_message(test_error),
      test_message)
    self.assertTrue(field.is_message_delegated(test_error))
    self.assertEqual(field.get_error_message(test_error), test_message)
    # surcharged
    field.delegated_message_list = [test_error]
    self.assertEqual(original_field.get_error_message(test_error),
      test_message)
    self.assertFalse(field.is_message_delegated(test_error))
    self.assertEqual(field.get_error_message(test_error), test_message2)

class TestFieldValueCache(ERP5TypeTestCase):
  """Tests field value caching system
  """

  def getTitle(self):
    return "Field Value Cache"

  def afterSetUp(self):
    self.root = self.portal
    self.root.form = ERP5Form('form', 'Form')
    self.root.getProperty = lambda key, d=None: \
      dict(on_memory_field='123').get(key, d)

    form = self.root.form
    def addField(field):
      form._setObject(field.id, field, set_owner=0, suppress_events=1)
    addField(StringField('field'))
    form.field._p_oid = makeDummyOid()
    # method field
    form.field.values['external_validator'] = Method('this_is_a_method')
    # on-memory field (not in zodb)
    addField(StringField('my_on_memory_field'))
    form.my_on_memory_field._p_oid = None
    addField(StringField('my_on_memory_tales_field'))
    form.my_on_memory_tales_field.manage_tales_xmlrpc({
      'default': 'python: repr(here)'})
    form.my_on_memory_field._p_oid = None
    # proxy field
    addField(ProxyField.ProxyField('proxy_field'))
    form.proxy_field._p_oid = makeDummyOid()
    form.proxy_field.values['form_id'] = 'form'
    form.proxy_field.values['field_id'] = 'field'
    # proxy field with tales
    addField(ProxyField.ProxyField('proxy_field_tales'))
    form.proxy_field_tales._p_oid = makeDummyOid()
    form.proxy_field_tales.tales['form_id'] = TALESMethod('string:form')
    form.proxy_field_tales.tales['field_id'] = TALESMethod('string:field')
    # datetime field (input style is list)
    addField(DateTimeField('datetime_field'))
    form.datetime_field._p_oid = makeDummyOid()
    form.datetime_field._edit(dict(input_style='list'))
    for i in form.datetime_field._get_sub_form().fields.values():
      i._p_oid = makeDummyOid()

  def test_method_field(self):
    field = self.root.form.field
    value, cacheable = getFieldValue(field, field, 'external_validator')
    self.assertEqual(False, value.value is field.values['external_validator'])
    self.assertEqual(True, type(value.value) is Method)

  def _getCacheSize(self, cache_id):
    count = 0
    for cache_key in field_value_cache.iterkeys():
      if cache_key[0] == cache_id:
        count += 1

    return count

  def test_using_cache_or_not(self):
    # check standard field in zodb
    # make sure that this will use cache.
    cache_size = self._getCacheSize('Form.get_value')
    self.root.form.field.get_value('title')
    self.assertEqual(True, cache_size < self._getCacheSize('Form.get_value'))

    # check on-memory field
    # make sure that this will not use cache.
    cache_size = self._getCacheSize('Form.get_value')
    self.assertEqual(repr(self.root),
      self.root.form.my_on_memory_tales_field.get_value('default'))
    self.assertEqual('123',
      self.root.form.my_on_memory_field.get_value('default'))
    self.assertEqual(True, cache_size == self._getCacheSize('Form.get_value'))

    # check proxy field
    # make sure that this will use cache.
    cache_size = self._getCacheSize('ProxyField.get_value')
    self.root.form.proxy_field.get_value('title')
    self.assertEqual(True, cache_size < self._getCacheSize('ProxyField.get_value'))

    # check proxy field with tales
    # make sure that this will not use cache.
    cache_size = self._getCacheSize('ProxyField.get_value')
    self.root.form.proxy_field_tales.get_value('title')
    self.assertEqual(True, cache_size == self._getCacheSize('ProxyField.get_value'))


def makeDummyOid():
  import time, random
  return '%s%s' % (time.time(), random.random())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRenderViewAPI))
  suite.addTest(unittest.makeSuite(TestFloatField))
  suite.addTest(unittest.makeSuite(TestIntegerField))
  suite.addTest(unittest.makeSuite(TestStringField))
  suite.addTest(unittest.makeSuite(TestDateTimeField))
  suite.addTest(unittest.makeSuite(TestTextAreaField))
  suite.addTest(unittest.makeSuite(TestLinesField))
  suite.addTest(unittest.makeSuite(TestCheckBoxField))
  suite.addTest(unittest.makeSuite(TestListField))
  suite.addTest(unittest.makeSuite(TestMultiListField))
  suite.addTest(unittest.makeSuite(TestProxyField))
  suite.addTest(unittest.makeSuite(TestFieldValueCache))
  return suite
