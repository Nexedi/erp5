# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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
from Products.ERP5OOo.tests.TestFormPrintoutMixin import TestFormPrintoutMixin
from Products.ERP5OOo.OOoUtils import OOoBuilder
from Products.ERP5OOo.tests.utils import Validator
from Products.ERP5Type.tests.utils import FileUpload
from lxml import etree
import os

class TestFormPrintoutAsODG(TestFormPrintoutMixin):
  """
    XXX-Tatuya:
    Currently following _validate() methods are failing because LibreOffice 3.4
    itself outputs 'xmlns:graphics' element which is incosistent with the scheme.
    Thus I comment out these validation for now so that we run the other parts
    of the tests. This could be better than to mark them expectedFailure,
    in the aspect of these tests's importance of existence.
  """

  run_all_test = 1

  def getTitle(self):
    """
      Return the title of the current test set.
    """
    return "FormPrintoutAsODG"

  def afterSetUp(self):
    self.login()
    # XML validator
    v12schema_url = os.path.join(os.path.dirname(__file__),
                                 'OpenDocument-v1.2-os-schema.rng')
    self.validator = Validator(schema_url=v12schema_url)

    foo_file_path = os.path.join(os.path.dirname(__file__),
                                'test_document',
                                'Foo_001.odg')
    foo_file = open(foo_file_path, 'rb')
    self._validate(foo_file.read())
    custom = self.portal.portal_skins.custom
    addStyleSheet = custom.manage_addProduct['OFSP'].manage_addFile
    if custom._getOb('Foo_getODGStyleSheet', None) is None:
      addStyleSheet(id='Foo_getODGStyleSheet', file=foo_file, title='',
                    content_type='application/vnd.oasis.opendocument.graphics')
    erp5OOo = custom.manage_addProduct['ERP5OOo']

    if custom._getOb('Foo_viewAsODGPrintout', None) is None:
      erp5OOo.addFormPrintout(id='Foo_viewAsODGPrintout', title='',
                              form_name='Foo_view', template='Foo_getODGStyleSheet')
    if custom._getOb('Foo_viewProxyFieldAsODGPrintout', None) is None:
      erp5OOo.addFormPrintout(id='Foo_viewProxyFieldAsODGPrintout', title='',
                              form_name='Foo_viewProxyField', template='Foo_getODGStyleSheet')
    if custom._getOb('FooReport_viewAsODGPrintout', None) is None:
      erp5OOo.addFormPrintout(id='FooReport_viewAsODGPrintout',
                              title='')

    ## append 'test1' data to a listbox
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    if test1._getOb("foo_1", None) is None:
      test1.newContent("foo_1", title='Foo Line 1', portal_type='Foo Line')
    if test1._getOb("foo_2", None) is None:
      test1.newContent("foo_2", title='Foo Line 2', portal_type='Foo Line')
    self.tic()

  def getStyleDictFromFieldName(self, content_xml, field_id):
    '''parse content_xml string and return a dict with node node.tag
    as key and style dict as value
    '''
    element_tree = etree.XML(content_xml)
    text_xpath = '//draw:frame[@draw:name="%s"]/*' % field_id
    node_list = element_tree.xpath(text_xpath, namespaces=element_tree.nsmap)
    style_dict = {}
    for target_node in node_list:
      style_dict = {}
      for descendant in target_node.iterdescendants():
        style_dict.setdefault(descendant.tag, {}).update(descendant.attrib)
    return style_dict

  # see comment at top
  def test_01_TextField(self):
    """
    mapping a field to textbox
    """
    portal = self.getPortal()
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    test1.setTitle('Foo title!')
    self.tic()

    style_dict = {'{urn:oasis:names:tc:opendocument:xmlns:text:1.0}span':
                    {'{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name': 'T2'},
                  '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p': {}
                 }

    # test target
    foo_printout = portal.foo_module.test1.Foo_viewAsODGPrintout
    original_file_content = self.getODFDocumentFromPrintout(foo_printout)
    self._validate(original_file_content)

    # extract content.xml from original odg document
    original_doc_builder = OOoBuilder(original_file_content)
    original_content_xml = original_doc_builder.extract("content.xml")
    # get style of the title in the orignal test document
    original_document_style_dict = self.getStyleDictFromFieldName(original_content_xml,
        'my_title')

    # check the style is good before the odg generation
    self.assertEqual(original_document_style_dict, style_dict)

    request = self.app.REQUEST
    # 1. Normal case: "my_title" field to the "my_title" reference in the ODF document
    odf_document = foo_printout.index_html(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    final_document_style_dict = self.getStyleDictFromFieldName(content_xml,
        'my_title')

    # check the style is keept after the odg generation
    self.assertEqual(final_document_style_dict, style_dict)

    self.assertTrue(content_xml.find("Foo title!") > 0)
    self.assertEqual(request.RESPONSE.getHeader('content-type'),
                     'application/vnd.oasis.opendocument.graphics')
    self.assertEqual(request.RESPONSE.getHeader('content-disposition'),
                     'inline;filename="Foo_viewAsODGPrintout.odg"')
    self._validate(odf_document)

    # 2. Normal case: change the field value and check again the ODF document
    test1.setTitle("Changed Title!")
    #foo_form.my_title.set_value('default', "Changed Title!")
    odf_document = foo_printout.index_html(request)
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
    odf_document = foo_printout.index_html(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("you cannot find") > 0)
    self._validate(odf_document)
    # put back
    foo_form.manage_renameObject('xxx_title', 'my_title', REQUEST=request)

    ## 4. False case: does not set a ODF template
    self.assertTrue(foo_printout.template == 'Foo_getODGStyleSheet')
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
    # when just call FormPrintout, it does not change content-type
    self.assertEqual(request.RESPONSE.getHeader('content-type'), 'text/html')
    self._validate(odf_document)

    # 5. Normal case: utf-8 string
    test1.setTitle("Français")
    odf_document = foo_printout(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français") > 0)
    self._validate(odf_document)

    # 6. Normal case: unicode string
    test1.setTitle(u'Français test2')
    odf_document = foo_printout(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français test2") > 0)
    # leave _validate() here not to forget the validation failure
    self._validate(odf_document)

  def test_02_TextFieldWithMultiLines(self):
    """
    mapping a field containing many lines ('\n') to a textbox
    """
    portal = self.getPortal()

    # add a description field in the form
    foo_form = self.portal.foo_module.test1.Foo_view
    if foo_form._getOb("my_description", None) is None:
      foo_form.manage_addField('my_description', 'Description', 'TextAreaField')
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    test1.setDescription('A text a bit more longer\n\nWith a newline !')
    self.tic()

    style_dict = {'{urn:oasis:names:tc:opendocument:xmlns:text:1.0}line-break': {},
                  '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p': {},
                  '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}span':
                    {'{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name': 'T4'}
                 }

    # test target
    foo_printout = portal.foo_module.test1.Foo_viewAsODGPrintout
    original_file_content = self.getODFDocumentFromPrintout(foo_printout)
    self._validate(original_file_content)

    # extract content.xml from original odg document
    original_doc_builder = OOoBuilder(original_file_content)
    original_content_xml = original_doc_builder.extract("content.xml")
    # get style of the title in the orignal test document
    original_document_style_dict = self.getStyleDictFromFieldName(original_content_xml,
        'my_description')

    # check the style is good before the odg generation
    self.assertEqual(original_document_style_dict, style_dict)

    request = self.app.REQUEST
    # 1. Normal case: "my_title" field to the "my_title" reference in the ODF document
    odf_document = foo_printout.index_html(request)
    self.assertTrue(odf_document is not None)
    # validate the generated document
    self._validate(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    content = etree.XML(content_xml)
    final_document_style_dict = self.getStyleDictFromFieldName(content_xml,
        'my_description')

    # check the style is keept after the odg generation
    self.assertEqual(final_document_style_dict, style_dict)

    # check the two lines are prensent in the generated document
    self.assertTrue(content_xml.find('A text a bit more longer') > 0)
    self.assertTrue(content_xml.find('With a newline !') > 0)

    # check there is two line-break in the element my_description
    text_xpath = '//draw:frame[@draw:name="my_description"]//text:line-break'
    node_list = content.xpath(text_xpath, namespaces=content.nsmap)
    self.assertEqual(len(node_list), 2)

  def test_03_Image(self):
    """
    Mapping an ImageField to odg document.
    Check it's possible to use an odg document to map an image with a
    form.ImageField
    """
    # create a new person
    request = self.portal.REQUEST
    person_module = self.portal.getDefaultModule('Person')
    if person_module._getOb('person1', None) is None:
      person_module.newContent(id='person1', portal_type='Person')
    person1 =  person_module.person1

    # add an image to this person
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    image_path = os.path.join(parent_dir, 'www', 'form_printout_icon.png')
    file_data = FileUpload(image_path)
    image = person1.newContent(portal_type='Embedded File')
    image.edit(file=file_data)

    foo_printout = image.Foo_viewAsODGPrintout
    foo_form = image.Foo_view
    # add an image_field to Foo_view if there is not
    if foo_form._getOb("image_view", None) is None:
      foo_form.manage_addField('image_view', 'logo', 'ImageField')
    image_view_field = foo_form.image_view
    # set the image on the field
    image_view_field.values['default'] = image.absolute_url_path()

    # 01 - Normal image mapping
    odf_document = foo_printout(request)
    self.assertTrue(odf_document is not None)
    self._validate(odf_document)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    content = etree.XML(content_xml)
    image_element_list = content.xpath('//draw:image', namespaces=content.nsmap)
    self.assertTrue(len(image_element_list) > 0)

    # check the image is in the odg file
    try:
      image_path = image_element_list[0].get('{http://www.w3.org/1999/xlink}href')
      image_data = builder.extract(image_path)
    except KeyError:
      self.fail('image %r not found in odg document' % image_path)
    self.assertEqual(image.getData(), image_data,
                      '%s != %s' % (len(image.getData()), len(image_data)))
    image_frame_xpath = '//draw:frame[@draw:name="image_view"]'
    image_frame_list = content.xpath(image_frame_xpath, namespaces=content.nsmap)
    self.assertTrue(len(image_frame_list) > 0)
    image_frame = image_frame_list[0]
    # Check the image size.
    # as the test image (form_printout_icon.png) is a square, proportions
    # should be keept, so heigh and width should be same and equal to the
    # height of the original image in the original odf test document.
    self.assertEqual(image_frame.attrib['{%s}height' % content.nsmap['svg']],
                     '1.206cm')
    self.assertEqual(image_frame.attrib['{%s}width' % content.nsmap['svg']],
                     '1.206cm')

    # 02: No image defined
    image_view_field.values['default'] = ''
    odf_document = foo_printout(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    # confirming the image was removed
    content = etree.XML(content_xml)
    image_element_list = content.xpath('//draw:image', namespaces=content.nsmap)
    self.assertFalse(len(image_element_list) > 0)
    self._validate(odf_document)

  def test_04_ProxyField(self):
    """
    Check it's possible to use an odg document to map proxyfields
    """
    portal = self.getPortal()
    foo_module = self.portal.foo_module
    if foo_module._getOb('test1', None) is None:
      foo_module.newContent(id='test1', portal_type='Foo')
    test1 =  foo_module.test1
    test1.setTitle('Foo title!')
    self.tic()

    style_dict = {'{urn:oasis:names:tc:opendocument:xmlns:text:1.0}span':
                    {'{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name': 'T2'},
                  '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p': {}
                 }

    # test target
    foo_printout = portal.foo_module.test1.Foo_viewProxyFieldAsODGPrintout
    original_file_content = self.getODFDocumentFromPrintout(foo_printout)
    self._validate(original_file_content)

    # extract content.xml from original odg document
    original_doc_builder = OOoBuilder(original_file_content)
    original_content_xml = original_doc_builder.extract("content.xml")
    # get style of the title in the orignal test document
    original_document_style_dict = self.getStyleDictFromFieldName(original_content_xml,
        'my_title')

    # check the style is good before the odg generation
    self.assertEqual(original_document_style_dict, style_dict)

    request = self.app.REQUEST
    # 1. Normal case: "my_title" field to the "my_title" reference in the ODF document
    odf_document = foo_printout.index_html(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    final_document_style_dict = self.getStyleDictFromFieldName(content_xml,
        'my_title')

    # check the style is keept after the odg generation
    self.assertEqual(final_document_style_dict, style_dict)

    self.assertTrue(content_xml.find("Foo title!") > 0)
    self.assertEqual(request.RESPONSE.getHeader('content-type'),
                     'application/vnd.oasis.opendocument.graphics')
    self.assertEqual(request.RESPONSE.getHeader('content-disposition'),
                     'inline;filename="Foo_viewProxyFieldAsODGPrintout.odg"')
    self._validate(odf_document)

    # 2. Normal case: change the field value and check again the ODF document
    test1.setTitle("Changed Title!")
    #foo_form.my_title.set_value('default', "Changed Title!")
    odf_document = foo_printout.index_html(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Changed Title!") > 0)
    self._validate(odf_document)

    # 3. False case: change the field name
    test1.setTitle("you cannot find")
    # rename id 'my_title' to 'xxx_title', then does not match in the ODF document
    foo_form = portal.foo_module.test1.Foo_viewProxyField
    foo_form.manage_renameObject('my_title', 'xxx_title', REQUEST=request)
    odf_document = foo_printout.index_html(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertFalse(content_xml.find("you cannot find") > 0)
    self._validate(odf_document)
    # put back
    foo_form.manage_renameObject('xxx_title', 'my_title', REQUEST=request)

    ## 4. False case: does not set a ODF template
    self.assertTrue(foo_printout.template == 'Foo_getODGStyleSheet')
    tmp_template = foo_printout.template
    foo_printout.template = None
    self.assertRaises(ValueError, foo_printout.index_html, request)
    # put back
    foo_printout.template = tmp_template

    # 5. Normal case: just call a FormPrintout object
    request.RESPONSE.setHeader('Content-Type', 'text/html')
    test1.setTitle("call!")
    odf_document = foo_printout(request) # call
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("call!") > 0)
    self.assertEqual(request.RESPONSE.getHeader('content-type'),
                     'application/vnd.oasis.opendocument.graphics')
    self._validate(odf_document)

    # 5. Normal case: utf-8 string
    test1.setTitle("Français")
    odf_document = foo_printout(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français") > 0)
    self._validate(odf_document)

    # 6. Normal case: unicode string
    test1.setTitle(u'Français test2')
    odf_document = foo_printout(request)
    self.assertTrue(odf_document is not None)
    builder = OOoBuilder(odf_document)
    content_xml = builder.extract("content.xml")
    self.assertTrue(content_xml.find("Français test2") > 0)
    self._validate(odf_document)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFormPrintoutAsODG))
  return suite
