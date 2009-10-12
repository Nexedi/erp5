##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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

import unittest
import os
from zLOG import LOG

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime

class TestScribusUtils(ERP5TypeTestCase):
  '''Unit test for SribusUtils API'''

  run_all_test = True
  username = 'rc'

  def getTitle(self):
    return "PDF Editor"

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdf_editor')

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Manager'], [])
    user = uf.getUserById(self.username).__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    self.login()

  def makeFileUpload(self, filename):
    return FileUpload(
            os.path.join(os.path.dirname(__file__),
            'data', filename), 'rb')

  def test_01_SimpleModuleCreation(self):
    '''Just create a module using scribus file and pdf file with minimal 
    option'''

    self.portal.ERP5Site_createModuleScribus(
                  module_portal_type="Dummy Module",
                  portal_skins_folder="erp5_test",
                  object_portal_type="Dummy",
                  object_title="Dummy",
                  module_id="dummy_module",
                  module_title="Dummy Module Title",
                  import_pdf_file=self.makeFileUpload('test_1.pdf'),
                  import_scribus_file=self.makeFileUpload('test_1.sla'),)

    self.assertNotEqual(self.portal._getOb('dummy_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_test", None), None)
    self.assertEquals("Dummy Module Title",
                      self.portal.dummy_module.getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy Module"),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy"), None)


  def test_02_ModuleCreationWithBackground(self):
    '''Create a module with the option_html. That mean, a background will be
    generated (using convert), and a css file created'''

    self.portal.ERP5Site_createModuleScribus(
              self,
              option_html=1,
              desired_width=800,
              desired_height=1132,
              module_portal_type="Dummy Module",
              portal_skins_folder="erp5_test",
              object_portal_type="Dummy",
              object_title="Dummy",
              module_id="dummy_module",
              module_title="Dummy Module Title",
              import_pdf_file=self.makeFileUpload('test_background.pdf'),
              import_scribus_file=self.makeFileUpload('test_background.sla'),)

    self.assertNotEqual(self.portal._getOb('dummy_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_test", None), None)
    self.assertEquals("Dummy Module Title",
                      self.portal.dummy_module.getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy Module"),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy"), None)

    # test the background existense
    skin_folder = self.portal.portal_skins._getOb("erp5_test", None)
    background_object = getattr(skin_folder,'Dummy_background_0', None)
    self.assertNotEquals(background_object, None)


  def test_03_ModuleListBox(self):
    '''Check the module listBox could be rendered without errors'''

    self.portal.ERP5Site_createModuleScribus(
                  module_portal_type="Dummy Module",
                  portal_skins_folder="erp5_test",
                  object_portal_type="Dummy",
                  object_title="Dummy",
                  module_id="dummy_module",
                  module_title="Dummy Module Title",
                  import_pdf_file=self.makeFileUpload('test_1.pdf'),
                  import_scribus_file=self.makeFileUpload('test_1.sla'),)
    # a form is created for the module
    form = self.portal.portal_skins.erp5_test._getOb(
                                      'DummyModule_viewDummyList', None)
    self.assertNotEquals(form, None)
    self.assertEquals(form.pt, 'form_list')
    self.assertTrue(hasattr(form, 'listbox'))
    # listbox is in bottom group
    self.assertTrue('listbox' in [field.getId() for field in 
                                  form.get_fields_in_group('bottom')])
    # the listbox managment screen can be accessed without error
    form.listbox.manage_main()
    # After we call changeSkin() so that portal_skins realize we have a new
    # skin folder, the listbox can be used to render the module without error
    self.portal.changeSkin(None)
    self.portal.dummy_module.DummyModule_viewDummyList()

  def test_04_SimpleModuleUpdate(self):
    ''' Update a module created with a scribus file and pdf file.
        Change a field name in the new scribus file, and check that after 
        update, the ERP5 StringField have the new name.'''

    # first module creation:
    self.portal.ERP5Site_createModuleScribus(
                  module_id="dummy_module",
                  module_portal_type="Dummy Module",
                  module_title="Dummy Module Title",
                  import_pdf_file=self.makeFileUpload('test_1.pdf'),
                  import_scribus_file=self.makeFileUpload('test_1.sla'),
                  portal_skins_folder="erp5_test",
                  object_title="Dummy",
                  object_portal_type="Dummy")

    self.assertNotEqual(self.portal._getOb('dummy_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_test", None), None)
    self.assertEquals("Dummy Module Title",
                      self.portal.dummy_module.getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy Module"),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy"), None)

    # check that a field with title text_1 (present in the sla file) 
    # has been created in the form
    self.assertNotEquals(getattr(self.portal.portal_skins.erp5_test.Dummy_view,
      'text_1', None), None)


    # Update the ERP5Form, scribus, PDFForm, css and background picture
    self.portal.ERP5Site_updateModuleScribus(
                  self,
                  import_pdf_file=self.makeFileUpload('test_1.pdf'),
                  import_scribus_file=self.makeFileUpload('test_2.sla'),
                  object_portal_type="Dummy")

    # check that the modified field with title text_couscous (present in the
    # new sla file) has been created in the form
    self.assertNotEquals(getattr(self.portal.portal_skins.erp5_test.Dummy_view,
      'text_couscous', None), None)
    # the old field text_1 must have been removed
    self.assertEquals(getattr(self.portal.portal_skins.erp5_test.Dummy_view,
      'text_1', None), None)

  def test_05_requiredFields(self):
    ''' Set required property on a scribus field. After creating module with
    scribus, the ERP5 field should have the required property set on.'''

    # module creation using scribus file containing fields with requied
    # property set:
    self.portal.ERP5Site_createModuleScribus(
          module_id="dummy_module",
          module_portal_type="Dummy Module",
          module_title="Dummy Module Title",
          import_pdf_file=self.makeFileUpload('test_field_properties.pdf'),
          import_scribus_file=self.makeFileUpload('test_field_properties.sla'),
          portal_skins_folder="erp5_test",
          object_title="Dummy",
          object_portal_type="Dummy")

    self.assertNotEqual(self.portal._getOb('dummy_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_test", None), None)
    self.assertEquals("Dummy Module Title",
                      self.portal.dummy_module.getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy Module"),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy"), None)

    # define some field lists
    required_field_name_list = ['my_required_string_field',
                                'my_required_date']
    not_required_field_name_list = [ 'my_simple_string_field', 
                                     'my_simple_date']
    all_field_name_list = required_field_name_list + \
                                        not_required_field_name_list

    # check the that fields prensent in the sla file have been created in the
    # erp5 form
    form = self.portal.portal_skins.erp5_test.Dummy_view
    for field_name in all_field_name_list:
      self.assertNotEquals(getattr(form, field_name, None), None)

    # check the required fields are required :
    for field_name in required_field_name_list:
      field = getattr(form, field_name, None)
      self.assertEquals(field.values['required'], 1)

    # check fields not required are not :
    for field_name in not_required_field_name_list:
      field = getattr(form, field_name, None)
      self.assertNotEquals(field.values['required'], 1)

  def test_06_readOnlyFields(self):
    '''check the read_only fields are really read_only'''
    # module creation using scribus file containing fields with read only
    # property set:
    self.portal.ERP5Site_createModuleScribus(
          module_id="dummy_module",
          module_portal_type="Dummy Module",
          module_title="Dummy Module Title",
          import_pdf_file=self.makeFileUpload('test_field_properties.pdf'),
          import_scribus_file=self.makeFileUpload('test_field_properties.sla'),
          portal_skins_folder="erp5_test",
          object_title="Dummy",
          object_portal_type="Dummy")

    self.assertNotEqual(self.portal._getOb('dummy_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_test", None), None)
    self.assertEquals("Dummy Module Title",
                      self.portal.dummy_module.getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy Module"),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Dummy"), None)

    # define some field lists
    read_only_field_name_list = ['my_read_only_string_field',
                                'my_read_only_date']
    not_read_only_field_name_list = [ 'my_simple_string_field', 
                                     'my_simple_date']
    all_field_name_list = read_only_field_name_list + \
                                        not_read_only_field_name_list

    # check the that fields prensent in the sla file have been created in the
    # erp5 form
    form = self.portal.portal_skins.erp5_test.Dummy_view
    for field_name in all_field_name_list:
      self.assertNotEquals(getattr(form, field_name, None), None)

    # check the read_only fields are read_only :
    for field_name in read_only_field_name_list:
      field = getattr(form, field_name, None)
      self.assertEquals(field.values['editable'], 0)

    # check fields not read_only are not :
    for field_name in not_read_only_field_name_list:
      field = getattr(form, field_name, None)
      self.assertEquals(field.values['editable'], 1)

  def test_07_DateTimeFieldWithModuleCreation(self):
    '''test DateTime format'''

    self.portal.ERP5Site_createModuleScribus(
                  option_html=1,
                  desired_width=800,
                  desired_height=600,
                  module_portal_type="Authorisation Module",
                  portal_skins_folder="erp5_authorisation",
                  object_portal_type="Authorisation",
                  object_title="Authorisation",
                  module_id="authorisation_module",
                  module_title="Authorisation Module Title",
                import_pdf_file=self.makeFileUpload('Authorisation.pdf'),
                import_scribus_file=self.makeFileUpload('Authorisation.sla'),)
    portal = self.getPortal()
    portal_types = self.portal.portal_types
    self.assertNotEqual(self.portal._getOb('authorisation_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_authorisation", None), None)
    self.assertEquals("Authorisation Module Title",
                      self.portal.authorisation_module.getTitle())
    module_portal_type = portal_types.getTypeInfo("Authorisation Module")
    self.assertNotEqual(module_portal_type, None)
    self.assertNotEqual(portal_types.getTypeInfo("Authorisation"), None)
    # Create an Authorisation
    # add property sheet Task in portal type Authorisation
    self.portal.portal_types.Authorisation._setTypePropertySheet('Task')
    authorisation_module = self.portal.authorisation_module
    start_date = DateTime('2000/01/01')
    stop_date = DateTime('2001/01/01 12:00 GMT')
    authorisation = authorisation_module.newContent(\
          portal_type='Authorisation',
          title = 'Mum Dad',
          start_date = start_date,
          stop_date = stop_date
        )

    form = self.portal.portal_skins.erp5_authorisation.Authorisation_view
    # test property input_order on all DateTimeField
    input_order_other_date = form.my_other_date.get_value('input_order')
    input_order_start_date = form.my_start_date.get_value('input_order')
    input_order_stop_date = form.my_stop_date.get_value('input_order')
    self.assertEqual(input_order_other_date,'ymd')
    self.assertEqual(input_order_start_date,'dmy')
    self.assertEqual(input_order_stop_date,'ymd')
    # test result of expression TALES with DateTimeField
    form = self.portal.portal_skins.erp5_authorisation
    pdf = form.Authorisation_viewAuthorisationAsPdf
    cell_name_other_date = pdf.getCellNames()[0]
    cell_name_start_date = pdf.getCellNames()[1]
    cell_name_stop_date = pdf.getCellNames()[2]
    tales_expr_other_date = pdf.getCellTALES(cell_name_other_date)
    tales_expr_start_date = pdf.getCellTALES(cell_name_start_date)
    tales_expr_stop_date = pdf.getCellTALES(cell_name_stop_date)
    from Products.CMFCore.Expression import Expression
    from Products.CMFCore.Expression import getExprContext
    expr_other_date = Expression(tales_expr_other_date)
    expr_start_date = Expression(tales_expr_start_date)
    expr_stop_date = Expression(tales_expr_stop_date)
    result_other_date = expr_other_date(getExprContext(authorisation, 
                                                       authorisation))
    result_start_date = expr_start_date(getExprContext(authorisation, 
                                                       authorisation))
    result_stop_date = expr_stop_date(getExprContext(authorisation, 
                                                     authorisation))
    self.assertEquals(result_other_date, '')
    self.assertEquals(result_start_date, start_date.strftime('%d/%m/%Y'))
    self.assertEquals(result_stop_date, stop_date.strftime('%Y/%m/%d %H:%M'))

  def test_08_ModuleCreationWithoutField(self):
    '''check it's possible to create a module using an empty scribus file without errors'''
    self.portal.ERP5Site_createModuleScribus(
            module_portal_type="Empty Module",
            portal_skins_folder="erp5_empty",
            object_portal_type="Empty",
            object_title="Empty",
            module_id="empty_module",
            module_title="Empty Module Title",
            import_pdf_file=self.makeFileUpload('test_without_field.pdf'),
            import_scribus_file=self.makeFileUpload('test_without_field.sla'),)
    self.assertNotEqual(self.portal._getOb('empty_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_empty", None), None)
    self.assertEquals("Empty Module Title",
                      self.portal.empty_module.getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Empty Module"),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Empty"), None)
    form = self.portal.portal_skins.erp5_empty.Empty_view
    self.assertEquals(0, len(form.objectValues()))

  def test_09_creationRadioField(self):
    '''check it's possible to put a field radioField in ERP5 Form created with
    scribus.
       Create a RadioField if possible only when you use ERP5 Form rendering
       and not graphic rendering
       RadioField with 3 items : young, adult and senior
    '''
    self.portal.ERP5Site_createModuleScribus(
            module_portal_type="Radio Module",
            portal_skins_folder="erp5_radio",
            object_portal_type="Radio",
            object_title="Radio",
            module_id="radio_module",
            module_title="Radio Module Title",
            import_pdf_file=self.makeFileUpload('test_RadioField.pdf'),
            import_scribus_file=self.makeFileUpload('test_RadioField.sla'),)
    self.assertNotEqual(self.portal._getOb('radio_module', None), None)
    self.assertNotEqual(
        self.portal.portal_skins._getOb("erp5_radio", None), None)
    self.assertEquals("Radio Module Title",
                      self.portal.radio_module.getTitle())
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Radio Module"),
                        None)
    self.assertNotEqual(self.portal.portal_types.getTypeInfo("Radio"), None)
    form = self.portal.portal_skins.erp5_radio.Radio_view
    field_radio = form.my_radio
    self.assertEquals(3,
                      len(field_radio.get_value('items')))
    items_list = [('young', 'Young'), ('adult', 'Adult'), ('senior', 'Senior')]
    self.assertEquals(items_list, field_radio.get_value('items'))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestScribusUtils))
  return suite
