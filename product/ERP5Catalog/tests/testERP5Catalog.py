# -*- coding: utf-8 -*-
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

from functools import partial
import httplib
from random import randint
import sys
import threading
import traceback
import unittest
import six
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_base
from DateTime import DateTime
from _mysql_exceptions import ProgrammingError
from OFS.ObjectManager import ObjectManager
from Products.CMFActivity import ActivityTool
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import LogInterceptor, createZODBPythonScript, todo_erp5, getExtraSqlConnectionStringList
from Products.PageTemplates.Expressions import getEngine
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery, SimpleQuery
from Testing import ZopeTestCase
from zLOG import LOG

def format_stack(thread=None):
  frame_dict = sys._current_frames()
  if thread is not None:
    thread_id = thread.ident
    frame_dict = {
      thread_id: frame_dict[thread_id],
    }
  frame = None
  try:
    return ''.join((
      'Thread %s\n    %s' % (
        thread_id,
        '     '.join(traceback.format_stack(frame)),
      )
      for thread_id, frame in frame_dict.iteritems()
    ))
  finally:
    del frame, frame_dict

class TransactionThread(threading.Thread):
  """
  Run payload(portal_value=portal_value) within a separate transaction.
  Note: because of transaction isolation, given portal_value will be a
  different instance of the same persistent object.

  Instances of this class may be used as a context manager to manage thread
  lifespam, especially to be properly informed of any exception which happened
  during thread's life. In which case, join_timeout is used upon context exit.
  """
  def __init__(self, portal_value, payload, join_timeout=10):
    super(TransactionThread, self).__init__()
    self.daemon = True
    self.zodb = portal_value._p_jar.db()
    self.root_physical_path = portal_value.getPhysicalPath()
    self.payload = payload
    self.exception = None
    self.join_timeout = join_timeout

  def run(self):
    try:
      # Get a new portal, in a new transactional connection bound to default
      # transaction manager (which should be the threaded transaction manager).
      portal_value = self.zodb.open().root()['Application'].unrestrictedTraverse(
        self.root_physical_path,
      )
      # Trigger ERP5Site magic
      portal_value.getSiteManager()
      # Trigger skin magic
      portal_value.changeSkin(None)
      # Login
      newSecurityManager(None, portal_value.acl_users.getUser('ERP5TypeTestCase'))
      self.payload(portal_value=portal_value)
    except Exception as self.exception:
      if six.PY2:
        self.exception.__traceback__ = sys.exc_info()[2]

  def join(self, *args, **kw):
    super(TransactionThread, self).join(*args, **kw)
    if not self.is_alive():
      exception = self.exception
      # Break reference cycle:
      # run frame -> self -> exception -> __traceback__ -> run frame
      # Not re-raising on subsequent calls is kind of a bug, but it's really up
      # to caller to either not ignore exceptions or keep them around.
      self.exception = None
      if exception is not None:
        if six.PY3:
          raise exception
        six.reraise(exception, None, exception.__traceback__)

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    try:
      self.join(self.join_timeout)
      # Note: if context was interrupted by an exception, being unable to join
      # the thread may be unavoidable (ex: context could not signal blocked
      # thread), in which case this assertion will be mostly useless noise.
      # But conditionally ignoring this seems worse.
      assert not self.is_alive(), format_stack(self)
    except Exception as join_exc_val:
      if exc_val is None:
        # No exception from context: just propagate exception
        raise
      # Both an exception from context and an exception in thread
      if six.PY3:
        # PY3: "raise join_exc_val from exc_val"
        six.raise_from(join_exc_val, exc_val)
      # PY2, handle our exception ourselves and let interpreter reraise
      # context's.
      traceback.print_exc()

class IndexableDocument(ObjectManager):
  # This tests uses a simple ObjectManager, but ERP5Catalog only
  # support classes inherting from ERP5Type.Base.

  # this property is required for dummy providesIMovement
  __allow_access_to_unprotected_subobjects__ = 1
  isRADContent = 0

  def __init__(self, path):
    super(IndexableDocument, self).__init__()
    self._path = path

  def getUid(self):
    uid = getattr(self, 'uid', None)
    if uid is None:
      self.uid = uid = randint(1, 100) + 100000
    return uid

  def __getattr__(self, name):
    # Case for all "is..." magic properties (isMovement, ...)
    if name.startswith('is') or \
       name.startswith('provides'):
      return lambda: 0
    raise AttributeError, name

  def getProperty(self, prop, default=None):
    return getattr(aq_base(self), prop, default)

  _getProperty = getProperty

  def getPath(self):
    return self._path

  def getRelativeUrl(self):
    return '' # Whatever

  def getRootDocumentPath(self):
    return '' # Whatever

  def SearchableText(self):
    return '' # Whatever

class FooDocument(IndexableDocument):
  def getReference(self):
    return 'foo'

class BarDocument(IndexableDocument):
  # Does not define any getReference method.
  pass

