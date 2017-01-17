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
import os
from App.config import getConfiguration
from urllib import pathname2url
#import tempfile
from Products.ERP5.Document.BusinessPackage import InstallationTree, createInstallationData
#from Products.ERP5Type.tests.runUnitTest import tests_home

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
      'erp5_dms',
      'erp5_property_sheets',
      'erp5_business_package',
      )

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    #self.export_dir = tempfile.mkdtmp(dir=tests_home)
    self.export_dir = ''
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
    package = self.portal.portal_templates.newContent(id=new_id, portal_type='Business Package')
    #self.assertTrue(package.getBuildingState() == 'draft')
    #self.assertTrue(package.getInstallationState() == 'not_installed')
    package.edit(title = new_id,
                  version='1.0',
                  description='package for live test')
    self.tic()
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

    cfg = getConfiguration()
    bp_title = pathname2url(package.getTitle())
    package_path = os.path.join(cfg.instancehome, 'tests', '%s' % (bp_title,))

    # Export package (not needed)
    package.export(path=package_path, local=True)
    self.tic()
    import_package = self.portal.portal_templates.download(
                    url='file:'+package_path,
                    id=package.id+'1',
                    is_package=True)

    return import_package

  def _importBusinessPackage(self, package):
    self.portal.portal_templates.manage_delObjects(package.getId())
    self.tic()
    import_package = self.portal.portal_templates.download(
                                  url='file:'+self.export_dir,
                                  id=package.getId(),
                                  is_package=True)
    return import_package

  def _installBusinessPackage(self, package):
    """
    Install the package from its built version.
    Expected to install the PathTemplateObject items
    """
    package.install()

  def test_fileImportAndReinstallForDocument(self):
    """
    Test Business Package build and install with test document.

    Expected result: Installs the exported object to the path expected on site.
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
    import_package = self._buildAndExportBusinessPackage(package)

    # Delete document from site
    self.portal.document_module.manage_delObjects([document_file.getId(),])
    self.tic()

    # Test if the file is gone
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(file_path))
    #import_package = self._importBusinessPackage(package)

    # Install package
    self._installBusinessPackage(import_package)

    # Test if the file is back
    self.assertIsNotNone(self.portal.restrictedTraverse(file_path))
    document = self.portal.restrictedTraverse(file_path)
    self.assertEquals(document.title, 'Test Document')

  def test_sameFileImportAndReinstallOnTwoPackages(self):
    """
    Test two Business Packages build and installation of same file.

    Here we will be using Insatallation Tree to install in the two packages
    all together, rather than doing installation one after another.

    Expected result: If we install same object from 2 different business packages,
    then in that case the installation object should compare between the
    state of OFS and installation and install accordingly.
    """

    old_package = self._createBusinessPackage()
    new_package = self._createBusinessPackage()

    document_file = self.portal.document_module.newContent(
                                    portal_type = 'File',
                                    title = 'Test Document',
                                    reference = 'erp5-package.Test.Document.Two.BP',
                                    data = 'test file',
                                    content_type = None)
    self.tic()

    file_path = document_file.getRelativeUrl()
    old_package.edit(template_path_list=[file_path,])
    new_package.edit(template_path_list=[file_path,])
    self.tic()

    # Build both the packages
    self._buildAndExportBusinessPackage(old_package)
    self._buildAndExportBusinessPackage(new_package)
    self.tic()

    # Get installation data from the list of packages which we want to install
    package_list = [old_package, new_package]

    final_data, conflicted_data = createInstallationData(package_list)

    # Delete document from site
    self.portal.document_module.manage_delObjects([document_file.getId(),])
    self.tic()

    # Test if the file doesn't exist on site anymore
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(file_path))

    if not conflicted_data:
      # Create InstallationTree object
      installation_tree = InstallationTree(final_data)
      # We try to install pakcages via mapping the installation tree to ZODB
      # As both have exactly same document we expect that only one of them get installed
      installation_tree.mapToERP5Site(self.portal)


    # Test if the file is back
    self.assertIsNotNone(self.portal.restrictedTraverse(file_path))
    document = self.portal.restrictedTraverse(file_path)
    self.assertEquals(document.title, document_file.title)

  def test_AddConflictedFileAtSamePathViaTwoPackages(self):
    """
    Test the result of conflict of two files to be installed at same path
    by two different Business Packages
    """
    old_package = self._createBusinessPackage()
    new_package = self._createBusinessPackage()

    document_file = self.portal.document_module.newContent(
                                    portal_type = 'File',
                                    title = 'Test Document',
                                    reference = 'erp5-package.Test.Document.Two.BP',
                                    data = 'test file',
                                    content_type = None)
    self.tic()

    file_path = document_file.getRelativeUrl()
    old_package.edit(template_path_list=[file_path,])

    # Build the first package
    self._buildAndExportBusinessPackage(old_package)
    self.tic()

    # Change something in the document file
    document_file.edit(data='Voila, we play with conflict')
    self.tic()
    new_package.edit(template_path_list=[file_path,])

    # Build the second package
    self._buildAndExportBusinessPackage(new_package)
    self.tic()

    # Get installation data from the list of packages which we want to install
    package_list = [old_package, new_package]

    final_data, conflicted_data = createInstallationData(package_list)

    # Delete document from site
    self.portal.document_module.manage_delObjects([document_file.getId(),])
    self.tic()

    # Assert that the final data is empty and conflicted data contains \
    # two different versions of the file
    self.assertFalse(final_data)
    self.assertTrue(conflicted_data)
    self.assertEquals(len(conflicted_data[file_path]), 2)

  def test_checkPathTemplateBuildForFolder(self):
    """
    This test should ensure that we are able to use folder as path for Business
    Packages without the need to export every path inside it explicitly

    In this test, we take the example to do this first with default catalog,
    then with multiple catalogs
    """

    # With single catalog
    folder_path = 'portal_catalog/erp5_mysql_innodb/**'
    package = self._createBusinessPackage()
    package.edit(template_path_list=[folder_path,])
    self._buildAndExportBusinessPackage(package)
    self.tic()

    # Check for the presence of catalog objects/paths in the business package
    built_package = self.portal._getOb(package.getId())
    path_item = built_package._path_item

    folder = self.portal.unrestrictedTraverse('portal_catalog/erp5_mysql_innodb')
    folder_object_id_list = sorted([l for l in folder.objectIds()])
    folder_object_count =  len(folder_object_id_list)

    package_object_id_list = sorted([l.getId() for l in path_item._objects.values()])
    package_object_count = len(package_object_id_list)

    self.assertEquals(folder_object_count, package_object_count)
    self.assertEquals(folder_object_id_list, package_object_id_list)

    # With multiple catalogs
    folder_path_list = [ 
          'portal_catalog/erp5_mysql_innodb/**',
          'portal_catalog/erp5_mysql_innodb100/**'
          ]

    package.edit(template_path_list=folder_path_list)
    self.tic()
    # XXX: Here, we are not exporting the package and its objects, just building
    # and saving it inside the package for the tests.
    self._buildAndExportBusinessPackage(package)
    self.tic()

    # Check for presence of catalog objects from all the catalogs mentioned in
    # the folder path list
    built_package = self.portal._getOb(package.getId())
    path_item = built_package._path_item
    new_folder = self.portal.unrestrictedTraverse('portal_catalog/erp5_mysql_innodb100')
    new_folder_id_list = sorted([l for l in new_folder.objectIds()])
    new_folder_object_count =  len(new_folder_id_list)

    total_object_count  = new_folder_object_count + folder_object_count
    package_object_id_list = sorted([l.getId() for l in path_item._objects.values()])
    object_id_list = sorted(folder_object_id_list + new_folder_id_list) 
    package_object_count = len(package_object_id_list)
    self.assertEquals(total_object_count, package_object_count)
    self.assertEquals(object_id_list, package_object_id_list)

  def test_addObjectPropertyTemplateItemInPackage(self):
    """
    Add ObjectPropertyTemplateItem to Business Package with the hash
    """
    package = self._createBusinessPackage()
    relative_url = 'portal_catalog/erp5_mysql_innodb'
    file_path_list = [relative_url]

    portal_catalog = self.portal.portal_catalog
    catalog_object = self.portal.unrestrictedTraverse(relative_url)
    object_property_list = []
    for property_id in catalog_object.propertyIds(): 
      object_property_list.append('%s | %s'%(relative_url, property_id))

    for property_id in portal_catalog.propertyIds():
      object_property_list.append('%s | %s'%(portal_catalog.getRelativeUrl(), property_id))

    package.edit(template_path_list=file_path_list)
    package.edit(template_object_property_list=object_property_list)
    self.tic()

    self._buildAndExportBusinessPackage(package)
    self.tic()

    # Check for presence of catalog objects from all the catalogs mentioned in
    # the folder path list
    built_package = self.portal._getOb(package.getId())
    object_property_item = built_package._object_property_item

    property_object_path_list = sorted(object_property_item._objects.keys())
    self.assertIn(relative_url, property_object_path_list)
    self.assertIn(portal_catalog.getRelativeUrl(), property_object_path_list)

    property_object_hash_list = sorted(object_property_item._hash.keys())
    self.assertIn(relative_url, property_object_hash_list)
    self.assertIn(portal_catalog.getRelativeUrl(), property_object_hash_list)

  def test_udpateInstallationStateOnlyForBusinessPackage(self):
    """
    Updating Business Package with the changed installation state and trying
    to show the diff between the two installation state
    """
    pass
