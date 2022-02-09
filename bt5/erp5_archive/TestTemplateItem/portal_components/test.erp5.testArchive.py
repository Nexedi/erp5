# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurélien Calonne <aurel@nexedi.com>
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

import time
import unittest

from Testing.ZopeTestCase import _print, PortalTestCase
from AccessControl.SecurityManagement import \
  getSecurityManager, newSecurityManager
from zLOG import LOG
from DateTime import DateTime
from Products.ERP5Type.tests.utils import getExtraSqlConnectionStringList
from Products.ERP5.tests.testInventoryAPI import InventoryAPITestCase
from Products.ERP5Type.tests.utils import reindex, createZODBPythonScript


class TestArchive(InventoryAPITestCase):
  """
    Tests for Archive.
  """

  def getTitle(self):
    return "ERP5Archive"

  def getBusinessTemplateList(self):
    return InventoryAPITestCase.getBusinessTemplateList(self) + (
      'erp5_archive',
    )

  # Different variables used for this test
  run_all_test = 0
  quiet = 1

  def afterSetUp(self):
    self.login()
    InventoryAPITestCase.afterSetUp(self)
    # make sure there is no message any more


  def beforeTearDown(self):
    for module in [ self.getPersonModule(),
                    self.getOrganisationModule(),
                    self.getCategoryTool().region,
                    self.getCategoryTool().group ]:
      module.manage_delObjects(list(module.objectIds()))
    self.getPortal().portal_activities.manageClearActivities()
    self.tic()

  def login(self, *args, **kw):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def getSQLPathList(self,connection_id='erp5_sql_connection'):
    """
    Give the full list of path in the catalog
    """
    portal = self.getPortal()
    zsql_method_id = "Base_zGetTestPath"
    portal_skins_custom = portal.portal_skins.custom
    zsql_method = getattr(portal_skins_custom, zsql_method_id, None)
    if zsql_method is None:
      portal_skins_custom.manage_addProduct['ZSQLMethods']\
               .manage_addZSQLMethod(
          id = zsql_method_id,
          title = '',
          connection_id = connection_id,
          arguments = "",
          template = "select path from catalog")
      zsql_method = portal_skins_custom[zsql_method_id]
      zsql_method.max_rows_ = 0
    # it is mandatory to provide connection_id, or the
    # zsql method will look at preference and use the one
    # defined by the archive
    result = zsql_method(connection_id=connection_id)
    path_list = [x['path'] for x in result]
    return path_list

  def checkRelativeUrlInSQLPathList(self,url_list,connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      #LOG('checkRelativeUrlInSQLPathList found path:',0,path)
      self.assertTrue(path in path_list)

  def checkRelativeUrlNotInSQLPathList(self,url_list,connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      #LOG('checkRelativeUrlInSQLPathList not found path:',0,path)
      self.assertTrue(path not in  path_list)

  @reindex
  def _makeInventory(self, date): # pylint: disable=arguments-differ
    """
    Create inventory, use to check if they goes to the right catalog
    """
    portal = self.getPortal()
    inventory_module = portal.getDefaultModule(portal_type = "Inventory Module")
    inventory = inventory_module.newContent(portal_type = "Inventory")
    inventory.edit(stop_date = date,)
    return inventory

  def test_Archive(self, quiet=quiet, run=1): #run_all_test):
    if not run: return
    if not quiet:
      message = 'Archive'
      _print('\n%s ' % message)
      LOG('Testing... ',0,message)

    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    portal_archive = self.getArchiveTool()
    portal_catalog = self.getCatalogTool()
    inventory_module = portal.getDefaultModule(portal_type = "Inventory Module")
    # Create some objects
    self.base_category = portal_category.newContent(portal_type='Base Category',
                                               title="GreatTitle1")
    module = portal.getDefaultModule('Organisation')
    self.organisation = module.newContent(portal_type='Organisation',
                                     title="GreatTitle2")
    getInventory = self.getSimulationTool().getInventory
    self.mvt = self._makeMovement(quantity=100, stop_date=DateTime("2006/06/06"),
                                  simulation_state='delivered',)
    self.assertEqual(100, getInventory(node_uid=self.node.getUid()))
    self.assertEqual(len(self.folder.searchFolder(portal_type="Dummy Movement")), 1)

    # Create an inventory object
    self.inventory = self._makeInventory(date=DateTime("2006/06/15"))
    self.assertEqual(len(inventory_module.searchFolder(portal_type="Inventory")), 1)

    # Flush message queue
    self.tic()

    # Check well in catalog
    self.original_connection_id = 'erp5_sql_connection'
    self.original_deferred_connection_id = 'erp5_sql_deferred_connection'
    path_list = [self.organisation.getRelativeUrl(), self.inventory.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.original_connection_id)

    # Create new connectors for destination
    addSQLConnection = portal.manage_addProduct['ZMySQLDA'] \
      .manage_addZMySQLConnection
    self.new_connection_id = 'erp5_sql_connection1'
    db1, db2 = getExtraSqlConnectionStringList()[:2]
    addSQLConnection(self.new_connection_id,'', db1)
    new_connection = portal[self.new_connection_id]
    new_connection.manage_open_connection()
    # the deferred one
    self.new_deferred_connection_id = 'erp5_sql_connection2'
    addSQLConnection(self.new_deferred_connection_id,'', db1)
    new_deferred_connection = portal[self.new_deferred_connection_id]
    new_deferred_connection.manage_open_connection()

    # Create new connectors for archive
    self.archive_connection_id = 'erp5_sql_connection3'
    addSQLConnection(self.archive_connection_id,'', db2)
    archive_connection = portal[self.archive_connection_id]
    archive_connection.manage_open_connection()
    # the deferred one
    self.archive_deferred_connection_id = 'erp5_sql_connection4'
    addSQLConnection(self.archive_deferred_connection_id,'', db2)
    archive_deferred_connection = portal[self.archive_deferred_connection_id]
    archive_deferred_connection.manage_open_connection()

    # Create new catalog for destination
    self.original_catalog_id = 'erp5_mysql_innodb'
    self.new_catalog_id = self.original_catalog_id + '_2'
    cp_data = portal_catalog.manage_copyObjects(ids=('erp5_mysql_innodb',))
    new_id = portal_catalog.manage_pasteObjects(cp_data)[0]['new_id']
    new_catalog_id = 'erp5_mysql_innodb_2'
    portal_catalog.manage_renameObject(id=new_id,new_id=new_catalog_id)

    # Create new catalog for archive
    self.archive_catalog_id = self.original_catalog_id + '_archive'
    cp_data = portal_catalog.manage_copyObjects(ids=('erp5_mysql_innodb',))
    archive_id = portal_catalog.manage_pasteObjects(cp_data)[0]['new_id']
    archive_catalog_id = 'erp5_mysql_innodb_archive'
    portal_catalog.manage_renameObject(id=archive_id,new_id=archive_catalog_id)

    # Create an archive
    archive = portal_archive.newContent(portal_type="Archive",
                                        catalog_id=self.archive_catalog_id,
                                        connection_id=self.archive_connection_id,
                                        deferred_connection_id=self.archive_deferred_connection_id,
                                        priority=3,
                                        inventory_method_id='Archive_createAllInventory',
                                        test_method_id='Archive_test',
                                        stop_date_range_min=DateTime("2006/06/01"),
                                        stop_date_range_max=DateTime("2006/07/01"),
                                        )
    archive.ready()
    # Create an archive for destination catalog
    dest = portal_archive.newContent(portal_type="Archive",
                                     catalog_id=self.new_catalog_id,
                                     connection_id=self.new_connection_id,
                                     deferred_connection_id=self.new_deferred_connection_id,
                                     priority=1,
                                     test_method_id='Archive_test',
                                     stop_date_range_min=DateTime("2006/07/01"),
                                     )
    dest.ready()

    # make sure to commit to release any lock on tables
    self.commit()

    # Do archive
    portal_archive.manage_archive(destination_archive_id=dest.getId(),
                                  archive_id=archive.getId(),
                                  update_destination_sql_catalog=True,
                                  update_archive_sql_catalog=True,
                                  clear_destination_sql_catalog=True,
                                  clear_archive_sql_catalog=True)

    self.tic()
    self.assertEqual(portal_catalog.getSQLCatalog().id, self.new_catalog_id)
    self.assertEqual(archive.getValidationState(), 'validated')
    self.assertEqual(dest.getValidationState(), 'validated')
    # Check objects organisation are indexed
    # in both archive and current catalog and old one
    path_list = [self.organisation.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)
    # Create a new organisation and check it goes in both catalog and not old one
    self.organisation_1 = module.newContent(portal_type='Organisation',
                                            title="GreatTitle3")
    self.tic()
    path_list = [self.organisation_1.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)

    # Check objects movement are indexed
    # in archive and old one and not in current catalog
    path_list = [self.mvt.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)

    # Check inventory are indexed
    # in archive and old one and not in current catalog
    path_list = [self.inventory.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)

    # Create a new movement and check it goes only in new catalog
    self.assertEqual(len(self.folder.searchFolder(portal_type="Dummy Movement")), 0)
    self.assertEqual(100, getInventory(node_uid=self.node.getUid()))
    self.new_mvt = self._makeMovement(quantity=50, stop_date=DateTime("2006/08/06"),
                                      simulation_state='delivered',)
    self.tic()
    self.assertEqual(len(self.folder.searchFolder(portal_type="Dummy Movement")), 1)
    # Check objects movement are indexed
    # not in archive and old one but in current catalog
    path_list = [self.new_mvt.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.archive_connection_id)
    self.assertEqual(150, getInventory(node_uid=self.node.getUid()))

    # now play with preference to select to view document from archive
    portal_preferences = self.getPreferenceTool()
    self.pref = portal_preferences.newContent(id='user_pref',
                                              portal_type='Preference',
                                              preferred_archive=archive.getRelativeUrl())
    self.tic()
    self.getPreferenceTool().recursiveReindexObject()

    self.portal.portal_workflow.doActionFor(self.pref,
                                            'enable_action',
                                            wf_id='preference_workflow')
    self.assertEqual(self.pref.getPreferenceState(),    'enabled')

    path_list = [self.pref.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)

    self.assertEqual(portal_catalog.getPreferredSQLCatalogId(), archive.getCatalogId())
    self.assertEqual(len(self.folder.searchFolder(portal_type="Dummy Movement")), 1)

    # As we only have first movement in archive, inventory must be 100
    self.assertEqual(100, getInventory(node=self.node.getRelativeUrl()))

    # go on current catalog
    self.pref.edit(preferred_archive=None)
    self.tic()

    # unindex and reindex an older movement and check it's well reindexed
    self.inventory.unindexObject()
    self.tic()
    path_list = [self.inventory.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.archive_connection_id)
    self.inventory.reindexObject()
    self.tic()
    path_list = [self.inventory.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)
    # check inventory in archive now
    self.pref.edit(preferred_archive=archive.getRelativeUrl())
    self.tic()
    self.assertEqual(100, getInventory(node=self.node.getRelativeUrl()))

    # check if we unindex an object, it's remove in all catalog:
    module.manage_delObjects([self.organisation_1.id,])
    self.tic()
    path_list = [self.organisation_1.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.archive_connection_id)

    # check the current archive
    self.assertEqual(portal_archive.getCurrentArchive(), dest)

  def test_MaximumRecursionDepthExceededWithComplexSecurity(self):
    skin = self.portal.portal_skins.custom
    colour = self.portal.portal_categories.colour
    if not colour.hasObject('green'):
      colour.newContent('green')
    login = str(time.time())
    script_id = ["ERP5Type_getSecurityCategoryMapping",
                 "ERP5Type_getSecurityCategory"]
    createZODBPythonScript(skin, script_id[0], "",
      "return ((%r, ('colour',)),)" % script_id[1])
    createZODBPythonScript(skin, script_id[1],
      "base_category_list, user_name, object, portal_type, depth=[]", """if 1:
      # This should not be called recursively, or at least if should not fail.
      # Because RuntimeError is catched by 'except:' clauses, we detect it
      # with a static variable.
      depth.append(None)
      assert not portal_type, portal_type
      object.getSourceDecisionRelatedValueList()
      bc, = base_category_list
      depth.pop()
      return [] if depth else [{bc: 'green'}]
      """)
    person = self.portal.person_module.newContent(reference=login)
    try:
      self.tic()
      PortalTestCase.login(self, person.Person_getUserId())
      self.assertEqual(['green'], getSecurityManager().getUser().getGroups())
      self.portal.portal_caches.clearAllCache()
      PortalTestCase.login(self, person.Person_getUserId())
      self.assertEqual(
        ['green'], getSecurityManager().getUser().getGroups())
    finally:
      skin.manage_delObjects(script_id)
      self.commit()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestArchive))
  return suite
