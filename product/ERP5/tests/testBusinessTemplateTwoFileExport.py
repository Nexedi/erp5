# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from App.config import getConfiguration
import shutil
import os
import tempfile

class TestBusinessTemplateTwoFileExport(ERP5TypeTestCase):
  """
    Test export and import of business templates with files (e.g. Web Script)

    - Create a template

    - Create a file

    - Build and export the template

    - Check that the expected files are exported

    - Import the exported template and install it

    - Check that the files are imported properly
  """

  def getBusinessTemplateList(self):
    return ['erp5_core_proxy_field_legacy',
                            'erp5_property_sheets',
                            'erp5_jquery',
                            'erp5_jquery_ui',
                            'erp5_full_text_mroonga_catalog',
                            'erp5_base',
                            'erp5_core',
                            'erp5_ingestion_mysql_innodb_catalog',
                            'erp5_ingestion',
                            'erp5_xhtml_style',
                            'erp5_web',
                            'erp5_hal_json_style',
                            'erp5_dms',
                            'erp5_web_renderjs_ui',
                            'erp5_slideshow_style',
                            'erp5_knowledge_pad',
                            'erp5_run_my_doc'
                            ]

  def afterSetUp(self):
    self.cfg = getConfiguration()
    self.export_dir = tempfile.mkdtemp()
    self.template_tool = self.getTemplateTool()
    self.template = self._createNewBusinessTemplate(self.template_tool)

  def beforeTearDown(self):
    export_dir_path = os.path.join(self.cfg.instancehome, self.export_dir)
    if os.path.exists(export_dir_path):
      shutil.rmtree(self.export_dir)

  def _createNewBusinessTemplate(self, template_tool):
    template = template_tool.newContent(portal_type='Business Template')
    self.assertTrue(template.getBuildingState() == 'draft')
    self.assertTrue(template.getInstallationState() == 'not_installed')
    template.edit(title ='test_template',
                  version='1.0',
                  description='bt for unit_test')
    return template

  def _buildAndExportBusinessTemplate(self):
    self.tic()
    self.template.build()
    self.tic()

    self.template.export(path=self.export_dir, local=True)
    self.tic()

  def _importBusinessTemplate(self):
    template_id = self.template.getId()
    template_path = os.path.join(self.cfg.instancehome, self.export_dir)
    self.template_tool.manage_delObjects(template_id)

    import_template = self.template_tool.download(url='file:'+template_path)

    self.assertFalse(import_template is None)
    self.assertEqual(import_template.getPortalType(), 'Business Template')

    return import_template

  def _exportAndReImport(self, xml_document_path,
                        file_document_path, data, removed_property_list):

    self._buildAndExportBusinessTemplate()
    self.assertTrue(os.path.exists(xml_document_path))
    self.assertTrue(os.path.exists(file_document_path))
    test_file=open(file_document_path,'r+')
    self.assertEqual(test_file.read(), data)
    test_file.close()
    xml_file=open(xml_document_path,'r+')
    xml_file_content = xml_file.read()
    xml_file.close()
    for exported_property in removed_property_list:
      self.assertFalse('<string>'+exported_property+'</string>' in xml_file_content)

    import_template = self._importBusinessTemplate()
    return import_template

  def test_twoFileImportExportForTestDocument(self):
    """Test Business Template Import And Export With Test Document"""
    test_component_kw = {"title": "foo",
                         "text_content": "def dummy(): pass",
                         "portal_type": "Test Component"}

    test_document_page = self.portal.portal_components.newContent(**test_component_kw)
    test_component_kw['id'] = test_component_id = test_document_page.getId()

    self.template.edit(template_test_id_list=['portal_components/'+test_component_id,])

    test_component_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                       'TestTemplateItem', 'portal_components',
                                       test_component_id)
    import_template = self._exportAndReImport(
                                  test_component_path + ".xml",
                                  test_component_path +".py",
                                  test_component_kw["text_content"],
                                  ['text_content'])

    self.portal.portal_components.manage_delObjects([test_component_id])

    import_template.install()

    test_page = self.portal.portal_components[test_component_id]

    for property_id, property_value in test_component_kw.iteritems():
      self.assertEqual(test_page.getProperty(property_id), property_value)

  def test_twoFileImportExportForWebPage(self):
    """Test Business Template Import And Export With Web Page"""
    html_document_kw = {"title": "foo", "text_content": "<html></html>",
                        "portal_type": "Web Page"}
    html_page = self.portal.web_page_module.newContent(**html_document_kw)
    js_document_kw = {"title": "foo.js", "text_content": "// JavaScript",
                      "portal_type": "Web Script"}
    js_page = self.portal.web_page_module.newContent(**js_document_kw)
    css_document_kw = {"title": "foo.css", "text_content": "<style></style>",
                       "portal_type": "Web Style"}
    css_page = self.portal.web_page_module.newContent(**css_document_kw)
    html_document_kw['id'] = html_file_id = html_page.getId()
    js_document_kw['id'] = js_file_id = js_page.getId()
    css_document_kw['id'] = css_file_id = css_page.getId()

    self.template.edit(template_path_list=['web_page_module/'+html_file_id,
                                      'web_page_module/'+js_file_id,
                                      'web_page_module/'+css_file_id,])

    self._buildAndExportBusinessTemplate()

    web_page_module_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                        'PathTemplateItem', 'web_page_module')

    for web_file in [(html_file_id, '.html', html_document_kw),
                     (js_file_id, '.js', js_document_kw),
                     (css_file_id, '.css', css_document_kw)]:
      xml_document_path = os.path.join(web_page_module_path, web_file[0]+'.xml')
      file_document_path = os.path.join(web_page_module_path,
                                        web_file[0]+web_file[1])
      self.assertTrue(os.path.exists(xml_document_path))
      self.assertTrue(os.path.exists(file_document_path))
      file_content=open(file_document_path,'r+')
      self.assertEqual(file_content.read(), web_file[2]["text_content"])
      xml_file=open(xml_document_path,'r+')
      self.assertFalse('<string>text_content</string>' in xml_file.read())

    import_template = self._importBusinessTemplate()

    self.portal.web_page_module.manage_delObjects([html_file_id])
    self.portal.web_page_module.manage_delObjects([js_file_id])
    self.portal.web_page_module.manage_delObjects([css_file_id])

    import_template.install()

    for web_file in [(html_file_id, html_document_kw),
                     (js_file_id, js_document_kw),
                     (css_file_id, css_document_kw)]:
      web_page = self.portal.web_page_module[web_file[0]]
      for property_id, property_value in web_file[1].iteritems():
        self.assertEqual(web_page.getProperty(property_id), property_value)

  def test_twoFileImportExportForPythonScript(self):
    """Test Business Template Import And Export With PythonScript"""
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    python_script_id = 'dummy_test_script'
    if python_script_id in skin_folder.objectIds():
      skin_folder.manage_delObjects([python_script_id])
    skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id=python_script_id)
    python_script = skin_folder[python_script_id]
    python_script.ZPythonScript_edit('', "context.setTitle('foo')")

    python_script_kw = {"_body": "context.setTitle('foo')\n",}

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+python_script_id,])

    python_script_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',skin_folder_id,python_script_id)


    import_template = self._exportAndReImport(
                                  python_script_path+".xml",
                                  python_script_path+".py",
                                  python_script_kw["_body"],
                                  ['_body','_code'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([python_script_id])

    import_template.install()

    python_script_page = self.portal.portal_skins[skin_folder_id][python_script_id]

    python_script_content = python_script_page.read()
    self.assertTrue(python_script_content.endswith(python_script_kw['_body']))

  def _checkTwoFileImportExportForImageInImageModule(self,
                                                    image_document_kw,
                                                    extension):
    image_page = self.portal.image_module.newContent(**image_document_kw)
    image_document_kw['id'] = image_file_id = image_page.getId()

    self.template.edit(template_path_list=['image_module/'+image_file_id,])


    image_document_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'PathTemplateItem', 'image_module',image_file_id)

    import_template = self._exportAndReImport(
                                  image_document_path+".xml",
                                  image_document_path+extension,
                                  image_document_kw["data"],
                                  ['data'])

    self.portal.image_module.manage_delObjects([image_file_id])

    import_template.install()

    image_page = self.portal.image_module[image_file_id]
    for property_id, property_value in image_document_kw.iteritems():
      self.assertEqual(image_page.getProperty(property_id), property_value)


  def test_twoFileImportExportForImageIdentifyingTypeByBase64(self):
    """
      Test Business Template Import And Export With Image In Image Module
      where extension is found by Base64 representation
    """
    image_data = """iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""
    image_document_kw = {"title": "foo", "data": image_data,
                         "portal_type": "Image"}

    self._checkTwoFileImportExportForImageInImageModule(image_document_kw, '.png')


  def test_twoFileImportExportForImageIdentifyingTypeByContentType(self):
    """
      Test Business Template Import And Export With Image In Image Module
      where extension (.pjpg) is found by content_type
    """
    image_data = """MalformedBase64HereiVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""
    image_document_kw = {"title": "foo", "data": image_data,
                         "portal_type": "Image", "content_type": "image/jpeg"}

    self._checkTwoFileImportExportForImageInImageModule(image_document_kw,
                                                        '.pjpg')

  def test_twoFileImportExportForImageNotIdentifyingType(self):
    """
      Test Business Template Import And Export With Image In Image Module
      where extension is not identified, so it is exported as '.bin'
    """
    image_data = """MalformedBase64HereiVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""
    image_document_kw = {"title": "foo", "data": image_data,
                         "portal_type": "Image"}

    self._checkTwoFileImportExportForImageInImageModule(image_document_kw,
                                                        '.bin')

  def _checkTwoFileImportExportForDocumentInDocumentModule(self,
                                                            file_document_kw,
                                                            extension):
    file_page = self.portal.document_module.newContent(**file_document_kw)
    file_document_kw['id'] = file_id = file_page.getId()

    self.template.edit(template_path_list=['document_module/'+file_id,])

    file_document_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'PathTemplateItem', 'document_module',
                                      file_id)

    import_template = self._exportAndReImport(
                                  file_document_path+".xml",
                                  file_document_path+extension,
                                  file_document_kw["data"],
                                  ['data'])

    self.portal.document_module.manage_delObjects([file_id])

    import_template.install()

    file_page = self.portal.document_module[file_id]

    for property_id, property_value in file_document_kw.iteritems():
      self.assertEqual(getattr(file_page, property_id), property_value)

  def test_twoFileImportExportForFileIdentifyingTypeByContentTypeJS(self):
    """
      Test Business Template Import And Export With File
      where extension (.js) is identified by the content_type
    """
    file_content = "a test file"
    file_content_type = "text/javascript"
    file_title = "foo"

    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.js')

  def test_twoFileImportExportForFileIdentifyingTypeByContentTypeObj(self):
    """
      Test Business Template Import And Export With File
      where extension (.obj) is identified by the content_type
    """
    file_content = "a test file"
    file_content_type = "application/octet-stream"
    file_title = "foo"
    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.obj')

  def test_twoFileImportExportForFileIdentifyingTypeByContentTypeEpub(self):
    """
      Test Business Template Import And Export With File
      where extension (.epub) is identified by the content_type
    """
    file_content = "a test file"
    file_content_type = "application/epub+zip"
    file_title = "foo"
    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.epub')

  def test_twoFileImportExportForFileIdentifyingTypeByTitleJS(self):
    """
      Test Business Template Import And Export With File
      where extension (.js) is identified by the title
    """
    file_content = "a test file"
    file_title = "foo.js"
    file_document_kw = {"title": file_title, "data": file_content,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.js')

  def test_twoFileImportExportForFileIdentifyingTypeByReferenceJS(self):
    """
      Test Business Template Import And Export With File
      where extension (.js) is identified by the reference
    """
    file_content = "<script> ... </script>"
    file_title = "foo"
    file_document_kw = {"title": file_title, "data": file_content,
                        "default_reference": file_title+".js",
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.js')

  def test_twoFileImportExportForFileNotIdentifyingTypeEmptyContentType(self):
    """
      Test Business Template Import And Export With File
      where extension is not identified, so it is exported as .bin
    """
    file_content = "a test file"
    file_content_type = None
    file_title = "foo"
    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.bin')

  def test_twoFileImportExportForFileNotIdentifyingTypeBinaryContentType(self):
    """
      Test Business Template Import And Export With File
      where extension is not identified by content_type (video/wavelet)
      but it is identified as binary in the mimetypes_registry so it is
      exported as .bin.
    """
    file_content = "a test file"
    file_content_type = 'video/wavelet'
    file_title = "foo"
    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.bin')

  def test_twoFileImportExportForFileNotIdentifyingTypeNonBinaryContentType(self):
    """
      Test Business Template Import And Export With File
      where extension is not identified by content_type (text/x-uri)
      but it is identified as non-binary in the mimetypes_registry so it is
      exported as .txt.
    """
    file_content = "a test file"
    file_content_type = 'text/x-uri'
    file_title = "foo"
    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '.txt')

  def test_twoFileImportExportForFileIdentifyingTypeByTitleXML(self):
    """
      Test Business Template Import And Export With File in portal skins
      where extension (.xml, exported as ._xml to avoid conflict with the meta-data file)
      is identified by the title
    """
    file_content = """<person>
<name>John</name>
<surname>Doe</surname>
</person>
    """
    file_title = "foo.xml"
    file_content_type = None
    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type,
                        "portal_type": "File"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(file_document_kw,
                                                              '._xml')

  def test_twoFileImportExportForFileInPortalSkinsIdentifyingTypeByTitleXML(self):
    """
      Test Business Template Import And Export With File in portal skins
      where extension (.xml, exported as ._xml to avoid conflict with the meta-data file)
      is identified by the title
    """
    file_content = """<person>
<name>John</name>
<surname>Doe</surname>
</person>
    """
    file_title = "foo.xml"
    file_document_kw = {"title": file_title, "data": file_content,}


    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].\
                                    manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    test_file_id = 'dummy_file_id'
    if test_file_id in self.portal.objectIds():
      self.portal.manage_delObjects([test_file_id])

    skin_folder.manage_addProduct['OFSP'].manage_addFile(id=test_file_id)
    zodb_file = skin_folder._getOb(test_file_id)
    zodb_file.manage_edit(title=file_title,
                          content_type='',
                          filedata=file_content)

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+test_file_id,])

    file_document_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                              skin_folder_id,test_file_id)

    import_template = self._exportAndReImport(
                                  file_document_path+".xml",
                                  file_document_path+"._xml",
                                  file_document_kw["data"],
                                  ['data'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([test_file_id])

    import_template.install()

    file_page = self.portal.portal_skins[skin_folder_id][test_file_id]

    for property_id, property_value in file_document_kw.iteritems():
      self.assertEqual(getattr(file_page, property_id), property_value)

  def test_twoFileImportExportForPDF(self):
    """Test Business Template Import And Export With A PDF Document"""
    pdf_data = """pdf content, maybe should update for base64 sample"""

    pdf_document_kw = {"title": "foo.pdf", "data": pdf_data,
                         "portal_type": "PDF"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(pdf_document_kw,
                                                              '.pdf')

  def test_twoFileImportExportForCatalogMethodInCatalog(self):
    """Test Business Template Import And Export With Catalog Method In Catalog"""
    catalog_tool = self.getCatalogTool()
    catalog = catalog_tool.getSQLCatalog()
    catalog_id = catalog.id

    self.assertTrue(catalog is not None)
    method_id = "z_another_dummy_method"
    if method_id in catalog.objectIds():
      catalog.manage_delObjects([method_id])

    method_document_kw = {'id': method_id, 'title': 'dummy_method_title',
                         'connection_id': 'erp5_sql_connection',
                         'arguments_src': 'args', 'src': 'dummy_method_template'}

    addSQLMethod = catalog.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
    addSQLMethod(id=method_id, title='dummy_method_title',
                 connection_id='erp5_sql_connection',
                 template='dummy_method_template',
                 arguments = 'args'
                )
    zsql_method = catalog._getOb(method_id, None)
    self.assertTrue(zsql_method is not None)

    self.template.edit(template_catalog_method_id_list=[catalog_id+'/'+method_id])
    self._buildAndExportBusinessTemplate()

    method_document_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'CatalogMethodTemplateItem',
                                     'portal_catalog',
                                      catalog_id, method_id)

    import_template = self._exportAndReImport(
                                  method_document_path + ".xml",
                                  method_document_path +".sql",
                                  'dummy_method_template',
                                  ['src'])

    catalog.manage_delObjects([method_id])

    import_template.install()

    method_page = catalog[method_id]

    for property_id, property_value in method_document_kw.iteritems():
      self.assertEqual(getattr(method_page, property_id), property_value)

  def test_twoFileImportExportForCatalogMethodInPortalSkins(self):
    """Test Business Template Import And Export With Catalog Method In Portal Skins"""

    method_id = "z_another_dummy_method"
    method_document_kw = {'id': method_id, 'title': 'dummy_method_title',
                         'connection_id': 'erp5_sql_connection',
                         'arguments_src': 'args', 'src': 'dummy_method_template'}

    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].\
                                  manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    if method_id in self.portal.objectIds():
      self.portal.manage_delObjects([method_id])

    addSQLMethod = skin_folder.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod
    addSQLMethod(id=method_id, title='dummy_method_title',
                 connection_id='erp5_sql_connection',
                 template='dummy_method_template',
                 arguments = 'args'
                )

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+method_id,])

    method_document_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                              skin_folder_id, method_id)
    import_template = self._exportAndReImport(
                                  method_document_path+".xml",
                                  method_document_path+".sql",
                                  'dummy_method_template',
                                  ['src'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([method_id])

    import_template.install()

    method_page = skin_folder[method_id]

    for property_id, property_value in method_document_kw.iteritems():
      self.assertEqual(getattr(method_page, property_id), property_value)

  def test_twoFileImportExportForZopePageTemplate(self):
    """Test Business Template Import And Export With ZopePageTemplate"""
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].\
                                  manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    page_template_id = 'dummy_page_template'
    if page_template_id in skin_folder.objectIds():
      skin_folder.manage_delObjects([page_template_id])
    page_template_text = '<html></html>'
    page_template_kw = {"id": page_template_id,
                         "_text": page_template_text,
                         "content_type": "text/html",
                         "output_encoding": "utf-8"}
    skin_folder.manage_addProduct['PageTemplates'].\
                      manage_addPageTemplate(id=page_template_id,
                                             text=page_template_text)

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+page_template_id,])

    page_template_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',skin_folder_id,page_template_id)

    import_template = self._exportAndReImport(
                                  page_template_path+".xml",
                                  page_template_path+".zpt",
                                  page_template_kw['_text'],
                                  ['_text'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([page_template_id])

    import_template.install()

    page_template_page = self.portal.portal_skins[skin_folder_id][page_template_id]

    for property_id, property_value in page_template_kw.iteritems():
      self.assertEqual(getattr(page_template_page, property_id), property_value)

  def test_twoFileImportExportForDTMLMethodIdentifyingTypeByTitle(self):
    """
      Test Business Template Import And Export With DTMLMethod where the
      extension is identified by the title
    """
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    dtml_method_id = 'dummy_dtml_method'
    dtml_method_title = 'dummy_dtml_method.js'
    dtml_method_data = 'dummy content'

    dtml_method_kw = {"__name__": dtml_method_id,
                         "title": dtml_method_title,
                         "raw": dtml_method_data}

    if dtml_method_id in skin_folder.objectIds():
      skin_folder.manage_delObjects([dtml_method_id])

    skin_folder.manage_addProduct['DTMLMethods'].\
                          manage_addDTMLMethod(id = dtml_method_id,
                          title = dtml_method_title)
    dtml_method = skin_folder[dtml_method_id]
    dtml_method.manage_edit(data=dtml_method_data, title = dtml_method_title)

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+dtml_method_id,])

    dtml_method_path = os.path.join(self.cfg.instancehome,
                                    self.export_dir,
                                    'SkinTemplateItem',
                                    'portal_skins',
                                    skin_folder_id,dtml_method_id)

    import_template = self._exportAndReImport(
                                  dtml_method_path+".xml",
                                  dtml_method_path+".js",
                                  dtml_method_kw['raw'],
                                  ['raw'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([dtml_method_id])

    import_template.install()

    dtml_method_page = self.portal.portal_skins[skin_folder_id][dtml_method_id]

    for property_id, property_value in dtml_method_kw.iteritems():
      self.assertEqual(getattr(dtml_method_page, property_id), property_value)

  def test_twoFileImportExportForDTMLMethodNotIdentifyingType(self):
    """
      Test Business Template Import And Export With DTMLMethod where the
      extension is not identified, so it is exported as '.txt'
    """
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].\
                                  manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    dtml_method_id = 'dummy_dtml_method'
    dtml_method_title = 'dummy_dtml_method'
    dtml_method_data = 'dummy content'

    dtml_method_kw = {"__name__": dtml_method_id,
                         "title": dtml_method_title,
                         "raw": dtml_method_data}

    if dtml_method_id in skin_folder.objectIds():
      skin_folder.manage_delObjects([dtml_method_id])

    skin_folder.manage_addProduct['DTMLMethods'].\
                                manage_addDTMLMethod(id = dtml_method_id,
                                                     title = dtml_method_title)
    dtml_method = skin_folder[dtml_method_id]
    dtml_method.manage_edit(data=dtml_method_data, title = dtml_method_title)

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+dtml_method_id,])

    dtml_method_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                              skin_folder_id,dtml_method_id)

    import_template = self._exportAndReImport(
                                  dtml_method_path+".xml",
                                  dtml_method_path+".txt",
                                  dtml_method_kw['raw'],
                                  ['raw'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([dtml_method_id])

    import_template.install()

    dtml_method_page = self.portal.portal_skins[skin_folder_id][dtml_method_id]

    for property_id, property_value in dtml_method_kw.iteritems():
      self.assertEqual(getattr(dtml_method_page, property_id), property_value)

  def test_twoFileImportExportForOOoTemplate(self):
    """Test Business Template Import And Export With OOoTemplate"""
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].\
                                manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    OOo_template_id = 'dummy_OOo_template'
    OOo_template_data = 'dummy OOotemplate content'

    OOo_template_kw = {"id": OOo_template_id,
                         "_text": OOo_template_data,
                         "output_encoding": "utf-8",
                         "content_type": "text/html"}

    if OOo_template_id in skin_folder.objectIds():
      skin_folder.manage_delObjects([OOo_template_id])

    addOOoTemplate =skin_folder.manage_addProduct['ERP5OOo'].addOOoTemplate
    addOOoTemplate(id=OOo_template_id, title=OOo_template_data)

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+OOo_template_id,])

    OOo_template_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                              skin_folder_id, OOo_template_id)

    import_template = self._exportAndReImport(
                                  OOo_template_path+".xml",
                                  OOo_template_path+".oot",
                                  OOo_template_kw['_text'],
                                  ['_text'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([OOo_template_id])

    import_template.install()

    OOo_template_page = self.portal.portal_skins[skin_folder_id][OOo_template_id]

    for property_id, property_value in OOo_template_kw.iteritems():
      self.assertEqual(getattr(OOo_template_page, property_id), property_value)

  def test_twoFileImportExportForSpreadsheetNotIdentifyingType(self):
    """
      Test Business Template Import And Export With Spreadsheed where the
      extension is not identified, so it is exported as '.bin'
    """
    # XXX addding a dummy string in data leads to 'NotConvertedError'
    spreadsheet_data = ''

    spreadsheet_document_kw = {"title": "foo", "data": spreadsheet_data,
                         "portal_type": "Spreadsheet"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(spreadsheet_document_kw,
                                                              '.bin')

  def test_twoFileImportExportForSpreadsheetIdentifyingTypeByContentType(self):
    """
      Test Business Template Import And Export With Spreadsheed where the
      extension is identified by content_type, so it is exported as '.ods'
    """
    # XXX addding a dummy string in data leads to 'NotConvertedError'
    spreadsheet_data = ''

    spreadsheet_document_kw = {"title": "foo", "data": spreadsheet_data,
              "portal_type": "Spreadsheet",
              "content_type": "application/vnd.oasis.opendocument.spreadsheet"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(spreadsheet_document_kw,
                                                              '.ods')

  def test_twoFileImportExportForSpreadsheetIdentifyingTypeByTitle(self):
    """
      Test Business Template Import And Export With Spreadsheed where the
      extension is identified by title, so it is exported as '.xlsx'
    """
    # XXX addding a dummy string in data leads to 'NotConvertedError'
    spreadsheet_data = ''

    spreadsheet_document_kw = {"title": "foo.xlsx", "data": spreadsheet_data,
                         "portal_type": "Spreadsheet"}

    self._checkTwoFileImportExportForDocumentInDocumentModule(spreadsheet_document_kw,
                                                              '.xlsx')

  def test_twoFileImportExportForTestPage(self):
    """Test Business Template Import And Export With A Test Page Document"""
    test_page_data = """<html></html>"""

    test_page_data_kw = {"title": "test_page",
                         "text_content": test_page_data,
                         "portal_type": "Test Page",
                         "content_type": "text/html"}

    test_page = self.portal.test_page_module.newContent(**test_page_data_kw)
    test_page_data_kw['id'] = test_page_id = test_page.getId()

    self.template.edit(template_path_list=['test_page_module/'+test_page_id,])

    test_page_document_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'PathTemplateItem', 'test_page_module',
                                      test_page_id)

    import_template = self._exportAndReImport(
                                  test_page_document_path+".xml",
                                  test_page_document_path+".html",
                                  test_page_data_kw["text_content"],
                                  ["text_content"])

    self.portal.test_page_module.manage_delObjects([test_page_id])

    import_template.install()

    test_page = self.portal.test_page_module[test_page_id]

    for property_id, property_value in test_page_data_kw.iteritems():
      self.assertEqual(getattr(test_page, property_id), property_value)

  def test_twoFileImportExportForERP5PythonScript(self):
    """Test Business Template Import And Export With Python Script"""
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    python_script_id = 'dummy_test_script'
    if python_script_id in skin_folder.objectIds():
      skin_folder.manage_delObjects([python_script_id])

    python_script = self.portal.portal_types.\
      getTypeInfo("Python Script").constructInstance(
        container=skin_folder,
        id=python_script_id)

    python_script.ZPythonScript_edit('', "context.setTitle('foo')")

    python_script_kw = {"id": python_script_id,
                        "_body": "context.setTitle('foo')\n",}

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+python_script_id,])

    python_script_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',skin_folder_id,python_script_id)


    import_template = self._exportAndReImport(
                                  python_script_path+".xml",
                                  python_script_path+".py",
                                  python_script_kw["_body"],
                                  ['_body','_code'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([python_script_id])

    import_template.install()

    python_script_page = self.portal.portal_skins[skin_folder_id][python_script_id]

    for property_id, property_value in python_script_kw.iteritems():
      self.assertEqual(getattr(python_script_page, property_id), property_value)

  def test_templateFolderIsCleanedUpInImportEndReexport(self):
    """
      Test that when TemplateTool.importAndReExportBusinessTemplateListFromPath is
      invoked the template folder is cleaned.

      1. Create a bt and export it in a temporary folder
      2. Add to the folder a text file
      3. Add to the folder a sub-folder
      4. Add to the sub-folder a second text file
      5. Add a third file to portal_templates folder
      6. Invoke TemplateTool.importAndReExportBusinessTemplateListFromPath in the
      template folder
      7. Assert that only the template elements are present
    """
    test_component_kw = {"title": "foo",
                         "text_content": "def dummy(): pass",
                         "portal_type": "Test Component"}

    test_document_page = self.portal.\
                              portal_components.newContent(**test_component_kw)
    test_component_kw['id'] = test_component_id = test_document_page.getId()

    self.template.edit(template_test_id_list=['portal_components/'+test_component_id,])

    test_component_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                       'TestTemplateItem', 'portal_components',
                                        test_component_id)

    self._buildAndExportBusinessTemplate()

    self.assertTrue(os.path.exists(os.path.join(self.export_dir, 'bt')))
    self.assertTrue(os.path.exists(test_component_path+'.xml'))
    self.assertTrue(os.path.exists(test_component_path+'.py'))

    # create a text file in the root
    text_file_name = "text_file.txt"
    text_file_path = os.path.join(self.export_dir, text_file_name)
    text_file = open(text_file_path, "w")
    text_file.close()
    self.assertTrue(os.path.exists(text_file_path))
    # create a sub_folder
    sub_folder_name = "subfolder"
    sub_folder_path = os.path.join(self.export_dir, sub_folder_name)
    os.mkdir(sub_folder_path)
    self.assertTrue(os.path.exists(sub_folder_path))
    # create another text file in the subfolder
    text_file_in_sub_folder_name = "text_file_in_sub_folder.txt"
    text_file_in_sub_folder_path = os.path.join(self.export_dir,
                                              text_file_in_sub_folder_name)
    text_file_in_sub_folder = open(text_file_in_sub_folder_path, "w")
    text_file_in_sub_folder.close()
    self.assertTrue(os.path.exists(text_file_in_sub_folder_path))
    # create another text file inside portal components
    text_file_in_portal_components_name = "text_file_in_sub_folder.txt"
    text_file_in_portal_components_path = os.path.join(self.export_dir,
                                            text_file_in_portal_components_name)
    text_file_in_portal_components = open(text_file_in_sub_folder_path, "w")
    text_file_in_portal_components.close()
    self.assertTrue(os.path.exists(text_file_in_portal_components_path))
    # invoke importAndReExportBusinessTemplateListFromPath
    self.template_tool.importAndReExportBusinessTemplateListFromPath(repository_list=['/tmp'])
    self.tic()
    # assert that unrelated objects were deleted
    self.assertFalse(os.path.exists(text_file_path))
    self.assertFalse(os.path.exists(sub_folder_path))
    self.assertFalse(os.path.exists(text_file_in_sub_folder_path))
    self.assertFalse(os.path.exists(text_file_in_portal_components_path))
    # assert that related objects exist
    self.assertTrue(os.path.exists(os.path.join(self.export_dir, 'bt')))
    self.assertTrue(os.path.exists(test_component_path+'.xml'))
    self.assertTrue(os.path.exists(test_component_path+'.py'))

  def test_twoFileImportExportForFileWithNoData(self):
    """
      Test Business Template Import And Export With File
      that has no data attribute. Only .xml metadata is exported
    """
    file_title = "foo"

    file_document_kw = {"title": file_title,
                        "portal_type": "File"}

    file_page = self.portal.document_module.newContent(**file_document_kw)
    file_document_kw['id'] = file_id = file_page.getId()

    self.template.edit(template_path_list=['document_module/'+file_id,])

    file_document_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'PathTemplateItem', 'document_module',
                                      file_id)

    self.template.build()
    self.tic()
    self.template.export(path=self.export_dir, local=True)
    self.tic()

    self.assertTrue(os.path.exists(file_document_path+'.xml'))
    # check that there is no other file exported
    self.assertEqual(len(os.listdir(file_document_path.rsplit('/', 1)[0])), 1)

    import_template = self._importBusinessTemplate()

    self.portal.document_module.manage_delObjects([file_id])

    import_template.install()

    file_page = self.portal.document_module[file_id]

    for property_id, property_value in file_document_kw.iteritems():
      self.assertEqual(getattr(file_page, property_id), property_value)
