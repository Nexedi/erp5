##############################################################################
#
# Copyright (c) 2002-2018 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
import transaction
import unittest
from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import ERP5TypeFunctionalTestCase

class TestFunctionalCorporateIdentityTemplateList(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "template_test_zuite"

  def getTitle(self):
    return 'Corporate Identity Classic UI Test'

  def getBusinessTemplateList(self):
    return (
      'erp5_base',
      'erp5_font',
      'erp5_web',
      'erp5_dms',
      'erp5_corporate_identity',
      'erp5_corporate_identity_test',
      'erp5_ui_test_core',
      'erp5_test_result'
    )

  def _removeZuite_SetSkipSaveScript(self):
    skin_folder = self.portal.portal_skins.custom
    if 'Zuite_setSkipSave' in skin_folder.objectIds():
      skin_folder.manage_delObjects(['Zuite_setSkipSave'])

  def _createZuite_createSetSkipSaveScript(self, return_value=None):
    skin_folder = self.portal.portal_skins.custom
    if 'Zuite_setSkipSave' not in skin_folder.objectIds():
      skin_folder.manage_addProduct['PythonScripts'].\
        manage_addPythonScript(id='Zuite_setSkipSave')
      python_script = skin_folder['Zuite_setSkipSave']
      python_script_body = """return %r""" % (return_value)
      python_script.ZPythonScript_edit('REQUEST=None', python_script_body)

  def afterSetUp(self):
    ERP5TypeFunctionalTestCase.afterSetUp(self)
    self._createZuite_createSetSkipSaveScript(return_value=True)
    self.tic()

  def beforeTearDown(self):
    ERP5TypeFunctionalTestCase.beforeTearDown(self)
    self._removeZuite_SetSkipSaveScript()
    transaction.commit()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFunctionalCorporateIdentityTemplateList))
  return suite
