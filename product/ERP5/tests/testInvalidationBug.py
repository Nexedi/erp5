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

import unittest
import os

import transaction

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from DateTime import DateTime

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
    module = self.getPortalObject().organisation_module
    organisation = module.newContent()    # modify ZODB and create activity
    organisation.immediateReindexObject() # modify catalog
    path = organisation.getPath()
    test_list = []
    for connection_id, table in (('erp5_sql_connection', 'catalog'),
                                 ('cmf_activity_sql_connection', 'message')):
      connection = self.portal[connection_id]
      connection = connection.__class__('_' + connection_id, '',
                                        '-' + connection.connection_string)
      query = "rollback\0select * from %s where path='%s'" % (table, path)
      test_list.append(lambda manage_test=connection.manage_test, query=query:
         len(manage_test(query)))
    result_list = [map(apply, test_list)]
    Transaction_commitResources = transaction.Transaction._commitResources
    def _commitResources(self):
      orig_tpc_finish_dict = dict((rm.__class__, rm.__class__.tpc_finish)
                                  for rm in self._resources)
      def tpc_finish(self, txn):
        orig_tpc_finish_dict[self.__class__](self, txn)
        result_list.append(map(apply, test_list))
      try:
        for cls in orig_tpc_finish_dict:
          cls.tpc_finish = tpc_finish
        return Transaction_commitResources(self)
      finally:
        for cls, tpc_finish in orig_tpc_finish_dict.iteritems():
          cls.tpc_finish = tpc_finish
    try:
      transaction.Transaction._commitResources = _commitResources
      transaction.commit()
    finally:
      transaction.Transaction._commitResources = Transaction_commitResources
    self.assertEqual(result_list[0], [0,0])
    self.assertEqual(result_list[1], [0,0])  # activity buffer first
    self.assertEqual(result_list[-2], [1,0]) # catalog
    self.assertEqual(result_list[-1], [1,1]) # activity tables last

  def _testReindex(self):
    print("To reproduce bugs easily, distribution step should be skipped for"
          " SQLDict, by writing messages with processing_node already at 0."
          " This can be done easily by patching SQLDict_writeMessageList.")
    module = self.getPortalObject().organisation_module
    module.newContent()
    module.setIdGenerator('_generatePerDayId')
    #module.migrateToHBTree()
    transaction.commit()
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
    transaction.commit()
    self.tic()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInvalidationBug))
  return suite
