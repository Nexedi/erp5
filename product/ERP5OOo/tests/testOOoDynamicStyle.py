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
import sys
import unittest
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Type.tests.utils import DummyLocalizer
from zLOG import LOG
from Products.ERP5OOo.tests.utils import Validator
from Testing import ZopeTestCase
from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO

class TestOooDynamicStyle(ZopeTestCase.FunctionalTestCase):
  manager_username = 'tatuya'
  manager_password = 'tatuya'
  content_type_writer = 'application/vnd.oasis.opendocument.text'
  content = "<office:document-content xmlns:draw='urn:oasis:names:tc:opendocument:xmlns:drawing:1.0' xmlns:office='urn:oasis:names:tc:opendocument:xmlns:office:1.0' xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0' xmlns:ooo='http://openoffice.org/2004/office' xmlns:number='urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0' xmlns:dc='http://purl.org/dc/elements/1.1/' xmlns:meta='urn:oasis:names:tc:opendocument:xmlns:meta:1.0' xmlns:table='urn:oasis:names:tc:opendocument:xmlns:table:1.0' xmlns:dr3d='urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0' xmlns:fo='urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0' xmlns:style='urn:oasis:names:tc:opendocument:xmlns:style:1.0' xmlns:xforms='http://www.w3.org/2002/xforms' xmlns:form='urn:oasis:names:tc:opendocument:xmlns:form:1.0' xmlns:script='urn:oasis:names:tc:opendocument:xmlns:script:1.0' xmlns:ooow='http://openoffice.org/2004/writer' xmlns:svg='urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0' xmlns:chart='urn:oasis:names:tc:opendocument:xmlns:chart:1.0' xmlns:dom='http://www.w3.org/2001/xml-events' xmlns:xlink='http://www.w3.org/1999/xlink' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:oooc='http://openoffice.org/2004/calc' xmlns:math='http://www.w3.org/1998/Math/MathML' xmlns:tal='http://xml.zope.org/namespaces/tal' office:version='1.2'><office:scripts /><office:font-face-decls /><office:automatic-styles /><office:body><office:text /></office:body></office:document-content>"

  def getTitle(self):
    return "TestOOoDynamicStyle"

  def login(self):
    uf = self.folder.acl_users
    uf._doAddUser(self.manager_username, self.manager_password, ['Manager'], [])
    user = uf.getUserById(self.manager_username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()
    ZopeTestCase.installProduct('Localizer')
    ZopeTestCase.installProduct('PythonScripts')
    ZopeTestCase.installProduct('ERP5OOo')
    self.folder.Localizer = DummyLocalizer()
    self.validator = Validator()
    en_file_path = os.path.join(os.path.dirname(__file__),
                                'test_document',
                                'DYNAMIC_STYLE_en.odt')
    en_file = open(en_file_path, 'rb')
    ja_file_path = os.path.join(os.path.dirname(__file__),
                                'test_document',
                                'DYNAMIC_STYLE_ja.odt')
    ja_file = open(ja_file_path, 'rb')

    addStyleSheet = self.folder.manage_addProduct['OFSP'].manage_addFile
    addStyleSheet(id='Test_getODTStyleSheet_en', file=en_file, title='',
      precondition='', content_type=self.content_type_writer)
    addStyleSheet(id='Test_getODTStyleSheet_ja', file=ja_file, title='',
      precondition='', content_type=self.content_type_writer)
    script_body = """
current_language = context.Localizer.get_selected_language()
return getattr(context, "%s_%s" % (parameter, current_language))
"""
    dispatcher = self.folder.manage_addProduct['PythonScripts']
    dispatcher.manage_addPythonScript('Base_getODTStyleSheetByLanguage')
    script = self.folder.Base_getODTStyleSheetByLanguage
    script.ZPythonScript_edit('parameter', script_body)

  def _validate(self, odf_file_data):
    error_list = self.validator.validate(odf_file_data)
    if error_list:
      self.fail(''.join(error_list))

  def _create_odt_zip_file(self, zip_string):
    zipped_io = StringIO()
    zipped_io.write(zip_string)
    try:
      odt_zip_file = ZipFile(zipped_io, mode='r', compression=ZIP_DEFLATED)
    except RuntimeError:
      odt_zip_file = ZipFile(zipped_io, mode='r')
    return  odt_zip_file

  def test_01_dynamic(self):
    """
    Test applying stylesheet dynamically, using a Python Script with
    a stylesheet file name parameter.
    """
    request = self.app.REQUEST
    addOOoTemplate = self.folder.manage_addProduct['ERP5OOo'].addOOoTemplate
    addOOoTemplate(id='Dynamic_viewAsOdt', title='')
    Dynamic_viewAsOdt = self.folder.Dynamic_viewAsOdt
    # The stylesheet file 'Test_getODTStyleSheet' is not exist in this site.
    # So, the 'Base_getODTStyleSheet', a python script creates dynamically 
    # exsited stylesheet file name. 
    self.assertFalse(self.folder.hasObject('Test_getODTStyleSheet'))
    self.assertTrue(self.folder.hasObject('Test_getODTStyleSheet_ja'))
    self.assertTrue(self.folder.hasObject('Test_getODTStyleSheet_en'))
    Dynamic_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                 ooo_stylesheet='Test_getODTStyleSheet', 
                                 script_name='Base_getODTStyleSheetByLanguage')
    Dynamic_viewAsOdt.pt_edit(self.content, content_type='application/vnd.oasis.opendocument.text')

    # 1. test a normal case, language: ja
    self.folder.Localizer.changeLanguage('ja')
    response = self.publish('/' + self.folder.Dynamic_viewAsOdt.absolute_url(1))
    self.assertEqual('application/vnd.oasis.opendocument.text',
                     response.getHeader('content-type').split(';')[0])
    self.assertEqual('inline;filename="Dynamic_viewAsOdt"',
                     response.getHeader('content-disposition'))
    self._validate(response.getBody()) 
    self.assertTrue(200, response.getStatus())

    odt_zip_file = self._create_odt_zip_file(response.getBody())
    styles_xml_body = odt_zip_file.read('styles.xml')
    self.assertTrue(len(styles_xml_body) > 0)
    # 'Style sheet ja' text is in the odt document header, 
    # and the header is in the 'styles.xml'.
    self.assertTrue(styles_xml_body.find('Style sheet ja') > 0)
  
    # 2. test a normal case, change the language to 'en', 
    #    so that the stylesheet changes dynamically.
    self.folder.Localizer.changeLanguage('en')
    response = self.publish('/' + self.folder.Dynamic_viewAsOdt.absolute_url(1))
    self._validate(response.getBody()) 
    odt_zip_file = self._create_odt_zip_file(response.getBody())
    styles_xml_body = odt_zip_file.read('styles.xml')
    self.assertTrue(styles_xml_body.find('Style sheet en') > 0)
    
    # 3. test a fail case, reset a not existed stylesheet
    Dynamic_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                 ooo_stylesheet='NotFound_getODTStyleSheet', 
                                 script_name='Base_getODTStyleSheet')
    self.assertFalse(self.folder.hasObject('NotFound_getODTStyleSheet'))
    self.assertFalse(self.folder.hasObject('NotFound_getODTStyleSheet_ja'))
    self.assertFalse(self.folder.hasObject('NotFound_getODTStyleSheet_en'))
    self.folder.Localizer.changeLanguage('en')
    response = self.publish('/' + self.folder.Dynamic_viewAsOdt.absolute_url(1))
    # then, it is not a zip stream 
    self.assertFalse(response.getBody().startswith('PK'))
    self.assertTrue(500, response.getStatus())
   

  def test_02_static(self):
    """
    Test applying stylesheet statically, using a stylesheet File object.
    """
    request = self.app.REQUEST
    addOOoTemplate = self.folder.manage_addProduct['ERP5OOo'].addOOoTemplate
    addOOoTemplate(id='Static_viewAsOdt', title='')
    Static_viewAsOdt = self.folder.Static_viewAsOdt
    # Test_getODTStyleSheet_ja is statically exist.
    self.assertTrue(self.folder.hasObject('Test_getODTStyleSheet_ja'))
    Static_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                ooo_stylesheet='Test_getODTStyleSheet_ja', script_name='')
    Static_viewAsOdt.pt_edit(self.content, content_type='application/vnd.oasis.opendocument.text')

    # 1. test a normal case
    response = self.publish('/' + self.folder.Static_viewAsOdt.absolute_url(1))
    self.assertTrue(200, response.getStatus())
    self.assertEqual('application/vnd.oasis.opendocument.text',
                     response.getHeader('content-type').split(';')[0])
    self.assertEqual('inline;filename="Static_viewAsOdt"',
                     response.getHeader('content-disposition'))
    self._validate(response.getBody()) 
    odt_zip_file = self._create_odt_zip_file(response.getBody())
    styles_xml_body = odt_zip_file.read('styles.xml')
    self.assertTrue(len(styles_xml_body) > 0)
    self.assertTrue(styles_xml_body.find('Style sheet ja') > 0)
    
    # 2. test a normal case, change the style sheet
    self.assertTrue(self.folder.hasObject('Test_getODTStyleSheet_en'))
    Static_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                ooo_stylesheet='Test_getODTStyleSheet_en', script_name='')
    response = self.publish('/' + self.folder.Static_viewAsOdt.absolute_url(1))
    self.assertTrue(200, response.getStatus())
    self._validate(response.getBody()) 
    odt_zip_file = self._create_odt_zip_file(response.getBody())
    styles_xml_body = odt_zip_file.read('styles.xml')
    self.assertTrue(len(styles_xml_body) > 0)
    self.assertTrue(styles_xml_body.find('Style sheet en') > 0)
 
    # 3. test a fail case
    self.assertFalse(self.folder.hasObject('NotFound_getODTStyleSheet'))
    Static_viewAsOdt.doSettings(request, title='', xml_file_id='content.xml',
                                ooo_stylesheet='NotFound_getODTStyleSheet', script_name='')
    response = self.publish('/' + self.folder.Static_viewAsOdt.absolute_url(1))
    self.assertFalse(response.getBody().startswith('PK'))
    self.assertTrue(500, response.getStatus())
     

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOooDynamicStyle))
  return suite
