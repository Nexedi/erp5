##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
import sys

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


try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestERP5Catalog(ERP5TypeTestCase, LogInterceptor):
  """
    Tests for ERP5 Catalog.
  """

  def getTitle(self):
    return "ERP5Catalog"

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  # Different variables used for this test
  run_all_test = 1
  quiet = 0
  username = 'seb'

  def afterSetUp(self):
    self.login()
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
    uf._doAddUser(self.username, '', ['Manager'], [])
    user = uf.getUserById(self.username).__of__(uf)
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
      self.failUnless(path in path_list)
      LOG('checkRelativeUrlInSQLPathList found path:',0,path)

  def checkRelativeUrlNotInSQLPathList(self,url_list,connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      self.failUnless(path not in  path_list)
      LOG('checkRelativeUrlInSQLPathList not found path:',0,path)

  def test_01_HasEverything(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoryTool()!=None)
    self.failUnless(self.getSimulationTool()!=None)
    self.failUnless(self.getTypeTool()!=None)
    self.failUnless(self.getSQLConnection()!=None)
    self.failUnless(self.getCatalogTool()!=None)

  def test_02_EverythingCatalogued(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Everything Catalogued')
      LOG('Testing... ',0,'testEverythingCatalogued')
    portal_catalog = self.getCatalogTool()
    self.tic()
    organisation_module_list = portal_catalog(portal_type='Organisation Module')
    self.assertEquals(len(organisation_module_list),1)

  def test_03_CreateAndDeleteObject(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Create And Delete Objects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    person = person_module.newContent(id='1',portal_type='Person')
    path_list = [person.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list)
    person.immediateReindexObject()
    self.checkRelativeUrlInSQLPathList(path_list)
    person_module.manage_delObjects('1')
    get_transaction().commit()
    self.tic()
    self.checkRelativeUrlNotInSQLPathList(path_list)
    # Now we will ask to immediatly reindex
    person = person_module.newContent(id='2',
                                      portal_type='Person',
                                      immediate_reindex=1)
    path_list = [person.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list)
    person.immediateReindexObject()
    self.checkRelativeUrlInSQLPathList(path_list)
    person_module.manage_delObjects('2')
    get_transaction().commit()
    self.tic()
    self.checkRelativeUrlNotInSQLPathList(path_list)
    # Now we will try with the method deleteContent
    person = person_module.newContent(id='3',portal_type='Person')
    path_list = [person.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list)
    person.immediateReindexObject()
    self.checkRelativeUrlInSQLPathList(path_list)
    person_module.deleteContent('3')
    # Now delete things is made with activities
    self.checkRelativeUrlNotInSQLPathList(path_list)
    get_transaction().commit()
    self.tic()
    self.checkRelativeUrlNotInSQLPathList(path_list)

  def test_04_SearchFolderWithDeletedObjects(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Search Folder With Deleted Objects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    person_module = self.getPersonModule()
    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)
    person = person_module.newContent(id='4',portal_type='Person',immediate_reindex=1)
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)
    person.immediateReindexObject()
    person_module.manage_delObjects('4')
    get_transaction().commit()
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

  def test_05_SearchFolderWithImmediateReindexObject(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Search Folder With Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

    person = person_module.newContent(id='4',portal_type='Person')
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)
    
    person_module.manage_delObjects('4')
    get_transaction().commit()
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

  def test_06_SearchFolderWithRecursiveImmediateReindexObject(self,
                                              quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Search Folder With Recursive Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

    person = person_module.newContent(id='4',portal_type='Person')
    person_module.recursiveImmediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)
    
    person_module.manage_delObjects('4')
    get_transaction().commit()
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

  def test_07_ClearCatalogAndTestNewContent(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Clear Catalog And Test New Content'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='4',portal_type='Person',immediate_reindex=1)
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)

  def test_08_ClearCatalogAndTestRecursiveImmediateReindexObject(self,
                                               quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Clear Catalog And Test Recursive Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='4',portal_type='Person')
    person_module.recursiveImmediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)

  def test_09_ClearCatalogAndTestImmediateReindexObject(self, quiet=quiet,
                                                        run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Clear Catalog And Test Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='4',portal_type='Person')
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)

  def test_10_OrderedSearchFolder(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Ordered Search Folder'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='a',portal_type='Person',title='a',description='z')
    person.immediateReindexObject()
    person = person_module.newContent(id='b',portal_type='Person',title='a',description='y')
    person.immediateReindexObject()
    person = person_module.newContent(id='c',portal_type='Person',title='a',description='x')
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getId()
              for x in person_module.searchFolder(sort_on=[('id','ascending')])]
    self.assertEquals(['a','b','c'],folder_object_list)
    folder_object_list = [x.getObject().getId()
              for x in person_module.searchFolder(
              sort_on=[('title','ascending'), ('description','ascending')])]
    self.assertEquals(['c','b','a'],folder_object_list)
    folder_object_list = [x.getObject().getId()
              for x in person_module.searchFolder(
              sort_on=[('title','ascending'),('description','descending')])]
    self.assertEquals(['a','b','c'],folder_object_list)

  def test_11_CastStringAsInt(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Cast String As Int With Order By'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='a',portal_type='Person',title='1')
    person.immediateReindexObject()
    person = person_module.newContent(id='b',portal_type='Person',title='2')
    person.immediateReindexObject()
    person = person_module.newContent(id='c',portal_type='Person',title='12')
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getTitle() for x in person_module.searchFolder(sort_on=[('title','ascending')])]
    self.assertEquals(['1','12','2'],folder_object_list)
    folder_object_list = [x.getObject().getTitle() for x in person_module.searchFolder(sort_on=[('title','ascending','int')])]
    self.assertEquals(['1','2','12'],folder_object_list)

  def test_12_TransactionalUidBuffer(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Transactional Uid Buffer'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    portal_catalog = self.getCatalogTool()
    catalog = portal_catalog.getSQLCatalog()
    self.failUnless(catalog is not None)

    # Clear out the uid buffer.
    if hasattr(catalog, '_v_uid_buffer'):
      del catalog._v_uid_buffer

    # Need to abort a transaction artificially, so commit the current
    # one, first.
    get_transaction().commit()

    catalog.newUid()
    self.failUnless(hasattr(catalog, '_v_uid_buffer'))
    self.failUnless(len(catalog._v_uid_buffer) > 0)

    get_transaction().abort()
    self.failUnless(len(getattr(catalog, '_v_uid_buffer', [])) == 0)

  def test_13_ERP5Site_reindexAll(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'ERP5Site_reindexAll'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    # Flush message queue
    get_transaction().commit()
    self.tic()
    # Create some objects
    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    base_category = portal_category.newContent(portal_type='Base Category',
                                               title="GreatTitle1")
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',
                                     title="GreatTitle2")
    # Flush message queue
    get_transaction().commit()
    self.tic()
    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    sql_connection = self.getSQLConnection()
    sql = 'select count(*) from catalog where portal_type!=NULL'
    result = sql_connection.manage_test(sql)
    message_count = result[0]['COUNT(*)']
    self.assertEquals(0, message_count)
    # Commit
    get_transaction().commit()
    # Reindex all
    portal.ERP5Site_reindexAll()
    get_transaction().commit()
    self.tic()
    get_transaction().commit()
    # Check catalog
    sql = 'select count(*) from message'
    result = sql_connection.manage_test(sql)
    message_count = result[0]['COUNT(*)']
    self.assertEquals(0, message_count)
    # Check if object are catalogued
    self.checkRelativeUrlInSQLPathList([
                organisation.getRelativeUrl(),
                'portal_categories/%s' % base_category.getRelativeUrl()])

  def test_14_ReindexWithBrokenCategory(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Reindexing an object with 1 broken category must not'\
                ' affect other valid categories '
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    # Flush message queue
    get_transaction().commit()
    self.tic()
    # Create some objects
    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    group_nexedi_category = portal_category.group\
                                .newContent( id = 'nexedi', )
    region_europe_category = portal_category.region\
                                .newContent( id = 'europe', )
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    organisation.setGroup('nexedi')
    self.assertEquals(organisation.getGroupValue(), group_nexedi_category)
    organisation.setRegion('europe')
    self.assertEquals(organisation.getRegionValue(), region_europe_category)
    organisation.setRole('not_exists')
    self.assertEquals(organisation.getRoleValue(), None)
    # Flush message queue
    get_transaction().commit()
    self.tic()
    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    sql_connection = self.getSQLConnection()
    
    sql = 'SELECT COUNT(*) FROM category '\
        'WHERE uid=%s and category_strict_membership = 1' %\
        organisation.getUid()
    result = sql_connection.manage_test(sql)
    message_count = result[0]['COUNT(*)']
    self.assertEquals(0, message_count)
    # Commit
    get_transaction().commit()
    self.tic()
    # Check catalog
    organisation.reindexObject()
    # Commit
    get_transaction().commit()
    self.tic()
    sql = 'select count(*) from message'
    result = sql_connection.manage_test(sql)
    message_count = result[0]['COUNT(*)']
    self.assertEquals(0, message_count)
    # Check region and group categories are catalogued
    for base_cat, theorical_count in {
                                      'region':1,
                                      'group':1,
                                      'role':0}.items() :
      sql = """SELECT COUNT(*) FROM category
            WHERE category.uid=%s and category.category_strict_membership = 1
            AND category.base_category_uid = %s""" % (organisation.getUid(),
                    portal_category[base_cat].getUid())
      result = sql_connection.manage_test(sql)
      cataloged_obj_count = result[0]['COUNT(*)']
      self.assertEquals(theorical_count, cataloged_obj_count,
            'category %s is not cataloged correctly' % base_cat)

  def test_15_getObject(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'getObject'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    # portal_catalog.getObject raises a ValueError if UID parameter is a string
    portal_catalog = self.getCatalogTool()
    self.assertRaises(ValueError, portal_catalog.getObject, "StringUID")
  
  def test_16_newUid(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'newUid'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    # newUid should not assign the same uid
    portal_catalog = self.getCatalogTool()
    from Products.ZSQLCatalog.SQLCatalog import UID_BUFFER_SIZE
    uid_dict = {}
    for i in xrange(UID_BUFFER_SIZE * 3):
      uid = portal_catalog.newUid()
      self.failUnless(isinstance(uid, long))
      self.failIf(uid in uid_dict)
      uid_dict[uid] = None
  
  def test_17_CreationDate_ModificationDate(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'getCreationDate, getModificationDate'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal_catalog = self.getCatalogTool()
    portal = self.getPortal()
    sql_connection = self.getSQLConnection()
    
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    creation_date = organisation.getCreationDate().ISO()
    get_transaction().commit()
    now = DateTime()
    self.tic()
    sql = """select creation_date, modification_date 
             from catalog where uid = %s""" % organisation.getUid()
    result = sql_connection.manage_test(sql)
    self.assertEquals(creation_date, result[0]['creation_date'].ISO())
    self.assertEquals(organisation.getModificationDate().ISO(),
                              result[0]['modification_date'].ISO())
    self.assertEquals(creation_date, result[0]['modification_date'].ISO())
    
    import time; time.sleep(3)
    organisation.edit(title='edited')
    get_transaction().commit()
    self.tic()
    result = sql_connection.manage_test(sql)
    self.assertEquals(creation_date, result[0]['creation_date'].ISO())
    self.assertNotEquals(organisation.getModificationDate(),
                              organisation.getCreationDate())
    # This test was first written with a now variable initialized with
    # DateTime(). But since we are never sure of the time required in
    # order to execute some line of code
    self.assertEquals(organisation.getModificationDate().ISO(),
                              result[0]['modification_date'].ISO())
    self.assertTrue(organisation.getModificationDate()>now)
    self.assertTrue(result[0]['creation_date']<result[0]['modification_date'])
  
  # TODO: this test is disabled (and maybe not complete), because this feature
  # is not implemented
  def test_18_buildSQLQueryAnotherTable(self, quiet=quiet, run=0):
    """Tests that buildSQLQuery works with another query_table than 'catalog'"""
    if not run: return
    if not quiet:
      message = 'buildSQLQuery with query_table'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal = self.getPortal()
    portal_catalog = self.getCatalogTool()
    # clear catalog
    portal_catalog.manage_catalogClear()
    get_transaction().commit()
    
    # create some content to use destination_section_title as related key
    # FIXME: create the related key here ?
    module = portal.getDefaultModule('Organisation')
    source_organisation = module.newContent( portal_type='Organisation',
                                        title = 'source_organisation')
    destination_organisation = module.newContent( portal_type='Organisation',
                                        title = 'destination_organisation')
    source_organisation.setDestinationSectionValue(destination_organisation)
    source_organisation.recursiveReindexObject()
    destination_organisation.recursiveReindexObject()
    get_transaction().commit()
    self.tic()

    # buildSQLQuery can use arbitrary table name.
    query_table = "node"
    sql_squeleton = """
    SELECT %(query_table)s.uid,
           %(query_table)s.id
    FROM
      <dtml-in prefix="table" expr="from_table_list"> 
        <dtml-var table_item> AS <dtml-var table_key>
        <dtml-unless sequence-end>, </dtml-unless>
      </dtml-in>
    <dtml-if where_expression>
    WHERE 
      <dtml-var where_expression>
    </dtml-if>
    <dtml-if order_by_expression>
      ORDER BY <dtml-var order_by_expression>
    </dtml-if>
    """ % {'query_table' : query_table}
    
    portal_skins_custom = portal.portal_skins.custom
    portal_skins_custom.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod(
          id = 'testMethod',
          title = '',
          connection_id = 'erp5_sql_connection',
          arguments = "\n".join([ 'from_table_list',
                                  'where_expression',
                                  'order_by_expression' ]),
          template = sql_squeleton)
    testMethod = portal_skins_custom['testMethod']
    
    default_parametrs = {}
    default_parametrs['portal_type'] = 'Organisation'
    default_parametrs['from_table_list'] = {}
    default_parametrs['where_expression'] = ""
    default_parametrs['order_by_expression'] = None
    
    #import pdb; pdb.set_trace()
    # check that we retrieve our 2 organisations by default.
    kw = default_parametrs.copy()
    kw.update( portal_catalog.buildSQLQuery(
                  query_table = query_table,
                  **kw) )
    LOG('kw', 0, kw)
    LOG('SQL', 0, testMethod(src__=1, **kw))
    self.assertEquals(len(testMethod(**kw)), 2)
    
    # check we can make a simple filter on title.
    kw = default_parametrs.copy()
    kw.update( portal_catalog.buildSQLQuery(
                  query_table = query_table,
                  title = 'source_organisation',
                  **kw) )
    LOG('kw', 1, kw)
    LOG('SQL', 1, testMethod(src__=1, **kw))
    self.assertEquals( len(testMethod(**kw)), 1,
                       testMethod(src__=1, **kw) )
    self.assertEquals( testMethod(**kw)[0]['uid'],
                        source_organisation.getUid(),
                        testMethod(src__=1, **kw) )
    
    # check sort
    kw = default_parametrs.copy()
    kw.update(portal_catalog.buildSQLQuery(
                  query_table = query_table,
                  sort_on = [('id', 'ascending')],
                  **kw))
    LOG('kw', 2, kw)
    LOG('SQL', 2, testMethod(src__=1, **kw))
    brains = testMethod(**kw)
    self.assertEquals( len(brains), 2,
                       testMethod(src__=1, **kw))
    self.failIf( brains[0]['id'] > brains[1]['id'],
                 testMethod(src__=1, **kw) )
    
    # check related keys works
    kw = default_parametrs.copy()
    kw.update(portal_catalog.buildSQLQuery(
                  query_table = query_table,
                  destination_section_title = 'organisation_destination'),
                  **kw)
    LOG('kw', 3, kw)
    LOG('SQL', 3, testMethod(src__=1, **kw))
    brains = testMethod(**kw)
    self.assertEquals( len(brains), 1, testMethod(src__=1, **kw) )
    self.assertEquals( brains[0]['uid'],
                       source_organisation.getUid(),
                       testMethod(src__=1, **kw) )
    
  def test_19_SearchFolderWithNonAsciiCharacter(self,
                                quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Search Folder With Non Ascii Character'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Now we will try the same thing as previous test and look at searchFolder
    title='S\xc3\xa9bastien'
    person = person_module.newContent(id='5',portal_type='Person',title=title)
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['5'],folder_object_list)
    folder_object_list = [x.getObject().getId() for x in 
                              person_module.searchFolder(title=title)]
    self.assertEquals(['5'],folder_object_list)
  

  def test_20_SearchFolderWithDynamicRelatedKey(self,
                                  quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Search Folder With Dynamic Related Key'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    # Create some objects
    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    portal_category.group.manage_delObjects([x for x in
        portal_category.group.objectIds()])
    group_nexedi_category = portal_category.group\
                                .newContent( id = 'nexedi', title='Nexedi',
                                             description='a')
    group_nexedi_category2 = portal_category.group\
                                .newContent( id = 'storever', title='Storever',
                                             description='b')
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    organisation.setGroup('nexedi')
    self.assertEquals(organisation.getGroupValue(), group_nexedi_category)
    organisation2 = module.newContent(portal_type='Organisation',)
    organisation2.setGroup('storever')
    organisation2.setTitle('Organisation 2')
    self.assertEquals(organisation2.getGroupValue(), group_nexedi_category2)
    # Flush message queue
    get_transaction().commit()
    self.tic()

    # Try to get the organisation with the group title Nexedi
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(group_title='Nexedi')]
    self.assertEquals(organisation_list,[organisation])
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(default_group_title='Nexedi')]
    self.assertEquals(organisation_list,[organisation])
    # Try to get the organisation with the group id 
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(group_id='storever')]
    self.assertEquals(organisation_list,[organisation2])
    # Try to get the organisation with the group description 'a'
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(group_description='a')]
    self.assertEquals(organisation_list,[organisation])
    # Try to get the organisation with the group description 'c'
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(group_description='c')]
    self.assertEquals(organisation_list,[])
    # Try to get the organisation with the default group description 'c'
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(default_group_description='c')]
    self.assertEquals(organisation_list,[])
    # Try to get the organisation with group relative_url
    group_relative_url = group_nexedi_category.getRelativeUrl()
    organisation_list = [x.getObject() for x in 
                 module.searchFolder(group_relative_url=group_relative_url)]
    self.assertEquals(organisation_list, [organisation])
    # Try to get the organisation with group uid
    organisation_list = [x.getObject() for x in 
                 module.searchFolder(group_uid=group_nexedi_category.getUid())]
    self.assertEquals(organisation_list, [organisation])
    # Try to get the organisation with the group id AND title of the document
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(group_id='storever',
                                             title='Organisation 2')]
    self.assertEquals(organisation_list,[organisation2])


  def test_21_SearchFolderWithDynamicStrictRelatedKey(self,
                                  quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Search Folder With Strict Dynamic Related Key'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    # Create some objects
    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    portal_category.group.manage_delObjects([x for x in
        portal_category.group.objectIds()])
    group_nexedi_category = portal_category.group\
                                .newContent( id = 'nexedi', title='Nexedi',
                                             description='a')
    sub_group_nexedi = group_nexedi_category\
                                .newContent( id = 'erp5', title='ERP5',
                                             description='b')
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    organisation.setGroup('nexedi/erp5')
    self.assertEquals(organisation.getGroupValue(), sub_group_nexedi)
    # Flush message queue
    get_transaction().commit()
    self.tic()

    # Try to get the organisation with the group title Nexedi
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(strict_group_title='Nexedi')]
    self.assertEquals(organisation_list,[])
    # Try to get the organisation with the group title ERP5
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(strict_group_title='ERP5')]
    self.assertEquals(organisation_list,[organisation])
    # Try to get the organisation with the group description a
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(strict_group_description='a')]
    self.assertEquals(organisation_list,[])
    # Try to get the organisation with the group description b
    organisation_list = [x.getObject() for x in 
                         module.searchFolder(strict_group_description='b')]
    self.assertEquals(organisation_list,[organisation])

  def test_22_SearchingWithUnicode(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test searching with unicode'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()
    person_module.newContent(portal_type='Person', title='A Person')
    get_transaction().commit()
    self.tic()
    self.assertNotEquals([], self.getCatalogTool().searchResults(
                                     portal_type='Person', title=u'A Person'))
    
  def test_23_DeleteObjectRaiseErrorWhenQueryFail(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test That Delete Object Raise Error When the Query Fail'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    # Now we will ask to immediatly reindex
    person = person_module.newContent(id='2',
                                      portal_type='Person',
                                      immediate_reindex=1)
    path_list = [person.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list)
    # We will delete the connector
    # in order to make sure it will not work any more
    portal = self.getPortal()
    portal.manage_delObjects('erp5_sql_connection')
    # Then it must be impossible to delete an object
    uid = person.getUid()
    unindex = portal_catalog.unindexObject
    self.assertRaises(AttributeError,unindex,person,uid=person.getUid())
    get_transaction().abort()

  def test_24_SortOn(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Sort On'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    self.assertEquals('catalog.title',
            self.getCatalogTool().buildSQLQuery(
            sort_on=(('catalog.title', 'ascending'),))['order_by_expression'])

  def test_25_SortOnDescending(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Sort On Descending'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    self.assertEquals('catalog.title DESC',
            self.getCatalogTool().buildSQLQuery(
            sort_on=(('catalog.title', 'descending'),))['order_by_expression'])
    
  def test_26_SortOnUnknownKeys(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not run: return
    if not quiet:
      message = 'Test Sort On Unknow Keys'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    self.assertEquals('',
          self.getCatalogTool().buildSQLQuery(
          sort_on=(('ignored', 'ascending'),))['order_by_expression'])
  
  def test_27_SortOnAmbigousKeys(self, quiet=quiet, run=run_all_test):
    # XXX This *describes* the current behaviour, which might be
    # non optimal, but at least we have a test to make sure that bugs are not
    # introduced here.
    if not run: return
    if not quiet:
      message = 'Test Sort On Ambigous Keys'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    # if the sort key is found on the catalog table, it will use that catalog
    # table.
    self.assertEquals('catalog.title',
          self.getCatalogTool().buildSQLQuery(
          sort_on=(('title', 'ascending'),))['order_by_expression'])
    
    # if not found on catalog, it won't do any filtering
    # in the above, start_date exists both in delivery and movement table.
    self._catch_log_errors(ignored_level = sys.maxint)
    self.assertEquals('',
          self.getCatalogTool().buildSQLQuery(
          sort_on=(('start_date', 'ascending'),))['order_by_expression'])
    self._ignore_log_errors()
    # buildSQLQuery will simply put a warning in the error log and ignore
    # this key.
    logged_errors = [ logrecord for logrecord in self.logged
                       if logrecord[0] == 'SQLCatalog' ]
    self.failUnless( 'could not build sort index' in logged_errors[0][2])
    
    # of course, in that case, it's possible to prefix with table name
    self.assertEquals('delivery.start_date',
          self.getCatalogTool().buildSQLQuery(
          sort_on=(('delivery.start_date', 'ascending'),
                    ))['order_by_expression'])
    
  def test_28_SortOnMultipleKeys(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Sort On Multiple Keys'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    self.assertEquals('catalog.title,catalog.id',
              self.getCatalogTool().buildSQLQuery(
              sort_on=(('catalog.title', 'ascending'),
                       ('catalog.id', 'asc')))
                       ['order_by_expression'].replace(' ', ''))

  def test_29_SortOnRelatedKey(self, quiet=quiet, run=run_all_test):
    """Sort-on parameter and related key. (Assumes that region_title is a \
    valid related key)"""
    if not run: return
    if not quiet:
      message = 'Test Sort On Related Keys'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    self.assertNotEquals('',
              self.getCatalogTool().buildSQLQuery(region_title='',
              sort_on=(('region_title', 'ascending'),))['order_by_expression'])
    self.assertNotEquals('',
              self.getCatalogTool().buildSQLQuery(
              sort_on=(('region_title', 'ascending'),))['order_by_expression'],
              'sort_on parameter must be taken into account even if related key '
              'is not a parameter of the current query')

  def _makeOrganisation(self, **kw):
    """Creates an Organisation in it's default module and reindex it.
    By default, it creates a group/nexedi category, and make the organisation a
    member of this category.
    """
    group_cat = self.getCategoryTool().group
    if not hasattr(group_cat, 'nexedi'):
      group_cat.newContent(id='nexedi', title='Nexedi Group',)
    module = self.getPortal().getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation')
    kw.setdefault('group', 'group/nexedi')
    organisation.edit(**kw)
    get_transaction().commit()
    self.tic()
    return organisation
  
  def test_30_SimpleQueryDict(self, quiet=quiet, run=run_all_test):
    """use a dict as a keyword parameter.
    """
    if not run: return
    if not quiet:
      message = 'Test Simple Query Dict'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    organisation_title = 'Nexedi Organisation'
    organisation = self._makeOrganisation(title=organisation_title)
    self.assertEquals([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                title={'query': organisation_title})])

  def test_31_RelatedKeySimpleQueryDict(self, quiet=quiet, run=run_all_test):
    """use a dict as a keyword parameter, but using a related key
    """
    if not run: return
    if not quiet:
      message = 'Test Related Key Simple Query Dict'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    organisation = self._makeOrganisation()
    self.assertEquals([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                group_title={'query': 'Nexedi Group'},
                # have to filter on portal type, because the group category is
                # also member of itself
                portal_type=organisation.getPortalTypeName())])

  def test_32_SimpleQueryDictWithOrOperator(self, quiet=quiet,
                                                    run=run_all_test):
    """use a dict as a keyword parameter, with OR operator.
    """
    if not run: return
    if not quiet:
      message = 'Test Query Dict With Or Operator'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    organisation_title = 'Nexedi Organisation'
    organisation = self._makeOrganisation(title=organisation_title)
  
    self.assertEquals([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                title={'query': (organisation_title, 'something else'),
                       'operator': 'or'})])

  def test_33_SimpleQueryDictWithAndOperator(self, quiet=quiet,
                                                     run=run_all_test):
    """use a dict as a keyword parameter, with AND operator.
    """
    if not run: return
    if not quiet:
      message = 'Test Query Dict With And Operator'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    organisation_title = 'Nexedi Organisation'
    organisation = self._makeOrganisation(title=organisation_title)
  
    self.assertEquals([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                # this is useless, we must find a better use case
                title={'query': (organisation_title, organisation_title),
                       'operator': 'and'})])

  def test_34_SimpleQueryDictWithMaxRangeParameter(self, quiet=quiet,
                                                     run=run_all_test):
    """use a dict as a keyword parameter, with max range parameter ( < )
    """
    if not run: return
    if not quiet:
      message = 'Test Query Dict With Max Range Operator'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')
  
    self.assertEquals([org_a.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': 'B', 'range': 'max'})])
  
  def test_35_SimpleQueryDictWithMinRangeParameter(self, quiet=quiet,
                                                     run=run_all_test):
    """use a dict as a keyword parameter, with min range parameter ( >= )
    """
    if not run: return
    if not quiet:
      message = 'Test Query Dict With Min Range Operator'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')
  
    self.failIfDifferentSet([org_b.getPath(), org_c.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': 'B', 'range': 'min'})])


  def test_36_SimpleQueryDictWithNgtRangeParameter(self, quiet=quiet,
                                                     run=run_all_test):
    """use a dict as a keyword parameter, with ngt range parameter ( <= )
    """
    if not run: return
    if not quiet:
      message = 'Test Query Dict With Ngt Range Operator'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')
  
    self.failIfDifferentSet([org_a.getPath(), org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': 'B', 'range': 'ngt'})])

  def test_37_SimpleQueryDictWithMinMaxRangeParameter(self, quiet=quiet,
                                                     run=run_all_test):
    """use a dict as a keyword parameter, with minmax range parameter ( >=  < )
    """
    if not run: return
    if not quiet:
      message = 'Test Query Dict With Min Max Range Operator'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')
  
    self.assertEquals([org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': ('B', 'C'), 'range': 'minmax'})])
  
  def test_38_SimpleQueryDictWithMinNgtRangeParameter(self, quiet=quiet,
                                                     run=run_all_test):
    """use a dict as a keyword parameter, with minngt range parameter ( >= <= )
    """
    if not run: return
    if not quiet:
      message = 'Test Query Dict With Min Ngt Range Operator'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')
  
    self.failIfDifferentSet([org_b.getPath(), org_c.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': ('B', 'C'), 'range': 'minngt'})])

  def test_39_DeferredConnection(self, quiet=quiet, run=run_all_test):
    """ERP5Catalog uses a deferred connection for full text indexing.
    """
    if not run: return
    if not quiet:
      message = 'Test Deferred Connection'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    erp5_sql_deferred_connection = getattr(self.getPortal(),
                                    'erp5_sql_deferred_connection',
                                    None)
    self.failUnless(erp5_sql_deferred_connection is not None)
    self.assertEquals('Z MySQL Deferred Database Connection',
                      erp5_sql_deferred_connection.meta_type)
    for method in ['z0_drop_fulltext',
                   'z0_uncatalog_fulltext',
                   'z_catalog_fulltext_list',
                   'z_create_fulltext', ]:
      self.assertEquals('erp5_sql_deferred_connection',
                getattr(self.getCatalogTool().getSQLCatalog(),
                              method).connection_id)

  def test_40_DeleteObject(self, quiet=quiet, run=run_all_test):
    """Simple test to exercise object deletion
    """
    if not run: return
    if not quiet:
      message = 'Test Delete Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    folder = self.getOrganisationModule()
    ob = folder.newContent()
    get_transaction().commit()
    self.tic()
    folder.manage_delObjects([ob.getId()])
    get_transaction().commit()
    self.tic()
    self.assertEquals(0, len(folder.searchFolder()))

  def test_41_ProxyRolesInRestrictedPython(self, quiet=quiet, run=run_all_test):
    """test that proxy roles apply to catalog queries within python scripts
    """
    if not run: return
    if not quiet:
      message = 'Proxy Roles In Restricted Python'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    login = PortalTestCase.login
    perm = 'View'

    uf = self.getPortal().acl_users
    uf._doAddUser('alice', '', ['Member', 'Manager', 'Assignor'], [])
    uf._doAddUser('bob', '', ['Member'], [])
    # create restricted object
    login(self, 'alice')
    folder = self.getOrganisationModule()
    ob = folder.newContent()
    # make sure permissions are correctly set
    folder.manage_permission('Access contents information', ['Member'], 1)
    folder.manage_permission(perm, ['Member'], 1)
    ob.manage_permission('Access contents information', ['Member'], 1)
    ob.manage_permission(perm, ['Manager'], 0)
    get_transaction().commit()
    self.tic()
    # check access
    self.assertEquals(1, getSecurityManager().checkPermission(perm, folder))
    self.assertEquals(1, getSecurityManager().checkPermission(perm, ob))
    login(self, 'bob')
    self.assertEquals(1, getSecurityManager().checkPermission(perm, folder))
    self.assertEquals(None, getSecurityManager().checkPermission(perm, ob))
    # add a script that calls a catalog method
    login(self, 'alice')
    script = createZODBPythonScript(self.getPortal().portal_skins.custom,
        'catalog_test_script', '', "return len(context.searchFolder())")

    # test without proxy role
    self.assertEquals(1, folder.catalog_test_script())
    login(self, 'bob')
    self.assertEquals(0, folder.catalog_test_script())

    # test with proxy role and correct role
    login(self, 'alice')
    script.manage_proxy(['Manager'])
    self.assertEquals(1, folder.catalog_test_script())
    login(self, 'bob')
    self.assertEquals(1, folder.catalog_test_script())

    # test with proxy role and wrong role
    login(self, 'alice')
    script.manage_proxy(['Assignor'])
    # proxy roles must overwrite the user's roles, even if he is the owner
    # of the script
    self.assertEquals(0, folder.catalog_test_script())
    login(self, 'bob')
    self.assertEquals(0, folder.catalog_test_script())

  def test_42_SearchableText(self, quiet=quiet, run=run_all_test):
    """Tests SearchableText is working in ERP5Catalog
    """
    if not run: return
    if not quiet:
      message = 'Searchable Text'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    folder = self.getOrganisationModule()
    ob = folder.newContent()
    ob.setTitle('The title of this object')
    self.failUnless('this' in ob.SearchableText(), ob.SearchableText())
    # add some other objects, we need to create a minimum quantity of data for
    # full text queries to work correctly
    for i in range(10):
      otherob = folder.newContent()
      otherob.setTitle('Something different')
      self.failIf('this' in otherob.SearchableText(), otherob.SearchableText())
    # catalog those objects
    get_transaction().commit()
    self.tic()
    self.assertEquals([ob],
        [x.getObject() for x in self.getCatalogTool()(
                portal_type='Organisation', SearchableText='title')])
    
    # 'different' is not revelant, because it's found in more than 50% of
    # records
    self.assertEquals([],
        [x.getObject for x in self.getCatalogTool()(
                portal_type='Organisation', SearchableText='different')])
    
    # test countResults
    self.assertEquals(1, self.getCatalogTool().countResults(
              portal_type='Organisation', SearchableText='title')[0][0])
    self.assertEquals(0, self.getCatalogTool().countResults(
              portal_type='Organisation', SearchableText='different')[0][0])
    
  def test_43_ManagePasteObject(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Manage Paste Objects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    person = person_module.newContent(id='1',portal_type='Person')
    get_transaction().commit()
    self.tic()
    copy_data = person_module.manage_copyObjects([person.getId()])
    new_id = person_module.manage_pasteObjects(copy_data)[0]['new_id']
    new_person = person_module[new_id]
    get_transaction().commit()
    self.tic()
    path_list = [new_person.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list)

  def test_44_ParentRelatedKeys(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Parent related keys'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    person_module.reindexObject()
    person = person_module.newContent(id='1',portal_type='Person')
    get_transaction().commit()
    self.tic()
    self.assertEquals([person],
        [x.getObject() for x in self.getCatalogTool()(
               parent_title=person_module.getTitle())])
    
  def test_45_QueryAndComplexQuery(self,quiet=quiet, run=run_all_test):
    """
    """
    if not run: return
    if not quiet:
      message = 'Query And Complex Query'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    org_a = self._makeOrganisation(title='abc',description='abc')
    org_b = self._makeOrganisation(title='bcd',description='bcd')
    org_c = self._makeOrganisation(title='efg',description='efg')
    org_e = self._makeOrganisation(title='foo',description='bir')
    org_f = self._makeOrganisation(title='foo',description='bar')

    # title='abc'
    catalog_kw= {'title':Query(title='abc')}
    self.failIfDifferentSet([org_a.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    # title with b and c
    catalog_kw= {'title':Query(title=['%b%','%c%'],operator='AND')}
    self.failIfDifferentSet([org_a.getPath(), org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    # title='bcd' OR description='efg'
    catalog_kw = {'query':ComplexQuery(Query(title='bcd'),
                                       Query(description='efg'),
                                       operator='OR')}
    self.failIfDifferentSet([org_b.getPath(), org_c.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    # Recursive Complex Query
    # (title='abc' and description='abc') OR 
    #  title='foo' and description='bar'
    catalog_kw = {'query':ComplexQuery(ComplexQuery(Query(title='abc'),
                                                    Query(description='abc'),
                                                    operator='AND'),
                                       ComplexQuery(Query(title='foo'),
                                                    Query(description='bar'),
                                                    operator='AND'),
                                       operator='OR')}
    self.failIfDifferentSet([org_a.getPath(), org_f.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
  
  def test_46_TestLimit(self,quiet=quiet, run=run_all_test):
    """
    """
    if not run: return
    if not quiet:
      message = 'Test Limit'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    ctool = self.getCatalogTool()
    old_default_result_limit = ctool.default_result_limit
    max_ = ctool.default_result_limit = 3
    #Create max + 2 Organisations
    for i in xrange(max_ + 2):
      self._makeOrganisation(title='abc%s' % (i), description='abc')
    self.assertEqual(max_,
                     len(self.getCatalogTool()(portal_type='Organisation')))
    self.assertEqual(max_ + 2,
            len(self.getCatalogTool()(portal_type='Organisation', limit=None)))
    ctool.default_result_limit = old_default_result_limit

  def playActivityList(self, method_id_list):
    get_transaction().commit()
    portal_activities = self.getActivityTool()
    for i in range(0,100):
      message_list = portal_activities.getMessageList()
      for message in message_list:
        #if message.method_id=='setHotReindexingState':
        #  import pdb;pdb.set_trace()
        if message.method_id in method_id_list:
          try:
            portal_activities.manageInvoke(message.object_path,message.method_id)
          except ActivityFlushError,m:
            pass
      get_transaction().commit()

  def test_48_ERP5Site_hotReindexAll(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Hot Reindex All'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    portal_activities = self.getActivityTool()
    self.base_category = portal_category.newContent(portal_type='Base Category',
                                               title="GreatTitle1")
    module = portal.getDefaultModule('Organisation')
    self.organisation = module.newContent(portal_type='Organisation',
                                     title="GreatTitle2")
    # Flush message queue
    get_transaction().commit()
    self.tic()
    # Create new connectors
    self.original_connection_id = 'erp5_sql_connection'
    self.new_connection_id = 'erp5_sql_connection2'
    portal.manage_addZMySQLConnection(self.new_connection_id,'',
                                      'test2 test2')
    new_connection = portal[self.new_connection_id]
    new_connection.manage_open_connection()
    # Create new catalog
    portal_catalog = self.getCatalogTool()
    self.original_catalog_id = 'erp5_mysql_innodb'
    self.new_catalog_id = self.original_catalog_id + '2'
    cp_data = portal_catalog.manage_copyObjects(ids=('erp5_mysql_innodb',))
    new_id = portal_catalog.manage_pasteObjects(cp_data)[0]['new_id']
    new_catalog_id = 'erp5_mysql_innodb2'
    portal_catalog.manage_renameObject(id=new_id,new_id=new_catalog_id)

    # Parse all methods in the new catalog in order to change the connector
    new_catalog = portal_catalog[self.new_catalog_id]
    for zsql_method in new_catalog.objectValues():
      setattr(zsql_method,'connection_id',self.new_connection_id)
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_hotReindexAll(self.original_catalog_id,
                                 self.new_catalog_id)
    # Flush message queue
    get_transaction().commit()
    self.tic()
    portal = self.getPortal()
    module = portal.getDefaultModule('Organisation')
    self.organisation2 = module.newContent(portal_type='Organisation',
                                     title="GreatTitle2")
    first_deleted_url = self.organisation2.getRelativeUrl()
    get_transaction().commit()
    self.tic()
    path_list = [self.organisation.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    path_list = [self.organisation2.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list, connection_id=self.original_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)

    # Make sure some zsql method use the right connection_id
    zslq_method = portal.portal_skins.erp5_core.Resource_zGetInventoryList
    self.assertEquals(getattr(zsql_method,'connection_id'),self.new_connection_id)

    self.assertEquals(portal_catalog.getHotReindexingState(),
                      HOT_REINDEXING_FINISHED_STATE)

    # Do a hot reindex in the reverse way, but this time a more
    # complicated hot reindex
    portal_catalog.manage_hotReindexAll(self.new_catalog_id,
                                 self.original_catalog_id)
    get_transaction().commit()
    self.assertEquals(portal_catalog.getHotReindexingState(),
                      HOT_REINDEXING_RECORDING_STATE)
    self.organisation3 = module.newContent(portal_type='Organisation',
                                     title="GreatTitle2")
    # Try something more complicated, create new object, reindex it
    # and then delete it
    self.deleted_organisation = module.newContent(portal_type='Organisation',
                                     title="GreatTitle2")
    self.deleted_organisation.immediateReindexObject()
    get_transaction().commit()
    deleted_url = self.deleted_organisation.getRelativeUrl()
    module.manage_delObjects(ids=[self.deleted_organisation.getId()])
    get_transaction().commit()
    # We will invoke acitivities one by one in order to make sure we can test
    # the double indexing state of hot reindexing
    self.playActivityList(('Folder_reindexAll',
                         'InventoryModule_reindexMovementList',
                         'immediateReindexObject',
                         'Folder_reindexObjectList',
                         'unindexObject',
                         'recursiveImmediateReindexObject'))
    # try to delete objects in double indexing state
    module.manage_delObjects(ids=[self.organisation2.getId()])
    self.playActivityList(('immediateReindexObject',
                         'unindexObject',
                         'recursiveImmediateReindexObject',
                         'playBackRecordedObjectList',
                         'getId',
                         'setHotReindexingState'))
    self.assertEquals(portal_catalog.getHotReindexingState(),
                      HOT_REINDEXING_DOUBLE_INDEXING_STATE)
    # Now we have started an double indexing
    self.next_deleted_organisation = module.newContent(portal_type='Organisation',
                                     title="GreatTitle2",id='toto')
    next_deleted_url = self.next_deleted_organisation.getRelativeUrl()
    get_transaction().commit()
    self.playActivityList(( 'immediateReindexObject',
                         'recursiveImmediateReindexObject',))
    path_list=[next_deleted_url]
    self.checkRelativeUrlInSQLPathList(path_list,connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list,connection_id=self.original_connection_id)
    module.manage_delObjects(ids=[self.next_deleted_organisation.getId()])
    get_transaction().commit()
    self.tic()
    self.assertEquals(portal_catalog.getHotReindexingState(),
                      HOT_REINDEXING_FINISHED_STATE)
    path_list = [self.organisation3.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list,connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list,connection_id=self.original_connection_id)
    path_list = [first_deleted_url,deleted_url,next_deleted_url]
    self.checkRelativeUrlNotInSQLPathList(path_list,connection_id=self.new_connection_id)
    self.checkRelativeUrlNotInSQLPathList(path_list,connection_id=self.original_connection_id)
    # Make sure module are there
    path_list = [module.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.new_connection_id)
    self.checkRelativeUrlInSQLPathList(path_list, connection_id=self.original_connection_id)
    
  def test_47_Unrestricted(self, quiet=quiet, run=run_all_test):
    """test unrestricted search/count results.
    """
    if not run: return
    if not quiet:
      message = 'Unrestricted queries'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    login = PortalTestCase.login

    uf = self.getPortal().acl_users
    uf._doAddUser('alice', '', ['Member', 'Manager', 'Assignor'], [])
    uf._doAddUser('bob', '', ['Member'], [])

    # create a document that only alice can view
    login(self, 'alice')
    folder = self.getOrganisationModule()
    ob = folder.newContent(title='Object Title')
    ob.manage_permission('View', ['Manager'], 0)
    get_transaction().commit()
    self.tic()
    
    # bob cannot see the document
    login(self, 'bob')
    ctool = self.getCatalogTool()
    self.assertEquals(0, len(ctool.searchResults(title='Object Title')))
    self.assertEquals(0, ctool.countResults(title='Object Title')[0][0])
    
    # unless using unrestricted searches
    self.assertEquals(1,
                len(ctool.unrestrictedSearchResults(title='Object Title')))
    self.assertEquals(1,
                ctool.unrestrictedCountResults(title='Object Title')[0][0])
    
  def test_49_IndexInOrderedSearchFolder(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Index In Ordered Search Folder'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()
    catalog = portal_catalog.objectValues()[0]

    person = person_module.newContent(id='a',portal_type='Person',title='a',description='z')
    person.immediateReindexObject()
    person = person_module.newContent(id='b',portal_type='Person',title='a',description='y')
    person.immediateReindexObject()
    person = person_module.newContent(id='c',portal_type='Person',title='a',description='x')
    person.immediateReindexObject()
    index_columns = getattr(catalog, 'sql_catalog_index_on_order_keys', None)
    self.assertNotEqual(index_columns, None)
    self.assertEqual(len(index_columns), 0)
    # Check catalog don't tell to use index if nothing defined
    sql = person_module.searchFolder(src__=1)
    self.failUnless('use index' not in sql)
    sql = person_module.searchFolder(src__=1, sort_on=[('id','ascending')])
    self.failUnless('use index' not in sql)
    sql = person_module.searchFolder(src__=1, sort_on=[('title','ascending')])
    self.failUnless('use index' not in sql)
    # Defined that catalog must tell to use index when order by catalog.title
    index_columns = ('catalog.title',)
    setattr(catalog, 'sql_catalog_index_on_order_keys', index_columns)
    index_columns = getattr(catalog, 'sql_catalog_index_on_order_keys', None)
    self.assertNotEqual(index_columns, None)
    self.assertEqual(len(index_columns), 1)
    # Check catalog tell to use index only when ordering by catalog.title
    sql = person_module.searchFolder(src__=1)
    self.failUnless('use index' not in sql)
    sql = person_module.searchFolder(src__=1, sort_on=[('id','ascending')])
    self.failUnless('use index' not in sql)
    sql = person_module.searchFolder(src__=1, sort_on=[('title','ascending')])
    self.failUnless('use index' in sql)

  def test_50_LocalRolesArgument(self, quiet=quiet, run=run_all_test):
    """test local_roles= argument
    """
    if not run: return
    if not quiet:
      message = 'local_roles= argument'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    login = PortalTestCase.login

    uf = self.getPortal().acl_users
    uf._doAddUser('bob', '', ['Member'], [])

    # create two documents, one with Assignee local roles, one without
    folder = self.getOrganisationModule()
    ob1 = folder.newContent(title='Object Title')
    ob1.manage_permission('View', ['Member'], 1)
    ob2 = folder.newContent(title='Object Title')
    ob2.manage_addLocalRoles('bob', ['Assignee'])
    get_transaction().commit()
    self.tic()
    
    # by default bob can see those 2 documents
    login(self, 'bob')
    ctool = self.getCatalogTool()
    self.assertEquals(2, len(ctool.searchResults(title='Object Title')))
    self.assertEquals(2, ctool.countResults(title='Object Title')[0][0])
    
    # if we specify local_roles= it will only returns documents on with bob has
    # a local roles
    self.assertEquals(1,
                len(ctool.searchResults(title='Object Title',
                                        local_roles='Assignee')))
    self.assertEquals(1,
                ctool.countResults(title='Object Title',
                                   local_roles='Assignee')[0][0])

    # this also work for searchFolder and countFolder
    self.assertEquals(1, len(folder.searchFolder(title='Object Title',
                                             local_roles='Assignee')))
    self.assertEquals(1, folder.countFolder(title='Object Title',
                                             local_roles='Assignee')[0][0])
    
    # and local_roles can be a list, then this a OR (ie. you must have at least
    # one role).
    self.assertEquals(1,
                len(ctool.searchResults(title='Object Title',
                                       local_roles=['Assignee', 'Auditor'])))
    self.assertEquals(1,
                ctool.countResults(title='Object Title',
                                   local_roles=['Assignee', 'Auditor'])[0][0])

    # this list can also be given in ; form, for worklists URL
    self.assertEquals(1,
                len(ctool.searchResults(title='Object Title',
                                       local_roles='Assignee;Auditor')))
    self.assertEquals(1,
                ctool.countResults(title='Object Title',
                                   local_roles='Assignee;Auditor')[0][0])

  def test_51_SearchWithKeyWords(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test searching with SQL keywords'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()
    and_ = person_module.newContent(portal_type='Person', title='AND')
    or_ = person_module.newContent(portal_type='Person', title='OR')
    like_ = person_module.newContent(portal_type='Person', title='LIKE')
    select_ = person_module.newContent(portal_type='Person', title='SELECT')

    get_transaction().commit()
    self.tic()
    ctool = self.getCatalogTool()
    self.assertEquals([and_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='AND')])

    self.assertEquals([or_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='OR')])

    self.assertEquals([like_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='LIKE')])

    self.assertEquals([select_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='SELECT')])

  def test_52_QueryAndTableAlias(self,quiet=quiet, run=run_all_test):
    """
    Make sure we can use aliases for tables wich will
    be used by related keys. This allow in some particular
    cases to decrease a lot the number of aliases
    """
    if not run: return
    if not quiet:
      message = 'Query And Table Alias'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    org_a = self._makeOrganisation(title='abc',default_address_city='abc')
    module = self.getOrganisationModule()
    module.immediateReindexObject()
    # First try without aliases
    query1 = Query(parent_portal_type="Organisation")
    query2 = Query(grand_parent_portal_type="Organisation Module")
    complex_query = ComplexQuery(query1, query2, operator="AND")
    self.failIfDifferentSet([org_a.getPath() + '/default_address'],
        [x.path for x in self.getCatalogTool()(query=complex_query)])
    # Then try without aliases
    query1 = Query(parent_portal_type="Organisation", 
                   table_alias_list=(("catalog" , "parent"),))
    query2 = Query(grand_parent_portal_type="Organisation Module",
                   table_alias_list=(("catalog" , "parent"), 
                                    ("catalog", "grand_parent")))
    complex_query = ComplexQuery(query1, query2, operator="AND")
    self.failIfDifferentSet([org_a.getPath() + '/default_address'],
        [x.path for x in self.getCatalogTool()(query=complex_query)])
    sql_kw = self.getCatalogTool().buildSQLQuery(query=complex_query)
    # Make sure we have the right list of aliases
    table_alias_list = sql_kw["from_table_list"]
    self.failIfDifferentSet((("catalog","catalog"),
                             ("parent","catalog"),
                             ("grand_parent","catalog")),
                             table_alias_list)
    
  def test_53_DateFormat(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Date Format'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    org_a = self._makeOrganisation(title='org_a')
    org_b = self._makeOrganisation(title='org_b')
    sql_connection = self.getSQLConnection()
    # Add a method in order to directly put values we want into
    # the catalog.
    def updateDate(organisation,date):
      uid = organisation.getUid()
      sql = "UPDATE catalog SET modification_date='%s' '\
          'WHERE uid=%s" %\
          (date,uid)
      result = sql_connection.manage_test(sql)
    updateDate(org_a,'2007-01-12 01:02:03')
    updateDate(org_b,'2006-02-24 15:09:06')

    catalog_kw = {'modification_date':{'query':'24/02/2006',
                               'format':'%d/%m/%Y',
                               'type':'date'}}
    self.failIfDifferentSet([org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    catalog_kw = {'modification_date':{'query':'2007-01-12',
                               'format':'%Y-%m-%d',
                               'type':'date'}}
    self.failIfDifferentSet([org_a.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    catalog_kw = {'modification_date':{'query':'>31/12/2006',
                               'format':'%d/%m/%Y',
                               'type':'date'}}
    self.failIfDifferentSet([org_a.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    catalog_kw = {'modification_date':{'query':'2006',
                               'format':'%Y',
                               'type':'date'}}
    self.failIfDifferentSet([org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    catalog_kw = {'modification_date':{'query':'>2006',
                               'format':'%Y',
                               'type':'date'}}
    self.failIfDifferentSet([org_a.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    # If the date is an empty string, check that all objects are displayed.
    catalog_kw = {'modification_date':{'query':'',
                               'format':'%d/%m/%Y',
                               'type':'date'}}
    self.failIfDifferentSet([org_a.getPath(), org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])

  def test_54_FixIntUid(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test if portal_catalog ensures that uid is long'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal_catalog = self.getCatalogTool()
    portal = self.getPortal()

    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    # Ensure that the new uid is long.
    uid = organisation.uid
    self.failUnless(isinstance(uid, long))
    get_transaction().commit()
    self.tic()

    # Ensure that the uid did not change after the indexing.
    self.assertEquals(organisation.uid, uid)

    # Force to convert the uid to int.
    self.uid = int(uid)
    get_transaction().commit()
    self.tic()

    # After the indexing, the uid must be converted to long automatically,
    # and the value must be equivalent.
    self.failUnless(isinstance(uid, long))
    self.assertEquals(organisation.uid, uid)

  def test_55_FloatFormat(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Float Format'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    catalog_kw = {'uid': {'query': '2 567.54',
                          'format': '1 234.12',
                          'type': 'float'}}
    sql_src = self.getCatalogTool()(src__=1, **catalog_kw)
    self.failUnless("TRUNCATE(catalog.uid,2) = '2567.54'" in sql_src)

  def test_SearchOnOwner(self):
    # owner= can be used a search key in the catalog to have all documents for
    # a specific owner and on which he have the View permission.
    obj = self._makeOrganisation(title='The Document')
    obj2 = self._makeOrganisation(title='The Document')
    obj2.manage_permission('View', [], 0)
    obj2.reindexObject()
    get_transaction().commit()
    self.tic()
    ctool = self.getCatalogTool()
    self.assertEquals([obj], [x.getObject() for x in
                                   ctool(title='The Document',
                                         owner=self.username)])
    self.assertEquals([], [x.getObject() for x in
                                   ctool(title='The Document',
                                         owner='somebody else')])


  def test_SubDocumentsSecurityIndexing(self):
    # make sure indexing of security on sub-documents works as expected
    uf = self.getPortal().acl_users
    uf._doAddUser('bob', '', ['Member'], [])
    obj = self._makeOrganisation(title='The Document')
    obj2 = obj.newContent(portal_type='Bank Account')
    obj2.manage_addLocalRoles('bob', ['Auditor'])
    get_transaction().commit()
    self.tic()

    PortalTestCase.login(self, 'bob')
    self.assertEquals([obj2], [x.getObject() for x in
                               obj.searchFolder(portal_type='Bank Account')])
    # now if we pass the bank account in deleted state, it's no longer returned
    # by searchFolder.
    # This will work as long as Bank Account are associated to a workflow that
    # allow deletion.
    obj2.delete()
    get_transaction().commit()
    self.tic()
    self.assertEquals([], [x.getObject() for x in
                           obj.searchFolder(portal_type='Bank Account')])


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5Catalog))
  return suite

