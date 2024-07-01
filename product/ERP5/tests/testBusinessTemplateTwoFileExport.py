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

from Products.ERP5Type.tests.ERP5TypeTestCase import \
  ERP5TypeTestCase, immediateCompilation
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from runUnitTest import tests_home
import base64
import glob
import shutil
import os
import tempfile
from lxml import etree
import six

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
    self.export_dir = tempfile.mkdtemp(dir=tests_home)
    self.template_tool = self.getTemplateTool()
    self.template = self._createNewBusinessTemplate(self.template_tool)

  def beforeTearDown(self):
    if os.path.exists(self.export_dir):
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
    self.template_tool.manage_delObjects(self.template.getId())
    import_template = self.template_tool.download(url='file:'+self.export_dir)
    self.assertEqual(import_template.getPortalType(), 'Business Template')
    return import_template

  def _exportAndReImport(self, document_path, extension,
                         data, removed_property_list):
    self._buildAndExportBusinessTemplate()
    xml_document_path = document_path + ".xml"
    exported = glob.glob(document_path + ".*")
    exported.remove(document_path + ".xml")
    if extension:
      try:
        exported.remove(document_path + ".catalog_keys.xml")
        self.assertEqual(extension, ".sql")
      except ValueError:
        pass
      file_document_path = document_path + extension
      self.assertEqual([os.path.basename(file_document_path)],
                       list(map(os.path.basename, exported)))
      with open(file_document_path, 'rb') as test_file:
        self.assertEqual(test_file.read(), data)
    else:
      self.assertFalse(exported)
    with open(xml_document_path, 'rb') as xml_file:
      xml_file_content = xml_file.read()
    for exported_property in removed_property_list:
      self.assertNotIn(('<string>%s</string>' % exported_property).encode(),
                       xml_file_content)

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

    test_component_path = os.path.join(self.export_dir,
                                       'TestTemplateItem', 'portal_components',
                                       test_component_id)
    import_template = self._exportAndReImport(
                                  test_component_path,
                                  ".py",
                                  test_component_kw["text_content"].encode(),
                                  ['text_content'])

    self.portal.portal_components.manage_delObjects([test_component_id])

    import_template.install()

    test_page = self.portal.portal_components[test_component_id]

    for property_id, property_value in six.iteritems(test_component_kw):
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

    web_page_module_path = os.path.join(self.export_dir,
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
      self.assertNotIn('<string>text_content</string>', xml_file.read())

    import_template = self._importBusinessTemplate()

    self.portal.web_page_module.manage_delObjects([html_file_id])
    self.portal.web_page_module.manage_delObjects([js_file_id])
    self.portal.web_page_module.manage_delObjects([css_file_id])

    import_template.install()

    for web_file in [(html_file_id, html_document_kw),
                     (js_file_id, js_document_kw),
                     (css_file_id, css_document_kw)]:
      web_page = self.portal.web_page_module[web_file[0]]
      for property_id, property_value in six.iteritems(web_file[1]):
        self.assertEqual(web_page.getProperty(property_id), property_value)

  def test_twoFileImportExportForPythonScript(self):
    """Test Business Template Import And Export With PythonScript"""
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    python_script_id = 'dummy_test_script'
    skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(
      id=python_script_id)
    skin_folder[python_script_id].ZPythonScript_edit('', "return 1")

    python_script_kw = {"_body": "return 1\n",}

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+python_script_id,])

    python_script_path = os.path.join(self.export_dir,
      'SkinTemplateItem', 'portal_skins', skin_folder_id, python_script_id)


    with immediateCompilation():
      import_template = self._exportAndReImport(
                                  python_script_path,
                                  ".py",
                                  python_script_kw["_body"].encode(),
                                  ['_body','_code'])

      skin_folder.manage_delObjects(python_script_id)

      import_template.install()

      script = skin_folder[python_script_id]

      self.assertTrue(script.read().endswith(python_script_kw['_body']))
      self.assertEqual(1, script())

  def _checkTwoFileImportExportForImageInImageModule(self,
                                                    image_document_kw,
                                                    extension):
    image_page = self.portal.image_module.newContent(**image_document_kw)
    image_document_kw['id'] = image_file_id = image_page.getId()

    self.template.edit(template_path_list=['image_module/'+image_file_id,])


    image_document_path = os.path.join(self.export_dir,
      'PathTemplateItem', 'image_module',image_file_id)

    import_template = self._exportAndReImport(
                                  image_document_path,
                                  extension,
                                  image_document_kw["data"],
                                  ['data'])

    self.portal.image_module.manage_delObjects([image_file_id])

    import_template.install()

    image_page = self.portal.image_module[image_file_id]
    for property_id, property_value in six.iteritems(image_document_kw):
      self.assertEqual(image_page.getProperty(property_id), property_value)


  png_data = base64.b64decode(b"""iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg==""")

  def test_twoFileImportExportForImageIdentifyingTypeByContent(self):
    """
      Test Business Template Import And Export With Image In Image Module
      where extension is found by Base64 representation
    """
    self._checkTwoFileImportExportForImageInImageModule(dict(
      title = "foo",
      data = self.png_data,
      portal_type = "Image",
    ), '.png')

  def test_twoFileImportExportForImageIdentifyingTypeByContentType(self):
    """
      Test Business Template Import And Export With Image In Image Module
      where extension (.jpg) is found by content_type
    """
    self._checkTwoFileImportExportForImageInImageModule(dict(
      title = "foo",
      data = self.png_data, # just to check priorities
      content_type = "image/jpeg",
      portal_type = "Image",
    ), '.jpg')

  def test_twoFileImportExportForImageNotIdentifyingType(self):
    """
      Test Business Template Import And Export With Image In Image Module
      where extension is not identified, so it is exported as '.bin'
    """
    self._checkTwoFileImportExportForImageInImageModule(dict(
      title = "foo",
      data = b"malformed data",
      portal_type = "Image",
    ), '.bin')

  def _checkTwoFileImportExportForDocumentInDocumentModule(self,
                                                            file_document_kw,
                                                            extension):
    file_page = self.portal.document_module.newContent(**file_document_kw)
    file_document_kw['id'] = file_id = file_page.getId()

    self.template.edit(template_path_list=['document_module/'+file_id,])

    file_document_path = os.path.join(self.export_dir,
                                     'PathTemplateItem', 'document_module',
                                      file_id)

    try:
      args = file_document_kw['data'], (b'data',) if extension else ()
    except KeyError:
      args = None, ('data',)
    import_template = self._exportAndReImport(
                                  file_document_path,
                                  extension,
                                  *args)

    self.portal.document_module.manage_delObjects([file_id])

    import_template.install()

    file_page = self.portal.document_module[file_id]

    for property_id, property_value in six.iteritems(file_document_kw):
      self.assertEqual(getattr(file_page, property_id), property_value)

  def test_twoFileImportExportForFileIdentifyingTypeByContentTypeJS(self):
    """
      Test Business Template Import And Export With File
      where extension (.js) is identified by the content_type
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"a test file",
      content_type = "text/javascript",
      portal_type = "File",
    ), '.js')

  def test_twoFileImportExportForFileIdentifyingTypeByContentTypeObj(self):
    """
      Test Business Template Import And Export With File
      where extension (.bin) is identified by the content_type
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"a test file",
      content_type = "application/octet-stream",
      portal_type = "File",
    ), '.bin')

  def test_twoFileImportExportForFileIdentifyingTypeByContentTypeEpub(self):
    """
      Test Business Template Import And Export With File
      where extension (.epub) is identified by the content_type
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"a test file",
      content_type = "application/epub+zip",
      portal_type = "File",
    ), '.epub')

  def test_twoFileImportExportForFileIdentifyingTypeByTitleJS(self):
    """
      Test Business Template Import And Export With File
      where extension (.js) is identified by the title
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo.js",
      data = b"a test file",
      portal_type = "File",
    ), '.js')

  def test_twoFileImportExportForFileIdentifyingTypeByReferenceJS(self):
    """
      Test Business Template Import And Export With File
      where extension (.js) is identified by the reference
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"<script> ... </script>",
      default_reference = "foo.js",
      portal_type = "File",
    ), '.js')

  def test_twoFileImportExportForFileNotIdentifyingTypeEmptyContentType(self):
    """
      Test Business Template Import And Export With File
      where extension is not identified, so it is exported as .bin
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"a test file",
      content_type = None,
      portal_type = "File",
    ), '.bin')

  def test_twoFileImportExportForFileNotIdentifyingTypeBinaryContentType(self):
    """
      Test Business Template Import And Export With File
      where extension is not identified by content_type (video/wavelet)
      but it is identified as binary in the mimetypes_registry so it is
      exported as .bin.
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"a test file",
      content_type = "video/wavelet",
      portal_type = "File",
    ), '.bin')

  def test_twoFileImportExportForFileNotIdentifyingTypeNonBinaryContentType(self):
    """
      Test Business Template Import And Export With File
      where extension is not identified by content_type (text/x-uri)
      but it is identified as non-binary in the mimetypes_registry so it is
      exported as .txt.
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"a test file",
      content_type = "text/x-uri",
      portal_type = "File",
    ), '.txt')

  def test_twoFileImportExportForFileIdentifyingTypeByTitleXML(self):
    """
      Test Business Template Import And Export With File in portal skins
      where extension (.xml, exported as ._xml to avoid conflict with the meta-data file)
      is identified by the title
    """
    file_content = b"""<person>
<name>John</name>
<surname>Doe</surname>
</person>
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo.xml",
      data = file_content,
      content_type = None,
      portal_type = "File",
    ), '._xml')

  def test_twoFileImportExportForFileInPortalSkinsIdentifyingTypeByTitleXML(self):
    """
      Test Business Template Import And Export With File in portal skins
      where extension (.xml, exported as ._xml to avoid conflict with the meta-data file)
      is identified by the title
    """
    file_content = b"""<person>
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

    file_document_path = os.path.join(self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                              skin_folder_id,test_file_id)

    import_template = self._exportAndReImport(
                                  file_document_path,
                                  "._xml",
                                  file_document_kw["data"],
                                  ['data'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([test_file_id])

    import_template.install()

    file_page = self.portal.portal_skins[skin_folder_id][test_file_id]

    for property_id, property_value in six.iteritems(file_document_kw):
      self.assertEqual(getattr(file_page, property_id), property_value)

  def test_twoFileImportExportForPDF(self):
    """Test Business Template Import And Export With A PDF Document"""
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo.pdf",
      data =b"pdf content, maybe should update for base64 sample" ,
      portal_type = "PDF",
    ), '.pdf')

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

    method_document_path = os.path.join(self.export_dir,
                                     'CatalogMethodTemplateItem',
                                     'portal_catalog',
                                      catalog_id, method_id)

    import_template = self._exportAndReImport(
                                  method_document_path,
                                  ".sql",
                                  b'dummy_method_template',
                                  ['src'])

    catalog.manage_delObjects([method_id])

    import_template.install()

    method_page = catalog[method_id]

    for property_id, property_value in six.iteritems(method_document_kw):
      self.assertEqual(getattr(method_page, property_id), property_value)

  def test_twoFileImportExportForERP5SQLMethodInCatalog(self):
    """Test Business Template Import And Export With ERP5 SQL Method In Catalog"""
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

    addSQLMethod = catalog.newContent
    addSQLMethod(portal_type='SQL Method', id=method_id,
                 title='dummy_method_title',
                 connection_id='erp5_sql_connection',
                 arguments_src = 'args',
                 src='dummy_method_template',
                )
    zsql_method = catalog._getOb(method_id, None)
    self.assertTrue(zsql_method is not None)

    self.template.edit(template_catalog_method_id_list=[catalog_id+'/'+method_id])
    self._buildAndExportBusinessTemplate()

    method_document_path = os.path.join(self.export_dir,
                                     'CatalogMethodTemplateItem',
                                     'portal_catalog',
                                      catalog_id, method_id)

    import_template = self._exportAndReImport(
                                  method_document_path,
                                  ".sql",
                                  b'dummy_method_template',
                                  ['src'])

    catalog.manage_delObjects([method_id])

    import_template.install()

    method_page = catalog[method_id]

    for property_id, property_value in six.iteritems(method_document_kw):
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

    method_document_path = os.path.join(self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                              skin_folder_id, method_id)
    import_template = self._exportAndReImport(
                                  method_document_path,
                                  ".sql",
                                  b'dummy_method_template',
                                  ['src'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([method_id])

    import_template.install()

    method_page = skin_folder[method_id]

    for property_id, property_value in six.iteritems(method_document_kw):
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
    page_template_text = '<?xml version="1.0"?><foo/>'
    page_template_kw = {"id": page_template_id,
                         "_text": page_template_text,
                         "content_type": "text/xml",
                         "output_encoding": "utf-8"}
    skin_folder._setObject(page_template_id, ZopePageTemplate(
      page_template_id, page_template_text, page_template_kw["content_type"]))

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+page_template_id,])

    page_template_path = os.path.join(self.export_dir,
      'SkinTemplateItem', 'portal_skins', skin_folder_id, page_template_id)

    import_template = self._exportAndReImport(
                                  page_template_path,
                                  ".zpt",
                                  page_template_kw['_text'].encode(),
                                  ['_text'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([page_template_id])

    import_template.install()

    page_template_page = self.portal.portal_skins[skin_folder_id][page_template_id]

    for property_id, property_value in six.iteritems(page_template_kw):
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

    dtml_method_path = os.path.join(self.export_dir,
                                    'SkinTemplateItem',
                                    'portal_skins',
                                    skin_folder_id,dtml_method_id)

    import_template = self._exportAndReImport(
                                  dtml_method_path,
                                  ".js",
                                  dtml_method_kw['raw'].encode(),
                                  ['raw'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([dtml_method_id])

    import_template.install()

    dtml_method_page = self.portal.portal_skins[skin_folder_id][dtml_method_id]

    for property_id, property_value in six.iteritems(dtml_method_kw):
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

    dtml_method_path = os.path.join(self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                              skin_folder_id,dtml_method_id)

    import_template = self._exportAndReImport(
                                  dtml_method_path,
                                  ".txt",
                                  dtml_method_kw['raw'].encode(),
                                  ['raw'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([dtml_method_id])

    import_template.install()

    dtml_method_page = self.portal.portal_skins[skin_folder_id][dtml_method_id]

    for property_id, property_value in six.iteritems(dtml_method_kw):
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
    OOo_template_data = u'dummy OOotemplate content …'

    OOo_template_kw = {"id": OOo_template_id,
                         "_text": OOo_template_data,
                         "output_encoding": "utf-8",
                         "content_type": "text/html"}

    from Products.ERP5OOo.OOoTemplate import OOoTemplate
    skin_folder._setObject(OOo_template_id,
      OOoTemplate(OOo_template_id, OOo_template_data, content_type=''))

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+OOo_template_id,])

    key = os.path.join('portal_skins', skin_folder_id, OOo_template_id)
    OOo_template_path = os.path.join(self.export_dir, 'SkinTemplateItem', key)

    import_template = self._exportAndReImport(
                                  OOo_template_path,
                                  ".oot",
                                  OOo_template_data.encode('utf-8'),
                                  ['_text'])

    self.assertIs(type(import_template._skin_item._objects[key]._text),
                  type(skin_folder[OOo_template_id]._text))

    self.portal.portal_skins[skin_folder_id].manage_delObjects([OOo_template_id])

    import_template.install()

    OOo_template_page = self.portal.portal_skins[skin_folder_id][OOo_template_id]

    for property_id, property_value in six.iteritems(OOo_template_kw):
      self.assertEqual(getattr(OOo_template_page, property_id), property_value)

  def test_twoFileImportExportForSpreadsheetNotIdentifyingType(self):
    """
      Test Business Template Import And Export With Spreadsheed where the
      extension is not identified, so it is exported as '.bin'
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"", # XXX dummy data in data leads to 'NotConvertedError'
      portal_type = "Spreadsheet",
    ), '.bin')

  def test_twoFileImportExportForSpreadsheetIdentifyingTypeByContentType(self):
    """
      Test Business Template Import And Export With Spreadsheed where the
      extension is identified by content_type, so it is exported as '.ods'
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = b"", # XXX dummy data in data leads to 'NotConvertedError'
      content_type = "application/vnd.oasis.opendocument.spreadsheet",
      portal_type = "Spreadsheet",
    ), '.ods')

  def test_twoFileImportExportForSpreadsheetIdentifyingTypeByTitle(self):
    """
      Test Business Template Import And Export With Spreadsheed where the
      extension is identified by title, so it is exported as '.xlsx'
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo.xlsx",
      data = b"", # XXX dummy data in data leads to 'NotConvertedError'
      portal_type = "Spreadsheet",
    ), '.xlsx')

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

    test_page_document_path = os.path.join(self.export_dir,
                                     'PathTemplateItem', 'test_page_module',
                                      test_page_id)

    import_template = self._exportAndReImport(
                                  test_page_document_path,
                                  ".html",
                                  test_page_data_kw["text_content"].encode(),
                                  ["text_content"])

    self.portal.test_page_module.manage_delObjects([test_page_id])

    import_template.install()

    test_page = self.portal.test_page_module[test_page_id]

    for property_id, property_value in six.iteritems(test_page_data_kw):
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

    python_script_path = os.path.join(self.export_dir,
      'SkinTemplateItem', 'portal_skins',skin_folder_id,python_script_id)


    import_template = self._exportAndReImport(
                                  python_script_path,
                                  ".py",
                                  python_script_kw["_body"].encode(),
                                  ['_body','_code'])

    self.portal.portal_skins[skin_folder_id].manage_delObjects([python_script_id])

    import_template.install()

    python_script_page = self.portal.portal_skins[skin_folder_id][python_script_id]

    for property_id, property_value in six.iteritems(python_script_kw):
      self.assertEqual(getattr(python_script_page, property_id), property_value)

  def test_templateFolderIsCleanedUpInImportAndReexport(self):
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

    test_component_path = os.path.join(self.export_dir,
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
    self.template_tool.importAndReExportBusinessTemplateListFromPath(
      repository_list=[tests_home])
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
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      content_type = "text/javascript",
      portal_type = "File",
    ), None)

  def test_twoFileImportExportForFileWithNullData(self):
    """
      Test Business Template Import And Export with File with data=None,
      in which case there's nothing exported as a separate file.
    """
    self._checkTwoFileImportExportForDocumentInDocumentModule(dict(
      title = "foo",
      data = None,
      content_type = "text/javascript",
      portal_type = "File",
    ), None)

  def test_twoFileImportExportForZopePageTemplateISO_8859_15(self):
    """
      Test Business Template Import And Export With ZopePageTemplate with
      output_encoding iso-8859-15. Test checks that the encoding
      does not change on export
    """
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].\
                                  manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    page_template_id = 'dummy_page_template'
    page_template_text = '<html></html>'
    page_template_kw = {"id": page_template_id,
                         "_text": page_template_text,
                         "content_type": "text/html",
                         "output_encoding": "iso-8859-15"}
    skin_folder._setObject(page_template_id, ZopePageTemplate(
      page_template_id, page_template_text, page_template_kw["content_type"]))
    skin_folder._getOb(page_template_id).manage_changeProperties(
      output_encoding=page_template_kw["output_encoding"])

    self.template.edit(template_skin_id_list=[skin_folder_id+'/'+page_template_id,])

    page_template_path = os.path.join(self.export_dir,
      'SkinTemplateItem', 'portal_skins',
      skin_folder_id, page_template_id)

    self.template.build()
    self.template.export(path=self.export_dir, local=True)

    # check that .xml and .zpt were exported
    self.assertTrue(os.path.exists(page_template_path + '.xml'))
    self.assertTrue(os.path.exists(page_template_path + '.zpt'))

    # check that the encoding value on the .xml file is iso-8859-15
    root = etree.parse(page_template_path + '.xml').getroot()
    self.assertEqual('iso-8859-15',
      root.xpath('.//item[key/string[.="output_encoding"]]/value/string')[0].text)

    # delete the business template and the zope page templatefrom the portal
    self.template_tool.manage_delObjects(self.template.getId())
    self.portal.portal_skins[skin_folder_id].manage_delObjects([page_template_id])

    # import the business template from the file-system
    import_template = self.template_tool.download(url='file:'+self.export_dir)
    self.assertFalse(import_template is None)
    self.assertEqual(import_template.getPortalType(), 'Business Template')

    # delete all elements from the export directory
    file_object_list = [x for x in os.listdir(self.export_dir)]
    for file_object in file_object_list:
      file_object_path = os.path.join(self.export_dir, file_object)
      if os.path.isfile(file_object_path):
        os.unlink(file_object_path)
      else:
        shutil.rmtree(file_object_path)
    # check that export directory is empty
    self.assertEqual(os.listdir(self.export_dir), [])

    # install the imported business template
    import_template.install()

    # check that the page template has the expected attributes
    # but the installed version encoding is utf-8
    page_template = self.portal.portal_skins[skin_folder_id][page_template_id]
    for property_id, property_value in six.iteritems(page_template_kw):
      self.assertEqual(getattr(page_template, property_id), property_value)

    # uninstall and export the business template
    import_template.uninstall()
    import_template.export(path=self.export_dir, local=True)

    # check that .xml and .zpt were exported
    self.assertTrue(os.path.exists(page_template_path + '.xml'))
    self.assertTrue(os.path.exists(page_template_path + '.zpt'))

    # check that the encoding value on the .xml file is iso-8859-15
    root = etree.parse(page_template_path + '.xml').getroot()
    self.assertEqual('iso-8859-15',
      root.xpath('.//item[key/string[.="output_encoding"]]/value/string')[0].text)

  def test_twoFileImportExportPreinstallForPythonScript(self):
    """
      Check that preinstall works correctly in
      the two file export case for PythonScript
    """
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
    python_script.ZPythonScript_edit('', "foo")

    self.template.edit(template_skin_id_list=['%s/%s' % (skin_folder_id, python_script_id)])

    python_script_path = os.path.join(self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',
                                             skin_folder_id,python_script_id)

    self.template.build()
    self.tic()
    self.template.export(path=self.export_dir, local=True)

    # check that PythonScript was exported as two files
    self.assertTrue(os.path.exists('%s.xml' % python_script_path))
    self.assertTrue(os.path.exists('%s.py' % python_script_path))

    self.template.install()
    self.tic()

    import_template = self.template_tool.download(url='file:'+self.export_dir)

    # check that preinstalling the import_template no difference is found
    result = import_template.preinstall()
    self.assertEqual(result, {})

    # edit python PythonScript code
    self.portal.portal_skins[skin_folder_id][python_script_id]._body = "bar"

    # check that preinstalling the import_template still no difference is found
    # since the change was in the portal and not installed
    result = import_template.preinstall()
    self.assertEqual(result, {})

    import_template.build()
    import_template.install()
    self.tic()

    second_import_template = self.template_tool.download(
      url='file:'+self.export_dir)
    # check that preinstalling the second_import_template
    # the PythonScript is recognised as modified
    result = second_import_template.preinstall()
    self.assertEqual(result.get('portal_skins/%s/%s' % (skin_folder_id, python_script_id)),
                      ('Modified', 'Skin'))
