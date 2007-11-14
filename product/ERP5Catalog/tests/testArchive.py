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

import unittest

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from DateTime import DateTime
from Products.CMFCore.tests.base.testcase import LogInterceptor
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ZSQLCatalog.ZSQLCatalog import HOT_REINDEXING_FINISHED_STATE,\
      HOT_REINDEXING_RECORDING_STATE, HOT_REINDEXING_DOUBLE_INDEXING_STATE
from Products.CMFActivity.Errors import ActivityFlushError
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from Products.ERP5.tests.testInventoryAPI import InventoryAPITestCase
from DateTime import DateTime
from Products.ERP5Type.tests.utils import reindex

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestArchive(InventoryAPITestCase):
  """
    Tests for Archive.
  """

  def getTitle(self):
    return "ERP5Archive"

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_trade',
            'erp5_apparel',
            'erp5_dummy_movement',
            'erp5_archive',
            )

  # Different variables used for this test
  run_all_test = 0
  quiet = 1

  def afterSetUp(self):
    self.login()
    InventoryAPITestCase.afterSetUp(self)
    # make sure there is no message any more
    self.tic()

  def beforeTearDown(self):
    for module in [ self.getPersonModule(),
                    self.getOrganisationModule(),
                    self.getCategoryTool().region,
                    self.getCategoryTool().group ]:
      module.manage_delObjects(list(module.objectIds()))
    self.getPortal().portal_activities.manageClearActivities()
    get_transaction().commit()

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def getSQLPathList(self,connection_id=None):
    """
    Give the full list of path in the catalog
    """
    if connection_id is None:
      sql_connection = self.getSQLConnection()
    else:
      sql_connection = getattr(self.getPortal(),connection_id)
    sql = 'select path from catalog'
    result = sql_connection.manage_test(sql)
    path_list = map(lambda x: x['path'],result)
    return path_list

  def checkRelativeUrlInSQLPathList(self,url_list,connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      #LOG('checkRelativeUrlInSQLPathList found path:',0,path)
      self.failUnless(path in path_list)

  def checkRelativeUrlNotInSQLPathList(self,url_list,connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      #LOG('checkRelativeUrlInSQLPathList not found path:',0,path)
      self.failUnless(path not in  path_list)

  @reindex
  def _makeInventory(self, date):
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
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    portal_activities = self.getActivityTool()
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
    self.assertEquals(100, getInventory(node_uid=self.node.getUid()))
    self.assertEqual(len(self.folder.searchFolder(portal_type="Dummy Movement")), 1)

    # Create an inventory object
    self.inventory = self._makeInventory(date=DateTime("2006/06/15"))
    self.assertEqual(len(inventory_module.searchFolder(portal_type="Inventory")), 1)    

    # Flush message queue
    get_transaction().commit()
    self.tic()

    # Check well in catalog
    self.original_connection_id = 'erp5_sql_connection'
    self.original_deferred_connection_id = 'erp5_sql_deferred_connection'
    path_list = [self.organisation.getRelativeUrl(), self.inventory.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.original_connection_id)
    
    # Create new connectors for destination
    self.new_connection_id = 'erp5_sql_connection1'
    portal.manage_addZMySQLConnection(self.new_connection_id,'',
                                      'test2 test2')
    new_connection = portal[self.new_connection_id]
    new_connection.manage_open_connection()
    # the deferred one
    self.new_deferred_connection_id = 'erp5_sql_connection2'
    portal.manage_addZMySQLConnection(self.new_deferred_connection_id,'',
                                      'test2 test2')
    new_deferred_connection = portal[self.new_deferred_connection_id]
    new_deferred_connection.manage_open_connection()

    # Create new connectors for archive
    self.archive_connection_id = 'erp5_sql_connection3'
    portal.manage_addZMySQLConnection(self.archive_connection_id,'',
                                      'test3 test3')
    archive_connection = portal[self.archive_connection_id]
    archive_connection.manage_open_connection()
    # the deferred one
    self.archive_deferred_connection_id = 'erp5_sql_connection4'
    portal.manage_addZMySQLConnection(self.archive_deferred_connection_id,'',
                                      'test3 test3')
    archive_deferred_connection = portal[self.archive_deferred_connection_id]
    archive_deferred_connection.manage_open_connection()

    # Create new catalog for destination
    self.original_catalog_id = 'erp5_mysql_innodb'
    self.new_catalog_id = self.original_catalog_id + '_2'
    cp_data = portal_catalog.manage_copyObjects(ids=('erp5_mysql_innodb',))
    new_id = portal_catalog.manage_pasteObjects(cp_data)[0]['new_id']
    new_catalog_id = 'erp5_mysql_innodb_2'
    portal_catalog.manage_renameObject(id=new_id,new_id=new_catalog_id)
    dest_catalog = portal_catalog[new_catalog_id]

    # Create new catalog for archive
    self.archive_catalog_id = self.original_catalog_id + '_archive'
    cp_data = portal_catalog.manage_copyObjects(ids=('erp5_mysql_innodb',))
    archive_id = portal_catalog.manage_pasteObjects(cp_data)[0]['new_id']
    archive_catalog_id = 'erp5_mysql_innodb_archive'
    portal_catalog.manage_renameObject(id=archive_id,new_id=archive_catalog_id)
    archive_catalog = portal_catalog[archive_catalog_id]

    # Create an archive
    archive = portal_archive.newContent(portal_typ="Archive",
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
    dest = portal_archive.newContent(portal_typ="Archive",
                                     catalog_id=self.new_catalog_id,
                                     connection_id=self.new_connection_id,
                                     deferred_connection_id=self.new_deferred_connection_id,
                                     priority=1,
                                     test_method_id='Archive_test',
                                     stop_date_range_min=DateTime("2006/07/01"),
                                     )
    dest.ready()

    # Do archive
    portal_archive.manage_archive(destination_archive_id=dest.getId(),
                                  archive_id=archive.getId(),
                                  update_destination_sql_catalog=True,
                                  update_archive_sql_catalog=True,
                                  clear_destination_sql_catalog=True,
                                  clear_archive_sql_catalog=True)

    get_transaction().commit()
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
    get_transaction().commit()
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
    self.assertEquals(100, getInventory(node_uid=self.node.getUid()))
    self.new_mvt = self._makeMovement(quantity=50, stop_date=DateTime("2006/08/06"),
                                      simulation_state='delivered',)
    get_transaction().commit()
    self.tic()
    self.assertEqual(len(self.folder.searchFolder(portal_type="Dummy Movement")), 1)
    # Check objects movement are indexed
    # not in archive and old one but in current catalog
    path_list = [self.new_mvt.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.archive_connection_id)
    self.assertEquals(150, getInventory(node_uid=self.node.getUid()))

    # now play with preference to select to view document from archive
    portal_preferences = self.getPreferenceTool()
    self.pref = portal_preferences.newContent(id='user_pref',
                                              portal_type='Preference',
                                              preferred_archive=archive.getRelativeUrl())
    get_transaction().commit()
    self.getPreferenceTool().recursiveReindexObject()
    self.tic()
    self.portal.portal_workflow.doActionFor(self.pref,
                                            'enable_action',
                                            wf_id='preference_workflow')
    self.assertEquals(self.pref.getPreferenceState(),    'enabled')

    path_list = [self.pref.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)

    self.assertEqual(portal_catalog.getPreferredSQLCatalogId(), archive.getCatalogId())
    self.assertEqual(len(self.folder.searchFolder(portal_type="Dummy Movement")), 1)
    
    # As we only have first movement in archive, inventory must be 100
    self.assertEquals(100, getInventory(node=self.node.getRelativeUrl()))

    # go on current catalog
    self.pref.edit(preferred_archive=None)
    get_transaction().commit()
    self.tic()

    # unindex and reindex an older movement and check it's well reindexed    
    self.inventory.unindexObject()
    get_transaction().commit()
    self.tic()
    path_list = [self.inventory.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.archive_connection_id)
    self.inventory.reindexObject()
    get_transaction().commit()
    self.tic()
    path_list = [self.inventory.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.archive_connection_id)
    # check inventory in archive now
    self.pref.edit(preferred_archive=archive.getRelativeUrl())
    get_transaction().commit()
    self.tic()
    self.assertEquals(100, getInventory(node=self.node.getRelativeUrl()))

    

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestArchive))
  return suite

