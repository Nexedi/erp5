##############################################################################
#
# Copyright (c) 2007-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Kazuhiko <kazuhiko@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import contextlib
import unittest
from threading import Thread
from six.moves._thread import get_ident
from unittest import skip

import transaction
import ZODB

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.ERP5Form.Selection import Selection
from Products.ERP5Form.Tool.SelectionTool import SelectionTool

class TestSelectionTool(ERP5TypeTestCase):

  def getTitle(self):
    return "SelectionTool"

  def getBusinessTemplateList(self):
    return tuple()

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager', 'Assignor'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)
    self.portal_selections = self.getPortal().portal_selections
    name = 'test_selection'
    self.portal_selections.setSelectionFor(name, Selection(name))
    self.portal_selections.setSelectionParamsFor('test_selection', {'key':'value'})

  def testGetSelectionContainer(self):
    self.assertEqual(['test_selection'],
                      self.portal_selections.getSelectionNameList())
    self.assertEqual(['test_selection'],
                      self.portal_selections.getSelectionNames())
    self.assertTrue(self.portal_selections._getContainer() is not None)
    self.assertTrue(getattr(self.portal_selections, 'selection_data', None)
                 is not None)
    self.assertTrue(getattr(self.portal_selections, '_v_selection_container', None)
                 is not None)

  def testGetSelectionFor(self):
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assertTrue(isinstance(selection, Selection))
    self.assertEqual('test_selection', selection.name)

  def testGetSelectionParamsFor(self):
    self.assertEqual({'key':'value', 'ignore_unknown_columns': True},
                      self.portal_selections.getSelectionParamsFor('test_selection'))

  def testGetSelectionParamsDictInterface(self):
    self.assertEqual('value',
                      self.portal_selections['test_selection']['key'])
    # the main use case is to have a dict interface in TALES expressions:
    from Products.PageTemplates.Expressions import getEngine
    evaluate_tales = getEngine().getContext(dict(context=self.portal)).evaluate
    self.assertEqual('value',
            evaluate_tales('context/portal_selections/test_selection/key'))
    self.assertEqual('default', evaluate_tales(
      'context/portal_selections/test_selection/not_found | string:default'))


  @skip('Test to be written')
  def testCallSelectionFor(self):
    self.assertEqual(None,
                      self.portal_selections.callSelectionFor('not_found_selection'))
    raise NotImplementedError('more tests needed')

  def testCheckedUids(self):
    self.assertEqual([],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))
    self.portal_selections.setSelectionCheckedUidsFor('test_selection',
                                                      ['foo'])
    self.assertEqual(['foo'],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))
    self.portal_selections.updateSelectionCheckedUidList('test_selection',
                                                         ['foo'], ['bar'])
    self.assertEqual(['bar'],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))
    self.portal_selections.checkAll('test_selection',
                                    ['foo', 'baz'])
    self.assertEqual(sorted(['foo', 'bar', 'baz']),
                      sorted(self.portal_selections.getSelectionCheckedUidsFor('test_selection')))
    self.portal_selections.uncheckAll('test_selection',
                                    ['foo', 'bar'])
    self.assertEqual(['baz'],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))

  def testGetSelectionListUrlFor(self):
    self.assertEqual('',
                      self.portal_selections.getSelectionListUrlFor('test_selection'))

  def testInvertMode(self):
    self.portal_selections.setSelectionInvertModeFor('test_selection', 1)
    self.assertEqual(1,
                      self.portal_selections.getSelectionInvertModeFor('test_selection'))
    self.assertEqual([],
                      self.portal_selections.getSelectionInvertModeUidListFor('test_selection'))

  def testSetSelectionToAll(self):
    self.portal_selections.checkAll('test_selection',
                                    ['foo', 'bar'])
    self.portal_selections.setSelectionToAll('test_selection')
    self.assertEqual(0,
                      self.portal_selections.getSelectionInvertModeFor('test_selection'))
    self.assertEqual({},
                      self.portal_selections.getSelectionParamsFor('test_selection'))
    self.assertEqual([],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))

  def testSortOrder(self):
    self.portal_selections.setSelectionSortOrder('test_selection',
                                                 [('title', 'ascending')])
    self.assertSequenceEqual([('title', 'ascending')],
                      self.portal_selections.getSelectionSortOrder('test_selection'))
    self.portal_selections.setSelectionQuickSortOrder('test_selection',
                                                      'title')
    self.assertSequenceEqual([('title', 'descending')],
                      self.portal_selections.getSelectionSortOrder('test_selection'))
    self.portal_selections.setSelectionQuickSortOrder('test_selection',
                                                      'date')
    self.assertSequenceEqual([('date', 'ascending')],
                      self.portal_selections.getSelectionSortOrder('test_selection'))

  def testColumns(self):
    self.assertEqual([],
                      self.portal_selections.getSelectionColumns('test_selection'))
    self.assertEqual([('default_key', 'default_val')],
                      self.portal_selections.getSelectionColumns('test_selection', [('default_key', 'default_val')]))
    self.portal_selections.setSelectionColumns('test_selection',
                                                 [('key', 'val')])
    self.assertEqual([('key', 'val')],
                      self.portal_selections.getSelectionColumns('test_selection'))
    self.assertEqual([('key', 'val')],
                      self.portal_selections.getSelectionColumns('test_selection', [('default_key', 'default_val')]))

  def testStats(self):
    self.assertEqual([' ', ' ', ' ', ' ', ' ', ' '],
                      self.portal_selections.getSelectionStats('test_selection'))
    self.portal_selections.setSelectionStats('test_selection',
                                                 [])
    self.assertEqual([],
                      self.portal_selections.getSelectionStats('test_selection'))

  @skip('Test to be written')
  def testView(self):
    raise NotImplementedError('test should be added')

  @skip('Test to be written')
  def testPage(self):
    raise NotImplementedError('test should be added')

  def testDict(self):
    self.assertEqual({},
                      self.portal_selections.getSelectionDomainDictFor('test_selection'))
    self.assertEqual({},
                      self.portal_selections.getSelectionReportDictFor('test_selection'))

  def testIndex(self):
    self.assertEqual(None,
                      self.portal_selections.getSelectionIndexFor('test_selection'))

  def testDeleteSelection(self):
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assertTrue(isinstance(selection, Selection))
    self.portal_selections.manage_deleteSelection('test_selection')
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assertEqual(selection, None)

  def testDeleteSelectionForUser(self):
    # XXX: There is side effect, that manager, running user, is the same use
    #      and there is no way (for now) to get selections per user...
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assertTrue(isinstance(selection, Selection))
    self.portal_selections.manage_deleteSelectionForUser('test_selection',
        'manager')
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assertEqual(selection, None)

  def testDeleteGlobalSelection(self):
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assertTrue(isinstance(selection, Selection))
    self.portal_selections.manage_deleteGlobalSelection('test_selection')
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assertEqual(selection, None)

