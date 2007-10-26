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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from AccessControl.SecurityManagement import newSecurityManager

class TestCreateModuleScribus(ERP5TypeTestCase):
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

  def test_SimpleModuleCreation(self):
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


  def test_ModuleListBox(self):
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


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCreateModuleScribus))
  return suite
