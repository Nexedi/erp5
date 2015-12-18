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

  def afterSetUp(self):
    self.cfg = getConfiguration()
    self.export_dir = tempfile.mkdtemp()

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

  def _buildAndExportBusinessTemplate(self, template, export_dir):
    self.tic()
    template.build()
    self.tic()

    template.export(path=export_dir, local=True)
    self.tic()

  def _importBusinessTemplate(self, template, export_dir, template_tool, cfg):
    template_id = template.getId()
    template_path = os.path.join(cfg.instancehome, export_dir)
    template_tool.manage_delObjects(template_id)

    import_template = template_tool.download(url='file:'+template_path)

    self.assertFalse(import_template is None)
    self.assertEqual(import_template.getPortalType(), 'Business Template')

    return import_template

  def test_twoFileImportExportForTestDocument(self):
    """Test Business Template Import And Export With Test Document"""
    template_tool = self.getTemplateTool()
    template = self._createNewBusinessTemplate(template_tool)

    test_component_kw = {"title": "foo",
                         "text_content": "def dummy(): pass",
                         "portal_type": "Test Component"}

    test_document_page = self.portal.portal_components.newContent(**test_component_kw)
    test_component_kw['id'] = test_component_id = test_document_page.getId()

    template.edit(template_test_id_list=['portal_components/'+test_component_id,])

    self._buildAndExportBusinessTemplate(template, self.export_dir)

    test_component_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                       'TestTemplateItem', 'portal_components')
    xml_document_path = os.path.join(test_component_path, test_component_id+'.xml')
    test_document_path = os.path.join(test_component_path, test_component_id+'.py')

    self.assertTrue(os.path.exists(xml_document_path))
    self.assertTrue(os.path.exists(test_document_path))
    test_file=open(test_document_path,'r+')
    self.assertEqual(test_file.read(), test_component_kw["text_content"])
    xml_file=open(xml_document_path,'r+')
    self.assertFalse('<string>text_content</string>' in xml_file.read())

    import_template = self._importBusinessTemplate(template, self.export_dir, template_tool, self.cfg)

    self.portal.portal_components.manage_delObjects([test_component_id])

    import_template.install()

    test_page = self.portal.portal_components[test_component_id]

    for property_id, property_value in test_component_kw.iteritems():
      self.assertEqual(test_page.getProperty(property_id), property_value)

  def test_twoFileImportExportForWebPage(self):
    """Test Business Template Import And Export With Web Page"""
    template_tool = self.getTemplateTool()
    template = self._createNewBusinessTemplate(template_tool)

    html_document_kw = {"title": "foo", "text_content": "<html></html>",
                        "portal_type": "Web Page"}
    html_page = self.portal.web_page_module.newContent(**html_document_kw)
    js_document_kw = {"title": "foo", "text_content": "// JavaScript",
                      "portal_type": "Web Script"}
    js_page = self.portal.web_page_module.newContent(**js_document_kw)
    css_document_kw = {"title": "foo", "text_content": "<style></style>",
                       "portal_type": "Web Style"}
    css_page = self.portal.web_page_module.newContent(**css_document_kw)
    html_document_kw['id'] = html_file_id = html_page.getId()
    js_document_kw['id'] = js_file_id = js_page.getId()
    css_document_kw['id'] = css_file_id = css_page.getId()

    template.edit(template_path_list=['web_page_module/'+html_file_id,
                                      'web_page_module/'+js_file_id,
                                      'web_page_module/'+css_file_id,])

    self._buildAndExportBusinessTemplate(template, self.export_dir)

    web_page_module_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                        'PathTemplateItem', 'web_page_module')

    for web_file in [(html_file_id, '.html', html_document_kw),
                     (js_file_id, '.js', js_document_kw),
                     (css_file_id, '.css', css_document_kw)]:
      xml_document_path = os.path.join(web_page_module_path, web_file[0]+'.xml')
      file_document_path = os.path.join(web_page_module_path, web_file[0]+web_file[1])
      self.assertTrue(os.path.exists(xml_document_path))
      self.assertTrue(os.path.exists(file_document_path))
      file_content=open(file_document_path,'r+')
      self.assertEqual(file_content.read(), web_file[2]["text_content"])
      xml_file=open(xml_document_path,'r+')
      self.assertFalse('<string>text_content</string>' in xml_file.read())

    import_template = self._importBusinessTemplate(template, self.export_dir, template_tool, self.cfg)

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
    template_tool = self.getTemplateTool()
    template = self._createNewBusinessTemplate(template_tool)
    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    python_script_id = 'dummy_test_script'
    if python_script_id in skin_folder.objectIds():
      skin_folder.manage_delObjects([python_script_id])
    skin_folder.manage_addProduct['PythonScripts'].manage_addPythonScript(id = python_script_id)
    python_script = skin_folder[python_script_id]
    python_script.ZPythonScript_edit('', "context.setTitle('foo')")

    python_script_kw = {"_body": "context.setTitle('foo')\n",}

    template.edit(template_skin_id_list=[skin_folder_id+'/'+python_script_id,])

    self._buildAndExportBusinessTemplate(template, self.export_dir)

    python_script_module_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',skin_folder_id)
    xml_document_path = os.path.join(python_script_module_path, python_script_id+'.xml')
    python_script_path = os.path.join(python_script_module_path, python_script_id+'.py')

    self.assertTrue(os.path.exists(xml_document_path))
    self.assertTrue(os.path.exists(python_script_path))
    python_script_file=open(python_script_path,'r+')
    self.assertEqual(python_script_file.read(), python_script_kw["_body"])
    xml_file=open(xml_document_path,'r+')
    xml_file_content = xml_file.read()
    self.assertFalse('<string>_body</string>' in xml_file_content)
    self.assertFalse('<string>_code</string>' in xml_file_content)

    import_template = self._importBusinessTemplate(template, self.export_dir, template_tool, self.cfg)

    self.portal.portal_skins[skin_folder_id].manage_delObjects([python_script_id])

    import_template.install()

    python_script_page = self.portal.portal_skins[skin_folder_id][python_script_id]

    python_script_content = python_script_page.read()
    self.assertTrue(python_script_content.endswith(python_script_kw['_body']))

  def test_twoFileImportExportForImage(self):
    """Test Business Template Import And Export With Image In Image Module"""
    image_data = """iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""
    template_tool = self.getTemplateTool()
    template = self._createNewBusinessTemplate(template_tool)

    image_document_kw = {"title": "foo", "data": image_data,
                         "portal_type": "Image"}

    image_page = self.portal.image_module.newContent(**image_document_kw)
    image_document_kw['id'] = image_file_id = image_page.getId()

    template.edit(template_path_list=['image_module/'+image_file_id,])

    self._buildAndExportBusinessTemplate(template, self.export_dir)

    image_module_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'PathTemplateItem', 'image_module')
    xml_document_path = os.path.join(image_module_path, image_file_id+'.xml')
    image_document_path = os.path.join(image_module_path, image_file_id+'.png')
    self.assertTrue(os.path.exists(xml_document_path))
    self.assertTrue(os.path.exists(image_document_path))
    image_file=open(image_document_path,'r+')
    self.assertEqual(image_file.read(), image_document_kw["data"])
    xml_file=open(xml_document_path,'r+')
    self.assertFalse('<string>data</string>' in xml_file.read())

    import_template = self._importBusinessTemplate(template, self.export_dir, template_tool, self.cfg)

    self.portal.image_module.manage_delObjects([image_file_id])

    import_template.install()

    image_page = self.portal.image_module[image_file_id]
    for property_id, property_value in image_document_kw.iteritems():
      self.assertEqual(image_page.getProperty(property_id), property_value)

  def test_twoFileImportExportForFile(self):
    """Test Business Template Import And Export With File"""
    template_tool = self.getTemplateTool()
    template = self._createNewBusinessTemplate(template_tool)

    file_content = "a test file"
    file_content_type = "text/javascript"
    file_title = "foo.js"
    file_document_kw = {"title": file_title, "data": file_content,
                        "content_type": file_content_type}


    skin_folder_id = 'dummy_test_folder'
    if skin_folder_id in self.portal.portal_skins.objectIds():
      self.portal.portal_skins.manage_delObjects([skin_folder_id])

    self.portal.portal_skins.manage_addProduct['OFSP'].manage_addFolder(skin_folder_id)
    skin_folder = self.portal.portal_skins[skin_folder_id]

    test_file_id = 'dummy_file_id'
    if test_file_id in self.portal.objectIds():
      self.portal.manage_delObjects([test_file_id])

    skin_folder.manage_addProduct['OFSP'].manage_addFile(id=test_file_id)
    zodb_file = skin_folder._getOb(test_file_id)
    zodb_file.manage_edit(title=file_title,
                          content_type=file_content_type,
                          filedata=file_content)

    template.edit(template_skin_id_list=[skin_folder_id+'/'+test_file_id,])

    self._buildAndExportBusinessTemplate(template, self.export_dir)

    file_module_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                             'SkinTemplateItem', 'portal_skins',skin_folder_id)

    xml_document_path = os.path.join(file_module_path, test_file_id+'.xml')
    file_document_path = os.path.join(file_module_path, test_file_id+'.js')
    self.assertTrue(os.path.exists(xml_document_path))
    self.assertTrue(os.path.exists(file_document_path))
    file_content=open(file_document_path,'r+')
    self.assertEqual(file_content.read(), file_document_kw["data"])
    xml_file=open(xml_document_path,'r+')
    self.assertFalse('<string>data</string>' in xml_file.read())

    import_template = self._importBusinessTemplate(template, self.export_dir, template_tool, self.cfg)

    self.portal.portal_skins[skin_folder_id].manage_delObjects([test_file_id])

    import_template.install()

    file_page = self.portal.portal_skins[skin_folder_id][test_file_id]
    # XXX do not like this check, to find a better way to
    # access keys and values for ImplicitAcquisitionWrapper
    for property_id, property_value in file_document_kw.iteritems():
      self.assertTrue(property_id in list(file_page.__dict__.keys()))
      self.assertTrue(property_value in file_page.__dict__.values())

  def test_twoFileImportExportForSpreadsheet(self):
    """Test Business Template Import And Export With A Spreadsheet Document"""
    spreadsheet_data = """spreadsheet content, maybe should update for base64 sample"""
    template_tool = self.getTemplateTool()
    template = self._createNewBusinessTemplate(template_tool)

    spreadsheet_document_kw = {"title": "foo.ods", "data": spreadsheet_data,
                         "portal_type": "Spreadsheet"}

    spreadsheet_page = self.portal.document_module.newContent(**spreadsheet_document_kw)
    spreadsheet_document_kw['id'] = spreadsheet_file_id = spreadsheet_page.getId()

    template.edit(template_path_list=['document_module/'+spreadsheet_file_id,])

    self._buildAndExportBusinessTemplate(template, self.export_dir)

    spreadsheet_module_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'PathTemplateItem', 'document_module')
    xml_document_path = os.path.join(spreadsheet_module_path, spreadsheet_file_id+'.xml')
    spreadsheet_document_path = os.path.join(spreadsheet_module_path, spreadsheet_file_id+'.ods')
    self.assertTrue(os.path.exists(xml_document_path))
    self.assertTrue(os.path.exists(spreadsheet_document_path))
    spreadsheet_file=open(spreadsheet_document_path,'r+')
    self.assertEqual(spreadsheet_file.read(), spreadsheet_document_kw["data"])
    xml_file=open(xml_document_path,'r+')
    self.assertFalse('<string>data</string>' in xml_file.read())

    import_template = self._importBusinessTemplate(template, self.export_dir, template_tool, self.cfg)

    self.portal.image_module.manage_delObjects([spreadsheet_file_id])

    import_template.install()

    spreadsheet_page = self.portal.document_module[spreadsheet_file_id]
    for property_id, property_value in spreadsheet_document_kw.iteritems():
      self.assertEqual(spreadsheet_page.getProperty(property_id), property_value)

  def test_twoFileImportExportForPDF(self):
    """Test Business Template Import And Export With A PDF Document"""
    pdf_data = """pdf content, maybe should update for base64 sample"""
    template_tool = self.getTemplateTool()
    template = self._createNewBusinessTemplate(template_tool)

    pdf_document_kw = {"title": "foo.pdf", "data": pdf_data,
                         "portal_type": "PDF"}

    pdf_page = self.portal.document_module.newContent(**pdf_document_kw)
    pdf_document_kw['id'] = pdf_file_id = pdf_page.getId()

    template.edit(template_path_list=['document_module/'+pdf_file_id,])

    self._buildAndExportBusinessTemplate(template, self.export_dir)

    pdf_module_path = os.path.join(self.cfg.instancehome, self.export_dir,
                                     'PathTemplateItem', 'document_module')
    xml_document_path = os.path.join(pdf_module_path, pdf_file_id+'.xml')
    pdf_document_path = os.path.join(pdf_module_path, pdf_file_id+'.pdf')
    self.assertTrue(os.path.exists(xml_document_path))
    self.assertTrue(os.path.exists(pdf_document_path))
    pdf_file=open(pdf_document_path,'r+')
    self.assertEqual(pdf_file.read(), pdf_document_kw["data"])
    xml_file=open(xml_document_path,'r+')
    self.assertFalse('<string>data</string>' in xml_file.read())

    import_template = self._importBusinessTemplate(template, self.export_dir, template_tool, self.cfg)

    self.portal.image_module.manage_delObjects([pdf_file_id])

    import_template.install()

    pdf_page = self.portal.document_module[pdf_file_id]
    for property_id, property_value in pdf_document_kw.iteritems():
      self.assertEqual(pdf_page.getProperty(property_id), property_value)
