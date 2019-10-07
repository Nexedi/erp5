##############################################################################
#
# Copyright (c) 2019 Nexedi SARL and Contributors. All Rights Reserved.
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

##############################################################################

from __future__ import division
from functools import wraps
from Testing.ZopeTestCase import TestCase
from Products.ERP5Type.ConflictFree import DoublyLinkList
from Products.ERP5Type.Workflow import WorkflowHistoryList
from Products.ERP5Type.patches.WorkflowTool import \
  WorkflowHistoryList as LegacyWorkflowHistoryList
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

orig_maybe_rotate = DoublyLinkList._maybe_rotate.__func__

def _maybe_rotate(self):
  if len(self._log) < 16:
    self._p_changed = 1
  else:
    self._rotate()

def fixed_count_bucket(wrapped):
  def wrapper(*args, **kw):
    try:
      DoublyLinkList._maybe_rotate = _maybe_rotate
      return wrapped(*args, **kw)
    finally:
      DoublyLinkList._maybe_rotate = orig_maybe_rotate
  return wraps(wrapped)(wrapper)

def new(cls, items):
  dll = cls()
  for item in items:
    dll.append(item)
  return dll

def old(items):
  whl = WorkflowHistoryList()
  whl.__class__ = LegacyWorkflowHistoryList
  for item in items:
    if len(whl._log) < 16:
      whl._log.append(item)
    else:
      prev = whl.__new__(whl.__class__)
      prev._prev = whl._prev
      prev._log = whl._log
      whl._prev = prev
      whl._log = [item]
  return whl

COUNT = 45
EXPECTED = range(COUNT)

class TestWorkflowHistoryList(TestCase):

  from transaction import abort, commit

  def checkList(self, ddl):
    self.assertEqual(len(ddl), COUNT)
    self.assertEqual(len(ddl._log), 13)
    self.assertEqual(len(ddl._next._log), 16)
    self.assertEqual(EXPECTED, list(ddl))
    self.assertEqual(EXPECTED[::-1], list(reversed(ddl)))
    self.assertEqual(EXPECTED[::-1], list(reversed(ddl)))
    self.assertEqual(ddl, new(type(ddl), EXPECTED))

    class check(object):
      def __getitem__(_, item):
        try:
          a = EXPECTED[item]
        except IndexError:
          with self.assertRaises(IndexError):
            ddl[item]
        else:
          assert a != [], a
          self.assertEqual(a, ddl[item])
    check = check()

    i = COUNT + 1
    for i in xrange(-i, i):
      check[i]
    check[-50:10]
    check[:20:3]
    check[5:40]
    check[32::4]
    check[::-1]
    check[-5::-7]
    check[50:40:-1]
    check[30:-50:-4]
    check[:30:-3]

    self.assertFalse(ddl[-5:30])
    self.assertFalse(ddl[30:-5:-1])

  def checkClass(self, ddl, cls):
    ddl._p_activate()
    self.assertIs(type(ddl), cls)
    bucket = ddl._prev
    while bucket is not None:
      bucket._p_activate()
      self.assertIs(type(bucket), cls)
      bucket = bucket._prev
      if bucket is ddl:
        break

  @fixed_count_bucket
  def test_01_DoublyLinkList(self):
    EXPECTED = range(COUNT)
    self.checkList(new(DoublyLinkList, EXPECTED))

  @fixed_count_bucket
  def test_02_LegacyWorkflowHistoryList(self):
    whl = old(EXPECTED[:40])

    # Check common operations that don't require migration.
    self.assertTrue(whl)
    whl.append(40)
    whl += EXPECTED[41:]
    self.assertEqual(EXPECTED[::-1], list(reversed(whl)))
    self.assertEqual(EXPECTED[-1], whl[-1])
    self.checkClass(whl, LegacyWorkflowHistoryList)

    # Automatic migration on another operation.
    self.assertEqual(whl[0], 0)
    self.checkClass(whl, WorkflowHistoryList)

    self.checkList(whl)

  @fixed_count_bucket
  def test_03_MigrationPersistence(self):
    self.app.whl = whl = old(EXPECTED)
    self.commit()
    whl._p_jar.cacheMinimize()

    prev, slots = whl.__getstate__()
    self.assertIs(prev, whl._prev)
    self.assertEqual(slots, EXPECTED[32:])

    whl += xrange(3)
    self.checkClass(whl, LegacyWorkflowHistoryList)
    whl += xrange(2)
    self.checkClass(whl, WorkflowHistoryList)
    self.abort()

    whl += xrange(3)
    self.checkClass(whl, LegacyWorkflowHistoryList)
    whl.append('foo')
    whl.append('bar')
    self.checkClass(whl, WorkflowHistoryList)
    self.abort()

    self.checkClass(whl, LegacyWorkflowHistoryList)
    self.assertEqual(len(whl), COUNT)
    self.checkClass(whl, WorkflowHistoryList)
    self.commit()
    whl._p_jar.cacheMinimize()

    self.checkClass(whl, WorkflowHistoryList)
    self.checkList(whl)

  def test_04_rotation(self):
    self.app.ddl = ddl = DoublyLinkList()
    item_size = ddl._bucket_size // 3
    for _ in xrange(3):
      for _ in xrange(3):
        ddl.append('.' * item_size)
      self.commit()
    self.assertEqual(6, ddl._tail_count)
    self.assertEqual(3, ddl._prev._tail_count)
    self.assertEqual(0, ddl._prev._prev._tail_count)


class TestDedup(ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    return ('erp5_base',)

  def test(self):
    self.login()
    deduped = []
    def dedupStrings(obj):
      new = orig_dedupStrings(obj)
      self.assertEqual(new, obj)
      deduped.append(len(new))
      return new
    from Products.ERP5Type import Workflow
    orig_dedupStrings = Workflow.dedupStrings
    try:
      Workflow.dedupStrings = dedupStrings
      ob = self.portal.person_module.newContent()
      whl = ob.workflow_history["edit_workflow"]
      while whl._prev is None:
        ob.edit()
        self.commit()
        whl._p_deactivate()
    finally:
      Workflow.dedupStrings = orig_dedupStrings
    self.assertEqual(deduped, [24])
    self.assertEqual(len(list(whl)), 25)
