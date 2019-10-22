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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import os
import unittest
from cStringIO import StringIO
from zipfile import ZipFile
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import DummyLocalizer
from Products.ERP5OOo.tests.utils import Validator
from Products.ERP5OOo.OOoUtils import OOoBuilder


class TestOooDynamicStyle(ERP5TypeTestCase):
  manager_username = 'tatuya'
  manager_password = 'tatuya'
  content_type_writer = 'application/vnd.oasis.opendocument.text'
  content = "<office:document-content xmlns:draw='urn:oasis:names:tc:opendocument:xmlns:drawing:1.0' xmlns:office='urn:oasis:names:tc:opendocument:xmlns:office:1.0' xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0' xmlns:ooo='http://openoffice.org/2004/office' xmlns:number='urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0' xmlns:dc='http://purl.org/dc/elements/1.1/' xmlns:meta='urn:oasis:names:tc:opendocument:xmlns:meta:1.0' xmlns:table='urn:oasis:names:tc:opendocument:xmlns:table:1.0' xmlns:dr3d='urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0' xmlns:fo='urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0' xmlns:style='urn:oasis:names:tc:opendocument:xmlns:style:1.0' xmlns:xforms='http://www.w3.org/2002/xforms' xmlns:form='urn:oasis:names:tc:opendocument:xmlns:form:1.0' xmlns:script='urn:oasis:names:tc:opendocument:xmlns:script:1.0' xmlns:ooow='http://openoffice.org/2004/writer' xmlns:svg='urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0' xmlns:chart='urn:oasis:names:tc:opendocument:xmlns:chart:1.0' xmlns:dom='http://www.w3.org/2001/xml-events' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:oooc='http://openoffice.org/2004/calc' xmlns:math='http://www.w3.org/1998/Math/MathML' xmlns:tal='http://xml.zope.org/namespaces/tal' office:version='1.2'><office:scripts /><office:font-face-decls /><office:automatic-styles /><office:body><office:text /></office:body></office:document-content>"

  def getTitle(self):
    return "TestOOoDynamicStyle"

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_mroonga_catalog',
            'erp5_base',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_ingestion',
            'erp5_web',
            'erp5_dms',
            'erp5_odt_style')


  def afterSetUp(self):
    self.login()
    self.getPortal().Localizer = DummyLocalizer()
    v12schema_url = os.path.join(os.path.dirname(__file__),
                                 'OpenDocument-v1.2-os-schema.rng')
    self.validator = Validator(schema_url=v12schema_url)
    en_file_path = os.path.join(os.path.dirname(__file__),
                                'test_document',
                                'DYNAMIC_STYLE_en.odt')
    en_file = open(en_file_path, 'rb')
    ja_file_path = os.path.join(os.path.dirname(__file__),
                                'test_document',
                                'DYNAMIC_STYLE_ja.odt')
    ja_file = open(ja_file_path, 'rb')

    addStyleSheet = self.getPortal().manage_addProduct['OFSP'].manage_addFile
    if getattr(self.getPortal(), 'Test_getODTStyleSheet_en', None) is None:
      addStyleSheet(id='Test_getODTStyleSheet_en', file=en_file, title='',
        content_type=self.content_type_writer)
    if getattr(self.getPortal(), 'Test_getODTStyleSheet_ja', None) is None:
      addStyleSheet(id='Test_getODTStyleSheet_ja', file=ja_file, title='',
        content_type=self.content_type_writer)
    if getattr(self.getPortal(), 'Base_getODTStyleSheetByLanguage', None) is None:
      script_body = """
current_language = context.Localizer.get_selected_language()
return getattr(context, "%s_%s" % (parameter, current_language))
"""
      dispatcher = self.getPortal().manage_addProduct['PythonScripts']
      dispatcher.manage_addPythonScript('Base_getODTStyleSheetByLanguage')
      script = self.getPortal().Base_getODTStyleSheetByLanguage
      script.ZPythonScript_edit('parameter', script_body)

  def _validate(self, odf_file_data):
    error_list = self.validator.validate(odf_file_data)
    if error_list:
      self.fail(''.join(error_list))

  def test_01_dynamic(self):
    """
    Test applying stylesheet dynamically, using a Python Script with
    a stylesheet file name parameter.
    """
    request = self.app.REQUEST
    addOOoTemplate = self.getPortal().manage_addProduct['ERP5OOo'].addOOoTemplate
    addOOoTemplate(id='Dynamic_viewAsOdt', title='')
    Dynamic_viewAsOdt = self.getPortal().Dynamic_viewAsOdt
    # The stylesheet file 'Test_getODTStyleSheet' is not exist in this site.
    # So, the 'Base_getODTStyleSheet', a python script creates dynamically
    # exsited stylesheet file name.
    self.assertFalse(self.getPortal().hasObject('Test_getODTStyleSheet'))
    self.assertTrue(self.getPortal().hasObject('Test_getODTStyleSheet_ja'))
    self.assertTrue(self.getPortal().hasObject('Test_getODTStyleSheet_en'))
    Dynamic_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                 ooo_stylesheet='Test_getODTStyleSheet',
                                 script_name='Base_getODTStyleSheetByLanguage')
    Dynamic_viewAsOdt.pt_edit(self.content, content_type='application/vnd.oasis.opendocument.text')

    # 1. test a normal case, language: ja
    self.getPortal().Localizer.changeLanguage('ja')
    response = self.publish('/' + self.getPortal().Dynamic_viewAsOdt.absolute_url(1))
    self.assertEqual('application/vnd.oasis.opendocument.text',
                     response.getHeader('content-type').split(';')[0])
    self.assertEqual('attachment; filename="Dynamic_viewAsOdt.odt"',
                     response.getHeader('content-disposition'))
    self._validate(response.getBody())
    self.assertEqual(200, response.getStatus())

    ooo_builder = OOoBuilder(response.getBody())
    styles_xml_body = ooo_builder.extract('styles.xml')
    self.assertTrue(len(styles_xml_body) > 0)
    # 'Style sheet ja' text is in the odt document header,
    # and the header is in the 'styles.xml'.
    self.assertTrue(styles_xml_body.find('Style sheet ja') > 0)

    # 2. test a normal case, change the language to 'en',
    #    so that the stylesheet changes dynamically.
    self.getPortal().Localizer = DummyLocalizer()
    self.getPortal().Localizer.changeLanguage('en')
    response = self.publish('/' + self.getPortal().Dynamic_viewAsOdt.absolute_url(1))
    self._validate(response.getBody())
    ooo_builder = OOoBuilder(response.getBody())
    styles_xml_body = ooo_builder.extract('styles.xml')
    self.assertTrue(styles_xml_body.find('Style sheet en') > 0)

    # 3. test a fail case, reset a not existed stylesheet
    Dynamic_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                 ooo_stylesheet='NotFound_getODTStyleSheet',
                                 script_name='Base_getODTStyleSheet')
    self.assertFalse(self.getPortal().hasObject('NotFound_getODTStyleSheet'))
    self.assertFalse(self.getPortal().hasObject('NotFound_getODTStyleSheet_ja'))
    self.assertFalse(self.getPortal().hasObject('NotFound_getODTStyleSheet_en'))
    self.getPortal().Localizer.changeLanguage('en')
    response = self.publish('/' + self.getPortal().Dynamic_viewAsOdt.absolute_url(1))
    # then, it is not a zip stream
    self.assertFalse(response.getBody().startswith('PK'))
    self.assertEqual(500, response.getStatus())


  def test_02_static(self):
    """
    Test applying stylesheet statically, using a stylesheet File object.
    """
    request = self.app.REQUEST
    addOOoTemplate = self.getPortal().manage_addProduct['ERP5OOo'].addOOoTemplate
    addOOoTemplate(id='Static_viewAsOdt', title='')
    Static_viewAsOdt = self.getPortal().Static_viewAsOdt
    # Test_getODTStyleSheet_ja is statically exist.
    self.assertTrue(self.getPortal().hasObject('Test_getODTStyleSheet_ja'))
    Static_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                ooo_stylesheet='Test_getODTStyleSheet_ja', script_name='')
    Static_viewAsOdt.pt_edit(self.content, content_type='application/vnd.oasis.opendocument.text')

    # 1. test a normal case
    response = self.publish('/' + self.getPortal().Static_viewAsOdt.absolute_url(1))
    self.assertEqual(200, response.getStatus())
    self.assertEqual('application/vnd.oasis.opendocument.text',
                     response.getHeader('content-type').split(';')[0])
    self.assertEqual('attachment; filename="Static_viewAsOdt.odt"',
                     response.getHeader('content-disposition'))
    self._validate(response.getBody())
    ooo_builder = OOoBuilder(response.getBody())
    styles_xml_body = ooo_builder.extract('styles.xml')
    self.assertTrue(len(styles_xml_body) > 0)
    self.assertTrue(styles_xml_body.find('Style sheet ja') > 0)

    # 2. test a normal case, change the style sheet
    self.assertTrue(self.getPortal().hasObject('Test_getODTStyleSheet_en'))
    Static_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                ooo_stylesheet='Test_getODTStyleSheet_en', script_name='')
    response = self.publish('/' + self.getPortal().Static_viewAsOdt.absolute_url(1))
    self.assertEqual(200, response.getStatus())
    self._validate(response.getBody())
    ooo_builder = OOoBuilder(response.getBody())
    styles_xml_body = ooo_builder.extract('styles.xml')
    self.assertTrue(len(styles_xml_body) > 0)
    self.assertTrue(styles_xml_body.find('Style sheet en') > 0)

    # 3. test a fail case
    self.assertFalse(self.getPortal().hasObject('NotFound_getODTStyleSheet'))
    Static_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                ooo_stylesheet='NotFound_getODTStyleSheet', script_name='')
    response = self.publish('/' + self.getPortal().Static_viewAsOdt.absolute_url(1))
    self.assertFalse(response.getBody().startswith('PK'))
    self.assertEqual(500, response.getStatus())

  def test_include_img(self):
    """
      Create an OOoTemplate from scratch, using pt_editAction to set the
      content, the content contains an include_img, when the OOo is rendered we
      have:
       - valid odf
       - an image included in the "ZIP"
       - the image properly listed in manifest
    """
    request = self.app.REQUEST
    filename = 'cmyk_sample.jpg'
    file_path = os.path.join(os.path.dirname(__file__), 'test_document',
        filename)
    upload_file = FileUpload(file_path)
    document = self.portal.portal_contributions.newContent(file=upload_file)
    addOOoTemplate = self.getPortal().manage_addProduct['ERP5OOo'].addOOoTemplate
    addOOoTemplate(id='Base_viewIncludeImageAsOdt', title='')
    custom_content = self.content.replace("<office:text />",
        "<office:text><office:include_img path='%s'/></office:text>" % document.getRelativeUrl())
    Base_viewIncludeImageAsOdt = self.getPortal().Base_viewIncludeImageAsOdt
    Base_viewIncludeImageAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                ooo_stylesheet='Base_getODTStyleSheet',
                                script_name='')
    Base_viewIncludeImageAsOdt.pt_edit(custom_content,
        content_type='application/vnd.oasis.opendocument.text')
    self.tic()

    response = self.publish('/' + self.getPortal().Base_viewIncludeImageAsOdt.absolute_url(1))
    body = response.getBody()
    self.assertEqual(200, response.getStatus(), body)
    self.assertEqual('application/vnd.oasis.opendocument.text',
                     response.getHeader('content-type').split(';')[0])
    self.assertEqual('attachment; filename="Base_viewIncludeImageAsOdt.odt"',
                     response.getHeader('content-disposition'))
    cs = StringIO()
    cs.write(body)
    zip_document = ZipFile(cs)
    picture_list = filter(lambda x: "Pictures" in x.filename,
        zip_document.infolist())
    self.assertNotEquals([], picture_list)
    manifest = zip_document.read('META-INF/manifest.xml')
    content = zip_document.read('content.xml')
    for picture in picture_list:
      self.assertTrue(picture.filename in manifest)
      self.assertTrue(picture.filename in content)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOooDynamicStyle))
  return suite