class TestSelectionPersistence(unittest.TestCase):
  """SelectionTool tests that needs a "real" FileStorage to make sure selection
  are really persistent and supports conflict resolution.
  """
  def setUp(self):
    # patch selection tool class so that we don't need a portal_membership to
    # find the current user name
    SelectionTool._getUserId_saved = SelectionTool._getUserId
    SelectionTool._getUserId = lambda self: 'user'
    SelectionTool.isAnonymous = lambda self: 0

    self.db = ZODB.DB(ZODB.DemoStorage.DemoStorage())
    self.cnx = self.db.open()
    self.portal_selections = \
      self.cnx.root().portal_selections = SelectionTool()
    name = 'test_selection'
    self.portal_selections.setSelectionFor(name, Selection(name))
    transaction.commit()

  def tearDown(self):
    # revert the patch from setUp
    SelectionTool._getUserId = SelectionTool._getUserId_saved
    self.cnx.close()
    self.db.close()

  def _runWithAnotherConnection(self, thread_func):
    """runs `thread_func` with another ZODB connection

    thread_func must be a callable accepting the connection factory as only
    argument.
    """
    t = Thread(target=thread_func, args=(self.db.open,))
    t.start()
    t.join(60)
    self.assertFalse(t.isAlive())

  def testSelectionParamConflictResolution(self):
    # same user edits the same selection with two different parameters
    self.portal_selections.setSelectionParamsFor(
                       'test_selection', dict(a="b"))
    def thread_func(cnx_factory):
      with contextlib.closing(cnx_factory()) as cnx:
        portal_selections = cnx.root().portal_selections
        portal_selections.setSelectionParamsFor(
                              'test_selection', dict(a="c"))
        transaction.commit()

    self._runWithAnotherConnection(thread_func)

    # This would raise a ConflictError without conflict resolution code
    transaction.commit()
    params = self.portal_selections.getSelectionParamsFor('test_selection')
    self.assertTrue(params.get('a'))

  def testSelectionNameConflictResolution(self):
    # same user edits two different selections
    self.portal_selections.setSelectionParamsFor(
                       'test_selection2', dict(a="b"))
    def thread_func(cnx_factory):
      with contextlib.closing(cnx_factory()) as cnx:
        portal_selections = cnx.root().portal_selections
        portal_selections.setSelectionParamsFor(
                       'test_selection1', dict(a="b"))
        transaction.commit()

    self._runWithAnotherConnection(thread_func)

    # This would raise a ConflictError without conflict resolution code
    transaction.commit()
    params = self.portal_selections.getSelectionParamsFor('test_selection1')
    self.assertEqual(params.get('a'), 'b')
    params = self.portal_selections.getSelectionParamsFor('test_selection2')
    self.assertEqual(params.get('a'), 'b')

  def testDifferentUsernameConflictResolution(self):
    # different users edits selections
    SelectionTool._getUserId = lambda self: 'user-%s' % get_ident()
    # Note that in current implementation, the first time we initialized a
    # selection for a user the mapping user -> selections is modified, which
    # will generate a conflict if we have two new users at the same time.
    # This test just checks that once we have initialized a user it doesn't
    # generate conflicts when another users also modifies it owns selection.
    # So we make sure that selection container is initialized for this user
    self.portal_selections.setSelectionParamsFor(
                       'test_selection', dict(initialized="1"))
    transaction.commit()

    self.portal_selections.setSelectionParamsFor(
                       'test_selection', dict(a="b"))
    def thread_func(cnx_factory):
      with contextlib.closing(cnx_factory()) as cnx:
        portal_selections = cnx.root().portal_selections
        portal_selections.setSelectionParamsFor(
                       'test_selection', dict(a="b"))
        transaction.commit()
    self._runWithAnotherConnection(thread_func)

    transaction.commit()
    # this check is quite low level.
    # we know that setUp stored one selection, and each of our 2 threads stored
    # one selection.
    self.assertEqual(3, len(self.portal_selections.selection_data.keys()))

  def testPersistentSelections(self):
    # test that selection parameters are persistent
    self.portal_selections.setSelectionParamsFor(
                 'test_selection', dict(key="saved_value"))
    transaction.commit()
    self.cnx.close()

    self.cnx = self.db.open()
    portal_selections = self.cnx.root().portal_selections
    self.assertEqual('saved_value',
        portal_selections.getSelectionParamsFor('test_selection').get('key'))