class TestERP5Catalog(ERP5TypeTestCase, LogInterceptor):
  """
    Tests for ERP5 Catalog.
  """

  def getTitle(self):
    return "ERP5Catalog"

  def getBusinessTemplateList(self):
    return ('erp5_full_text_mroonga_catalog', 'erp5_base',)

  # Different variables used for this test
  username = 'seb'
  new_erp5_sql_connection = 'erp5_sql_connection2'
  new_erp5_deferred_sql_connection = 'erp5_sql_deferred_connection2'
  new_catalog_id = 'erp5_mysql_innodb2'

  __cleanups = ()

  def _addCleanup(self, callable):
    self.__cleanups += (callable,)
    return callable

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser(self.username, '', ['Manager'], [])

    self.loginByUserName(self.username)
    # make sure there is no message any more
    self.tic()

  def beforeTearDown(self):
    # restore default_catalog
    self.portal.portal_catalog._setDefaultSqlCatalogId('erp5_mysql_innodb')
    self.portal.portal_catalog.hot_reindexing_state = None
    # clear Modules
    for module in [ self.getPersonModule(),
                    self.getOrganisationModule(),
                    self.getCategoryTool().region,
                    self.getCategoryTool().group ]:
      module.manage_delObjects(list(module.objectIds()))
      module.reindexObject()
    # Remove copied sql_connector and catalog
    if self.new_erp5_sql_connection in self.portal.objectIds():
      self.portal.manage_delObjects([self.new_erp5_sql_connection])
    if self.new_erp5_deferred_sql_connection in self.portal.objectIds():
      self.portal.manage_delObjects([self.new_erp5_deferred_sql_connection])
    if self.new_catalog_id in self.portal.portal_catalog.objectIds():
      self.portal.portal_catalog.manage_delObjects([self.new_catalog_id])
    for cleanup in self.__cleanups:
      cleanup(self)
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

  def checkRelativeUrlInSQLPathList(self, url_list, connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    path_base = '/' + self.getPortalId() + '/'
    for url in url_list:
      # Note: not using assertIn as path_list is expected to be huge:
      # including it in the error message would not provide any help.
      self.assertTrue(path_base + url in path_list, url)

  def checkRelativeUrlNotInSQLPathList(self, url_list, connection_id=None):
    path_list = self.getSQLPathList(connection_id=connection_id)
    path_base = '/' + self.getPortalId() + '/'
    for url in url_list:
      # Note: not using assertNotIn as path_list is expected to be huge:
      # including it in the error message would not provide any help.
      self.assertFalse(path_base + url in path_list, url)

  def test_01_HasEverything(self):
    self.assertNotEquals(self.getCategoryTool(), None)
    self.assertNotEquals(self.getSimulationTool(), None)
    self.assertNotEquals(self.getTypeTool(), None)
    self.assertNotEquals(self.getSQLConnection(), None)
    self.assertNotEquals(self.getCatalogTool(), None)

  def test_02_EverythingCatalogued(self):
    portal_catalog = self.getCatalogTool()
    self.tic()
    organisation_module_list = portal_catalog(portal_type='Organisation Module')
    self.assertEqual(len(organisation_module_list),1)

  def test_03_CreateAndDeleteObject(self):
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    person = person_module.newContent(id='1',portal_type='Person')
    address = person.newContent(portal_type='Address')
    path_list = [person.getRelativeUrl(), address.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list)
    self.tic()
    self.checkRelativeUrlInSQLPathList(path_list)
    # Delete subobject in a first transaction, then do not tic and...
    person.manage_delObjects(ids=[address.getId()])
    self.commit()
    # ...delete its container in another transaction, to check that both
    # do get properly unindexed (subobject's unindexation does not get
    # deleted when deleting its container).
    person_module.manage_delObjects('1')
    self.tic()
    self.checkRelativeUrlNotInSQLPathList(path_list)
    # Now we will ask to immediatly reindex
    person = person_module.newContent(id='2',
                                      portal_type='Person',
                                      immediate_reindex=True,
    )
    path_list = [person.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list)
    self.tic()
    self.checkRelativeUrlInSQLPathList(path_list)
    person_module.manage_delObjects('2')
    self.tic()
    self.checkRelativeUrlNotInSQLPathList(path_list)
    # Now we will try with the method deleteContent
    person = person_module.newContent(id='3',portal_type='Person')
    path_list = [person.getRelativeUrl()]
    self.checkRelativeUrlNotInSQLPathList(path_list)
    self.tic()
    self.checkRelativeUrlInSQLPathList(path_list)
    person_module.deleteContent('3')
    # Now delete things is made with activities
    self.checkRelativeUrlNotInSQLPathList(path_list)
    self.tic()
    self.checkRelativeUrlNotInSQLPathList(path_list)
    # Now delete document while its indexation is running
    # (both started and not committed yet).
    # First, create a person but do not index it.
    person = person_module.newContent(id='4', portal_type='Person')
    path_list = [person.getRelativeUrl()]
    self.commit()
    self.checkRelativeUrlNotInSQLPathList(path_list)
    rendez_vous = threading.Event()
    unblock_activity = threading.Event()
    # Prepare an isolated transaction to act as one activity node.
    def runValidablePendingActivities(portal_value, node_id):
      """
      Validate messages once, execute whatever is immediately executable.
      """
      activity_tool = portal_value.portal_activities
      activity_tool.distribute()
      # XXX: duplicate ActivityTool.tic, without locking as we are being
      # multiple activity nodes in a single process.
      for activity in ActivityTool.activity_dict.itervalues():
        while not activity.dequeueMessage(activity_tool, node_id, ()):
          pass
    # Monkey-patch catalog to synchronise between main thread and the
    # isolated transaction.
    catalog_tool_class = self.portal.portal_catalog.__class__
    orig_catalogObjectList = catalog_tool_class.catalogObjectList
    def catalogObjectList(*args, **kw):
      # Note: rendez-vous/unblock_activity *before* modifying tables, otherwise
      # unindexation's synchronous catalog update will deadlock:
      #   unindexation UPDATE -> indexation UPDATE -> unblock_activity -> unindexation commit
      rendez_vous.set()
      assert unblock_activity.wait(10), format_stack()
      orig_catalogObjectList(*args, **kw)
    catalog_tool_class.catalogObjectList = catalogObjectList
    try:
      # Let pending activities (indexation) start.
      with TransactionThread(
        portal_value=self.portal,
        payload=partial(runValidablePendingActivities, node_id=2),
      ):
        # Wait until indexation is indeed initiated.
        assert rendez_vous.wait(10), format_stack()
        # Delete object, which will try to modify catalog content and spawn
        # unindexation activity.
        person_module.manage_delObjects(ids=['4'])
        self.commit()
        # Try to run this activity. It should not run, as it must wait on
        # indexation to be over.
        runValidablePendingActivities(self.portal, 1)
        # Let indexation carry on, it is still able to access the object.
        unblock_activity.set()
    finally:
      # Un-monkey-patch.
      catalog_tool_class.catalogObjectList = orig_catalogObjectList
    # Document must be indexed: unindexation must have waited for indexation
    # to finish, so runValidablePendingActivities(..., 1) must have been
    # a no-op.
    self.checkRelativeUrlInSQLPathList(path_list)
    self.tic()
    # And now it's gone.
    self.checkRelativeUrlNotInSQLPathList(path_list)

  def test_04_SearchFolderWithDeletedObjects(self):
    person_module = self.getPersonModule()
    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual([],folder_object_list)
    person = person_module.newContent(id='4',portal_type='Person',)
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual(['4'],folder_object_list)
    self.tic()
    person_module.manage_delObjects('4')
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual([],folder_object_list)

  def test_05_SearchFolderWithImmediateReindexObject(self):
    person_module = self.getPersonModule()

    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual([],folder_object_list)

    person = person_module.newContent(id='4',portal_type='Person')
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual(['4'],folder_object_list)

    person_module.manage_delObjects('4')
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual([],folder_object_list)

  def test_06_SearchFolderWithRecursiveImmediateReindexObject(self):
    person_module = self.getPersonModule()

    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual([],folder_object_list)

    person = person_module.newContent(id='4',portal_type='Person')
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual(['4'],folder_object_list)

    person_module.manage_delObjects('4')
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual([],folder_object_list)

  def test_10_OrderedSearchFolder(self):
    person_module = self.getPersonModule()
    person_uid_list = [
      person_module.newContent(id='a', portal_type='Person', title='a', description='z').getUid(),
      person_module.newContent(id='b', portal_type='Person', title='a', description='y').getUid(),
      person_module.newContent(id='c', portal_type='Person', title='a', description='x').getUid(),
    ]
    self.tic()
    self.assertEqual(
      ['a','b','c'],
      [
        x.getObject().getId()
        for x in person_module.searchFolder(
          sort_on=[('id', 'ascending')],
        )
      ],
    )
    self.assertEqual(
      ['c','b','a'],
      [
        x.getObject().getId()
        for x in person_module.searchFolder(
          sort_on=[('title', 'ascending'), ('description', 'ascending')],
        )
      ],
    )
    self.assertEqual(
      ['a','b','c'],
      [
        x.getObject().getId()
        for x in person_module.searchFolder(
          sort_on=[('title', 'ascending'), ('description', 'descending')],
        )
      ],
    )

  def test_11_CastStringAsInt(self):
    person_module = self.getPersonModule()
    person_uid_list = [
      person_module.newContent(portal_type='Person', title='1').getUid(),
      person_module.newContent(portal_type='Person', title='2').getUid(),
      person_module.newContent(portal_type='Person', title='12').getUid(),
    ]
    self.tic()
    self.assertEqual(
      ['1', '12', '2'],
      [
        x.getObject().getTitle()
        for x in person_module.searchFolder(
          sort_on=[('title', 'ascending')],
          uid=person_uid_list,
        )
      ],
    )
    self.assertEqual(
      ['1', '2', '12'],
      [
        x.getObject().getTitle()
        for x in person_module.searchFolder(
          sort_on=[('title', 'ascending', 'int')],
          uid=person_uid_list,
        )
      ],
    )

  def test_12_TransactionalUidBuffer(self):
    catalog = self.getCatalogTool().getSQLCatalog()
    self.assertTrue(catalog is not None)
    from Products.ZSQLCatalog.SQLCatalog import global_reserved_uid_lock
    # Clear out the uid buffer.
    #from Products.ZSQLCatalog.SQLCatalog import uid_buffer_dict, get_ident
    #uid_buffer_key = get_ident()
    #if uid_buffer_key in uid_buffer_dict:
    #  del uid_buffer_dict[uid_buffer_key]
    def getUIDBuffer(*args, **kw):
      with global_reserved_uid_lock:
        return catalog.getUIDBuffer(*args, **kw)

    getUIDBuffer(force_new_buffer=True)

    # Need to abort a transaction artificially, so commit the current
    # one, first.
    self.commit()

    catalog.newUid()
    uid_buffer = getUIDBuffer()
    self.assertTrue(len(uid_buffer) > 0)

    self.abort()
    uid_buffer = getUIDBuffer()
    self.assertTrue(len(uid_buffer) == 0)

  def test_14_ReindexWithBrokenCategory(self):
    """Reindexing an object with 1 broken category must not affect other valid
    categories"""
    self.tic()
    portal_category = self.getCategoryTool()
    group_nexedi_category = portal_category.group.newContent(id='nexedi')
    region_europe_category = portal_category.region.newContent(id='europe')
    organisation = self.portal.getDefaultModule('Organisation').newContent(portal_type='Organisation')
    organisation.setGroup('nexedi')
    self.assertEqual(organisation.getGroupValue(), group_nexedi_category)
    organisation.setRegion('europe')
    self.assertEqual(organisation.getRegionValue(), region_europe_category)
    organisation.setRole('not_exists')
    self.assertEqual(organisation.getRoleValue(), None)
    self.tic()
    sql_connection = self.getSQLConnection()
    # Check region and group categories are catalogued
    for base_cat, theorical_count in (
      ('region', 1),
      ('group', 1),
      ('role', 0),
    ):
      self.assertEqual(
        theorical_count,
        sql_connection.manage_test(
          "SELECT COUNT(*) FROM category WHERE category.uid=%s and category.category_strict_membership = 1 AND category.base_category_uid = %s" % (organisation.getUid(), portal_category[base_cat].getUid())
        )[0]['COUNT(*)'],
        'category %s is not cataloged correctly' % base_cat,
      )

  def test_15_getObject(self,):
    # portal_catalog.getObject raises a ValueError if UID parameter is a string
    portal_catalog = self.getCatalogTool()
    self.assertRaises(ValueError, portal_catalog.getObject, "StringUID")

    obj = self._makeOrganisation()
    # otherwise it returns the object
    self.assertEqual(obj, portal_catalog.getObject(obj.getUid()).getObject())
    # but raises KeyError if object is not in catalog
    self.assertRaises(KeyError, portal_catalog.getObject, sys.maxint)

  def test_getRecordForUid(self):
    portal_catalog = self.getCatalogTool()
    obj = self._makeOrganisation()
    self.assertEqual(obj,
        portal_catalog.getSQLCatalog().getRecordForUid(obj.getUid()).getObject())

  def test_path(self):
    portal_catalog = self.getCatalogTool()
    obj = self._makeOrganisation()
    self.assertEqual(obj.getPath(), portal_catalog.getpath(obj.getUid()))
    self.assertRaises(KeyError, portal_catalog.getpath, sys.maxint)

  def test_16_newUid(self):
    # newUid should not assign the same uid
    portal_catalog = self.getCatalogTool()
    from Products.ZSQLCatalog.SQLCatalog import UID_BUFFER_SIZE
    uid_dict = {}
    for i in xrange(UID_BUFFER_SIZE * 3):
      uid = portal_catalog.newUid()
      self.assertTrue(isinstance(uid, long))
      self.assertFalse(uid in uid_dict)
      uid_dict[uid] = None

  def test_17_CreationDate_ModificationDate(self):
    portal_catalog = self.getCatalogTool()
    portal = self.getPortal()
    sql_connection = self.getSQLConnection()

    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    creation_date = organisation.getCreationDate().toZone('UTC').ISO()
    modification_date = organisation.getModificationDate().toZone('UTC').ISO()
    self.commit()
    now = DateTime()
    self.tic()
    sql = """select creation_date, modification_date
             from catalog where uid = %s""" % organisation.getUid()
    result = sql_connection.manage_test(sql)
    self.assertEqual(creation_date,
                      result[0]['creation_date'].ISO())
    self.assertEqual(modification_date,
                      result[0]['modification_date'].ISO())
    self.assertEqual(creation_date,
                      result[0]['modification_date'].ISO())

    import time; time.sleep(3)
    organisation.edit(title='edited')
    self.tic()
    result = sql_connection.manage_test(sql)
    self.assertEqual(creation_date, result[0]['creation_date'].ISO())
    modification_date = organisation.getModificationDate().toZone('UTC').ISO()
    self.assertNotEquals(modification_date,
                         organisation.getCreationDate())
    # This test was first written with a now variable initialized with
    # DateTime(). But since we are never sure of the time required in
    # order to execute some line of code
    self.assertEqual(modification_date,
                      result[0]['modification_date'].ISO())
    self.assertTrue(organisation.getModificationDate()>now)
    self.assertTrue(result[0]['creation_date']<result[0]['modification_date'])

  def test_19_SearchFolderWithNonAsciiCharacter(self):
    person_module = self.getPersonModule()

    title = 'Sébastien'
    person = person_module.newContent(id='5',portal_type='Person',title=title)
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEqual(['5'],folder_object_list)
    folder_object_list = [x.getObject().getId() for x in
                              person_module.searchFolder(title=title)]
    self.assertEqual(['5'],folder_object_list)

  def test_Collation(self):
    person_module = self.getPersonModule()

    title = 'Sébastien'
    person = person_module.newContent(id='5',portal_type='Person', title=title)
    self.tic()
    folder_object_list = [x.getObject().getId() for x in
                              person_module.searchFolder(title=title)]
    self.assertEqual(['5'],folder_object_list)

    # Searching for Sebastien should also find Sébastien
    folder_object_list = [x.getObject().getId() for x in
                              person_module.searchFolder(title='Sebastien')]
    self.assertEqual(['5'],folder_object_list)

    # Same for sebastien, as catalog searches are case insensitive
    folder_object_list = [x.getObject().getId() for x in
                              person_module.searchFolder(title='sebastien')]
    self.assertEqual(['5'],folder_object_list)


  def test_20_SearchFolderWithDynamicRelatedKey(self):
    # Create some objects
    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    portal_category.group.manage_delObjects([x for x in
        portal_category.group.objectIds()])
    group_nexedi_category = portal_category.group\
                                .newContent( id = 'nexedi', title='Nexedi',
                                             reference='a')
    group_nexedi_category2 = portal_category.group\
                                .newContent( id = 'storever', title='Storever',
                                             reference='b')
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    organisation.setGroup('nexedi')
    self.assertEqual(organisation.getGroupValue(), group_nexedi_category)
    organisation2 = module.newContent(portal_type='Organisation',)
    organisation2.setGroup('storever')
    organisation2.setTitle('Organisation 2')
    self.assertEqual(organisation2.getGroupValue(), group_nexedi_category2)
    # Flush message queue
    self.tic()

    # Try to get the organisation with the group title Nexedi
    organisation_list = [x.getObject() for x in
                         module.searchFolder(group_title='Nexedi')]
    self.assertEqual(organisation_list,[organisation])
    organisation_list = [x.getObject() for x in
                         module.searchFolder(default_group_title='Nexedi')]
    self.assertEqual(organisation_list,[organisation])
    # Try to get the organisation with the group id
    organisation_list = [x.getObject() for x in
                         module.searchFolder(group_id='storever')]
    self.assertEqual(organisation_list,[organisation2])
    # Try to get the organisation with the group reference 'a'
    organisation_list = [x.getObject() for x in
                         module.searchFolder(group_reference='a')]
    self.assertEqual(organisation_list,[organisation])
    # Try to get the organisation with the group reference 'c'
    organisation_list = [x.getObject() for x in
                         module.searchFolder(group_reference='c')]
    self.assertEqual(organisation_list,[])
    # Try to get the organisation with the default group reference 'c'
    organisation_list = [x.getObject() for x in
                         module.searchFolder(default_group_reference='c')]
    self.assertEqual(organisation_list,[])
    # Try to get the organisation with group relative_url
    group_relative_url = group_nexedi_category.getRelativeUrl()
    organisation_list = [x.getObject() for x in
                 module.searchFolder(group_relative_url=group_relative_url)]
    self.assertEqual(organisation_list, [organisation])
    # Try to get the organisation with group uid
    organisation_list = [x.getObject() for x in
                 module.searchFolder(group_uid=group_nexedi_category.getUid())]
    self.assertEqual(organisation_list, [organisation])
    # Try to get the organisation with the group id AND title of the document
    organisation_list = [x.getObject() for x in
                         module.searchFolder(group_id='storever',
                                             title='Organisation 2')]
    self.assertEqual(organisation_list,[organisation2])


  def test_21_SearchFolderWithDynamicStrictRelatedKey(self):
    # Create some objects
    portal = self.getPortal()
    portal_category = self.getCategoryTool()
    portal_category.group.manage_delObjects([x for x in
        portal_category.group.objectIds()])
    group_nexedi_category = portal_category.group\
                                .newContent( id = 'nexedi', title='Nexedi',
                                             reference='a')
    sub_group_nexedi = group_nexedi_category\
                                .newContent( id = 'erp5', title='ERP5',
                                             reference='b')
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    organisation.setGroup('nexedi/erp5')
    self.assertEqual(organisation.getGroupValue(), sub_group_nexedi)
    # Flush message queue
    self.tic()

    # Try to get the organisation with the group title Nexedi
    organisation_list = [x.getObject() for x in
                         module.searchFolder(strict_group_title='Nexedi')]
    self.assertEqual(organisation_list,[])
    # Try to get the organisation with the group title ERP5
    organisation_list = [x.getObject() for x in
                         module.searchFolder(strict_group_title='ERP5')]
    self.assertEqual(organisation_list,[organisation])
    # Try to get the organisation with the group reference a
    organisation_list = [x.getObject() for x in
                         module.searchFolder(strict_group_reference='a')]
    self.assertEqual(organisation_list,[])
    # Try to get the organisation with the group reference b
    organisation_list = [x.getObject() for x in
                         module.searchFolder(strict_group_reference='b')]
    self.assertEqual(organisation_list,[organisation])

  def test_22_SearchingWithUnicode(self):
    person_module = self.getPersonModule()
    person_module.newContent(portal_type='Person', title='A Person')
    self.tic()
    self.assertNotEquals([], self.getCatalogTool().searchResults(
                                     portal_type='Person', title=u'A Person'))

  def test_23_DeleteObjectRaiseErrorWhenQueryFail(self):
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    # Now we will ask to immediatly reindex
    person = person_module.newContent(id='2',
                                      portal_type='Person',)
    self.tic()
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
    self.abort()

  def test_24_SortOn(self):
    self.assertTrue(
            self.getCatalogTool().buildSQLQuery(
            sort_on=(('catalog.title', 'ascending'),))['order_by_expression'] in \
            ('catalog.title', '`catalog`.`title` ASC', 'catalog.title ASC'))

  def test_25_SortOnDescending(self):
    self.assertTrue(
            self.getCatalogTool().buildSQLQuery(
            sort_on=(('catalog.title', 'descending'),))['order_by_expression'] in \
            ('catalog.title DESC', '`catalog`.`title` DESC'))

  def test_26_SortOnUnknownKeys(self):
    self.assertEqual('',
          self.getCatalogTool().buildSQLQuery(select_list=('uid', 'path'),
          sort_on=(('ignored', 'ascending'),))['order_by_expression'])

  def test_27_SortOnAmbigousKeys(self):
    # if the sort key is found on the catalog table, it will use that catalog
    # table.
    self.assertTrue(
          self.getCatalogTool().buildSQLQuery(
          sort_on=(('title', 'ascending'),))['order_by_expression'] in \
          ('catalog.title', '`catalog`.`title` ASC'))

    # if not found on catalog, it won't do any filtering
    # in the above, start_date exists both in delivery and movement table.
    self.assertRaises(ValueError, self.getCatalogTool().buildSQLQuery,
          sort_on=(('start_date', 'ascending'),))

    # of course, in that case, it's possible to prefix with table name
    self.assertTrue(
          self.getCatalogTool().buildSQLQuery(
          sort_on=(('delivery.start_date', 'ascending'),
                    ))['order_by_expression'] in \
          ('delivery.start_date', 'delivery.start_date ASC'))

  def test_28_SortOnMultipleKeys(self):
    self.assertTrue(
              self.getCatalogTool().buildSQLQuery(
              sort_on=(('catalog.title', 'ascending'),
                       ('catalog.id', 'asc')))
                       ['order_by_expression'].replace(' ', '') in \
              ('catalog.title,catalog.id', '`catalog`.`title`ASC,`catalog`.`id`ASC', 'catalog.titleASC,catalog.idASC'))

  def test_29_SortOnRelatedKey(self):
    """Sort-on parameter and related key. (Assumes that region_title is a \
    valid related key)"""
    self.assertTrue(
              self.getCatalogTool().buildSQLQuery(region_reference='foo',
              sort_on=(('region_reference', 'ascending'),))['order_by_expression'].endswith('.`reference` ASC'))
    self.assertTrue(
              self.getCatalogTool().buildSQLQuery(region_reference='foo',
              sort_on=(('region_reference', 'descending'),))['order_by_expression'].endswith('.`reference` DESC'))
    self.assertTrue(
              self.getCatalogTool().buildSQLQuery(
              sort_on=(('region_reference', 'ascending'),))['order_by_expression'].endswith('.`reference` ASC'),
              'sort_on parameter must be taken into account even if related key '
              'is not a parameter of the current query')
    self.assertTrue(
              self.getCatalogTool().buildSQLQuery(
              sort_on=(('region_reference', 'descending'),))['order_by_expression'].endswith('.`reference` DESC'),
              'sort_on parameter must be taken into account even if related key '
              'is not a parameter of the current query')

  def test_sortOnRelatedKeyWithUnsetRelation(self):
    """
      Check that sorting on a related key does not filter out objects for
      which the relation is not set.
    """
    portal = self.getPortalObject()
    organisation = portal.organisation_module.\
                   newContent(portal_type="Organisation")
    person_module = portal.person_module
    person_1 = person_module.newContent(portal_type="Person")
    person_2 = person_module.newContent(portal_type="Person",
                 career_subordination_value=organisation)
    self.tic()
    self.assertEqual(len(person_module.searchFolder()),
                     len(person_module.searchFolder(sort_on=[('subordination_title', 'ascending')])))

  def test_sortOnRelatedKeyWithoutLeftJoinSupport(self):
    """Check that sorting on a related key that does not support left join.
    """
    portal = self.getPortalObject()
    org_a = self._makeOrganisation(title='abc', default_address_city='abc')

    # now turn the z_related_grand_parent into an old-style method, without
    # RELATED_QUERY_SEPARATOR
    method = portal.portal_catalog.getSQLCatalog().z_related_grand_parent
    old_src = method.src

    @self._addCleanup
    def cleanGrandParentMethod(self):
      method.manage_edit(method.title, method.connection_id,
                         method.arguments_src, old_src)

    src = old_src.replace('<dtml-var RELATED_QUERY_SEPARATOR>', ' AND ')
    method.manage_edit(method.title, method.connection_id, method.arguments_src,
                       src)

    query = dict(grand_parent_portal_type="Organisation Module",
                 parent_reference=org_a.getReference())
    self.tic()
    self.assertNotEquals(0, len(portal.portal_catalog(
      portal_type='Address',
      sort_on=[('grand_parent_portal_type', 'ascending')])))

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
    self.tic()
    return organisation

  def test_30_SimpleQueryDict(self):
    """use a dict as a keyword parameter.
    """
    organisation_title = 'Nexedi Organisation'
    organisation = self._makeOrganisation(title=organisation_title)
    self.assertEqual([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                title={'query': organisation_title})])

  def test_31_RelatedKeySimpleQueryDict(self):
    """use a dict as a keyword parameter, but using a related key
    """
    organisation = self._makeOrganisation()
    self.assertEqual([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                group_title={'query': 'Nexedi Group'},
                # have to filter on portal type, because the group category is
                # also member of itself
                portal_type=organisation.getPortalTypeName())])

  def test_32_SimpleQueryDictWithOrOperator(self):
    """use a dict as a keyword parameter, with OR operator.
    """
    organisation_title = 'Nexedi Organisation'
    organisation = self._makeOrganisation(title=organisation_title)

    self.assertEqual([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                **{'catalog.title':{'query': (organisation_title, 'something else'),
                                    'operator': 'or'}})])

  def test_33_SimpleQueryDictWithAndOperator(self):
    """use a dict as a keyword parameter, with AND operator.
    """
    organisation_title = 'Nexedi Organisation'
    organisation = self._makeOrganisation(title=organisation_title)

    self.assertEqual([organisation.getPath()],
        [x.path for x in self.getCatalogTool()(
                # this is useless, we must find a better use case
                title={'query': (organisation_title, organisation_title),
                       'operator': 'and'})])

  def test_34_SimpleQueryDictWithMaxRangeParameter(self):
    """use a dict as a keyword parameter, with max range parameter ( < )
    """
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')

    self.assertEqual([org_a.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': 'B', 'range': 'max'})])

  def test_35_SimpleQueryDictWithMinRangeParameter(self):
    """use a dict as a keyword parameter, with min range parameter ( >= )
    """
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')

    self.failIfDifferentSet([org_b.getPath(), org_c.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': 'B', 'range': 'min'})])


  def test_36_SimpleQueryDictWithNgtRangeParameter(self):
    """use a dict as a keyword parameter, with ngt range parameter ( <= )
    """
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')

    self.failIfDifferentSet([org_a.getPath(), org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': 'B', 'range': 'ngt'})])

  def test_37_SimpleQueryDictWithMinMaxRangeParameter(self):
    """use a dict as a keyword parameter, with minmax range parameter ( >=  < )
    """
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')

    self.assertEqual([org_b.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': ('B', 'C'), 'range': 'minmax'})])

  def test_38_SimpleQueryDictWithMinNgtRangeParameter(self):
    """use a dict as a keyword parameter, with minngt range parameter ( >= <= )
    """
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')

    self.failIfDifferentSet([org_b.getPath(), org_c.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',
                title={'query': ('B', 'C'), 'range': 'minngt'})])

  def test_QueryDictFromRequest(self):
    """use a dict from REQUEST as a keyword parameter.
    """
    org_a = self._makeOrganisation(title='A')
    org_b = self._makeOrganisation(title='B')
    org_c = self._makeOrganisation(title='C')

    query_dict = {'query': ('B', 'C'), 'range': 'minngt'}
    from ZPublisher.HTTPRequest import record
    query_record = record()
    for k, v in query_dict.items():
      setattr(query_record, k, v)

    self.assertEqual({org_b.getPath(), org_c.getPath()},
      {x.path for x in self.getCatalogTool()(portal_type='Organisation',
                                             title=query_record)})

  def test_39_DeferredConnection(self):
    """ERP5Catalog uses a deferred connection for full text indexing.
    """
    erp5_sql_deferred_connection = getattr(self.getPortal(),
                                    'erp5_sql_deferred_connection',
                                    None)
    self.assertTrue(erp5_sql_deferred_connection is not None)
    self.assertEqual('Z MySQL Deferred Database Connection',
                      erp5_sql_deferred_connection.meta_type)
    for method in ['z0_uncatalog_fulltext',
                   'z_catalog_fulltext_list']:
      self.assertEqual('erp5_sql_deferred_connection',
                getattr(self.getCatalogTool().getSQLCatalog(),
                              method).connection_id)

  def test_40_DeleteObject(self):
    """Simple test to exercise object deletion
    """
    folder = self.getOrganisationModule()
    ob = folder.newContent()
    self.tic()
    folder.manage_delObjects([ob.getId()])
    self.tic()
    self.assertEqual(0, len(folder.searchFolder()))

  def test_41_ProxyRolesInRestrictedPython(self):
    """test that proxy roles apply to catalog queries within python scripts
    """
    perm = 'View'

    uf = self.getPortal().acl_users
    uf._doAddUser('alice', '', ['Member', 'Manager', 'Assignor'], [])
    uf._doAddUser('bob', '', ['Member'], [])
    # create restricted object
    self.loginByUserName('alice')
    folder = self.getOrganisationModule()
    ob = folder.newContent()
    # make sure permissions are correctly set
    folder.manage_permission('Access contents information', ['Member'], 1)
    folder.manage_permission(perm, ['Member'], 1)
    ob.manage_permission('Access contents information', ['Member'], 1)
    ob.manage_permission(perm, ['Manager'], 0)
    self.tic()
    # check access
    self.assertEqual(1, getSecurityManager().checkPermission(perm, folder))
    self.assertEqual(1, getSecurityManager().checkPermission(perm, ob))
    self.loginByUserName('bob')
    self.assertEqual(1, getSecurityManager().checkPermission(perm, folder))
    self.assertEqual(None, getSecurityManager().checkPermission(perm, ob))
    # add a script that calls a catalog method
    self.loginByUserName('alice')
    script = createZODBPythonScript(self.getPortal().portal_skins.custom,
        'catalog_test_script', '', "return len(context.searchFolder())")

    # test without proxy role
    self.assertEqual(1, folder.catalog_test_script())
    self.loginByUserName('bob')
    self.assertEqual(0, folder.catalog_test_script())

    # test with proxy role and correct role
    self.loginByUserName('alice')
    script.manage_proxy(['Manager'])
    self.assertEqual(1, folder.catalog_test_script())
    self.loginByUserName('bob')
    self.assertEqual(1, folder.catalog_test_script())

    # test with proxy role and wrong role
    self.loginByUserName('alice')
    script.manage_proxy(['Assignor'])
    # proxy roles must overwrite the user's roles, even if he is the owner
    # of the script
    self.assertEqual(0, folder.catalog_test_script())
    self.loginByUserName('bob')
    self.assertEqual(0, folder.catalog_test_script())

  def test_42_SearchableText(self):
    """Tests SearchableText is working in ERP5Catalog
    """
    folder = self.getOrganisationModule()
    ob = folder.newContent()
    ob.setTitle('The title of this object')
    self.assertTrue('this' in ob.SearchableText(), ob.SearchableText())
    # add some other objects, we need to create a minimum quantity of data for
    # full text queries to work correctly
    for i in range(10):
      otherob = folder.newContent()
      otherob.setTitle('Something different')
      self.assertFalse('this' in otherob.SearchableText(), otherob.SearchableText())
    # catalog those objects
    self.tic()
    catalog_tool = self.getCatalogTool()
    self.assertEqual([ob],
        [x.getObject() for x in catalog_tool(portal_type='Organisation',
                                             SearchableText='title')])
    self.assertEqual(1,
                      catalog_tool.countResults(portal_type='Organisation',
                                                SearchableText='title')[0][0])

    # 'different' is found in more than 50% of records
    # MySQL ignores such a word, but Mroonga does not ignore.
    if 'ENGINE=Mroonga' in self.portal.erp5_sql_connection.manage_test(
        'SHOW CREATE TABLE full_text')[0][1]:
      # Mroonga
      self.assertEqual(10, self.getCatalogTool().countResults(
                portal_type='Organisation', SearchableText='different')[0][0])
    else:
      # MySQL
      self.assertEqual([],
          [x.getObject for x in self.getCatalogTool()(
                  portal_type='Organisation', SearchableText='different')])
      self.assertEqual(0, self.getCatalogTool().countResults(
                portal_type='Organisation', SearchableText='different')[0][0])

  def test_43_ManagePasteObject(self):
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    person = person_module.newContent(id='1',portal_type='Person')
    self.tic()
    copy_data = person_module.manage_copyObjects([person.getId()])
    new_id = person_module.manage_pasteObjects(copy_data)[0]['new_id']
    new_person = person_module[new_id]
    self.tic()
    path_list = [new_person.getRelativeUrl()]
    self.checkRelativeUrlInSQLPathList(path_list)

  def test_44_ParentRelatedKeys(self):
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    person_module.reindexObject()
    person = person_module.newContent(id='1',portal_type='Person')
    self.tic()
    self.assertEqual([person],
        [x.getObject() for x in self.getCatalogTool()(
               parent_title=person_module.getTitle())])

  def test_45_QueryAndComplexQuery(self):
    """
    """
    org_a = self._makeOrganisation(title='abc',description='abc')
    org_b = self._makeOrganisation(title='bcd',description='bcd')
    org_c = self._makeOrganisation(title='efg',description='efg')
    org_e = self._makeOrganisation(title='foo',description='bir')
    org_f = self._makeOrganisation(title='foo',description='bar')

    # uid=[]
    catalog_kw= {'query':Query(uid=[])}
    self.failIfDifferentSet(
        [x.getPath() for x in (org_a, org_b, org_c, org_e, org_f)],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
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
                                       logical_operator='OR')}
    self.failIfDifferentSet([org_b.getPath(), org_c.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])
    # Recursive Complex Query
    # (title='abc' and description='abc') OR
    #  title='foo' and description='bar'
    catalog_kw = {'query':ComplexQuery(ComplexQuery(SimpleQuery(title='abc'),
                                                    SimpleQuery(description='abc'),
                                                    logical_operator='AND'),
                                       ComplexQuery(SimpleQuery(title='foo'),
                                                    SimpleQuery(description='bar'),
                                                    logical_operator='AND'),
                                       logical_operator='OR')}
    self.failIfDifferentSet([org_a.getPath(), org_f.getPath()],
        [x.path for x in self.getCatalogTool()(
                portal_type='Organisation',**catalog_kw)])

  def test_46_TestLimit(self):
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

  def test_48bis_ERP5Site_hotReindexAllCheckCachedValues(self):
    """
      test the hot reindexing of catalog -> catalog2
      Check that cached values are invalidated due to
      catalog migration
    """
    portal = self.portal
    original_connection_id = 'erp5_sql_connection'
    original_deferred_connection_id = 'erp5_sql_deferred_connection'
    new_connection_string = getExtraSqlConnectionStringList()[0]

    # Skip this test if default connection string is not "test test".
    original_connection = getattr(portal, original_connection_id)
    connection_string = original_connection.connection_string
    if (connection_string == new_connection_string):
      message = 'SKIPPED: default connection string is the same as the one for hot-reindex catalog'
      ZopeTestCase._print(message)
      LOG('Testing... ',0, message)

    # Create new connectors
    addSQLConnection = portal.manage_addProduct['ZMySQLDA'] \
      .manage_addZMySQLConnection
    addSQLConnection(self.new_erp5_sql_connection,'', new_connection_string)
    new_connection = portal[self.new_erp5_sql_connection]
    new_connection.manage_open_connection()
    addSQLConnection(self.new_erp5_deferred_sql_connection,'',
                                      new_connection_string)
    new_connection = portal[self.new_erp5_deferred_sql_connection]
    new_connection.manage_open_connection()
    # the transactionless connector must not be change because this one
    # create the portal_ids otherwise it create of conflicts with uid
    # objects

    # Create new catalog
    portal_catalog = self.getCatalogTool()
    original_catalog = portal_catalog.getSQLCatalog()
    original_catalog_id = original_catalog.getId()
    cp_data = portal_catalog.manage_copyObjects(ids=(original_catalog_id,))
    new_catalog_id = portal_catalog.manage_pasteObjects(cp_data)[0]['new_id']
    new_catalog = portal_catalog[new_catalog_id]

    # Add new searchable table in new catalog
    create_dummy_table_sql = """
    CREATE TABLE `dummy` (
    `uid` BIGINT UNSIGNED NOT NULL,
    `dummy_title` varchar(32) NOT NULL default '',
    PRIMARY KEY  (`uid`)
    ) ENGINE=InnoDB;
    """
    drop_summy_table_sql = """
    DROP TABLE IF EXISTS `dummy`
    """
    for catalog, connection_id in ((original_catalog, original_connection_id),
        (new_catalog, self.new_erp5_sql_connection)):
      catalog.newContent(
                    portal_type='SQL Method',
                    id='z_create_dummy_table',
                    title='',
                    arguments_src="",
                    connection_id=connection_id,
                    src=create_dummy_table_sql)
      catalog.newContent(
                    portal_type='SQL Method',
                    id='z0_drop_dummy_table',
                    title='',
                    arguments_src="",
                    connection_id=connection_id,
                    src=drop_summy_table_sql)

    # update catalog configuration and declare new ZSQLMethods
    sql_clear_catalog_list = list(original_catalog.sql_clear_catalog)
    sql_clear_catalog_list.extend(['z0_drop_dummy_table',
                                   'z_create_dummy_table'])
    sql_clear_catalog_list.sort()
    original_catalog.sql_clear_catalog = new_catalog.sql_clear_catalog = \
      tuple(sql_clear_catalog_list)

    sql_search_table_list = list(original_catalog.sql_search_tables)
    sql_search_table_list.append('dummy')
    sql_search_table_list.sort()
    original_catalog.sql_search_tables = new_catalog.sql_search_tables = \
      tuple(sql_search_table_list)

    portal_catalog.manage_catalogClear()
    self.commit()
    # Catalog structure changed, so we should be able to build new queries
    # with new table columns
    # Check that column map is updated according new structure of catalog.
    self.assertTrue('dummy.dummy_title' in portal_catalog.getSQLCatalog().getColumnMap())
    # Check more cached methods of SQLCatalog by building SQLQuery
    query = portal_catalog.getSQLCatalog().buildQuery(kw={'dummy.dummy_title': 'Foo'})
    self.assertTrue(query.query_list)

    # prepare arguments for hot reindex
    source_sql_connection_id_list=list((original_connection_id,
                                  original_deferred_connection_id))
    destination_sql_connection_id_list=list((self.new_erp5_sql_connection,
                                       self.new_erp5_deferred_sql_connection))
    # launch the full hot reindexing
    portal_catalog.manage_hotReindexAll(source_sql_catalog_id=original_catalog_id,
                 destination_sql_catalog_id=new_catalog_id,
                 source_sql_connection_id_list=source_sql_connection_id_list,
                 destination_sql_connection_id_list=destination_sql_connection_id_list,
                 update_destination_sql_catalog=True)

    # Flush message queue
    self.tic()
    self.assertEqual(portal_catalog.getSQLCatalog().getId(), new_catalog_id)
    # Check that column map is updated according new structure of catalog.
    self.assertTrue('dummy.dummy_title' in portal_catalog.getSQLCatalog().getColumnMap())
    # Check more cached methods of SQLCatalog by building SQLQuery
    query = portal_catalog.getSQLCatalog().buildQuery(kw={'dummy.dummy_title': 'Foo'})
    self.assertTrue(query.query_list)
    # We need to reset SQL connections in skin folder's zsql methods
    sql_connection_id_dict = {}
    for destination_sql_connection_id, source_sql_connection_id in \
          zip(destination_sql_connection_id_list,
              source_sql_connection_id_list):
        if source_sql_connection_id != destination_sql_connection_id:
          sql_connection_id_dict[destination_sql_connection_id] = \
              source_sql_connection_id
    portal_catalog.changeSQLConnectionIds(
      folder=portal.portal_skins,
      sql_connection_id_dict = sql_connection_id_dict)

  def test_47_Unrestricted(self):
    """test unrestricted search/count results.
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('alice', '', ['Member', 'Manager', 'Assignor'], [])
    uf._doAddUser('bob', '', ['Member'], [])

    # create a document that only alice can view
    self.loginByUserName('alice')
    folder = self.getOrganisationModule()
    ob = folder.newContent(title='Object Title')
    ob.manage_permission('View', ['Manager'], 0)
    self.tic()

    # bob cannot see the document
    self.loginByUserName('bob')
    ctool = self.getCatalogTool()
    self.assertEqual(0, len(ctool.searchResults(title='Object Title')))
    self.assertEqual(0, ctool.countResults(title='Object Title')[0][0])

    # unless using unrestricted searches
    self.assertEqual(1,
                len(ctool.unrestrictedSearchResults(title='Object Title')))
    self.assertEqual(1,
                ctool.unrestrictedCountResults(title='Object Title')[0][0])

  @todo_erp5
  def test_49_IndexInOrderedSearchFolder(self):
    searchFolder = self.getPersonModule().searchFolder
    catalog = self.getCatalogTool().objectValues()[0]
    self.tic()
    self.assertEqual(catalog.sql_catalog_index_on_order_keys, ())
    # Check catalog don't tell to use index if nothing defined
    self.assertNotIn('use index', searchFolder(src__=1))
    self.assertNotIn('use index', searchFolder(src__=1, sort_on=[('id','ascending')]))
    self.assertNotIn('use index', searchFolder(src__=1, sort_on=[('title','ascending')]))
    # Defined that catalog must tell to use index when order by catalog.title
    catalog.sql_catalog_index_on_order_keys = ('catalog.title', )
    # Check catalog tell to use index only when ordering by catalog.title
    self.assertNotIn('use index', searchFolder(src__=1))
    self.assertNotIn('use index', searchFolder(src__=1, sort_on=[('id','ascending')]))
    self.assertIn('use index', searchFolder(src__=1, sort_on=[('title','ascending')]))

  def test_50_LocalRolesArgument(self):
    """test local_roles= argument
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('bob', '', ['Member'], [])

    # create two documents, one with Assignee local roles, one without
    folder = self.getOrganisationModule()
    ob1 = folder.newContent(title='Object Title')
    ob1.manage_permission('View', ['Member'], 1)
    ob2 = folder.newContent(title='Object Title')
    ob2_id = ob2.getId()
    ob2.manage_addLocalRoles('bob', ['Assignee'])
    self.tic()

    # by default bob can see those 2 documents
    self.loginByUserName('bob')
    ctool = self.getCatalogTool()
    self.assertEqual(2, len(ctool.searchResults(title='Object Title')))
    self.assertEqual(2, ctool.countResults(title='Object Title')[0][0])

    # if we specify local_roles= it will only returns documents on with bob has
    # a local roles
    self.assertEqual(0,
                len(ctool.searchResults(title='Object Title',
                                        local_roles='UnexistingRole')))
    self.assertEqual(0,
                len(ctool.searchResults(title='Object Title',
                                        local_roles='Assignor')))
    self.assertEqual(1,
                len(ctool.searchResults(title='Object Title',
                                        local_roles='Assignee')))
    self.assertEqual(1,
                ctool.countResults(title='Object Title',
                                   local_roles='Assignee')[0][0])

    # this also work for searchFolder and countFolder
    self.assertEqual(1, len(folder.searchFolder(title='Object Title',
                                             local_roles='Assignee')))
    self.assertEqual(1, folder.countFolder(title='Object Title',
                                             local_roles='Assignee')[0][0])

    # and local_roles can be a list, then this a OR (ie. you must have at least
    # one role).
    self.assertEqual(1,
                len(ctool.searchResults(title='Object Title',
                                       local_roles=['Assignee', 'Auditor'])))
    self.assertEqual(1,
                ctool.countResults(title='Object Title',
                                   local_roles=['Assignee', 'Auditor'])[0][0])

    # this list can also be given in ; form, for worklists URL
    self.assertEqual(1,
                len(ctool.searchResults(title='Object Title',
                                       local_roles='Assignee;Auditor')))
    self.assertEqual(1,
                ctool.countResults(title='Object Title',
                                   local_roles='Assignee;Auditor')[0][0])

    #Test if bob can't see object even if Assignee role (without View permission) is defined on object
    ob1.manage_addLocalRoles('bob', ['Assignee'])
    ob1.manage_permission('View', ['Assignor'], 0)
    ob1.reindexObject()
    self.tic()
    user = getSecurityManager().getUser()
    self.assertFalse(user.has_permission('View', ob1))
    self.assertTrue(user.has_role('Assignee', ob1))
    result_list = [r.getId() for r in ctool(title='Object Title', local_roles='Assignee')]
    self.assertEqual(1, len(result_list))
    self.assertEqual([ob2_id], result_list)
    self.assertEqual(1,
                ctool.countResults(title='Object Title',
                                   local_roles='Assignee')[0][0])

    # this also work for searchFolder and countFolder
    self.assertEqual(1, len(folder.searchFolder(title='Object Title',
                                             local_roles='Assignee')))
    self.assertEqual(1, folder.countFolder(title='Object Title',
                                             local_roles='Assignee')[0][0])

  def test_51_SearchWithKeyWords(self):
    person_module = self.getPersonModule()
    and_ = person_module.newContent(portal_type='Person', title='AND')
    or_ = person_module.newContent(portal_type='Person', title='OR')
    like_ = person_module.newContent(portal_type='Person', title='LIKE')
    select_ = person_module.newContent(portal_type='Person', title='SELECT')

    self.tic()
    ctool = self.getCatalogTool()
    self.assertEqual([and_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='AND')])

    self.assertEqual([or_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='OR')])

    self.assertEqual([like_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='LIKE')])

    self.assertEqual([select_], [x.getObject() for x in
                                   ctool(portal_type='Person', title='SELECT')])

  def test_52_QueryAndTableAlias(self):
    """
    Make sure we can use aliases for tables wich will
    be used by related keys. This allow in some particular
    cases to decrease a lot the number of aliases
    """
    org_a = self._makeOrganisation(title='abc',default_address_city='abc')
    module = self.getOrganisationModule()
    self.tic()
    # First try without aliases
    query1 = Query(parent_portal_type="Organisation")
    query2 = Query(grand_parent_portal_type="Organisation Module")
    complex_query = ComplexQuery(query1, query2, logical_operator="AND")
    self.failIfDifferentSet([org_a.getPath() + '/default_address'],
        [x.path for x in self.getCatalogTool()(query=complex_query)])
    # Then try with aliases
    query1 = Query(parent_portal_type="Organisation",
                   table_alias_list=(("catalog" , "parent"),))
    query2 = Query(grand_parent_portal_type="Organisation Module",
                   table_alias_list=(("catalog" , "parent"),
                                    ("catalog", "grand_parent")))
    complex_query = ComplexQuery(query1, query2, logical_operator="AND")
    self.failIfDifferentSet([org_a.getPath() + '/default_address'],
        [x.path for x in self.getCatalogTool()(query=complex_query)])
    sql_kw = self.getCatalogTool().buildSQLQuery(query=complex_query)
    # Make sure we have the right list of aliases
    table_alias_list = sql_kw["from_table_list"]
    self.failIfDifferentSet((("catalog","catalog"),
                             ("parent","catalog"),
                             ("grand_parent","catalog")),
                             table_alias_list)

  def test_53_DateFormat(self):
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

  def test_54_FixIntUid(self):
    portal_catalog = self.getCatalogTool()
    portal = self.getPortal()

    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',)
    # Ensure that the new uid is long.
    uid = organisation.uid
    self.assertTrue(isinstance(uid, long))
    self.tic()

    # Ensure that the uid did not change after the indexing.
    self.assertEqual(organisation.uid, uid)

    # Force to convert the uid to int.
    self.uid = int(uid)
    self.tic()

    # After the indexing, the uid must be converted to long automatically,
    # and the value must be equivalent.
    self.assertTrue(isinstance(uid, long))
    self.assertEqual(organisation.uid, uid)

  def test_55_FloatFormat(self):
    catalog_kw = {'uid': {'query': '2 567.54',
                          'format': '1 234.12',
                          'type': 'float'}}
    sql_src = self.getCatalogTool().buildSQLQuery(**catalog_kw)['where_expression']
    self.assertTrue("TRUNCATE(catalog.uid,2) = '2567.54'" in sql_src or \
                    'TRUNCATE(`catalog`.`uid`, 2) = 2567.54' in sql_src, sql_src)

  def test_56_CreateUidDuringClearCatalog(self):
    """
      Create a script in the catalog to generate a uid list
      Check the creation some objects, or activities, during a clear
    """
    # Add a script to create uid list
    catalog = self.getCatalogTool().getSQLCatalog()
    script_id = 'z0_zCreateUid'
    script = createZODBPythonScript(
      catalog,
      script_id,
      '*args,**kw',
      "context.getPortalObject().portal_ids.generateNewIdList(id_generator='uid', id_group='text_uid')",
    )
    sql_clear_catalog_orig = catalog.sql_clear_catalog
    catalog.sql_clear_catalog = tuple(sorted(sql_clear_catalog_orig + (script_id, )))
    # launch the sql_clear_catalog with the script after the drop tables and
    # before the recreate tables of catalog
    try:
      self.commit()
      catalog.manage_catalogClear()
    finally:
      self.abort()
      catalog.sql_clear_catalog = sql_clear_catalog_orig
      self.commit()
      self.portal.ERP5Site_reindexAll(clear_catalog=True)
      self.tic()

  def test_SearchOnOwner(self):
    # owner= can be used a search key in the catalog to have all documents for
    # a specific owner and on which he have the View permission.
    obj = self._makeOrganisation(title='The Document')
    obj2 = self._makeOrganisation(title='The Document')
    obj2.manage_permission('View', [], 0)
    obj2.reindexObject()
    self.tic()
    ctool = self.getCatalogTool()
    self.assertEqual([obj], [x.getObject() for x in
                                   ctool(title='The Document',
                                         owner=self.username)])
    self.assertEqual([], [x.getObject() for x in
                                   ctool(title='The Document',
                                         owner='somebody else')])


  def test_SubDocumentsSecurityIndexing(self):
    # make sure indexing of security on sub-documents works as expected
    uf = self.getPortal().acl_users
    uf._doAddUser('bob', '', ['Member'], [])
    obj = self._makeOrganisation(title='The Document')
    obj2 = obj.newContent(portal_type='Bank Account')
    obj2.manage_addLocalRoles('bob', ['Auditor'])
    self.tic()

    self.loginByUserName('bob')
    self.assertEqual([obj2], [x.getObject() for x in
                               obj.searchFolder(portal_type='Bank Account')])
    # now if we pass the bank account in deleted state, it's no longer returned
    # by searchFolder.
    # This will work as long as Bank Account are associated to a workflow that
    # allow deletion.
    self.login()
    obj2.delete()
    self.tic()
    self.loginByUserName('bob')
    self.assertEqual([], [x.getObject() for x in
                           obj.searchFolder(portal_type='Bank Account')])

  @todo_erp5
  def test_SubDocumentsWithAcquireLocalRoleSecurityIndexing(self):
    # Check that sub object indexation is compatible with ZODB settings
    # when the sub object acquires the parent local roles
    perm = 'View'

    # Create some users
    logout = self.logout
    user1 = 'local_foo_1'
    user2 = 'local_bar_1'
    uf = self.getPortal().acl_users
    uf._doAddUser(user1, user1, ['Member', ], [])
    uf._doAddUser(user2, user2, ['Member', ], [])

    container_portal_type = 'Organisation'
    # Create a container, define a local role, and set view permission
    folder = self.getOrganisationModule()

    # user1 should be auditor on container
    # user2 should be assignor on subdocument
    container = folder.newContent(portal_type=container_portal_type)
    container.manage_setLocalRoles(user1, ['Auditor'])
#     container.manage_setLocalRoles(user2, [])
    container.manage_permission(perm, ['Owner', 'Auditor', 'Assignor'], 0)

    # By default, local roles are acquired from container for Email portal type
    object_portal_type = 'Email'
    obj = container.newContent(portal_type=object_portal_type)
    # Acquire permission from parent
    obj.manage_permission(perm, [], 1)
    obj.manage_setLocalRoles(user2, ['Assignor'])

    obj.reindexObject()
    self.tic()

    logout()
    self.loginByUserName(user1)
    result = obj.portal_catalog(portal_type=object_portal_type)
    self.assertSameSet([obj, ], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=object_portal_type,
                                local_roles='Owner')
    self.assertSameSet([], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=object_portal_type,
                                local_roles='Assignor')
    self.assertSameSet([], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=object_portal_type,
                                local_roles='Auditor')
    self.assertSameSet([obj], [x.getObject() for x in result])

    logout()
    self.loginByUserName(user2)
    result = obj.portal_catalog(portal_type=object_portal_type)
    self.assertSameSet([obj, ], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=object_portal_type,
                                local_roles='Owner')
    self.assertSameSet([], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=object_portal_type,
                                local_roles='Assignor')
    self.assertSameSet([obj], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=object_portal_type,
                                local_roles='Auditor')
    self.assertSameSet([], [x.getObject() for x in result])

  def test_60_ViewableOwnerIndexing(self):
    logout = self.logout
    uf = self.getPortal().acl_users
    uf._doAddUser('super_owner', '', ['Member', 'Author', 'Assignee'], [])
    uf._doAddUser('little_owner', '', ['Member', 'Author'], [])

    perm = 'View'
    folder = self.getOrganisationModule()
    portal_type = 'Organisation'
    sub_portal_type_id = 'Address'
    sub_portal_type = self.getPortal().portal_types._getOb(sub_portal_type_id)

    sql_connection = self.getSQLConnection()
    sql = 'select viewable_owner as owner from catalog where uid=%s'

    self.loginByUserName('super_owner')

    # Check that Owner is not catalogued if he can't view the object
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, [], 0)
    self.tic()
    result = sql_connection.manage_test(sql % obj.getUid())
    self.assertSameSet([''], [x.owner for x in result])

    # Check that Owner is catalogued when he can view the object
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Owner'], 0)
    self.tic()
    result = sql_connection.manage_test(sql % obj.getUid())
    self.assertSameSet(['super_owner'], [x.owner for x in result])

    # Check that Owner is not catalogued when he can view the
    # object because he has another role
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Assignee'], 0)
    self.tic()
    result = sql_connection.manage_test(sql % obj.getUid())
    self.assertSameSet([''], [x.owner for x in result])

    # Check that Owner is not catalogued when he can't view the
    # object and when the portal type does not acquire the local roles.
    sub_portal_type.setTypeAcquireLocalRole(False)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change
    logout()
    self.loginByUserName('super_owner')
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Owner'], 0)
    logout()
    self.loginByUserName('little_owner')
    sub_obj = obj.newContent(portal_type='Address')
    sub_obj.manage_permission(perm, [], 0)
    self.tic()
    result = sql_connection.manage_test(sql % sub_obj.getUid())
    self.assertSameSet([''], [x.owner for x in result])

    # Check that Owner is catalogued when he can view the
    # object and when the portal type does not acquire the local roles.
    sub_portal_type.setTypeAcquireLocalRole(False)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change
    logout()
    self.loginByUserName('super_owner')
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Owner'], 0)
    logout()
    self.loginByUserName('little_owner')
    sub_obj = obj.newContent(portal_type='Address')
    sub_obj.manage_permission(perm, ['Owner'], 0)
    self.tic()
    result = sql_connection.manage_test(sql % sub_obj.getUid())
    self.assertSameSet(['little_owner'], [x.owner for x in result])

    # Check that Owner is catalogued when he can view the
    # object because permissions are acquired and when the portal type does not
    # acquire the local roles.
    sub_portal_type.setTypeAcquireLocalRole(False)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change
    logout()
    self.loginByUserName('super_owner')
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Owner'], 0)
    logout()
    self.loginByUserName('little_owner')
    sub_obj = obj.newContent(portal_type='Address')
    sub_obj.manage_permission(perm, [], 1)
    self.tic()
    result = sql_connection.manage_test(sql % sub_obj.getUid())
    self.assertSameSet(['little_owner'], [x.owner for x in result])

    # Check that Owner is not catalogued when he can't view the
    # object and when the portal type acquires the local roles.
    sub_portal_type.setTypeAcquireLocalRole(True)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change
    logout()
    self.loginByUserName('super_owner')
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Owner'], 0)
    logout()
    self.loginByUserName('little_owner')
    sub_obj = obj.newContent(portal_type='Address')
    sub_obj.manage_permission(perm, [], 0)
    self.tic()
    result = sql_connection.manage_test(sql % sub_obj.getUid())
    self.assertSameSet([''], [x.owner for x in result])

    # Check that Owner is catalogued when he can view the
    # object and when the portal type acquires the local roles.
    sub_portal_type.setTypeAcquireLocalRole(True)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change
    logout()
    self.loginByUserName('super_owner')
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Owner'], 0)
    logout()
    self.loginByUserName('little_owner')
    sub_obj = obj.newContent(portal_type='Address')
    sub_obj.manage_permission(perm, ['Owner'], 0)
    self.tic()
    result = sql_connection.manage_test(sql % sub_obj.getUid())
    self.assertSameSet(['little_owner'], [x.owner for x in result])

    # Check that Owner is catalogued when he can view the
    # object because permissions are acquired and when the portal type
    # acquires the local roles.
    sub_portal_type.setTypeAcquireLocalRole(True)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change
    logout()
    self.loginByUserName('super_owner')
    obj = folder.newContent(portal_type='Organisation')
    obj.manage_permission(perm, ['Owner'], 0)
    logout()
    self.loginByUserName('little_owner')
    sub_obj = obj.newContent(portal_type='Address')
    sub_obj.manage_permission(perm, [], 1)
    self.tic()
    result = sql_connection.manage_test(sql % sub_obj.getUid())
    self.assertSameSet(['little_owner'], [x.owner for x in result])

  def test_ExactMatchSearch(self):
    # test exact match search with queries
    doc = self._makeOrganisation(title='Foo%')
    other_doc = self._makeOrganisation(title='FooBar')
    ctool = self.getCatalogTool()

    # by default, % in catalog search is a wildcard:
    self.assertSameSet([doc, other_doc], [x.getObject() for x in
        ctool(portal_type='Organisation', title='Foo%')])
    # ... but you can force searches with an exact match key
    self.assertEqual([doc], [x.getObject() for x in
       ctool(portal_type='Organisation', title=dict(query='Foo%',
                                                    key='ExactMatch'))])

  def test_KeywordSearch(self):
    # test keyword search with queries
    doc = self._makeOrganisation(description='Foo')
    other_doc = self._makeOrganisation(description='Foobar')
    ctool = self.getCatalogTool()

    # description is not a keyword by default. (This might change in the
    # future, in this case, this test have to be updated)
    self.assertSameSet([doc], [x.getObject() for x in
        ctool(portal_type='Organisation', description='=Foo')])
    self.assertEqual({doc, other_doc}, {x.getObject() for x in
      ctool(portal_type='Organisation', description=dict(query='Foo',
                                                         key='Keyword'))})


  def test_ignore_empty_string(self):
    # ERP5Catalog ignore empty strings by default
    doc_with_description = self._makeOrganisation(description='X')
    doc_with_empty_description = self._makeOrganisation(description='')
    ctool = self.getCatalogTool()
    def searchResults(**kw):
      kw['portal_type'] = 'Organisation'
      return {x.getObject() for x in ctool.searchResults(**kw)}

    # description='' is ignored
    self.assertEqual({doc_with_empty_description, doc_with_description},
                      searchResults(description=''))
    # unless we exlicitly say we don't want to ignore empty strings
    self.assertEqual({doc_with_empty_description},
                      searchResults(ignore_empty_string=0, description=''))

  def test_ignore_empty_string_related_key(self):
    # ERP5Catalog ignore empty strings by default, also on related keys
    region_with_empty_description = self.portal.portal_categories.region.newContent(
                                        portal_type='Category', description='')
    doc_with_empty_region_description = self._makeOrganisation(
                            region_value=region_with_empty_description)
    doc_without_region = self._makeOrganisation()
    ctool = self.getCatalogTool()
    def searchResults(**kw):
      kw['portal_type'] = 'Organisation'
      return {x.getObject() for x in ctool.searchResults(**kw)}

    self.assertEqual({doc_with_empty_region_description, doc_without_region},
                      searchResults(region_description=''))
    self.assertEqual({doc_with_empty_region_description},
        searchResults(ignore_empty_string=0, region_description=''))

  def test_complex_query(self):
    # Make sure that complex query works on real environment.
    catalog = self.getCatalogTool()
    person_module = self.getPersonModule()

    # Add categories
    portal_category = self.getCategoryTool()
    africa = portal_category.region.newContent(id='africa')
    asia = portal_category.region.newContent(id='asia')
    europe = portal_category.region.newContent(id='europe')

    # A from Africa
    person_module.newContent(id='A', first_name='A', last_name='ERP5',
                             region='africa')

    # B from Asia
    person_module.newContent(id='B', first_name='B', last_name='ZOPE',
                             region='asia')

    # C from Europe
    person_module.newContent(id='C', first_name='C', last_name='PYTHON',
                             region='europe')

    # D from ????
    person_module.newContent(id='D', first_name='D', last_name='ERP5')

    self.tic()

    # simple query
    query = Query(portal_type='Person')
    self.assertEqual(len(catalog(query=query)), 4)

    # complex query
    query = ComplexQuery(Query(portal_type='Person'),
                         Query(region_uid=asia.getUid()),
                         logical_operator='AND')
    self.assertEqual(len(catalog(query=query)), 1)

    # complex query
    query = ComplexQuery(Query(portal_type='Person'),
                         Query(region_uid=(africa.getUid(), asia.getUid())),
                         logical_operator='AND')
    self.assertEqual(len(catalog(query=query)), 2)

    # more complex query
    query_find_european = ComplexQuery(Query(portal_type='Person'),
                                       Query(region_uid=europe.getUid()),
                                       logical_operator='AND')
    self.assertEqual(len(catalog(query=query_find_european)), 1)

    query_find_name_erp5 = ComplexQuery(Query(portal_type='Person'),
                                        Query(title='%ERP5'),
                                        logical_operator='AND')
    self.assertEqual(len(catalog(query=query_find_name_erp5)), 2)

    self.assertRaises(NotImplementedError, ComplexQuery, query_find_european, query_find_name_erp5, logical_operator='OR')

  def test_check_security_table_content(self):
    sql_connection = self.getSQLConnection()
    portal = self.getPortalObject()
    portal_types = portal.portal_types

    uf = self.getPortal().acl_users
    uf._doAddUser('foo', 'foo', ['Member', ], [])
    uf._doAddUser('ERP5TypeTestCase', 'ERP5TypeTestCase', ['Member', ], [])
    self.commit()
    self.getPortal().ERP5Site_reindexAll(clear_catalog=True)
    self.tic()

    # Person stuff
    person_module = portal.person_module
    person = 'Person'
    person_portal_type = portal_types._getOb(person)
    person_portal_type.setTypeAcquireLocalRole(False)
    # Organisation stuff
    organisation_module = portal.organisation_module
    organisation = 'Organisation'
    organisation_portal_type = portal_types._getOb(organisation)
    organisation_portal_type.setTypeAcquireLocalRole(True)
    self.commit() # So dynamic class gets updated for setTypeAcquireLocalRole change

    def newContent(container, portal_type, acquire_view_permission, view_role_list, local_role_dict):
      document = container.newContent(portal_type=portal_type)
      document.manage_permission('View', roles=view_role_list, acquire=acquire_view_permission)
      for user, role_list in local_role_dict.iteritems():
        document.manage_setLocalRoles(userid=user, roles=role_list)
      return document

    # Create documents for all combinations
    object_dict = {}

    def getObjectDictKey():
      """
        Get values from enclosing environment.
        Uggly, but makes calls less verbose.
      """
      return (portal_type, acquire_view_permission,
              tuple(view_role_list),
              tuple([(x, tuple(y))
                     for x, y in local_role_dict.iteritems()])
             )

    for container, portal_type in ((person_module, person),
                                   (organisation_module, organisation)):
      for acquire_view_permission in (True, False):
        for view_role_list in ([],
                               ['Owner'],
                               ['Owner', 'Author'],
                               ['Author']):
          for local_role_dict in ({},
                                  {'foo': ['Owner']},
                                  {'foo': ['Author']},
                                  {'foo': ['Owner'],
                                   'bar': ['Author']},
                                  {'foo': ['Owner', 'Author'],
                                   'bar': ['Whatever']},
                                  {'foo': ['Owner', 'Author'],
                                   'bar': ['Whatever', 'Author']}):
            object_dict[getObjectDictKey()] = \
              newContent(container, portal_type, acquire_view_permission,
                         view_role_list, local_role_dict)
    self.tic()

    def query(sql):
      result = sql_connection.manage_test(sql)
      return result.dictionaries()

    # Check that there is no Owner role in security table
    # Note: this tests *all* lines from security table. Not just the ones
    # inserted in this test.
    result = query('SELECT * FROM roles_and_users WHERE allowedRolesAndUsers LIKE "%:Owner"')
    self.assertEqual(len(result), 0, repr(result))

    # Check that for each "user:<user>:<role>" line there is exactly one
    # "user:<user>" line with the same uid.
    # Also, check that for each "user:<user>" there is at least one
    # "user:<user>:<role>" line with same uid.
    # Also, check if "user:..." lines are well-formed.
    # Note: this tests *all* lines from security table. Not just the ones
    # inserted in this test.
    line_list = query('SELECT * FROM roles_and_users WHERE allowedRolesAndUsers LIKE "user:%"')
    for line in line_list:
      role_list = line['allowedRolesAndUsers'].split(':')
      uid = line['uid']
      if len(role_list) == 3:
        stripped_role = ':'.join(role_list[:-1])
        result = query('SELECT * FROM roles_and_users WHERE allowedRolesAndUsers = "%s" AND uid = %i' % (stripped_role, uid) )
        self.assertEqual(len(result), 1, repr(result))
      elif len(role_list) == 2:
        result = query('SELECT * FROM roles_and_users WHERE allowedRolesAndUsers LIKE "%s:%%" AND uid = %i' % (line['allowedRolesAndUsers'], uid) )
        self.assertNotEqual(len(result), 0, 'No line found for allowedRolesAndUsers=%r and uid=%i' % (line['allowedRolesAndUsers'], uid))
      else:
        raise Exception, 'Malformed allowedRolesAndUsers value: %r' % (line['allowedRolesAndUsers'], )

    # Check that object that 'bar' can view because of 'Author' role can *not*
    # be found when searching for his other 'Whatever' role.
    local_role_dict = {'foo': ['Owner', 'Author'],
                       'bar': ['Whatever', 'Author']}
    for container, portal_type in ((person_module, person),
                                   (organisation_module, organisation)):
      for acquire_view_permission in (True, False):
        for view_role_list in (['Owner', 'Author'],
                               ['Author']):
          object = object_dict[getObjectDictKey()]
          result = query('SELECT roles_and_users.uid FROM roles_and_users, catalog WHERE roles_and_users.uid = catalog.security_uid AND catalog.uid = %i AND allowedRolesAndUsers = "user:bar:Whatever"' % (object.uid, ))
          self.assertEqual(len(result), 0, '%r: len(%r) != 0' % (getObjectDictKey(), result))

    # Check that no 'bar' role are in security table when 'foo' has local
    # roles allowing him to view an object but 'bar' can't.
    local_role_dict = {'foo': ['Owner', 'Author'],
                       'bar': ['Whatever']}
    for container, portal_type in ((person_module, person),
                                   (organisation_module, organisation)):
      for acquire_view_permission in (True, False):
        for view_role_list in (['Owner', 'Author'],
                               ['Author']):
          object = object_dict[getObjectDictKey()]
          result = query('SELECT roles_and_users.uid, roles_and_users.allowedRolesAndUsers FROM roles_and_users, catalog WHERE roles_and_users.uid = catalog.security_uid AND catalog.uid = %i AND roles_and_users.allowedRolesAndUsers LIKE "user:bar%%"' % (object.uid, ))
          self.assertEqual(len(result), 0, '%r: len(%r) != 0' % (getObjectDictKey(), result))

  def test_RealOwnerIndexing(self):
    logout = self.logout
    user1 = 'local_foo'
    user2 = 'local_bar'
    uf = self.getPortal().acl_users
    uf._doAddUser(user1, user1, ['Member', ], [])
    uf._doAddUser(user2, user2, ['Member', ], [])

    perm = 'View'
    folder = self.getOrganisationModule()
    folder.manage_setLocalRoles(user1, ['Author', 'Auditor'])
    folder.manage_setLocalRoles(user2, ['Author', 'Auditor'])
    portal_type = 'Organisation'

    sql_connection = self.getSQLConnection()

    self.loginByUserName(user2)
    obj2 = folder.newContent(portal_type=portal_type)
    obj2.manage_setLocalRoles(user1, ['Auditor'])
    obj2.manage_permission(perm, ['Owner', 'Auditor'], 0)

    self.loginByUserName(user1)

    obj = folder.newContent(portal_type=portal_type)
    obj.manage_setLocalRoles(user1, ['Owner', 'Auditor'])

    # Check that nothing is returned when user can not view the object
    obj.manage_permission(perm, [], 0)
    obj.reindexObject()
    self.tic()
    result = obj.portal_catalog(portal_type=portal_type)
    self.assertSameSet([obj2, ], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Owner')
    self.assertSameSet([], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
    self.assertSameSet([obj2, ], [x.getObject() for x in result])

    # Check that object is returned when he can view the object
    obj.manage_permission(perm, ['Auditor'], 0)
    obj.reindexObject()
    self.tic()
    result = obj.portal_catalog(portal_type=portal_type)
    self.assertSameSet([obj2, obj], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Owner')
    self.assertSameSet([], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
    self.assertSameSet([obj2, obj], [x.getObject() for x in result])

    # Check that object is returned when he can view the object
    obj.manage_permission(perm, ['Owner'], 0)
    obj.reindexObject()
    self.tic()
    result = obj.portal_catalog(portal_type=portal_type)
    self.assertSameSet([obj2, obj], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Owner')
    self.assertSameSet([obj], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
    self.assertSameSet([obj2, ], [x.getObject() for x in result])

    # Add a new table to the catalog
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()
    # Using newContent for an ERP5 object is not allowed to all roles, so
    # better to fix the roles on the user
    sql_catalog.manage_setLocalRoles(user1, ['Author', 'Auditor', 'Manager'])

    local_roles_table = "test_local_roles"

    create_local_role_table_sql = """
CREATE TABLE `%s` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `owner_reference` varchar(32) NOT NULL default '',
  PRIMARY KEY  (`uid`),
  KEY `version` (`owner_reference`)
) ENGINE=InnoDB;
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z_create_%s' % local_roles_table,
          title='',
          arguments_src="",
          connection_id='erp5_sql_connection',
          src=create_local_role_table_sql)

    drop_local_role_table_sql = """
DROP TABLE IF EXISTS %s
    """ % local_roles_table
    sql_catalog.newContent(portal_type='SQL Method',
          id='z0_drop_%s' % local_roles_table,
          title='',
          arguments_src="",
          connection_id='erp5_sql_connection',
          src=drop_local_role_table_sql)

    catalog_local_role_sql = """
REPLACE INTO
  %s
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="Base_getOwnerId[loop_item]" type="string" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z_catalog_%s_list' % local_roles_table,
          title='',
          connection_id='erp5_sql_connection',
          arguments_src="\n".join(['uid',
                                   'Base_getOwnerId']),
          src=catalog_local_role_sql)

    self.commit()
    current_sql_catalog_object_list = sql_catalog.sql_catalog_object_list
    sql_catalog.sql_catalog_object_list = \
      current_sql_catalog_object_list + \
         ('z_catalog_%s_list' % local_roles_table,)
    current_sql_clear_catalog = sql_catalog.sql_clear_catalog
    sql_catalog.sql_clear_catalog = \
      current_sql_clear_catalog + \
         ('z0_drop_%s' % local_roles_table, 'z_create_%s' % local_roles_table)
    current_sql_catalog_local_role_keys = \
          sql_catalog.sql_catalog_local_role_keys
    sql_catalog.sql_catalog_local_role_keys = ('Owner | %s.owner_reference' % \
       local_roles_table,)
    current_sql_search_tables = sql_catalog.sql_search_tables
    sql_catalog.sql_search_tables = sql_catalog.sql_search_tables + \
        [local_roles_table]
    self.commit()

    try:
      # Clear catalog
      portal_catalog = self.getCatalogTool()
      portal_catalog.manage_catalogClear()
      self.commit()
      self.portal.portal_caches.clearAllCache()
      self.commit()
      obj2.reindexObject()

      # Check that nothing is returned when user can not view the object
      obj.manage_permission(perm, [], 0)
      obj.reindexObject()
      self.tic()
      result = obj.portal_catalog(portal_type=portal_type)
      self.assertSameSet([obj2, ], [x.getObject() for x in result])
      method = obj.portal_catalog
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Owner')
      self.assertSameSet([], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
      self.assertSameSet([obj2, ], [x.getObject() for x in result])

      # Check that object is returned when he can view the object
      obj.manage_permission(perm, ['Auditor'], 0)
      obj.reindexObject()
      self.tic()
      result = obj.portal_catalog(portal_type=portal_type)
      self.assertSameSet([obj2, obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Owner')
      self.assertSameSet([obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
      self.assertSameSet([obj2, obj], [x.getObject() for x in result])

      # Check that object is returned when he can view the object
      obj.manage_permission(perm, ['Owner'], 0)
      obj.reindexObject()
      self.tic()
      result = obj.portal_catalog(portal_type=portal_type)
      self.assertSameSet([obj2, obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Owner')
      self.assertSameSet([obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
      self.assertSameSet([obj2, ], [x.getObject() for x in result])
    finally:
      sql_catalog.sql_catalog_object_list = \
        current_sql_catalog_object_list
      sql_catalog.sql_clear_catalog = \
        current_sql_clear_catalog
      sql_catalog.sql_catalog_local_role_keys = \
          current_sql_catalog_local_role_keys
      sql_catalog.sql_search_tables = current_sql_search_tables
      self.commit()

  def test_MonoValueAssigneeIndexing(self):
    logout = self.logout
    user1 = 'local_foo'
    user2 = 'local_bar'
    uf = self.getPortal().acl_users
    uf._doAddUser(user1, user1, ['Member', ], [])
    uf._doAddUser(user2, user2, ['Member', ], [])

    perm = 'View'
    folder = self.getOrganisationModule()
    folder.manage_setLocalRoles(user1, ['Author', 'Auditor'])
    folder.manage_setLocalRoles(user2, ['Author', 'Auditor'])
    portal_type = 'Organisation'

    sql_connection = self.getSQLConnection()

    self.loginByUserName(user2)
    obj2 = folder.newContent(portal_type=portal_type)
    obj2.manage_setLocalRoles(user1, ['Auditor'])
    obj2.manage_permission(perm, ['Assignee', 'Auditor'], 0)

    self.loginByUserName(user1)

    obj = folder.newContent(portal_type=portal_type)
    obj.manage_setLocalRoles(user1, ['Assignee', 'Auditor'])

    # Check that nothing is returned when user can not view the object
    obj.manage_permission(perm, [], 0)
    obj.reindexObject()
    self.tic()
    result = obj.portal_catalog(portal_type=portal_type)
    self.assertSameSet([obj2, ], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Assignee')
    self.assertSameSet([], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
    self.assertSameSet([obj2, ], [x.getObject() for x in result])

    # Check that object is returned when he can view the object
    obj.manage_permission(perm, ['Auditor'], 0)
    obj.reindexObject()
    self.tic()
    result = obj.portal_catalog(portal_type=portal_type)
    self.assertSameSet([obj2, obj], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Assignee')
    self.assertSameSet([], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
    self.assertSameSet([obj2, obj], [x.getObject() for x in result])

    # Check that object is returned when he can view the object
    obj.manage_permission(perm, ['Assignee'], 0)
    obj.reindexObject()
    self.tic()
    result = obj.portal_catalog(portal_type=portal_type)
    self.assertSameSet([obj2, obj], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Assignee')
    self.assertSameSet([obj], [x.getObject() for x in result])
    result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
    self.assertSameSet([obj2, ], [x.getObject() for x in result])

    # Add a new table to the catalog
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()
    # Using newContent for an ERP5 object is not allowed to all roles, so
    # better to fix the roles on the user
    sql_catalog.manage_setLocalRoles(user1, ['Author', 'Auditor', 'Manager'])

    local_roles_table = "test_assignee_local_roles"

    create_local_role_table_sql = """
CREATE TABLE `%s` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `assignee_reference` varchar(32) NOT NULL default '',
  `viewable_assignee_reference` varchar(32) NOT NULL default '',
  PRIMARY KEY  (`uid`),
  KEY `assignee_reference` (`assignee_reference`),
  KEY `viewable_assignee_reference` (`viewable_assignee_reference`)
) ENGINE=InnoDB;
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z_create_%s' % local_roles_table,
          title='',
          arguments_src="",
          connection_id='erp5_sql_connection',
          src=create_local_role_table_sql)

    drop_local_role_table_sql = """
DROP TABLE IF EXISTS %s
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z0_drop_%s' % local_roles_table,
          title='',
          arguments_src="",
          connection_id='erp5_sql_connection',
          src=drop_local_role_table_sql)

    catalog_local_role_sql = """
REPLACE INTO
  %s
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getAssignee[loop_item] or ''" type="string" optional>,
  <dtml-sqlvar expr="getViewPermissionAssignee[loop_item] or ''" type="string" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z_catalog_%s_list' % local_roles_table,
          title='',
          connection_id='erp5_sql_connection',
          arguments_src="\n".join(['uid',
                                   'getAssignee',
                                   'getViewPermissionAssignee']),
          src=catalog_local_role_sql)

    self.commit()
    current_sql_catalog_object_list = sql_catalog.sql_catalog_object_list
    sql_catalog.sql_catalog_object_list = \
      current_sql_catalog_object_list + \
         ('z_catalog_%s_list' % local_roles_table,)
    current_sql_clear_catalog = sql_catalog.sql_clear_catalog
    sql_catalog.sql_clear_catalog = \
      current_sql_clear_catalog + \
         ('z0_drop_%s' % local_roles_table, 'z_create_%s' % local_roles_table)
    current_sql_catalog_local_role_keys = \
          sql_catalog.sql_catalog_local_role_keys
    sql_catalog.sql_catalog_local_role_keys = ('Assignee | %s.assignee_reference' % \
       local_roles_table,)

    current_sql_catalog_role_keys = \
          sql_catalog.sql_catalog_role_keys
    sql_catalog.sql_catalog_role_keys = (
        'Assignee | %s.viewable_assignee_reference' % \
       local_roles_table,)
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'ERP5Site_filterUserIdSet',
      'group_and_user_id_set',
      'actual_user_set = %r\n'
      'return [x for x in group_and_user_id_set if x in actual_user_set]' % (
        (user1, user2),
      ),
    )
    current_sql_search_tables = sql_catalog.sql_search_tables
    sql_catalog.sql_search_tables = sql_catalog.sql_search_tables + \
        [local_roles_table]
    self.commit()

    try:
      # Clear catalog
      portal_catalog = self.getCatalogTool()
      portal_catalog.manage_catalogClear()
      self.commit()
      self.portal.portal_caches.clearAllCache()
      self.commit()
      obj2.reindexObject()

      # Check that nothing is returned when user can not view the object
      obj.manage_permission(perm, [], 0)
      obj.reindexObject()
      self.tic()
      result = obj.portal_catalog(portal_type=portal_type)
      self.assertSameSet([obj2, ], [x.getObject() for x in result])
      method = obj.portal_catalog
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Assignee')
      self.assertSameSet([], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
      self.assertSameSet([obj2, ], [x.getObject() for x in result])

      # Check that object is returned when he can view the object
      obj.manage_permission(perm, ['Auditor'], 0)
      obj.reindexObject()
      self.tic()
      result = obj.portal_catalog(portal_type=portal_type)
      self.assertSameSet([obj2, obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Assignee')
      self.assertSameSet([obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
      self.assertSameSet([obj2, obj], [x.getObject() for x in result])

      # Check that object is returned when he can view the object
      obj.manage_permission(perm, ['Assignee'], 0)
      obj.reindexObject()
      self.tic()
      result = obj.portal_catalog(portal_type=portal_type)
      self.assertSameSet([obj2, obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Assignee')
      self.assertSameSet([obj], [x.getObject() for x in result])
      result = obj.portal_catalog(portal_type=portal_type, local_roles='Auditor')
      self.assertSameSet([obj2, ], [x.getObject() for x in result])
    finally:
      self.portal.portal_skins.custom.manage_delObjects(ids=['ERP5Site_filterUserIdSet'])
      sql_catalog.sql_catalog_object_list = \
        current_sql_catalog_object_list
      sql_catalog.sql_clear_catalog = \
        current_sql_clear_catalog
      sql_catalog.sql_catalog_local_role_keys = \
          current_sql_catalog_local_role_keys
      sql_catalog.sql_catalog_role_keys = \
          current_sql_catalog_role_keys
      sql_catalog.sql_search_tables = current_sql_search_tables
      self.commit()

  def test_UserOrGroupRoleIndexing(self):
    logout = self.logout
    user1 = 'a_great_user_name'
    user1_group = 'a_great_user_group'
    uf = self.getPortal().acl_users
    uf._doAddUser(user1, user1, ['Member', ], [])
    uf.zodb_groups.addGroup( user1_group, user1_group, user1_group)
    new = uf.zodb_groups.addPrincipalToGroup( user1, user1_group )

    perm = 'View'
    folder = self.getOrganisationModule()
    folder.manage_setLocalRoles(user1, ['Author', 'Auditor'])
    portal_type = 'Organisation'
    organisation = folder.newContent(portal_type=portal_type)

    sql_connection = self.getSQLConnection()
    def query(sql):
      result = sql_connection.manage_test(sql)
      return result.dictionaries()

    self.loginByUserName(user1)

    # Add a new table to the catalog
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()
    # Using newContent for an ERP5 object is not allowed to all roles, so
    # better to fix the roles on the user
    sql_catalog.manage_setLocalRoles(user1, ['Author', 'Auditor', 'Manager'])

    local_roles_table = "test_user_or_group_local_roles"

    create_local_role_table_sql = """
CREATE TABLE `%s` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `assignee_reference` varchar(32) NOT NULL default '',
  `viewable_assignee_reference` varchar(32) NOT NULL default '',
  PRIMARY KEY  (`uid`),
  KEY `assignee_reference` (`assignee_reference`),
  KEY `viewable_assignee_reference` (`viewable_assignee_reference`)
) ENGINE=InnoDB;
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z_create_%s' % local_roles_table,
          title='',
          arguments_src="",
          connection_id='erp5_sql_connection',
          src=create_local_role_table_sql)

    drop_local_role_table_sql = """
DROP TABLE IF EXISTS %s
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z0_drop_%s' % local_roles_table,
          title='',
          arguments_src="",
          connection_id='erp5_sql_connection',
          src=drop_local_role_table_sql)

    catalog_local_role_sql = """
REPLACE INTO
  %s
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getAssignee[loop_item] or ''" type="string" optional>,
  <dtml-sqlvar expr="getViewPermissionAssignee[loop_item] or ''" type="string" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id='z_catalog_%s_list' % local_roles_table,
          title='',
          connection_id='erp5_sql_connection',
          arguments_src="\n".join(['uid',
                                   'getAssignee',
                                   'getViewPermissionAssignee']),
          src=catalog_local_role_sql)

    self.commit()
    current_sql_catalog_object_list = sql_catalog.sql_catalog_object_list
    sql_catalog.sql_catalog_object_list = \
      current_sql_catalog_object_list + \
         ('z_catalog_%s_list' % local_roles_table,)
    current_sql_clear_catalog = sql_catalog.sql_clear_catalog
    sql_catalog.sql_clear_catalog = \
      current_sql_clear_catalog + \
         ('z0_drop_%s' % local_roles_table, 'z_create_%s' % local_roles_table)
    current_sql_catalog_local_role_keys = \
          sql_catalog.sql_catalog_local_role_keys
    sql_catalog.sql_catalog_local_role_keys = (
        'Owner | viewable_owner',
        'Assignee | %s.assignee_reference' % \
       local_roles_table,)

    current_sql_catalog_role_keys = \
          sql_catalog.sql_catalog_role_keys
    sql_catalog.sql_catalog_role_keys = (
        'Assignee | %s.viewable_assignee_reference' % \
       local_roles_table,)
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'ERP5Site_filterUserIdSet',
      'group_and_user_id_set',
      'return [x for x in group_and_user_id_set if x == %r]' % (
        user1,
      ),
    )
    current_sql_search_tables = sql_catalog.sql_search_tables
    sql_catalog.sql_search_tables = sql_catalog.sql_search_tables + \
        [local_roles_table]

    portal = self.getPortal()
    self.commit()

    try:
      # Clear catalog
      portal_catalog = self.getCatalogTool()
      portal_catalog.manage_catalogClear()
      self.commit()
      self.portal.portal_caches.clearAllCache()
      self.commit()

      organisation_relative_url = organisation.getRelativeUrl()
      countResults = organisation.portal_catalog.countResults
      count_result_kw = {'relative_url': organisation_relative_url}

      use_case_number = 0
      for view_permission_role_list, security_group_list, \
          global_view, associate_view, assignee_view, both_view in \
          [
              # No view permission
              ([], [], 0, 0, 0, 0),
              ([], [(user1, ['Associate'])], 0, 0, 0, 0),
              ([], [(user1, ['Assignee'])], 0, 0, 0, 0),
              ([], [(user1, ['Assignee', 'Associate'])], 0, 0, 0, 0),
              ([], [(user1_group, ['Assignee'])], 0, 0, 0, 0),
              ([], [(user1_group, ['Assignee', 'Associate'])], 0, 0, 0, 0),
              ([], [(user1, ['Assignee']),
                    (user1_group, ['Assignee'])], 0, 0, 0, 0),
              ([], [(user1, ['Assignee']),
                    (user1_group, ['Assignee', 'Associate'])], 0, 0, 0, 0),

              # View permission for Assignee
              (['Assignee'], [], 0, 0, 0, 0),
              (['Assignee'], [(user1, ['Associate'])], 0, 0, 0, 0),
              (['Assignee'], [(user1, ['Assignee'])], 1, 0, 1, 1),
              (['Assignee'], [(user1, ['Assignee', 'Associate'])], 1, 0, 1, 1),
              (['Assignee'], [(user1_group, ['Assignee'])], 1, 0, 0, 0),
              (['Assignee'], [(user1_group, ['Assignee', 'Associate'])],
                              1, 0, 0, 0),
              (['Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee'])], 1, 0, 1, 1),
              (['Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee', 'Associate'])],
                               1, 0, 1, 1),

              # View permission for Associate
              (['Associate'], [], 0, 0, 0, 0),
              (['Associate'], [(user1, ['Associate'])], 1, 1, 0, 0),
              (['Associate'], [(user1, ['Assignee'])], 0, 0, 0, 0),
              (['Associate'], [(user1, ['Assignee', 'Associate'])], 1, 1, 1, 1),
              (['Associate'], [(user1_group, ['Assignee'])], 0, 0, 0, 0),
              (['Associate'], [(user1_group, ['Assignee', 'Associate'])],
                               1, 1, 0, 0),
              (['Associate'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee'])], 0, 0, 0, 0),
              (['Associate'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee', 'Associate'])],
                               1, 1, 1, 1),

              # View permission for Associate and Assignee
              (['Associate', 'Assignee'], [], 0, 0, 0, 0),
              (['Associate', 'Assignee'], [(user1, ['Associate'])], 1, 1, 0, 0),
              (['Associate', 'Assignee'], [(user1, ['Assignee'])], 1, 0, 1, 1),
              (['Associate', 'Assignee'],
                     [(user1, ['Assignee', 'Associate'])], 1, 1, 1, 1),
              (['Associate', 'Assignee'],
                     [(user1_group, ['Assignee'])], 1, 0, 0, 0),
              (['Associate', 'Assignee'],
                     [(user1_group, ['Assignee', 'Associate'])], 1, 1, 0, 0),
              (['Associate', 'Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee'])], 1, 0, 1, 1),
              (['Associate', 'Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee', 'Associate'])],
                               1, 1, 1, 1),
              ]:

        use_case_number += 1
        organisation.manage_permission(perm, view_permission_role_list, 0)
        organisation.manage_delLocalRoles([user1, user1_group])
        for security_group, local_role_list in security_group_list:
          organisation.manage_setLocalRoles(security_group, local_role_list)
        organisation.reindexObject()
        self.tic()

        for expected_result, local_roles in \
            [
                (global_view, None),
                (associate_view, 'Associate'),
                (assignee_view, 'Assignee'),
                (both_view, ['Associate', 'Assignee']),
                ]:

          object_security_uid = query(
            'SELECT security_uid FROM catalog WHERE relative_url="%s"' % \
            organisation_relative_url
              )[0]['security_uid']

          if object_security_uid is not None:
            roles_and_users = query(
              'SELECT allowedRolesAndUsers FROM roles_and_users WHERE uid="%s"' % \
              object_security_uid
                )
          else:
            roles_and_users = ''

          monovalue_references = query(
              'SELECT * FROM test_user_or_group_local_roles WHERE uid="%s"' % \
                  organisation.getUid())[0]
          assignee_reference = monovalue_references['assignee_reference']
          viewable_assignee_reference = \
            monovalue_references['viewable_assignee_reference']

          result = countResults(local_roles=local_roles, **count_result_kw)[0][0]
          if result != expected_result:
            countResults(local_roles=local_roles, src__=1,
                         **count_result_kw)
            self.fail('Use case %s\n\tView permission is given to: %s\n\t' \
                      'Local roles are: %s\n\t' \
                      'local_roles parameter is: %s\n\t' \
                      'Object IS %s returned by portal_catalog!\n\t' \
                      '\n\tSecurity uid is: %s\n\t'
                      'Roles and users:  %s\n\t'
                      'assignee_reference:  %s\n\t'
                      'viewable_assignee_reference:  %s\n\t'
                      '\n\tSQL generated: \n\n%s' \
                      '' % \
                      (use_case_number,
                       view_permission_role_list,
                       organisation.__ac_local_roles__,
                       local_roles, ['NOT', ''][result],
                       object_security_uid,
                       str([x['allowedRolesAndUsers'] for x in roles_and_users]),
                       assignee_reference,
                       viewable_assignee_reference,
                       countResults(local_roles=local_roles, src__=1,
                                    **count_result_kw)))

    finally:
      self.portal.portal_skins.custom.manage_delObjects(ids=['ERP5Site_filterUserIdSet'])
      sql_catalog.sql_catalog_object_list = \
        current_sql_catalog_object_list
      sql_catalog.sql_clear_catalog = \
        current_sql_clear_catalog
      sql_catalog.sql_catalog_local_role_keys = \
          current_sql_catalog_local_role_keys
      sql_catalog.sql_catalog_role_keys = \
          current_sql_catalog_role_keys
      sql_catalog.sql_search_tables = current_sql_search_tables
      self.commit()

  def test_UserOrGroupLocalRoleIndexing(self):
    logout = self.logout
    user1 = 'another_great_user_name'
    user1_group = 'another_great_user_group'
    uf = self.getPortal().acl_users
    uf._doAddUser(user1, user1, ['Member', ], [])
    uf.zodb_groups.addGroup( user1_group, user1_group, user1_group)
    new = uf.zodb_groups.addPrincipalToGroup( user1, user1_group )

    perm = 'View'
    folder = self.getOrganisationModule()
    folder.manage_setLocalRoles(user1, ['Author', 'Auditor'])
    portal_type = 'Organisation'
    organisation = folder.newContent(portal_type=portal_type)

    sql_connection = self.getSQLConnection()
    def query(sql):
      result = sql_connection.manage_test(sql)
      return result.dictionaries()

    self.loginByUserName(user1)

    # Add a new table to the catalog
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()
    # Using newContent for an ERP5 object is not allowed to all roles, so
    # better to fix the roles on the user
    sql_catalog.manage_setLocalRoles(user1, ['Author', 'Auditor', 'Manager'])

    local_roles_table = "another_test_user_or_group_local_roles"

    create_local_role_table_sql = """
CREATE TABLE `%s` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `viewable_assignee_reference` varchar(32) NOT NULL default '',
  PRIMARY KEY  (`uid`),
  KEY `viewable_assignee_reference` (`viewable_assignee_reference`)
) ENGINE=InnoDB;
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id = 'z_create_%s' % local_roles_table,
          title = '',
          arguments_src = "",
          connection_id = 'erp5_sql_connection',
          src = create_local_role_table_sql)

    drop_local_role_table_sql = """
DROP TABLE IF EXISTS %s
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id = 'z0_drop_%s' % local_roles_table,
          title = '',
          arguments_src = "",
          connection_id = 'erp5_sql_connection',
          src = drop_local_role_table_sql)

    catalog_local_role_sql = """
REPLACE INTO
  %s
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getViewPermissionAssignee[loop_item] or ''" type="string" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id = 'z_catalog_%s_list' % local_roles_table,
          title = '',
          connection_id = 'erp5_sql_connection',
          arguments_src = "\n".join(['uid',
                                 'getViewPermissionAssignee']),
          src = catalog_local_role_sql)

    self.commit()
    current_sql_catalog_object_list = sql_catalog.sql_catalog_object_list
    sql_catalog.sql_catalog_object_list = \
      current_sql_catalog_object_list + \
         ('z_catalog_%s_list' % local_roles_table,)
    current_sql_clear_catalog = sql_catalog.sql_clear_catalog
    sql_catalog.sql_clear_catalog = \
      current_sql_clear_catalog + \
         ('z0_drop_%s' % local_roles_table, 'z_create_%s' % local_roles_table)

    current_sql_catalog_role_keys = \
          sql_catalog.sql_catalog_role_keys
    sql_catalog.sql_catalog_role_keys = (
        'Owner | viewable_owner',
        'Assignee | %s.viewable_assignee_reference' % \
       local_roles_table,)
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'ERP5Site_filterUserIdSet',
      'group_and_user_id_set',
      'return [x for x in group_and_user_id_set if x == %r]' % (
        user1,
      ),
    )
    current_sql_search_tables = sql_catalog.sql_search_tables
    sql_catalog.sql_search_tables = sql_catalog.sql_search_tables + \
        [local_roles_table]

    portal = self.getPortal()
    self.commit()

    try:
      # Clear catalog
      portal_catalog = self.getCatalogTool()
      portal_catalog.manage_catalogClear()
      self.commit()
      self.portal.portal_caches.clearAllCache()
      self.commit()

      organisation_relative_url = organisation.getRelativeUrl()
      countResults = organisation.portal_catalog.countResults
      count_result_kw = {'relative_url': organisation_relative_url}

      use_case_number = 0
      for view_permission_role_list, security_group_list, \
          associate_view, assignee_view in \
          [
              # No view permission
              ([], [], 0, 0),
              ([], [(user1, ['Associate'])], 0, 0),
              ([], [(user1, ['Assignee'])], 0, 0),
              ([], [(user1, ['Assignee', 'Associate'])], 0, 0),
              ([], [(user1_group, ['Assignee'])], 0, 0),
              ([], [(user1_group, ['Assignee', 'Associate'])], 0, 0),
              ([], [(user1, ['Assignee']),
                    (user1_group, ['Assignee'])], 0, 0),
              ([], [(user1, ['Assignee']),
                    (user1_group, ['Assignee', 'Associate'])], 0, 0),

              # View permission for Assignee
              (['Assignee'], [], 0, 0),
              (['Assignee'], [(user1, ['Associate'])], 0, 0),
              (['Assignee'], [(user1, ['Assignee'])], 0, 1),
              (['Assignee'], [(user1, ['Assignee', 'Associate'])], 0, 1),
              (['Assignee'], [(user1_group, ['Assignee'])], 0, 1),
              (['Assignee'], [(user1_group, ['Assignee', 'Associate'])], 0, 1),
              (['Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee'])], 0, 1),
              (['Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee', 'Associate'])], 0, 1),

              # View permission for Associate
              (['Associate'], [], 0, 0),
              (['Associate'], [(user1, ['Associate'])], 1, 0),
              (['Associate'], [(user1, ['Assignee'])], 0, 0),
              (['Associate'], [(user1, ['Assignee', 'Associate'])], 1, 0),
              (['Associate'], [(user1_group, ['Assignee'])], 0, 0),
              (['Associate'], [(user1_group, ['Assignee', 'Associate'])], 1, 0),
              (['Associate'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee'])], 0, 0),
              (['Associate'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee', 'Associate'])], 1, 0),

              # View permission for Associate and Assignee
              (['Associate', 'Assignee'], [], 0, 0),
              (['Associate', 'Assignee'], [(user1, ['Associate'])], 1, 0),
              (['Associate', 'Assignee'], [(user1, ['Assignee'])], 0, 1),
              (['Associate', 'Assignee'],
                     [(user1, ['Assignee', 'Associate'])], 1, 1),
              (['Associate', 'Assignee'],
                     [(user1_group, ['Assignee'])], 0, 1),
              (['Associate', 'Assignee'],
                     [(user1_group, ['Assignee', 'Associate'])], 1, 1),
              (['Associate', 'Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee'])], 0, 1),
              (['Associate', 'Assignee'], [(user1, ['Assignee']),
                              (user1_group, ['Assignee', 'Associate'])], 1, 1),
              ]:

        use_case_number += 1
        organisation.manage_permission(perm, view_permission_role_list, 0)
        organisation.manage_delLocalRoles([user1, user1_group])
        for security_group, local_role_list in security_group_list:
          organisation.manage_setLocalRoles(security_group, local_role_list)
        organisation.reindexObject()
        self.tic()

        for expected_result, local_roles in \
            [
                (associate_view or assignee_view, None),
                (associate_view, 'Associate'),
                (assignee_view, 'Assignee'),
                (associate_view or assignee_view, ['Associate', 'Assignee']),
                ]:

          object_security_uid = query(
            'SELECT security_uid FROM catalog WHERE relative_url="%s"' % \
            organisation_relative_url
              )[0]['security_uid']

          if object_security_uid is not None:
            roles_and_users = query(
              'SELECT allowedRolesAndUsers FROM roles_and_users WHERE uid="%s"' % \
              object_security_uid
                )
          else:
            roles_and_users = ''

          monovalue_references = query(
              'SELECT * FROM %s WHERE uid="%s"' % \
                 (local_roles_table, organisation.getUid()))[0]
          viewable_assignee_reference = \
            monovalue_references['viewable_assignee_reference']

          result = countResults(local_roles=local_roles, **count_result_kw)[0][0]
          if result != expected_result:
            countResults(local_roles=local_roles, src__=1,
                         **count_result_kw)
            self.fail('Use case %s\n\tView permission is given to: %s\n\t' \
                      'Local roles are: %s\n\t' \
                      'local_roles parameter is: %s\n\t' \
                      'Object IS %s returned by portal_catalog!\n\t' \
                      '\n\tSecurity uid is: %s\n\t'
                      'Roles and users:  %s\n\t'
                      'viewable_assignee_reference:  %s\n\t'
                      '\n\tSQL generated: \n\n%s' \
                      '' % \
                      (use_case_number,
                       view_permission_role_list,
                       organisation.__ac_local_roles__,
                       local_roles, ['NOT', ''][result],
                       object_security_uid,
                       str([x['allowedRolesAndUsers'] for x in roles_and_users]),
                       viewable_assignee_reference,
                       countResults(local_roles=local_roles, src__=1,
                                    **count_result_kw)))

    finally:
      self.portal.portal_skins.custom.manage_delObjects(ids=['ERP5Site_filterUserIdSet'])
      sql_catalog.sql_catalog_object_list = \
        current_sql_catalog_object_list
      sql_catalog.sql_clear_catalog = \
        current_sql_clear_catalog
      sql_catalog.sql_catalog_role_keys = \
          current_sql_catalog_role_keys
      sql_catalog.sql_search_tables = current_sql_search_tables
      self.commit()

  def test_PersonDocumentWithMonovaluedLocalRole(self):
    """Test when user is added, which has local roles on own Person Document

    This is a case when Person document containting reference with local role
    which shall be monovalued is reindexed for first time.
    """
    sql_connection = self.getSQLConnection()
    def query(sql):
      result = sql_connection.manage_test(sql)
      return result.dictionaries()

    # Add a new table to the catalog
    sql_catalog = self.portal.portal_catalog.getSQLCatalog()

    local_roles_table = "person_document_test_user_or_group_local_roles"

    create_local_role_table_sql = """
CREATE TABLE `%s` (
  `uid` BIGINT UNSIGNED NOT NULL,
  `viewable_assignee_reference` varchar(32) NOT NULL default '',
  PRIMARY KEY  (`uid`),
  KEY `viewable_assignee_reference` (`viewable_assignee_reference`)
) ENGINE=InnoDB;
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id = 'z_create_%s' % local_roles_table,
          title = '',
          arguments_src = "",
          connection_id = 'erp5_sql_connection',
          src = create_local_role_table_sql)

    drop_local_role_table_sql = """
DROP TABLE IF EXISTS %s
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id = 'z0_drop_%s' % local_roles_table,
          title = '',
          arguments_src = "",
          connection_id = 'erp5_sql_connection',
          src = drop_local_role_table_sql)

    catalog_local_role_sql = """
REPLACE INTO
  %s
VALUES
<dtml-in prefix="loop" expr="_.range(_.len(uid))">
(
  <dtml-sqlvar expr="uid[loop_item]" type="int">,
  <dtml-sqlvar expr="getViewPermissionAssignee[loop_item] or ''" type="string" optional>
)
<dtml-if sequence-end>
<dtml-else>
,
</dtml-if>
</dtml-in>
    """ % local_roles_table
    sql_catalog.newContent(
          portal_type='SQL Method',
          id = 'z_catalog_%s_list' % local_roles_table,
          title = '',
          connection_id = 'erp5_sql_connection',
          arguments_src = "\n".join(['uid',
                                 'getViewPermissionAssignee']),
          src = catalog_local_role_sql)

    self.commit()
    current_sql_catalog_object_list = sql_catalog.sql_catalog_object_list
    sql_catalog.sql_catalog_object_list = \
      current_sql_catalog_object_list + \
         ('z_catalog_%s_list' % local_roles_table,)
    current_sql_clear_catalog = sql_catalog.sql_clear_catalog
    sql_catalog.sql_clear_catalog = \
      current_sql_clear_catalog + \
         ('z0_drop_%s' % local_roles_table, 'z_create_%s' % local_roles_table)

    current_sql_catalog_role_keys = \
          sql_catalog.sql_catalog_role_keys
    sql_catalog.sql_catalog_role_keys = (
        'Owner | viewable_owner',
        'Assignee | %s.viewable_assignee_reference' % \
       local_roles_table,)

    current_sql_search_tables = sql_catalog.sql_search_tables
    sql_catalog.sql_search_tables = sql_catalog.sql_search_tables + \
        [local_roles_table]

    portal = self.getPortal()
    self.commit()

    try:
      # Clear catalog
      portal_catalog = self.getCatalogTool()
      portal_catalog.manage_catalogClear()
      self.commit()
      self.portal.portal_caches.clearAllCache()
      self.commit()

      person = self.portal.person_module.newContent(portal_type='Person')
      user_id = person.Person_getUserId()
      createZODBPythonScript(
        self.portal.portal_skins.custom,
        'ERP5Site_filterUserIdSet',
        'group_and_user_id_set',
        'return [x for x in group_and_user_id_set if x == %r]' % (
          user_id,
        ),
      )
      person.manage_setLocalRoles(user_id, ['Assignee'])

      self.tic()

      roles_and_users_result = query('select * from roles_and_users where uid = (select security_uid from catalog where uid = %s)' % person.getUid())
      local_roles_table_result = query('select * from %s where uid = %s' % (local_roles_table, person.getUid()))[0]

      # check that local seucirty table is clean about created person object
      self.assertSameSet(
          sorted([q['allowedRolesAndUsers'] for q in roles_and_users_result]),
          ['Assignee', 'Assignor', 'Associate', 'Auditor', 'Author', 'Manager']
      )
      # check that user has optimised security declaration
      self.assertEqual(local_roles_table_result['viewable_assignee_reference'], user_id)
    finally:
      self.portal.portal_skins.custom.manage_delObjects(ids=['ERP5Site_filterUserIdSet'])
      sql_catalog.sql_catalog_object_list = \
        current_sql_catalog_object_list
      sql_catalog.sql_clear_catalog = \
        current_sql_clear_catalog
      sql_catalog.sql_catalog_role_keys = \
          current_sql_catalog_role_keys
      sql_catalog.sql_search_tables = current_sql_search_tables
      self.commit()

  def test_ObjectReindexationConcurency(self):
    portal = self.portal

    portal_activities = getattr(portal, 'portal_activities', None)
    if portal_activities is None:
      ZopeTestCase._print('\n Skipping test_ObjectReindexatoinConcurency (portal_activities not found)')
      return

    container = organisation_module = portal.organisation_module
    document_1 = container.newContent()
    document_1_1 = document_1.newContent()
    document_1_2 = document_1.newContent()
    document_2 = container.newContent()
    self.tic()
    # First case: parent, then child
    document_1.reindexObject()
    self.assertEqual(len(portal_activities.getMessageList()), 0)
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 1)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 1)
    document_1_1.reindexObject()
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 2)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 1)
    self.tic()
    # Variation of first case: parent's borther along
    document_1.reindexObject()
    document_2.reindexObject()
    self.assertEqual(len(portal_activities.getMessageList()), 0)
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 2)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 2)
    document_1_1.reindexObject()
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 3)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 2)
    self.tic()
    # Second case: child, then parent
    document_1_1.reindexObject()
    self.assertEqual(len(portal_activities.getMessageList()), 0)
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 1)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 1)
    document_1.reindexObject()
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 2)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 1)
    self.tic()
    # Variation of second case: parent's borther along
    document_1_1.reindexObject()
    document_2.reindexObject()
    self.assertEqual(len(portal_activities.getMessageList()), 0)
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 2)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 2)
    document_1.reindexObject()
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 3)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 2)
    self.tic()
    # Third case: child 1, then child 2
    document_1_1.reindexObject()
    self.assertEqual(len(portal_activities.getMessageList()), 0)
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 1)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 1)
    document_1_2.reindexObject()
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 2)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 1)
    self.tic()
    # Variation of third case: parent's borther along
    document_1_1.reindexObject()
    document_2.reindexObject()
    self.assertEqual(len(portal_activities.getMessageList()), 0)
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 2)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 2)
    document_1_2.reindexObject()
    self.commit()
    self.assertEqual(len(portal_activities.getMessageList()), 3)
    portal_activities.distribute()
    self.assertEqual(len([x for x in portal_activities.getMessageList() if x.processing_node == 0]), 2)
    self.tic()

  def test_reindexWithGroupId(self):
    CatalogTool = type(self.getCatalogTool().aq_base)
    counts = []
    orig_catalogObjectList = CatalogTool.catalogObjectList.__func__
    def catalogObjectList(self, object_list, *args, **kw):
      counts.append(len(object_list))
      return orig_catalogObjectList(self, object_list, *args, **kw)
    def check(*x):
      self.tic()
      self.assertEqual(counts, list(x))
      del counts[:]
    try:
      CatalogTool.catalogObjectList = catalogObjectList
      module = self.getPersonModule()
      ob = module.newContent(), module.newContent()
      check(2)
      ob[0].reindexObject(group_id='x')
      ob[1].reindexObject(group_id='x')
      check(2)
      ob[0].reindexObject(group_id='1')
      ob[1].reindexObject(group_id='2')
      check(1, 1)
      ob[0].reindexObject(activate_kw={'group_id':'x'})
      ob[1].reindexObject(activate_kw={'group_id':'x'})
      check(2)
      ob[0].reindexObject(activate_kw={'group_id':'1'})
      ob[1].reindexObject(activate_kw={'group_id':'2'})
      check(1, 1)
    finally:
      CatalogTool.catalogObjectList = orig_catalogObjectList

  def test_PercentCharacter(self):
    """
    Check expected behaviour of % character for simple query
    """
    portal_type = 'Organisation'
    folder = self.getOrganisationModule()
    folder.newContent(portal_type=portal_type, title='foo_organisation_1')
    folder.newContent(portal_type=portal_type, title='foo_organisation_2')
    self.tic()
    self.assertEqual(1, len(folder.portal_catalog(portal_type=portal_type,
                                                   title='foo_organisation_1')))
    self.assertEqual(1, len(folder.portal_catalog(portal_type=portal_type,
                                                   title='foo_organisation_2')))
    self.assertEqual(1, len(folder.portal_catalog(portal_type=portal_type,
                                                   title='%organisation_1')))
    self.assertEqual(2, len(folder.portal_catalog(portal_type=portal_type,
                                                   title='foo_organisation%')))
    self.assertEqual(1, len(folder.portal_catalog(portal_type=portal_type,
                                                   title='foo_org%ion_1')))

  def test_SearchedStringIsNotStripped(self):
    """
      Check that extra spaces in lookup values are preserved
    """
    portal_type = 'Organisation'
    folder = self.getOrganisationModule()
    first_doc = folder.newContent(portal_type=portal_type, reference="foo")
    second_doc = folder.newContent(portal_type=portal_type, reference=" foo")
    self.tic()
    def compareSet(reference, document_list):
      result = folder.portal_catalog(portal_type=portal_type,
                                     reference=reference)
      self.assertSameSet(document_list, [x.getObject() for x in result])
    compareSet('foo', [first_doc])
    compareSet(' foo', [second_doc])
    # XXX: Those will hardly work, and it probably not the responsability of python code:
    # MySQL ignores trailing spaces in conditions.
    # So it's probably not really part of this test.
    #compareSet('foo ', [])
    #compareSet(' foo ', [])

  def test_WildcardMatchesUnsetValue(self):
    """
      Check that the "%" wildcard matches unset values.
    """
    portal_type = 'Organisation'
    folder = self.getOrganisationModule()
    first_doc = folder.newContent(portal_type=portal_type, reference="doc 1")
    second_doc = folder.newContent(portal_type=portal_type, reference="doc 2", description="test")
    self.tic()
    result = folder.portal_catalog(portal_type=portal_type, reference='doc %', description='%')
    self.assertEqual(len(result), 2)

  def test_multipleRelatedKeyDoMultipleJoins(self):
    """
      Check that when multiple related keys are present in the same query,
      each one does a separate join.
      ie:
        Searching for an object whose site_title is "foo" and
        site_description is "bar" will yeld a result set which is the union
        of:
          - objects whose site_title is foo
          - objects whose site_description is bar
    """
    portal = self.portal
    def _create(**kw):
      return portal.organisation_module.newContent(portal_type='Organisation', **kw)
    def create(id, related_obect_list):
      return _create(id=id,
        site_value_list=related_obect_list,
        function_value_list=related_obect_list)
    def check(expected_result, description, query):
      result = [x.getObject() for x in portal.portal_catalog(portal_type='Organisation', query=query)]
      self.assertSameSet(expected_result, result,
        '%s:\nExpected: %r\nGot: %r' % (description,
           [x.getId() for x in expected_result],
           [x.getId() for x in result]))
    # completely artificial example, we just need relations
    related_1 = _create(title='foo1', reference='foo', description='bar')
    related_2 = _create(title='foo2', reference='foo'                   )
    related_3 = _create(                               description='bar')
    related_4 = _create()
    object_1  = create('object_1',  [related_1])
    object_2  = create('object_2',  [related_2])
    object_3  = create('object_3',  [related_3])
    object_4  = create('object_4',  [related_4])
    object_12 = create('object_12', [related_1, related_2])
    object_13 = create('object_13', [related_1, related_3])
    object_14 = create('object_14', [related_1, related_4])
    object_23 = create('object_23', [related_2, related_3])
    object_24 = create('object_24', [related_2, related_4])
    object_34 = create('object_34', [related_3, related_4])
    reference_object_list =   [object_1, object_2,                     object_12, object_13, object_14, object_23, object_24           ]
    description_object_list = [object_1,           object_3,           object_12, object_13, object_14, object_23,            object_34]
    both_object_list =        [object_1,                               object_12, object_13, object_14, object_23                      ]
    title_object_list =       [                                        object_12                                                       ]
    self.tic()
    # Single join
    check(reference_object_list,
          'site_reference="foo"',
          Query(site_reference='foo'))
    check(description_object_list,
          'site_description="bar"',
          Query(site_description='bar'))
    # Double join on different relations
    check(both_object_list,
          'site_reference="foo" AND function_description="bar"',
          ComplexQuery(Query(site_reference='foo'),
                       Query(function_description='bar'),
                       logical_operator='AND'))
    # Double join on same relation
    check(both_object_list,
          'site_reference="foo" AND site_description="bar"',
          ComplexQuery(Query(site_reference='foo'),
                       Query(site_description='bar'),
                       logical_operator='AND'))
    # Double join on same related key
    check(title_object_list,
          'site_title="foo1" AND site_title="foo2"',
          ComplexQuery(Query(site_title='=foo1'),
                       Query(site_title='=foo2'),
                       logical_operator='AND'))

  def test_SearchFolderWithRelatedDynamicRelatedKey(self):
    # Create some objects
    portal = self.portal
    portal_category = self.getCategoryTool()
    portal_category.group.manage_delObjects([x for x in
        portal_category.group.objectIds()])
    group_nexedi_category = portal_category.group\
                                .newContent( id = 'nexedi', title='Nexedi',
                                             reference='a')
    group_nexedi_category2 = portal_category.group\
                                .newContent( id = 'storever', title='Storever',
                                             reference='b')
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',
                                     title='Nexedi Orga',
                                     reference='c')
    organisation.setGroup('nexedi')
    self.assertEqual(organisation.getGroupValue(), group_nexedi_category)
    organisation2 = module.newContent(portal_type='Organisation',
                                      title='Storever Orga',
                                      reference='d')
    organisation2.setGroup('storever')
    organisation2.setTitle('Organisation 2')
    self.assertEqual(organisation2.getGroupValue(), group_nexedi_category2)
    # Flush message queue
    self.tic()

    base_category = portal_category.group
    # Try to get the category with the group related organisation title Nexedi
    # Orga
    category_list = [x.getObject() for x in
                         base_category.searchFolder(
                           group_related_title='Nexedi Orga')]
    self.assertEqual(category_list, [group_nexedi_category])
    category_list = [x.getObject() for x in
                         base_category.searchFolder(
                           default_group_related_title='Nexedi Orga')]
    self.assertEqual(category_list, [group_nexedi_category])
    # Try to get the category with the group related organisation id
    category_list = [x.getObject() for x in
                         base_category.searchFolder(group_related_id='storever')]
    self.assertEqual(category_list,[group_nexedi_category2])
    # Try to get the category with the group related organisation reference 'd'
    category_list = [x.getObject() for x in
                         base_category.searchFolder(group_related_reference='d')]
    self.assertEqual(category_list,[group_nexedi_category2])
    # Try to get the category with the group related organisation reference
    # 'e'
    category_list = [x.getObject() for x in
                         base_category.searchFolder(group_related_reference='e')]
    self.assertEqual(category_list,[])
    # Try to get the category with the default group related organisation reference
    # 'e'
    category_list = [x.getObject() for x in
                         base_category.searchFolder(default_group_related_reference='e')]
    self.assertEqual(category_list,[])
    # Try to get the category with the group related organisation relative_url
    organisation_relative_url = organisation.getRelativeUrl()
    category_list = [x.getObject() for x in
                 base_category.searchFolder(group_related_relative_url=organisation_relative_url)]
    self.assertEqual(category_list, [group_nexedi_category])
    # Try to get the category with the group related organisation uid
    category_list = [x.getObject() for x in
                 base_category.searchFolder(group_related_uid=organisation.getUid())]
    self.assertEqual(category_list, [group_nexedi_category])
    # Try to get the category with the group related organisation id and title
    # of the category
    category_list = [x.getObject() for x in
                         base_category.searchFolder(group_related_id=organisation2.getId(),
                                             title='Storever')]
    self.assertEqual(category_list,[group_nexedi_category2])

  def test_SearchFolderWithRelatedDynamicStrictRelatedKey(self):
    # Create some objects
    portal = self.portal
    portal_category = self.getCategoryTool()
    portal_category.group.manage_delObjects([x for x in
        portal_category.group.objectIds()])
    group_nexedi_category = portal_category.group\
                                .newContent( id = 'nexedi', title='Nexedi',
                                             reference='a')
    sub_group_nexedi = group_nexedi_category\
                                .newContent( id = 'erp5', title='ERP5',
                                             reference='b')
    module = portal.getDefaultModule('Organisation')
    organisation = module.newContent(portal_type='Organisation',
                                     title='ERP5 Orga',
                                     reference='c')
    organisation.setGroup('nexedi/erp5')
    self.assertEqual(organisation.getGroupValue(), sub_group_nexedi)
    organisation2 = module.newContent(portal_type='Organisation',
                                     title='Nexedi Orga',
                                     reference='d')
    organisation2.setGroup('nexedi')
    # Flush message queue
    self.tic()

    base_category = portal_category.group

    # Try to get the category with the group related organisation title Nexedi
    # Orga
    category_list = [x.getObject() for x in
                         base_category.portal_catalog(
                             strict_group_related_title='Nexedi Orga')]
    self.assertEqual(category_list,[group_nexedi_category])
    # Try to get the category with the group related organisation title ERP5
    # Orga
    category_list = [x.getObject() for x in
                         base_category.portal_catalog(
                           strict_group_related_title='ERP5 Orga')]
    self.assertEqual(category_list,[sub_group_nexedi])
    # Try to get the category with the group related organisation reference d
    category_list = [x.getObject() for x in
                         base_category.portal_catalog(
                           strict_group_related_reference='d')]
    self.assertEqual(category_list,[group_nexedi_category])
    # Try to get the category with the group related organisation reference c
    category_list = [x.getObject() for x in
                         base_category.portal_catalog(
                           strict_group_related_reference='c')]
    self.assertEqual(category_list,[sub_group_nexedi])

  def test_EscapingLoginInSescurityQuery(self):
    # Create some objects
    reference = "aaa.o'connor@fake.ie"
    portal = self.getPortal()
    uf = self.portal.acl_users
    uf._doAddUser(reference, 'secret', ['Member'], [])
    user = uf.getUserById(reference).__of__(uf)
    newSecurityManager(None, user)
    portal.view()

  def test_IndexationContextIndependence(self):
    def doCatalog(catalog, document):
      catalog.catalogObjectList([document], check_uid=0)
      result = catalog(select_list=['reference'], uid=document.getUid())
      self.assertEqual(len(result), 1)
      return result[0].reference

    # Create some dummy documents
    portal = self.getPortalObject()
    portal.foo = FooDocument(portal.getPath() + '/foo')
    portal.bar = BarDocument(portal.getPath() + '/bar')

    # Get instances, wrapping them in acquisition context implicitely.
    foo = portal.foo
    bar = portal.bar

    # Consistency checks
    self.assertTrue(getattr(foo, 'getReference', None) is not None)
    self.assertTrue(getattr(bar, 'getReference', None) is None)

    # Clean indexing
    portal_catalog = portal.portal_catalog
    self.assertEqual(doCatalog(portal_catalog, foo), 'foo')
    self.assertEqual(doCatalog(portal_catalog, bar), None)

    # Index an object wrapped in a "poisoned" acquisition chain
    bar_on_foo = portal.foo.bar
    self.assertTrue(getattr(bar_on_foo, 'getReference', None) is not None)
    self.assertEqual(bar_on_foo.getReference(), 'foo')
    self.assertEqual(doCatalog(portal_catalog, bar_on_foo), None)

    # Index an object with catalog wrapped in a "poisoned" acquisition chain
    portal_catalog_on_foo = portal.foo.portal_catalog
    self.assertTrue(getattr(portal_catalog_on_foo, 'getReference', None) is not None)
    self.assertEqual(portal_catalog_on_foo.getReference(), 'foo')
    self.assertEqual(doCatalog(portal_catalog_on_foo, foo), 'foo')
    self.assertEqual(doCatalog(portal_catalog_on_foo, bar), None)

    # Poison everything
    self.assertEqual(doCatalog(portal_catalog_on_foo, bar_on_foo), None)

    delattr(portal, 'foo')
    delattr(portal, 'bar')

  def test_distinct_select_expression(self):
    person = self.portal.person_module.newContent(portal_type='Person')
    self.tic()
    portal_catalog = self.getCatalogTool()
    res = portal_catalog.searchResults(
      select_dict={
        'count_reference': 'count(DISTINCT reference)',
      },
      group_by=['reference'],
      portal_type='Person',
    )
    self.assertEqual(1, len(res))
    self.assertEqual(person, res[0].getObject())

  def test_CatalogUidDuplicates(self):
    """
    Initially, the catalog was changing uids when a duplicate was found.

    This operation was really too dangerous, so now we raise errors in this
    case. Here we now check that the error is raised
    """
    # Create an object just to allocate a new valid uid.
    person_module = self.getPersonModule()
    person = person_module.newContent(portal_type='Person')
    self.tic()

    # Make sure that the new object is catalogued.
    portal_catalog = self.getPortalObject().portal_catalog
    self.assertEqual(person, portal_catalog(uid=person.uid)[0].getObject())

    # Delete the new object to free the uid.
    available_uid = person.uid
    person_module.manage_delObjects(uids=[available_uid])
    self.tic()

    # Make sure that the uid is not used any longer.
    self.assertEqual(0, len(portal_catalog(uid=person.uid)))

    # Now, we create two new objects without indexing, so the catalog
    # will not know anything about these objects.
    person1 = person_module.newContent(portal_type='Person', is_indexable=False)
    person2 = person_module.newContent(portal_type='Person', is_indexable=False)

    # Force to assign the same uid, and catalog them.
    person1.uid = person2.uid = available_uid
    person1.is_indexable = person2.is_indexable = True
    self.assertRaises(ValueError, portal_catalog.catalogObjectList,[person1, person2])

  def test_SearchFolderWithParenthesis(self):
    person_module = self.getPersonModule()

    # Make sure that the catalog will not split it with such research :
    # title=foo AND title=bar
    title='foo (bar)'
    person = person_module.newContent(portal_type='Person',title=title)
    person_id = person.getId()
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertTrue(person_id in folder_object_list)
    folder_object_list = [x.getObject().getId() for x in
                              person_module.searchFolder(title=title)]
    self.assertEqual([person_id],folder_object_list)

  def test_SearchFolderWithMultipleSpaces(self):
    person_module = self.getPersonModule()

    # Make sure that the catalog will not split it with such research :
    # title=foo AND title=bar
    title='foo bar'
    person_module.newContent(portal_type='Person',title=title)
    self.tic()
    title = title.replace(' ', '  ')
    person = person_module.newContent(portal_type='Person',title=title)
    person_id = person.getId()
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertTrue(person_id in folder_object_list)
    folder_object_list = [x.getObject().getId() for x in
                              person_module.searchFolder(**{'catalog.title':title})]
    self.assertEqual([person_id],folder_object_list)

  def test_SearchFolderWithSingleQuote(self):
    person_module = self.getPersonModule()

    # Make sure that the catalog will not split it with such research :
    # title=foo AND title=bar
    title="foo 'bar"
    person = person_module.newContent(portal_type='Person',title=title)
    person_id = person.getId()
    self.tic()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertTrue(person_id in folder_object_list)
    folder_object_list = [x.getObject().getId() for x in
                              person_module.searchFolder(title=title)]
    self.assertEqual([person_id],folder_object_list)

  def test_ParameterSelectDict(self):
    person_module = self.getPersonModule()

    # Make sure that we are able to retrieve data directly from mysql
    # without retrieving real objects
    title = "foo"
    description = "foobar"
    person = person_module.newContent(portal_type='Person',title=title,
                                      description=description)
    person_uid = person.getUid()
    self.tic()
    folder_object_list = person_module.searchFolder(uid=person_uid, select_dict={'title': None})
    new_title = 'bar'
    new_description = 'foobarfoo'
    person.setTitle(new_title)
    person.setDescription(new_description)
    self.assertEqual(new_title, person.getTitle())
    expected_sql_title_list = [title]
    self.assertEqual([x.title for x in folder_object_list],
                      expected_sql_title_list)
    self.assertEqual([x.getProperty('title') for x in
                      folder_object_list], expected_sql_title_list)
    expected_sql_description_list = [new_description]
    self.assertEqual([x.getProperty('description') for x in
                      folder_object_list], expected_sql_description_list)
    real_title_list = [new_title]
    self.assertEqual([x.getTitle() for x in
                      folder_object_list], real_title_list)

  def test_getParentUid(self):
    from Products.ERP5.Document.Assignment import Assignment
    import erp5.portal_type
    person_module = self.getPersonModule()

    person_id = person_module.generateNewId()
    person = erp5.portal_type.Person(person_id)
    person.setDefaultReindexParameters(activate_kw={'after_tag': self.id()})
    person = person_module[person_module._setObject(person_id, person)]
    self.assertFalse('uid' in person.__dict__)
    person.uid = None

    assignment_id = person.generateNewId()
    assignment = erp5.portal_type.Assignment(assignment_id)
    assignment.setDefaultReindexParameters(activate_kw={'tag': self.id()})
    assignment = person[person._setObject(assignment_id, assignment)]
    self.assertFalse('uid' in assignment.__dict__)
    assignment.uid = None
    self.commit()

    person_uid_list = []
    catalog_result_list = []
    Assignment_getParentUid = Assignment.getParentUid
    def getParentUid(self):
      person_uid_list.append(person.uid)
      uid = Assignment_getParentUid(self)
      catalog_result_list.append(len(self.portal_catalog(uid=uid)))
      return uid
    Assignment.getParentUid = getParentUid
    try:
      self.tic()
    finally:
      Assignment.getParentUid = Assignment_getParentUid
    self.assertEqual(catalog_result_list[0], 0)
    self.assertEqual(person_uid_list[0], None)
    self.assertTrue(int(person.uid))
    self.assertEqual(person.uid, assignment.getParentUid())

  def test_queriesEndingWithSemicolon(self):
    connector = self.getPortal().erp5_sql_connection
    result = connector.manage_test('select 1 as foo;')
    self.assertEqual(1, result[0].foo)

  def _createSomeGroupCategories(self):
    portal_category = self.getCategoryTool()
    group_category = portal_category.group
    group_data_map = dict(nexedi=('Nexedi', 'Nexedi Group'),
                          tiolive=('TIOLive', 'TioLive Group'),)
    existing_group_id_list = group_category.objectIds()
    for group_id, (title, description) in group_data_map.items():
      if group_id in existing_group_id_list:
        group = group_category[group_id]
      else:
        group = group_category.newContent(id=group_id)
      group.edit(title=title, description=description)

  def test_SelectDictWithDynamicRelatedKey(self):
    self._createSomeGroupCategories()

    # Create some orgs associated with varying association with the
    # groups created above.
    module = self.portal.getDefaultModule('Organisation')
    # org1 has no groups
    org1 = module.newContent(portal_type='Organisation', title='org1')
    # org2 has group nexedi
    org2 = module.newContent(portal_type='Organisation', title='org2')
    org2.setGroupList(['nexedi'])
    # org3 has group tiolive
    org3 = module.newContent(portal_type='Organisation', title='org3')
    org3.setGroupList(['tiolive'])
    # org4 has both groups
    org4 = module.newContent(portal_type='Organisation', title='org4')
    org4.setGroupList(['nexedi', 'tiolive'])
    # check associations are correct
    actual_group_title_map = {org.getTitle(): sorted(org.getGroupTitleList())
                              for org in (org1, org2, org3, org4)}
    expected_group_title_map = dict(org1=[],
                                    org2=['Nexedi'],
                                    org3=['TIOLive'],
                                    org4=['Nexedi', 'TIOLive'])
    self.assertEqual(actual_group_title_map, expected_group_title_map)
    # Flush message queue
    self.tic()

    # we will restrict our search to orgs with these ids to be resilient
    # to preexisting orgs:
    org_id_list = sorted(org.getId() for org in (org1, org2, org3, org4))
    # and we'll sort on title to make the output predictable
    search_kw = dict(id=org_id_list,
                     sort_on='title')
    # Try to get the organisations with the group title Nexedi to make sure
    # searching works correctly
    organisation_list = [x.getObject() for x in
                         module.searchFolder(strict_group_title='Nexedi',
                                             **search_kw)]
    self.assertEqual(organisation_list, [org2, org4])
    # Now lets fetch the titles of groups of the above orgs using select_dict.
    search_kw.update(select_dict=dict(strict_group_title=None))
    records = module.searchFolder(**search_kw)
    # By default the catalog returns all items, and the selected
    # strict_group_title is set to None for documents without groups
    # Besides, some entries will appear many times, according to the number of
    # relationships each catalog entry has in that related key.
    results = [(rec.title, rec.strict_group_title)
               for rec in records]
    self.assertEqual(sorted(results),
                      [('org1', None),
                       ('org2', 'Nexedi'),
                       ('org3', 'TIOLive'),
                       ('org4', 'Nexedi'),
                       ('org4', 'TIOLive')])
    # This also works if we force a left join on the column.
    # They'll still be repeated according to their relationships, though.
    search_kw.update(left_join_list=('strict_group_title',))
    records = module.searchFolder(**search_kw)
    results = [(rec.title, rec.strict_group_title)
               for rec in records]
    self.assertEqual(sorted(results),
                      [('org1', None),
                       ('org2', 'Nexedi'),
                       ('org3', 'TIOLive'),
                       ('org4', 'Nexedi'),
                       ('org4', 'TIOLive')])
    # To get only one of each org, we need to group by one of the
    # catalog keys.

    # Note that this relies on a non-standard behaviour
    # of MySQL: If a selected column is not present in the GROUP BY
    # clause, only the first ocurrence is taken.  Other databases,
    # like Oracle, assume that selected columns are either GROUPed BY
    # or are inside an aggregation function (COUNT, SUM, GROUP_CONCAT,
    # ...), and consider the query to be in error otherwise.
    search_kw.update(group_by_list=('uid',))
    organisation_list = [x.getObject() for x in
                         module.searchFolder(**search_kw)]
    self.assertEqual(organisation_list, [org1, org2, org3, org4])

  def test_BackwardCompatibilityWithOldMethods(self):
    'Dealing with RelatedKey methods missing the proper separator'
    module = self.getOrganisationModule()
    org_a = self._makeOrganisation(title='abc',default_address_city='abc')
    org_a.setReference(org_a.getId())
    # sometimes the module itself is not indexed yet...
    module.reindexObject()

    # Flush message queue
    self.tic()

    # make a query to fetch the address of the organisation above by
    # querying, among other things, the grand_parent
    query = dict(grand_parent_portal_type="Organisation Module",
                 parent_reference=org_a.getReference())
    catalog = self.getCatalogTool()
    # check the query works normally
    self.assertEqual([x.getObject() for x in catalog.searchResults(**query)],
                     [org_a.default_address])

    # even if we do a left_join
    query_lj = query.copy()
    query_lj.update(left_join_list=('grand_parent_portal_type',))
    self.assertEqual([x.getObject() for x in catalog.searchResults(**query_lj)],
                     [org_a.default_address])

    # now turn the z_related_grand_parent into an old-style method, without
    # RELATED_QUERY_SEPARATOR
    method = catalog.getSQLCatalog().z_related_grand_parent
    old_src = method.src

    @self._addCleanup
    def cleanGrandParentMethod(self):
      method.manage_edit(method.title, method.connection_id,
                         method.arguments_src, old_src)

    src = old_src.replace('<dtml-var RELATED_QUERY_SEPARATOR>', ' AND ')
    method.manage_edit(method.title, method.connection_id, method.arguments_src,
                       src)

    # check that it still works
    self.assertEqual([x.getObject() for x in catalog.searchResults(**query)],
                     [org_a.default_address])

    # now try to do a left-join on grand_parent_portal_type which
    # shouldn't work
    self.assertRaises(RuntimeError, lambda: catalog.searchResults(**query_lj))

    # Neither should it work if a left-join is attempted in a column
    # that has proper related-key rendering, but is present in the
    # same query as a column that hasn't, as the whole query is
    # converted into implicit inner joins.
    self.tic()
    query_lj.update(left_join_list=('strict_group_title',),
                    select_dict=('strict_group_title',))
    self.assertRaises(RuntimeError, lambda: catalog.searchResults(**query_lj))
    # though it should work on queries that don't use the broken related-key
    del query_lj['grand_parent_portal_type']
    self.assertEqual([x.getObject() for x in catalog.searchResults(**query_lj)],
                     [org_a.default_address])

  def testSearchAndActivateWithGroupMethodId(self):
    """
    Make sure searchAndActivate method could be used with a grouping method,
    and in particular make sure sure searchAndActivate can calls himself
    properly.

    We create 300 organisations and use a group method cost of 0.5.
    So this means searchAndActivate should first create 200 activities
    that will be grouped by 2. Then searchAndActivate will call himself
    another time to activate the last 100 organisations, and in their turn
    they will be grouped by 2.
    """
    group_method_call_list = []
    def doSomething(self, message_list):
      r = []
      for m in message_list:
        m.result = r.append(m.object.getPath())
      r.sort()
      group_method_call_list.append(r)
    self.portal.portal_activities.__class__.doSomething = doSomething
    now = DateTime()
    try:
        organisation_list = []
        for x in xrange(0,300):
          organisation_list.append(
            self.portal.organisation_module.newContent().getPath())
        self.tic()
        self.portal.portal_catalog.searchAndActivate(
             creation_date={'query': now, 'range': 'min'},
             method_id="dummyDoSomething",
             group_kw = {"group_method_id" : "portal_activities/doSomething",
                         "group_method_cost": 0.5},
        )
        self.tic()
        self.assertEqual(150, len(group_method_call_list))
        organisation_call_list = []
        for call_path_list in group_method_call_list:
          self.assertEqual(2, len(call_path_list))
          organisation_call_list.extend(call_path_list)
        organisation_call_list.sort()
        organisation_list.sort()
        self.assertEqual(organisation_call_list, organisation_list)
    finally:
      del self.portal.portal_activities.__class__.doSomething

  def test_filter_expression(self):
    catalog = self.portal.portal_catalog.getSQLCatalog()
    portal_type_list = catalog.getVisibleAllowedContentTypeList()
    assert portal_type_list
    econtext = getEngine().getContext()
    getExpressionInstance = lambda: catalog._getFilterDict()[indexation_method_id].get('expression_instance')
    evaluate = lambda: getExpressionInstance()(econtext)
    catalog_method_list = catalog.getSqlCatalogObjectListList()
    for portal_type in portal_type_list:
      indexation_method = catalog.newContent(portal_type=portal_type)
      indexation_method_id = indexation_method.getId()
      catalog.setSqlCatalogObjectListList(catalog_method_list + (indexation_method_id, ))
      try:
        indexation_method.setFiltered(True)
        indexation_method.setExpression('python: 1')
        self.assertEqual(evaluate(), 1)
        self.commit()
        self.assertEqual(evaluate(), 1)
        indexation_method.setExpression('python: 2')
        self.abort()
        self.assertEqual(evaluate(), 1)
        indexation_method.setExpression('python: 2')
        self.assertEqual(evaluate(), 2)
        self.commit()
        self.assertEqual(evaluate(), 2)
      finally:
        catalog.setSqlCatalogObjectListList(catalog_method_list)

  def test_publish_catalog(self):
    """When catalog is published by zope, it does not issue a catalog search but
    renders the default view.
    """
    ret = self.publish(
        self.portal.portal_catalog.getPath(),
        basic='ERP5TypeTestCase:')
    self.assertEqual(httplib.OK, ret.getStatus())
    # check if we did not just publish the result of `str(portal_catalog.__call__())`,
    # but a proper page
    self.assertIn('<title>Catalog Tool - portal_catalog', ret.getBody())


class CatalogToolUpgradeSchemaTestCase(ERP5TypeTestCase):
  """Tests for "upgrade schema" feature of ERP5 Catalog.
  """

  def getBusinessTemplateList(self):
    return ("erp5_full_text_mroonga_catalog",)

  def afterSetUp(self):
    # Add two connections
    db1, db2 = getExtraSqlConnectionStringList()[:2]
    addConnection = self.portal.manage_addProduct[
        "ZMySQLDA"].manage_addZMySQLConnection
    addConnection("erp5_test_connection_1", "", db1)
    addConnection("erp5_test_connection_2", "", db2)
    addConnection("erp5_test_connection_deferred_2", "", db2, deferred=True)

    self.catalog_tool = self.portal.portal_catalog
    self.catalog = self.catalog_tool.newContent(portal_type="Catalog")
    self.catalog.newContent(
        portal_type="SQL Method",
        connection_id="erp5_test_connection_1",
        id="z_create_catalog",
        src="CREATE TABLE dummy_catalog (uid int)")

    # These will be cleaned up at tear down
    self._db1_table_list = ["dummy_catalog"]
    self._db2_table_list = []

  def beforeTearDown(self):
    for table in self._db1_table_list:
      self.query_connection_1("DROP TABLE IF EXISTS `%s`" % table)
    for table in self._db2_table_list:
      self.query_connection_2("DROP TABLE IF EXISTS `%s`" % table)
    self.portal.manage_delObjects([
            "erp5_test_connection_1",
            "erp5_test_connection_2",
            "erp5_test_connection_deferred_2"])
    self.commit()

  def query_connection_1(self, q):
    return self.portal.erp5_test_connection_1().query(q)

  def query_connection_2(self, q):
    return self.portal.erp5_test_connection_2().query(q)

  def upgradeSchema(self):
    self.assertTrue(
        self.catalog_tool.upgradeSchema(
            sql_catalog_id=self.catalog.getId(), src__=True))

    self.catalog_tool.upgradeSchema(sql_catalog_id=self.catalog.getId())
    self.assertFalse(
        self.catalog_tool.upgradeSchema(
            sql_catalog_id=self.catalog.getId(), src__=True))

  def test_upgradeSchema_add_table(self):
    self._db1_table_list.append("add_table")
    method = self.catalog.newContent(
        portal_type="SQL Method",
        connection_id="erp5_test_connection_1",
        id=self.id(),
        src="CREATE TABLE add_table (a int)")
    self.catalog.setSqlClearCatalogList([method.getId()])
    self.commit()

    self.upgradeSchema()
    self.commit()
    self.query_connection_1("SELECT a from add_table")

  def test_upgradeSchema_alter_table(self):
    self._db1_table_list.append("altered_table")
    self.query_connection_1("CREATE TABLE altered_table (a int)")
    self.commit()
    method = self.catalog.newContent(
        portal_type="SQL Method",
        connection_id="erp5_test_connection_1",
        id=self.id(),
        src="CREATE TABLE altered_table (a int, b int)")
    self.catalog.setSqlClearCatalogList([method.getId()])
    self.commit()

    self.upgradeSchema()
    self.commit()
    self.query_connection_1("SELECT b from altered_table")

  def test_upgradeSchema_multi_connections(self):
    # Check that we can upgrade tables on more than one connection,
    # like when using an external datawarehouse. This is a reproduction
    # for https://nexedi.erp5.net/bug_module/20170426-A3962E
    # In this test we use both "normal" and deferred connections,
    # which is what happens in default erp5 catalog.
    self._db1_table_list.append("table1")
    self.query_connection_1("CREATE TABLE table1 (a int)")
    self._db2_table_list.extend(("table2", "table_deferred2"))
    self.query_connection_2("CREATE TABLE table2 (a int)")
    self.query_connection_2("CREATE TABLE table_deferred2 (a int)")
    self.commit()

    method1 = self.catalog.newContent(
        portal_type="SQL Method",
        connection_id="erp5_test_connection_1",
        src="CREATE TABLE table1 (a int, b int)")
    method2 = self.catalog.newContent(
        portal_type="SQL Method",
        connection_id="erp5_test_connection_2",
        src="CREATE TABLE table2 (a int, b int)")
    method_deferred2 = self.catalog.newContent(
        portal_type="SQL Method",
        connection_id="erp5_test_connection_deferred_2",
        src="CREATE TABLE table_deferred2 (a int, b int)")
    self.catalog.setSqlClearCatalogList(
        [method1.getId(),
         method2.getId(),
         method_deferred2.getId()])
    self.commit()

    self.upgradeSchema()
    self.commit()
    self.query_connection_1("SELECT b from table1")
    self.query_connection_2("SELECT b from table2")
    self.query_connection_2("SELECT b from table_deferred2")

    with self.assertRaisesRegexp(ProgrammingError,
                                 r"Table '.*\.table2' doesn't exist"):
      self.query_connection_1("SELECT b from table2")
    with self.assertRaisesRegexp(ProgrammingError,
                                 r"Table '.*\.table_deferred2' doesn't exist"):
      self.query_connection_1("SELECT b from table_deferred2")
    with self.assertRaisesRegexp(ProgrammingError,
                                 r"Table '.*\.table1' doesn't exist"):
      self.query_connection_2("SELECT b from table1")
