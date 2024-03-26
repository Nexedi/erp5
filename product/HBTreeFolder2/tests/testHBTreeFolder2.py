##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import random
import unittest
from Testing import ZopeTestCase
from Products.HBTreeFolder2.HBTreeFolder2 \
     import HBTreeFolder2, ExhaustedUniqueIdsError
from OFS.ObjectManager import BadRequestException
from OFS.Folder import Folder
from Acquisition import aq_base
import timeit
from textwrap import dedent
from unittest import expectedFailure
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.PythonScripts.PythonScript import PythonScript
import six
from six.moves import range


class HBTreeFolder2Tests(ERP5TypeTestCase):

    def getBase(self, ob):
        # This is overridden in subclasses.
        return aq_base(ob)

    def setUp(self):
        self.f = HBTreeFolder2('root')
        ff = HBTreeFolder2('item')
        self.f._setOb(ff.id, ff)
        self.ff = self.f._getOb(ff.id)

    def testKey(self):
        f = self.f
        ff = f.item
        ok = "a", "b-a", "b-b", "c-a-b", "c-a-d"
        for id in ok:
          f._setOb(id, ff)
          f._getOb(id)
        for id in "a-a", "b", "c-a":
          if id != "c-a":
            self.assertRaises(KeyError, f._setOb, id, ff)
          self.assertRaises(KeyError, f._getOb, id)
          self.assertRaises(KeyError, f._delOb, id)
        self.assertEqual(len(f), 1 + len(ok))
        self.assertEqual(f.getTreeIdList(), [None, "b", "c-a"])
        self.assertEqual(len(f._htree), 4)
        for id in ok:
          f._delOb(id)
        self.assertEqual(len(f._htree), 1)
        self.assertEqual(len(f), 1)
        self.assertEqual(f.getTreeIdList(), [None])
        self.assertEqual(ff.getTreeIdList(), [])

    def testAdded(self):
        self.assertEqual(self.ff.id, 'item')

    def testCount(self):
        self.assertEqual(self.f.objectCount(), 1)
        self.assertEqual(self.ff.objectCount(), 0)
        self.assertEqual(len(self.f), 1)
        self.assertEqual(len(self.ff), 0)

    def testObjectIds(self):
        self.assertEqual(list(self.f.objectIds()), ['item'])
        self.assertEqual(list(self.f.keys()), ['item'])
        self.assertEqual(list(self.ff.objectIds()), [])
        f3 = HBTreeFolder2('item3')
        self.f._setOb(f3.id, f3)
        lst = list(self.f.objectIds())
        lst.sort()
        self.assertEqual(lst, ['item', 'item3'])

    def testObjectValues(self):
        values = self.f.objectValues()
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].id, 'item')
        # Make sure the object is wrapped.
        self.assertTrue(values[0] is not self.getBase(values[0]))

    def testObjectItems(self):
        items = self.f.objectItems()
        self.assertEqual(len(items), 1)
        id, val = items[0]
        self.assertEqual(id, 'item')
        self.assertEqual(val.id, 'item')
        # Make sure the object is wrapped.
        self.assertTrue(val is not self.getBase(val))

    def testHasKey(self):
        self.assertTrue(self.f.hasObject('item'))  # Old spelling
        self.assertIn('item', self.f)  # New spelling

    def testDelete(self):
        self.f._delOb('item')
        self.assertEqual(list(self.f.objectIds()), [])
        self.assertEqual(self.f.objectCount(), 0)

    def testObjectIds_d(self):
        self.assertEqual(self.f.objectIds_d(), {'item': 1})

    def testCheckId(self):
        self.assertEqual(self.f._checkId('xyz'), None)
        self.assertRaises(BadRequestException, self.f._checkId, 'item')
        self.assertRaises(BadRequestException, self.f._checkId, 'REQUEST')

    def testSetObject(self):
        f2 = HBTreeFolder2('item2')
        self.f._setObject(f2.id, f2)
        self.assertIn('item2', self.f)
        self.assertEqual(self.f.objectCount(), 2)

    def testWrapped(self):
        # Verify that the folder returns wrapped versions of objects.
        base = self.f.item
        for x in (self.f._getOb('item'),
                  self.f['item'],
                  self.f.get('item')):
            self.assertIsNot(base, x)
            self.assertIs(base, self.getBase(x))

    def testGenerateId(self):
        ids = {}
        for n in range(10):
            ids[self.f.generateId()] = 1
        self.assertEqual(len(ids), 10)  # All unique
        for id in ids.keys():
            self.f._checkId(id)  # Must all be valid

    def testGenerateIdDenialOfServicePrevention(self):
        for n in range(10):
            item = Folder()
            item.id = 'item%d' % n
            self.f._setOb(item.id, item)
        self.f.generateId('item', rand_ceiling=20)  # Shouldn't be a problem
        self.assertRaises(ExhaustedUniqueIdsError,
                          self.f.generateId, 'item', rand_ceiling=9)

    def testReplace(self):
        old_f = Folder()
        old_f.id = 'item'
        inner_f = HBTreeFolder2('inner')
        old_f._setObject(inner_f.id, inner_f)
        self.ff._populateFromFolder(old_f)
        self.assertEqual(self.ff.objectCount(), 1)
        self.assertIn('inner', self.ff)
        self.assertEqual(self.getBase(self.ff._getOb('inner')), inner_f)

    def testObjectListing(self):
        f2 = HBTreeFolder2('somefolder')
        self.f._setObject(f2.id, f2)
        # Hack in an absolute_url() method that works without context.
        self.f.absolute_url = str
        info = self.f.getBatchObjectListing()
        self.assertEqual(info['b_start'], 1)
        self.assertEqual(info['b_end'], 2)
        self.assertEqual(info['prev_batch_url'], '')
        self.assertEqual(info['next_batch_url'], '')
        self.assertTrue(info['formatted_list'].find('</select>') > 0)
        self.assertTrue(info['formatted_list'].find('item') > 0)
        self.assertTrue(info['formatted_list'].find('somefolder') > 0)

        # Ensure batching is working.
        info = self.f.getBatchObjectListing({'b_count': 1})
        self.assertEqual(info['b_start'], 1)
        self.assertEqual(info['b_end'], 1)
        self.assertEqual(info['prev_batch_url'], '')
        self.assertTrue(info['next_batch_url'] != '')
        self.assertTrue(info['formatted_list'].find('item') > 0)
        self.assertTrue(info['formatted_list'].find('somefolder') < 0)

        info = self.f.getBatchObjectListing({'b_start': 2})
        self.assertEqual(info['b_start'], 2)
        self.assertEqual(info['b_end'], 2)
        self.assertTrue(info['prev_batch_url'] != '')
        self.assertEqual(info['next_batch_url'], '')
        self.assertTrue(info['formatted_list'].find('item') < 0)
        self.assertTrue(info['formatted_list'].find('somefolder') > 0)

    def testObjectListingWithSpaces(self):
        # The option list must use value attributes to preserve spaces.
        name = " some folder "
        f2 = HBTreeFolder2(name)
        self.f._setObject(f2.id, f2)
        self.f.absolute_url = str
        info = self.f.getBatchObjectListing()
        expect = '<option value="%s">%s</option>' % (name, name)
        self.assertTrue(info['formatted_list'].find(expect) > 0)

    def testIterItems(self):
        h = HBTreeFolder2()
        id_list = ['a-b', 'a-cd',
                   'b',
                   'd-a-b', 'd-c-d', 'd-f-a',
                   'e-cd', 'e-f',
                   'f']
        for i in id_list:
          h._setOb(i, tuple(i))
        while 1:
          for min in (None, 'a', 'a-a', 'a-b',
                      'a-b-a', 'a-c', 'a-cd',
                      'a-cde', 'a-d', 'aa', 'b',
                      'b-c-d', 'c', 'd'):
            if min:
              m = min.split('-')
              for i, id in enumerate(id_list):
                if m <= id.split('-'):
                  break
              else:
                i += 1
            else:
              i = 0
            expected = [(i, tuple(i)) for i in id_list[i:]]
            self.assertEqual(expected, list(h._htree_iteritems(min)))
          if not id_list:
            break
          i = random.choice(id_list)
          id_list.remove(i)
          h._delOb(i)

    def testRestrictedIteration(self):
        """
        Check content iterators can be used by restricted python code.
        """
        # To let restricted python access methods on folder
        marker = object()
        saved_class_attributes = {}
        for method_id in ('objectIds', 'objectValues', 'objectItems'):
          roles_id = method_id + '__roles__'
          saved_class_attributes[roles_id] = getattr(HBTreeFolder2, roles_id,
            marker)
          setattr(HBTreeFolder2, roles_id, None)
        try:
          h = HBTreeFolder2()
          # whatever value, as long as it has an __of__
          h._setOb('foo', HBTreeFolder2())
          script = PythonScript('test_script')
          script.ZPythonScript_edit('h', dedent("""
            for dummy in h.objectIds():
              pass
            for dummy in h.objectValues():
              pass
            for dummy in h.objectItems():
              pass
          """))
          class DummyRequest(object):
            # To make Shared.DC.Scripts.Bindings.Bindings._getTraverseSubpath
            # happy
            other = {}
          script.REQUEST = DummyRequest
          script(h)
        finally:
          for roles_id, orig in six.iteritems(saved_class_attributes):
            if orig is marker:
              delattr(HBTreeFolder2, roles_id)
            else:
              setattr(HBTreeFolder2, roles_id, orig)

    @expectedFailure
    def _testPerformanceInDepth(self):
        """
        Check HBTreeFolder2 GET performance with the depth and the number of
        documents.
        """
        init_1 = dedent("""
        from Products.HBTreeFolder2.HBTreeFolder2 import HBTreeFolder2
        from Products.CMFDefault.File import File
        h_depth_1 = HBTreeFolder2()
        for i in xrange(%d):
            id = str(i)
            h_depth_1[id] = File(id)
        """)
        init_2 = dedent("""
        from Products.HBTreeFolder2.HBTreeFolder2 import HBTreeFolder2
        from Products.CMFDefault.File import File
        h_depth_2 = HBTreeFolder2()
        for i in xrange(10):
            for j in xrange(%d / 10):
                id = "-".join(map(str, (i,j)))
                h_depth_2[id] = File(id)
        """)
        init_3 = dedent("""
        from Products.HBTreeFolder2.HBTreeFolder2 import HBTreeFolder2
        from Products.CMFDefault.File import File
        h_depth_3 = HBTreeFolder2()
        for i in xrange(10):
            for j in xrange(10):
                for k in xrange(%d / (10 * 10)):
                    id = "-".join(map(str, (i, j, k)))
                    h_depth_3[id] = File(id)
        """)

        N = 1000
        # measure 100 times of each test with timeit()
        t1 = timeit.Timer("h_depth_1['555']", init_1 % N).timeit(100)
        t2 = timeit.Timer("h_depth_2['5-55']", init_2 % N).timeit(100)
        t3 = timeit.Timer("h_depth_3['5-5-5']", init_3 % N).timeit(100)
        ZopeTestCase._print("\nN = 1000\n")
        ZopeTestCase._print("L1=%s\tL2=%s\tL3=%s" % (t1, t2, t3))

        N = 10000 # The N is 10 times larger than the previous measurement
        t2_1 = timeit.Timer("h_depth_1['5555']", init_1 % N).timeit(100)
        t2_2 = timeit.Timer("h_depth_2['5-555']", init_2 % N).timeit(100)
        t2_3 = timeit.Timer("h_depth_3['5-5-55']", init_3 % N).timeit(100)
        ZopeTestCase._print("\nN = 10000\n")
        ZopeTestCase._print("L1'=%s\tL2'=%s\tL3'=%s" % (t2_1, t2_2, t2_3))

        N = 100000  # The N is 10 times larger than the pevious measurement
        t3_1 = timeit.Timer("h_depth_1['22222']", init_1 % N).timeit(100)
        t3_2 = timeit.Timer("h_depth_2['2-2222']", init_2 % N).timeit(100)
        t3_3 = timeit.Timer("h_depth_3['2-2-222']", init_3 % N).timeit(100)
        ZopeTestCase._print("\nN = 100000\n")
        ZopeTestCase._print("L1''=%s\tL2''=%s\tL3''=%s" % (t3_1, t3_2, t3_3))

        # These assert are should be True, but right now those are not passed

        # assert L2 is faster than L1, because the leaves are fewer than L1
        self.assertTrue(t1 > t2)
        self.assertTrue(t2_1 > t2_2)
        self.assertTrue(t3_1 > t3_2)

        # assert L3 is faster than L2, because the leaves are fewer than L1
        self.assertTrue(t2 > t3)
        self.assertTrue(t2_2 > t2_3)
        self.assertTrue(t3_2 > t3_3)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(HBTreeFolder2Tests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