# pylint: disable=abstract-method
class TestSelectionToolMemcachedStorage(TestSelectionTool):

  def getTitle(self):
    return "SelectionTool with Memcached Storage"

  def afterSetUp(self):
    # create a Memcached Plugin
    memcached_tool = self.getPortal().portal_memcached
    if getattr(memcached_tool, 'default_memcached_plugin', None) is None:
      memcached_tool.newContent(id='default_memcached_plugin',
                                portal_type='Memcached Plugin',
                                int_index=0,
                                url_string='127.0.0.1:11211')
    self.portal.portal_selections.setStorage('portal_memcached/default_memcached_plugin')
    TestSelectionTool.afterSetUp(self)

  def testGetSelectionContainer(self):
    self.assertEqual([],
                      self.portal_selections.getSelectionNameList())
    self.assertEqual([],
                      self.portal_selections.getSelectionNames())
    self.assertTrue(self.portal_selections._getContainer() is not None)
    self.assertTrue(getattr(self.portal_selections, '_v_selection_container', None)
                 is not None)

  @skip('To be decided if implementation is required')
  def testDeleteGlobalSelection(self):
    pass

  def testChangeSelectionToolContainer(self):
    """
    After changing SelectionTool container, the new one should be used
    straightaway, and more specifically volatile variables should have
    been reset
    """
    from Products.ERP5Form.Tool.SelectionTool import (MemcachedContainer,
                                                      PersistentMappingContainer)

    # testGetSelectionFor() already checked if the Selection can be retrieved
    # from the container set in afterSetUp(), so no need to check again here
    self.portal_selections.setStorage('selection_data')
    transaction.commit()

    self.assertEqual(getattr(self.portal_selections, '_v_selection_container',
                             None), None)

    self.assertEqual(self.portal_selections.getSelectionFor('test_selection'),
                     None)

    self.assertTrue(isinstance(getattr(self.portal_selections,
                                       '_v_selection_container', None),
                                PersistentMappingContainer))


    self.portal_selections.setStorage('portal_memcached/default_memcached_plugin')
    transaction.commit()

    self.assertEqual(getattr(self.portal_selections, '_v_selection_container',
                             None), None)

    self.assertNotEqual(self.portal_selections.getSelectionFor('test_selection'),
                        None)

    self.assertTrue(isinstance(getattr(self.portal_selections,
                                       '_v_selection_container', None),
                               MemcachedContainer))

  def testChangeMemcached(self):
    """
    After Memcached has been changed, the new setting should be used and more
    specifically container volative variables should have been reset
    """
    self.assertNotEqual(self.portal_selections.getSelectionFor('test_selection'),
                        None)

    memcached_plugin = self.portal.portal_memcached.default_memcached_plugin
    url_string_before = memcached_plugin.getUrlString()

    memcached_plugin.setUrlString('127.0.0.1:4242')
    transaction.commit()

    try:
      self.assertEqual(getattr(self.portal_selections, '_v_selection_container',
                               None), None)

      self.assertEqual(self.portal_selections.getSelectionFor('test_selection'),
                       None)

      self.assertNotEqual(getattr(self.portal_selections, '_v_selection_container',
                                  None), None)
    finally:
      memcached_plugin.setUrlString(url_string_before)
      transaction.commit()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSelectionTool))
  suite.addTest(unittest.makeSuite(TestSelectionToolMemcachedStorage))
  suite.addTest(unittest.makeSuite(TestSelectionPersistence))
  return suite
