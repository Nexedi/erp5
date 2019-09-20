# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010-2011 Nexedi SA and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import unittest
import transaction
import ZODB
from ZODB.DemoStorage import DemoStorage
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestType(unittest.TestCase):

  def setUp(self):
    self.db = ZODB.DB(DemoStorage())
    self.tm1 = transaction.TransactionManager()
    self.conn1 = self.db.open(transaction_manager=self.tm1)
    self.tm2 = transaction.TransactionManager()
    self.conn2 = self.db.open(transaction_manager=self.tm2)

  def tearDown(self):
    self.db.close()
    del self.tm1, self.conn1, self.tm2, self.conn2, self.db

  def testConflictFreeLog(self):
    from Products.ERP5Type.ConflictFree import ConflictFreeLog
    for t in (1, 404, 4), (500, 407, 3), (1000, 407, 2), (1500, 808, 1):
      self.conn1.root()['x'] = x1 = ConflictFreeLog(bucket_size=t[0])
      self.tm1.commit()
      self.tm2.begin()
      x2 = self.conn2.root()['x']
      x1.append(-1)
      x2.extend(xrange(200))
      self.tm1.commit()
      self.tm2.commit()
      self.tm1.begin()
      x1 += 401, 402
      x2.extend(xrange(200, 400))
      self.tm2.commit()
      x2.append(400)
      self.tm2.commit()
      self.tm1.commit()
      self.tm2.begin()
      expected = range(-1, 403)
      self.assertEqual(expected, list(x1))
      self.assertEqual(expected, list(x2))
      self.assertEqual(expected[::-1], list(x1.reversed()))
      self.assertEqual(len(expected), len(x1))
      self.assertEqual(len(expected), len(x2))
      x1 += x2
      self.assertEqual(t[1], len(x1._log))
      bucket_count = 1
      x = x2._next
      while x not in (x2, None):
        x = x._next
        bucket_count += 1
      self.assertEqual(t[2], bucket_count)


class TestERP5(ERP5TypeTestCase):

  def getTitle(self):
    return "Conflict Resolution: ERP5"

  def afterSetUp(self):
    other_node = self.getOtherZopeNodeList()[0]
    self.other_node = self.portal.portal_web_services.connect(
      "http://%s%s" % (other_node, self.portal.getPath()),
      'ERP5TypeTestCase', '', 'xml-rpc')
    self.login()

  def testZODBCookie(self):
    cookie_name = self._testMethodName
    portal = self.portal
    cookie = portal.getCacheCookie(cookie_name) # 0
    self.commit()
    portal.newCacheCookie(cookie_name) # 1
    self.other_node.newCacheCookie(cookie_name) # 1
    self.other_node.newCacheCookie(cookie_name) # 2
    self.commit()# max(1, 2) + 1
    self.assertEqual(cookie + 3, portal.getCacheCookie(cookie_name))

  def testActiveProcess(self):
    active_process = self.portal.portal_activities.newActiveProcess()
    self.commit()
    remote = self.other_node
    remote.getId() # force storage sync of remote ZODB connection
                   # (see also Products.ERP5Type.patches.ZODBConnection)
    for id in active_process.getRelativeUrl().split('/'):
      remote = getattr(remote, id)
    for x in xrange(100):
      active_process.postResult(x)
    remote.testActiveProcess_postResult(100)
    try:
      self.commit()
    except:
      self.abort() # make failure more readable in case of regression
      raise
    self.assertEqual(sorted(active_process.getResultList()), range(101))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestType))
  suite.addTest(unittest.makeSuite(TestERP5))
  return suite
