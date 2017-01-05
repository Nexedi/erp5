##############################################################################
#
# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import time

class TestBusinessPackage(ERP5TypeTestCase):
  """
  Test class to test that Business Package object can export some paths
  and install them on an erp5 site

  Steps:
  - Create BusinessPackage object
  - Add path list to the object
  - Build the package and expect the items mentioned in path list gets
  exported in the build step
  - Remove the objects mentioned in path_list from the site
  - Install the package
  - Expected result should be that it installs the objects on the site
  """

  def getTitle(self):
    return "TestBusinessPackage"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return (
      'erp5_base',
      'erp5_core',
      'erp5_property_sheets',
      'erp5_business_package',
      )

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    #self.export_dir = tempfile.mkdtmp(dir=tests_home)
    self.portal = self.getPortalObject()

  def beforeTearDown(self):
    try:
      package_id  = self.package.getId()
      if package_id:
        self.portal.manage_delObjects([package_id,]) 
    except AttributeError:
      pass

  def _createBusinessPackage(self):
    new_id = 'package_%s'%str(time.time())
    package = self.portal.newContent(id=new_id, portal_type='Business Package')
    #self.assertTrue(package.getBuildingState() == 'draft')
    #self.assertTrue(package.getInstallationState() == 'not_installed')
    package.edit(title ='test_package',
                  version='1.0',
                  description='package for live test')
    return package

  def _buildAndExportBusinessPackage(self, package):
    """
    Builds and exports Business Package to a given export directory
    """
    # Build Package
    # Expected result should be while building the path object items
    # are going to be exported as XML(?)
    self.tic()
    package.build()
    self.tic()

    # Export package (not needed)
    #self.package.export(path=self.export_dir, local=True)
    #self.tic()

  def _installBusinessPackage(self, package):
    """
    Install the package from its built version.
    Expected to install the PathTemplateObject items
    """
    package.install()

  def test_fileImportAndReinstallForDocument(self):
    """
    Test Business Package build and install with test document
    """
    package = self._createBusinessPackage()
    document_file = self.portal.document_module.newContent(
                                    portal_type = 'File',
                                    title = 'Test Document',
                                    reference = 'erp5-package.Test.Document',
                                    data = 'test file',
                                    content_type = None)
    self.tic()

    file_path = document_file.getRelativeUrl()
    package.edit(template_path_list=[file_path,])

    # Build package
    self._buildAndExportBusinessPackage(package)

    # Delete document from site
    self.portal.document_module.manage_delObjects([document_file.getId(),])
    self.tic()

    # Test if the file is gone
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(file_path))

    # Install package
    self._installBusinessPackage(package)

    # Test if the file is back
    self.assertIsNotNone(self.portal.restrictedTraverse(file_path))
    document = self.portal.restrictedTraverse(file_path)
    self.assertEquals(document.title, 'Test Document')

  def test_sameFileImportAndReinstallOnTwoPackages(self):
    """
    Test two Business Packages build and installation of same file
    """
    self.assertEquals(1, 1)
