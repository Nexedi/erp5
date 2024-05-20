##############################################################################
#
# Copyright (c) 2018 Nexedi SARL and Contributors. All Rights Reserved.
#          Vincent Pelletier <vincent@nexedi.com>
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
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import LogInterceptor, getExtraSqlConnectionStringList
from Products.ZSQLCatalog.ZSQLCatalog import HOT_REINDEXING_FINISHED_STATE, HOT_REINDEXING_RECORDING_STATE, HOT_REINDEXING_DOUBLE_INDEXING_STATE
from zLOG import LOG

class TestVanillaERP5Catalog(ERP5TypeTestCase, LogInterceptor):
  """
  Tests for ERP5 Catalog where a pristine freshly-created-site catalog is
  needed. Clearing catalog is only allowed when comparing before/after for
  strict item equality.
  """

  def getTitle(self):
    return "VanillaERP5Catalog"

  def getBusinessTemplateList(self):
    return ('erp5_full_text_mroonga_catalog', 'erp5_base')

  # Different variables used for this test
  username = 'seb'
  new_erp5_sql_connection = 'erp5_sql_connection2'
  new_erp5_deferred_sql_connection = 'erp5_sql_deferred_connection2'
  original_catalog_id = 'erp5_mysql_innodb'
  new_catalog_id = 'erp5_mysql_innodb2'

  def afterSetUp(self):
    portal = self.portal
    portal.acl_users._doAddUser(self.username, '', ['Manager'], [])
    self.loginByUserName(self.username)
    self.tic()

  def beforeTearDown(self):
    # restore default_catalog
    portal = self.portal
    portal.portal_catalog._setDefaultSqlCatalogId(self.original_catalog_id)
    portal.portal_catalog.hot_reindexing_state = None
    module = self.getOrganisationModule()
    module.manage_delObjects(list(module.objectIds()))
    module.reindexObject()
    # Remove copied sql_connector and catalog
    if self.new_erp5_sql_connection in portal.objectIds():
      portal.manage_delObjects([self.new_erp5_sql_connection])
    if self.new_erp5_deferred_sql_connection in portal.objectIds():
      portal.manage_delObjects([self.new_erp5_deferred_sql_connection])
    if self.new_catalog_id in portal.portal_catalog.objectIds():
      portal.portal_catalog.manage_delObjects([self.new_catalog_id])
    self.tic()

  def getSQLPathList(self,connection_id=None, sql=None):
    """
    Give the full list of path in the catalog
    """
    if connection_id is None:
      sql_connection = self.getSQLConnection()
    else:
      sql_connection = getattr(self.getPortal(), connection_id)
    if sql is None:
      sql = 'select distinct(path) from catalog'
    _, row_list = sql_connection().query(sql, max_rows=0)
    return [x for x, in row_list]

  def getSQLPathListWithRolesAndUsers(self, connection_id):
    sql = 'select distinct(path) from catalog, roles_and_users\
           where catalog.security_uid=roles_and_users.uid'
    return self.getSQLPathList(connection_id, sql)

  def checkRelativeUrlInSQLPathList(self,url_list,connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      self.assertIn(path, path_list)
      LOG('checkRelativeUrlInSQLPathList found path:',0,path)

  def checkRelativeUrlNotInSQLPathList(self,url_list,connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      self.assertNotIn(path,  path_list)
      LOG('checkRelativeUrlInSQLPathList not found path:',0,path)

  def test_1_ERP5Site_reindexAll(self):
    portal = self.getPortal()
    portal.portal_categories.newContent(portal_type='Base Category', title="GreatTitle1")
    portal.organisation_module.newContent(portal_type='Organisation', title="GreatTitle2")
    self.tic()
    original_path_list = self.getSQLPathList()
    self.getCatalogTool().manage_catalogClear()
    self.assertEqual([], self.getSQLPathList())
    portal.ERP5Site_reindexAll()
    self.tic()
    # Check if all objects are catalogued as before
    self.maxDiff = None
    self.assertCountEqual(original_path_list, self.getSQLPathList())

  # Note: this test is only working as a sinde-effect of
  # test_1_ERP5Site_reindexAll being run first (it produces a "clean" catalog).
  # Otherwise, both would fail with the same error.
  def test_2_ERP5Site_hotReindexAll(self):
    """
      test the hot reindexing of catalog -> catalog2
      then a hot reindexing detailed catalog2 -> catalog
      this test use the variable environment: extra_sql_connection_string_list
    """
    portal = self.portal
    original_connection_id = 'erp5_sql_connection'
    extra_connection_string_list = getExtraSqlConnectionStringList()
    if not extra_connection_string_list or extra_connection_string_list[0] == getattr(portal, original_connection_id).connection_string:
      self.skipTest('default connection string is the same as the one for hot-reindex catalog')
    new_connection_string = extra_connection_string_list[0]
    new_deferred_connection_id = 'erp5_sql_deferred_connection2'
    module = portal.organisation_module
    organisation = module.newContent(portal_type='Organisation', title="GreatTitle2")
    self.tic()
    addSQLConnection = portal.manage_addProduct['ZMySQLDA'].manage_addZMySQLConnection
    # Create new connectors
    addSQLConnection(self.new_erp5_sql_connection, '', new_connection_string)
    portal[self.new_erp5_sql_connection].manage_open_connection()
    addSQLConnection(new_deferred_connection_id, '', new_connection_string)
    portal[new_deferred_connection_id].manage_open_connection()
    # Note: transactionless connector must not be changed because this one
    # create the portal_ids otherwise it create of conflicts with uid
    # objects.
    # Create new catalog
    portal_catalog = portal.portal_catalog
    portal_catalog.manage_renameObject(
      id=portal_catalog.manage_pasteObjects(
        portal_catalog.manage_copyObjects(ids=(self.original_catalog_id, )),
      )[0]['new_id'],
      new_id=self.new_catalog_id,
    )
    source_sql_connection_id_list = [original_connection_id, self.new_erp5_deferred_sql_connection]
    destination_sql_connection_id_list = [self.new_erp5_sql_connection, new_deferred_connection_id]
    portal_catalog.manage_hotReindexAll(
      source_sql_catalog_id=self.original_catalog_id,
      destination_sql_catalog_id=self.new_catalog_id,
      source_sql_connection_id_list=source_sql_connection_id_list,
      destination_sql_connection_id_list=destination_sql_connection_id_list,
      update_destination_sql_catalog=True,
    )
    self.tic()
    original_path_list = self.getSQLPathList(original_connection_id)
    new_path_list = self.getSQLPathList(self.new_erp5_sql_connection)
    self.maxDiff = None
    self.assertCountEqual(original_path_list, new_path_list)
    organisation2 = module.newContent(portal_type='Organisation', title="GreatTitle2")
    first_deleted_url = organisation2.getRelativeUrl()
    self.tic()
    path_list = [organisation.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_erp5_sql_connection)
    path_list = [first_deleted_url]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_erp5_sql_connection)

    self.assertEqual(portal.portal_skins.erp5_core.Resource_zGetInventoryList.connection_id, self.new_erp5_sql_connection)
    self.assertEqual(portal_catalog.getHotReindexingState(), HOT_REINDEXING_FINISHED_STATE)

    # Do a hot reindex in the reverse way, but this time a more
    # complicated hot reindex
    portal_catalog.manage_hotReindexAll(
      source_sql_catalog_id=self.new_catalog_id,
      destination_sql_catalog_id=self.original_catalog_id,
      source_sql_connection_id_list=destination_sql_connection_id_list,
      destination_sql_connection_id_list=source_sql_connection_id_list,
      update_destination_sql_catalog=True,
    )
    self.commit()
    self.assertEqual(portal_catalog.getHotReindexingState(), HOT_REINDEXING_RECORDING_STATE)
    organisation3 = module.newContent(portal_type='Organisation', title="GreatTitle2")
    # Try something more complicated, create new object, reindex it
    # and then delete it
    deleted_organisation = module.newContent(portal_type='Organisation', title="GreatTitle2")
    deleted_organisation.immediateReindexObject()
    self.commit()
    deleted_url = deleted_organisation.getRelativeUrl()
    module.manage_delObjects(ids=[deleted_organisation.getId()])
    self.commit()
    query = self.portal.cmf_activity_sql_connection().query
    query(
      'update message set processing_node=-4 where method_id in '
      '("playBackRecordedObjectList", "_finishHotReindexing")',
    )
    hasNoProcessableMessage = lambda message_list: all(
      x.processing_node == -4
      for x in message_list
    )
    self.tic(stop_condition=hasNoProcessableMessage)
    self.assertEqual(portal_catalog.getHotReindexingState(), HOT_REINDEXING_DOUBLE_INDEXING_STATE)
    # try to delete objects in double indexing state
    module.manage_delObjects(ids=[organisation2.getId()])
    self.commit()
    query(
      'update message set processing_node=-1 where '
      'method_id="playBackRecordedObjectList"',
    )
    self.tic(stop_condition=hasNoProcessableMessage)
    self.assertEqual(portal_catalog.getHotReindexingState(), HOT_REINDEXING_DOUBLE_INDEXING_STATE)
    # Now we have started an double indexing
    next_deleted_organisation = module.newContent(portal_type='Organisation', title="GreatTitle2",id='toto')
    next_deleted_url = next_deleted_organisation.getRelativeUrl()
    self.tic(stop_condition=hasNoProcessableMessage)
    path_list=[next_deleted_url]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_erp5_sql_connection)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=original_connection_id)
    module.manage_delObjects(ids=[next_deleted_organisation.getId()])
    # Create object during the double indexing to check the security object
    # after the hot reindexing
    module.newContent(portal_type='Organisation', title="GreatTitle2")
    self.commit()
    query(
      'update message set processing_node=-1 where '
      'method_id="_finishHotReindexing"',
    )
    self.tic()
    self.assertEqual(portal_catalog.getHotReindexingState(), HOT_REINDEXING_FINISHED_STATE)
    # Check Security UID object exist in roles and users
    # compare the number object in the catalog
    self.assertCountEqual(
      self.getSQLPathList(original_connection_id),
      self.getSQLPathListWithRolesAndUsers(original_connection_id),
    )

    path_list = [organisation3.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_erp5_sql_connection)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=original_connection_id)
    path_list = [first_deleted_url, deleted_url,next_deleted_url]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.new_erp5_sql_connection)
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=original_connection_id)
    # Make sure module are there
    path_list = [module.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_erp5_sql_connection)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=original_connection_id)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestVanillaERP5Catalog))
  return suite
