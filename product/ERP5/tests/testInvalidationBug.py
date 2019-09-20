# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
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

import threading
import unittest
import urllib
import transaction
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript

class TestInvalidationBug(ERP5TypeTestCase):

  def getTitle(self):
    return "Invalidation Bug"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base',)

  def afterSetUp(self):
    self.login()

  def testCommitOrder(self):
    """Check order of resources being committed"""
    module = self.portal.organisation_module
    organisation = module.newContent()    # modify ZODB and create activity
    organisation.immediateReindexObject() # modify catalog
    path = organisation.getPath()
    test_list = []
    for connection_id, table in (('erp5_sql_connection', 'catalog'),
                                 ('cmf_activity_sql_connection', 'message')):
      connection = self.portal[connection_id]
      query = connection.factory()('-' + connection.connection_string).query
      sql = "rollback\0select * from %s where path='%s'" % (table, path)
      test_list.append(lambda query=query, sql=sql: len(query(sql)[1]))
    result_list = [map(apply, test_list)]
    Transaction_commitResources = transaction.Transaction._commitResources
    connection = module._p_jar
    def _commitResources(self):
      def tpc_finish(rm, txn):
        rm.__class__.tpc_finish(rm, txn)
        result_list.append(None if rm is connection else map(apply, test_list))
      try:
        for rm in self._resources:
          rm.tpc_finish = lambda txn, rm=rm: tpc_finish(rm, txn)
        return Transaction_commitResources(self)
      finally:
        for rm in self._resources:
          del rm.tpc_finish
    try:
      transaction.Transaction._commitResources = _commitResources
      self.commit()
    finally:
      transaction.Transaction._commitResources = Transaction_commitResources
    self.tic()
    # Whether ZODB should be committed before or after catalog is not obvious.
    # Current behaviour is required to avoid creating duplicated applied rules.
    self.assertEqual(result_list[0], [0,0])
    self.assertEqual(result_list[1], [0,0])  # activity buffer first
    self.assertEqual(result_list[-3], [1,0]) # catalog
    self.assertEqual(result_list[-2], None)  # ZODB
    self.assertEqual(result_list[-1], [1,1]) # activity tables last

  def testLateInvalidationFromZEO(self):
    ### Check unit test is run properly
    from ZEO.ClientStorage import ClientStorage
    storage = self.portal._p_jar._storage
    self.assertIsInstance(
        storage,
        ClientStorage,
        "This test must be run with ZEO storage")
    node_list = self.getOtherZopeNodeList()
    activity_tool = self.portal.portal_activities

    ### Prepare unit test, to minimize amount of work during critical section
    ## make sure activity tool's OOBTree for family mapping is loaded before the test
    _ = activity_tool.getCurrentNodeFamilyIdSet()
    ## url to create some content using another zope
    new_content_url = "http://ERP5TypeTestCase:@%s%s/Folder_create" % (
      node_list[0], self.portal.organisation_module.getPath())
    ## prepare freeze/unfreeze of ZEO storage
    zeo_connection = storage._connection
    socket_map = zeo_connection._map
    freeze_lock = threading.Lock()
    freeze_lock.acquire()
    def unfreezeStorage():
      socket_map[zeo_connection.fileno()] = zeo_connection
      # wake up asyncore loop to take the new socket into account
      zeo_connection.trigger.pull_trigger()
    # link to ZEO will be unfrozen 1 second after we read 'message' table
    unfreeze_timer = threading.Timer(1, unfreezeStorage)
    unfreeze_timer.setDaemon(True)
    ## prepare monkey-patches (with code to revert them)
    from Products.CMFActivity.Activity.SQLDict import SQLDict
    zeo_server = storage._server
    def unpatch():
      storage._server = zeo_server
      SQLDict.getProcessableMessageList = SQLDict_getProcessableMessageList
    SQLDict_getProcessableMessageList = SQLDict.getProcessableMessageList
    def getProcessableMessageList(*args, **kw):
      result = SQLDict_getProcessableMessageList(*args, **kw)
      unpatch()
      unfreeze_timer.start()
      return result

    ### Perform unit test
    ## we should start without any pending activity
    self.assertNoPendingMessage()
    ## monkey-patch ...
    SQLDict.getProcessableMessageList = getProcessableMessageList
    try:
      # prevent nodes from processing activities automatically
      activity_tool.manage_removeFromProcessingList(node_list)
      self.commit()
      del socket_map[zeo_connection.fileno()]
      try:
        # wake up asyncore loop and wait we really woke up
        zeo_connection.trigger.pull_trigger(freeze_lock.release)
        freeze_lock.acquire()
        # make sure ZODB is not accessed until we get a message to process
        storage._server = None
        # ... monkey-patch done
        ## create object
        urllib.urlopen(new_content_url).read()
        ## validate reindex activity
        activity_tool.distribute()
        self.assertEqual(1, len(activity_tool.getMessageList()))
        ## reindex created object
        activity_tool.tic()
      finally:
        try:
          unfreeze_timer.join()
        except RuntimeError:
          unfreezeStorage()
    finally:
      unpatch()
      activity_tool.manage_addToProcessingList(node_list)
      self.commit()
    ## When the bug is not fixed, we get a -3 failed activity
    self.assertNoPendingMessage()

  def _testReindex(self):
    print("To reproduce bugs easily, distribution step should be skipped for"
          " SQLDict, by writing messages with processing_node already at 0."
          " This can be done easily by patching SQLDict_writeMessageList.")
    module = self.getPortalObject().organisation_module
    module.newContent()
    module.setIdGenerator('_generatePerDayId')
    #module.migrateToHBTree()
    self.tic()
    print 'OID(%s) = %r' % (module.getRelativeUrl(), module._p_oid)
    print '  OID(_tree) = %r' % module._tree._p_oid
    previous = DateTime()
    skin_folder = self.getPortal().portal_skins.custom
    if 'create_script' in skin_folder.objectIds():
      skin_folder.manage_delObjects(ids=['create_script'])
    skin = createZODBPythonScript(skin_folder, 'create_script', '**kw',
        """
from Products.ERP5Type.Log import log
id_list = []
for x in xrange(0, 1):
  organisation = context.newContent()
  id_list.append(organisation.getId())
log('Created Organisations', (context,id_list))
#log('All organisations', (context,[x for x in context.objectIds()]))
context.activate(activity='SQLQueue', priority=2).create_script()

count = len(context)
log('Organisation #', count)
if (count % 500) < 5:
  start = context.getProperty('perf_start')
  if start is None:
    context.setProperty('perf_start', (count, DateTime()))
  else:
    log('creation speed: %s obj/s' % ((count - start[0]) /
        (86400 * (DateTime() - start[1]))))
""")
    for x in xrange(0,200):
      module.activate(activity='SQLQueue', priority=2).create_script()
    self.tic()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInvalidationBug))
  return suite
