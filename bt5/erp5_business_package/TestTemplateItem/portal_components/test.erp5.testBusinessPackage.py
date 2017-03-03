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
from Products.ERP5.Document.BusinessPackage import createInstallationData

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

  def _createBusinessPackage(self, bp_id=None, title=None):
    if not bp_id:
      bp_id = 'package_%s'%str(time.time())
    if not title:
      title = bp_id
    package = self.portal.portal_templates.newContent(id=bp_id, portal_type='Business Package')
    package.edit(title = bp_id,
                  version='1.0',
                  description='package for live test')
    return package

  def _buildAndExportBusinessPackage(self, package):
    """
    Builds and exports Business Package to a given export directory
    Returns the path of export
    """
    package.build()

    cfg = getConfiguration()
    bp_title = pathname2url(package.getTitle())
    package_path = os.path.join(cfg.instancehome, 'tests', '%s' % (bp_title,))

    # Export package at the package_path
    package.export(path=package_path, local=True)

    return package_path

  def _importBusinessPackage(self, package, package_path):
    """
    Imports the package from the path where it had been exported.
    """
    self.portal.portal_templates.manage_delObjects(package.getId())

    import_package = self.portal.portal_templates.download(
                    url='file:'+package_path,
                    id=package.id+'1',
                    )

    return import_package

  def _installBusinessPackage(self, package):
    """
    Install the package from its built version.
    Expected to install the PathTemplateObject items
    """
    package.install()

  def _createBusinessManager(self, bm_id=None, title=None):
    if not bm_id:
      bm_id = 'manager_%s'%str(time.time())
    if not title:
      title = bm_id
    manager = self.portal.portal_templates.newContent(id=bm_id, \
                                                portal_type='Business Manager')
    self.tic()
    return manager

  def _exportBusinessManager(self, manager):
    """
    Exports a Business Manager object to the destined path
    """
    cfg = getConfiguration()
    bm_title = pathname2url(manager.getTitle())
    manager_path = os.path.join(cfg.instancehome, 'tests', '%s' % (bm_title,))

    # Export package at the package_path
    manager.export(path=manager_path, local=True)

    return manager_path

  def _importBusinessManager(self, manager, manager_path, increment):
    """
    Imports the package from the path where it had been exported.

    @params:
    increment: Used for changing the ID of downloaded Business Manager
    """

    import_manager = self.portal.portal_templates.download(
                    url='file:'+manager_path,
                    id=manager.id+str(increment),
                    )

    return import_manager

  def _installationOfBusinessManagerViaTemplateTool(self):
    """
    We try installing one or multiple Business Manager all via portal_templates,
    keeping in mind that any operation done on BM should result in a BM which
    can be easlily mapped with OFS.
    """
    manager = self._createBusinessManager()
    portal_templates = self.portal.portal_templates

    test_catalog_1 = self.portal.portal_catalog.newContent(
                                    portal_type = 'Catalog',
                                    title = 'Test Catalog 1 for Multiple BP5 Installation',
                                    )

    path_catalog_1 = test_catalog_1.getRelativeUrl()
    path_item_catalog_1 = '%s | %s | %s'%(path_catalog_1, 1, 1)
    path_item_list = [path_item_catalog_1]

    manager._setTemplatePathList(path_item_list)
    built_manager = manager.build()

    bm_list = []
    bm_list.append(built_manager)

    self.portal.portal_catalog.manage_delObjects( \
                                      [test_catalog_1.getId(),])

    # Test that the catalogs don't exist on site anymore
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(path_catalog_1))

    portal_templates.installMultipleBusinessManager(bm_list)

    catalog_1 = self.portal.restrictedTraverse(path_catalog_1)
    self.assertEquals(catalog_1.getTitle(), \
                      'Test Catalog 1 for Multiple BP5 Installation')

  def reduceBusinessManagerWithTwoConflictingPath(self):
    """
    Test the final Business Manager for Business Manager which have same path
    at different layer
    """
    portal_templates = self.portal.portal_templates
    manager_1 = self._createBusinessManager()
    manager_2 = self._createBusinessManager()

    test_catalog_1 = self.portal.portal_catalog.newContent(
                                    portal_type = 'Catalog',
                                    title = 'Test Catalog 1 for Multiple BP5 Installation',
                                    )

    path_catalog_1 = test_catalog_1.getRelativeUrl()
    path_item_catalog_1 = '%s | %s | %s'%(path_catalog_1, 1, 1)
    path_item_list_1 = [path_item_catalog_1]

    manager_1._setTemplatePathList(path_item_list_1)
    built_manager_1 = manager_1.build()

    test_catalog_1.edit(
                        title = 'Test Catalog 2 for Multiple BP5 Installation',
                        )

    path_item_catalog_2 = '%s | %s | %s'%(path_catalog_1, 1, 2)
    path_item_list_2 = [path_item_catalog_2]

    manager_2._setTemplatePathList(path_item_list_2)
    built_manager_2 = manager_2.build()

    self.portal.portal_catalog.manage_delObjects( \
                                      [test_catalog_1.getId(),])

    # Test that the catalogs don't exist on site anymore
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(path_catalog_1))

    bm_list = []
    bm_list.append(built_manager_1)
    bm_list.append(built_manager_2)

    portal_templates.installMultipleBusinessManager(bm_list)

    catalog_1 = self.portal.restrictedTraverse(path_catalog_1)
    self.assertEquals(catalog_1.getTitle(), \
                      'Test Catalog 2 for Multiple BP5 Installation')

  def test_globalInstallationOfBusinessTemplate(self):
    """

    NOTE:
    Keep in mind that the installation is done on build Business Manager
    objects only, we are not yet exporting a Business Manager object

    USE CASE:
    * 2 bt5: A / B
    * B has a path C
    * install A and B
    * you should have C in ZODB
    * modify B to remove path C
    * modify A to provide a path C (with a different content to simplify)
    * update A and B
    * C' should be in ZODB

    EXPECTED RESULT:
    Content of C': Something different than C, to be able to check
    where C' is path C provided by A

    """
    portal_templates = self.portal.portal_templates
    managerA = self._createBusinessManager()
    managerB = self._createBusinessManager()

    test_catalog = self.portal.portal_catalog.newContent(
                                    portal_type = 'Catalog',
                                    title = 'Test Catalog initial for Multiple BM Installation',
                                    )

    # Add catalog to the path list for Business Manager and build the object
    catalog_path = test_catalog.getRelativeUrl()
    path_item_catalog = '%s | %s | %s' % (catalog_path, 1, 1)
    path_item_list = [path_item_catalog]

    # Set catalog path item as path_item in managerB
    managerB._setTemplatePathList(path_item_list)

    # Build both Business Manager(s)
    built_manager_A = managerA.build()
    built_manager_B = managerB.build()

    # Delete the catalog object
    self.portal.portal_catalog.manage_delObjects(
                                            [test_catalog.getId(),])

    # Test that the catalog don't exist on site anymore
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(catalog_path))

    # Export the built Business Manager
    exported_manager_path_B = self._exportBusinessManager(built_manager_A)
    exported_manager_path_A = self._exportBusinessManager(built_manager_B)

    # Import the Business Managers
    imported_manager_A = self._importBusinessManager(managerA,
                                                      exported_manager_path_A,
                                                      increment=1)
    imported_manager_B = self._importBusinessManager(managerB,
                                                      exported_manager_path_B,
                                                      increment=1)

    # Install both the Business Manager(s)
    portal_templates.installMultipleBusinessManager([
                                                    imported_manager_A,
                                                    imported_manager_B,
                                                    ])

    # XXX: Match the state of manager A and B, nothing extra added
    # portal_templates.installMultipleBusinessManager([
    #                                                imported_package_A,
    #                                                imported_package_B,
    #                                                ])

    # Test that the catalog exists on ZODB after installation
    installed_test_catalog = self.portal.restrictedTraverse(catalog_path)
    self.assertEquals(installed_test_catalog.getTitle(), \
                      'Test Catalog initial for Multiple BM Installation')

    # Add catalog_path to managerA and remove the catalog_path from managerB
    managerA._setTemplatePathList(path_item_list)
    managerB._setTemplatePathList([])

    installed_test_catalog.edit(title='new_couscous')

    # Build both the Business Manager(s)
    built_manager_A = managerA.build()
    built_manager_B = managerB.build()

    # Then we change the title of test catalog again
    installed_test_catalog.edit(title='new_couscous_change_again')

    # Export the built Business Manager
    exported_manager_path_A = self._exportBusinessManager(built_manager_A)
    exported_manager_path_B = self._exportBusinessManager(built_manager_B)

    # Import the Business Managers
    imported_manager_A = self._importBusinessManager(managerA,
                                                      exported_manager_path_A,
                                                      increment=2)
    imported_manager_B = self._importBusinessManager(managerB,
                                                      exported_manager_path_B,
                                                      increment=2)

    # Match the overall state, 
    # Install both the Business Manager(s)
    portal_templates.installMultipleBusinessManager([
                                                    imported_manager_A,
                                                    imported_manager_B,
                                                    ])

    # Test that the catalog exists on ZODB after installation with the newer
    # updated version
    catalog = self.portal.restrictedTraverse(installed_test_catalog.getRelativeUrl())
    self.assertEquals(catalog.getTitle(), "new_couscous")

  def _UpdateVersionOfBusinessManager(self):
    """
    * install bm A which add one workflow W1
    * install bm B which surcharge workflow W2
    * drop workflow W2 from bm configuration
    * update bp5 B: ensure that the ZODB contains W1
    """
    portal_templates  = self.portal.portal_templates
    managerA = self._createBusinessManager()
    managerB = self._createBusinessManager()

    test_catalog_A = self.portal.portal_catalog.newContent(
                                    portal_type = 'Catalog',
                                    title = 'Test Catalog A for Multiple BM Installation',
                                    )

    # Add catalog to the path list for Business Manager and build the object
    path_catalog_A = test_catalog_A.getRelativeUrl()
    path_item_catalog_A = '%s | %s | %s'%(path_catalog_A, 1, 1)
    path_item_list_A = [path_item_catalog_A]
    managerA._setTemplatePathList(path_item_list_A)

    built_manager_A = managerA.build()

    # Delete the catalog object
    self.portal.portal_catalog.manage_delObjects(
                                            [test_catalog_A.getId(),])

    # Test that the catalog don't exist on site anymore
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(path_catalog_A))

    # Install the Business Manager A
    portal_templates.installMultipleBusinessManager([built_manager_A])

    # Test that the catalog exists
    catalog_1 = self.portal.restrictedTraverse(path_catalog_A)
    self.assertEquals(catalog_1.getTitle(), \
                      'Test Catalog A for Multiple BM Installation')

    # Create new  Business Manager B with some different object
    path_document_B = self.portal.document_module.newContent(
                                      portal_type='File',
                                      reference = 'erp5-package.Test.Document',
                                      data='test data',
                                      )

    path_item_document_B = '%s | %s | %s'%(path_document_B.getRelativeUrl(), 1, 1)
    managerB._setTemplatePathList([path_item_document_B])

    built_manager_B = managerB.build()

    # Delete the document object
    self.portal.document_module.manage_delObjects(
                                            [path_document_B.getId(),])

    # Add an empty path list in managerA
    managerA._setTemplatePathList([])
    built_manager_A = managerA.build()

    # Try installing built Business Managers A and B together
    bm_list = []

    bm_list.append(built_manager_A)
    bm_list.append(built_manager_B)
    portal_templates.installMultipleBusinessManager(bm_list)

    # Check if the catalog still exists
    catalog_1 = self.portal.restrictedTraverse(path_catalog_A)
    self.assertEquals(catalog_1.getTitle(), \
                      'Test Catalog A for Multiple BM Installation')    

  def _differentFileImportAndReinstallOnTwoPackages(self):
    """
    Test two Business Templates build and installation of same file.

    Here we will be using Insatallation Tree in Template Tool to install
    in the two configurations all together, rather than doing installation
    one after another.

    Expected result: If we install same object from 2 different business packages,
    then in that case the installation object should compare between the
    state of OFS and installation and install accordingly.
    """

    old_package = self._createBusinessPackage()
    new_package = self._createBusinessPackage()

    portal_templates = self.portal.portal_templates

    test_catalog_1 = self.portal.portal_catalog.newContent(
                                    portal_type = 'Catalog',
                                    title = 'Test Catalog 1 for Multiple BP5 Installation',
                                    )
    test_catalog_2 = self.portal.portal_catalog.newContent(
                                    portal_type = 'Catalog',
                                    title = 'Test Catalog 2 for Multiple BP5 Installation',
                                    )

    # Update the property for the above mentioned objects so that we can use
    # them in tests
    test_catalog_1.edit(
      sql_catalog_datetime_search_keys=[
        'alarm.alarm_date',
        'alarm_date',
        'catalog.creation_date',
        'catalog.grouping_date',
        'catalog.modification_date'
        ],
      )

    test_catalog_2.edit(
      sql_catalog_datetime_search_keys=[
         'creation_date',
         'date',
         'delivery.start_date',
         'delivery.start_date_range_max',
         'delivery.start_date_range_min',
        ],
      )

    property_list = [
      'sql_catalog_datetime_search_keys_list',
      'sql_catalog_full_text_search_keys_list',
      ]

    path_1 = test_catalog_1.getRelativeUrl()
    path_2 = test_catalog_2.getRelativeUrl()

    prop_list_1 = []
    prop_list_2 = []
    for prop_id in property_list:
      prop_line_1 = '%s | %s' % (path_1, prop_id)
      prop_line_2 = '%s | %s' % (path_2, prop_id)
      prop_list_1.append(prop_line_1)
      prop_list_2.append(prop_line_2)

    old_package.edit(
      template_path_list=[path_1,],
      template_object_property_list=prop_list_1,
                      )
    new_package.edit(
      template_path_list=[path_2,],
      template_object_property_list=prop_list_2,
      )

    # Build both the packages
    old_package_path = self._buildAndExportBusinessPackage(old_package)
    new_package_path = self._buildAndExportBusinessPackage(new_package)
    import_old_package = self._importBusinessPackage(old_package, old_package_path)
    import_new_package = self._importBusinessPackage(new_package, new_package_path)
    # Get installation data from the list of packages which we want to install
    package_list = [import_old_package, import_new_package]

    # Delete document from site
    self.portal.portal_catalog.manage_delObjects( \
                                      [
                                        test_catalog_1.getId(),
                                        test_catalog_2.getId(),
                                      ])

    # Test that the catalogs don't exist on site anymore
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(path_1))
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(path_2))

    # Install multiple Business Package all together
    portal_templates.installMultipleBusinessPackage(package_list)

    catalog_1 = self.portal.restrictedTraverse(path_1)
    catalog_2 = self.portal.restrictedTraverse(path_2)

    self.assertEquals(catalog_1.getTitle(), \
                      'Test Catalog 1 for Multiple BP5 Installation')

    self.assertEquals(catalog_2.getTitle(), \
                      'Test Catalog 2 for Multiple BP5 Installation')

  def _fileImportAndReinstallWithProperty(self):
    """
    Test Business Package for Path and ObjectProperty Items together.
    Here we export path as well propertie(s) for different objects and check
    if we are able to install them back using Business Package
    """
    bp_id = 'erp5_mysql_innodb_catalog_%s'%time.time()
    package = self._createBusinessPackage(bp_id=bp_id)
    catalog_path =  'portal_catalog/erp5_mysql_innodb'
    file_path_list = (
                      'portal_catalog/erp5_mysql_innodb',
                      'portal_catalog/erp5_mysql_innodb/**',
                      )

    #erp5_catalog = self.portal.unrestrictedTraverse(catalog_path)

    property_list = [
      'sql_catalog_datetime_search_keys_list',
      'sql_catalog_full_text_search_keys_list',
      'sql_catalog_keyword_search_keys_list',
      'sql_catalog_local_role_keys_list',
      'sql_catalog_multivalue_keys_list',
      'sql_catalog_related_keys_list',
      'sql_catalog_request_keys_list',
      'sql_search_result_keys_list',
      'sql_search_tables_list',
      'sql_catalog_role_keys_list',
      'sql_catalog_scriptable_keys_list',
      'sql_catalog_search_keys_list',
      'sql_catalog_security_uid_columns_list',
      'sql_catalog_topic_search_keys_list'
      ]

    prop_list = []
    for prop_id in property_list:
      prop_line = '%s | %s' % (catalog_path, prop_id)
      prop_list.append(prop_line)

    package.edit(
                  template_path_list=file_path_list,
                  template_object_property_list=prop_list
                  )

    package_path = self._buildAndExportBusinessPackage(package)
    import_package = self._importBusinessPackage(package, package_path)
    self._installBusinessPackage(import_package)

  def fileImportAndReinstallForDocument(self):
    """
    Test Business Package build and install with test document.

    Expected result: Installs the exported object to the path expected on site.
    """
    bp_id = 'erp5_mysql_innodb_catalog_%s'%time.time()
    package = self._createBusinessPackage(bp_id=bp_id)
    document_file = self.portal.document_module.newContent(
                                    portal_type = 'File',
                                    title = 'Test Document',
                                    reference = 'erp5-package.Test.Document',
                                    data = 'test file',
                                    content_type = None)

    file_path = document_file.getRelativeUrl()
    property_list = ['%s | title'%file_path,]
    package.edit(
      template_path_list=file_path,
      template_object_property_list=property_list,
    )

    # Build package
    package_path = self._buildAndExportBusinessPackage(package)

    # Delete the document
    self.portal.document_module.manage_delObjects([document_file.getId(),])
    # Assert that the file is gone
    self.assertRaises(KeyError, lambda: self.portal.restrictedTraverse(file_path))

    import_package = self._importBusinessPackage(package, package_path)

    # Install package
    self._installBusinessPackage(import_package)

    # Test if the file is back
    self.assertIsNotNone(self.portal.restrictedTraverse(file_path))
    document = self.portal.restrictedTraverse(file_path)
    self.assertEquals(document.title, 'Test Document')

  def _AddConflictedFileAtSamePathViaTwoPackages(self):
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

    file_path = document_file.getRelativeUrl()
    old_package.edit(template_path_list=[file_path,])

    # Build the first package
    self._buildAndExportBusinessPackage(old_package)

    # Change something in the document file
    document_file.edit(data='Voila, we play with conflict')
    new_package.edit(template_path_list=[file_path,])

    # Build the second package
    self._buildAndExportBusinessPackage(new_package)

    # Get installation data from the list of packages which we want to install
    package_list = [old_package, new_package]

    final_data, conflicted_data = createInstallationData(package_list)

    # Delete document from site
    self.portal.document_module.manage_delObjects([document_file.getId(),])

    # Assert that the final data is empty and conflicted data contains \
    # two different versions of the file
    self.assertFalse(final_data)
    self.assertTrue(conflicted_data)
    self.assertEquals(len(conflicted_data[file_path]), 2)

  def _checkPathTemplateBuildForFolder(self):
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
    
    # XXX: Here, we are not exporting the package and its objects, just building
    # and saving it inside the package for the tests.
    self._buildAndExportBusinessPackage(package)

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

  def _addObjectPropertyTemplateItemInPackage(self):
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

    self._buildAndExportBusinessPackage(package)

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

  def _udpateInstallationStateOnlyForBusinessPackage(self):
    """
    Updating Business Package with the changed installation state and trying
    to show the diff between the two installation state
    """
    pass
