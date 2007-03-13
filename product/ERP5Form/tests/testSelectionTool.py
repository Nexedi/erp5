##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kazuhiko <kazuhiko@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Testing import ZopeTestCase
from Products.ERP5Type.Utils import get_request
from Products.ERP5Form.Selection import Selection


class TestSelectionTool(ERP5TypeTestCase):
  quiet = 1
  run_all_test = 1
  
  def getTitle(self):
    return "SelectionTool"

  def getBusinessTemplateList(self):
    # Use the same framework as the functional testing for convenience.
    # This adds some specific portal types and skins.
    return ('erp5_ui_test',)

  def afterSetUp(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager', 'Assignor'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)
    self.portal_selections = self.getPortal().portal_selections
    self.portal_selections.setSelectionFor('test_selection', Selection())
    self.portal_selections.setSelectionParamsFor('test_selection', {'key':'value'})

  def testGetSelectionNames(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals(['test_selection'],
                      self.portal_selections.getSelectionNames())

  def testGetSelectionFor(self, quiet=quiet, run=run_all_test):
    if not run: return
    selection = self.portal_selections.getSelectionFor('test_selection')
    self.assert_(isinstance(selection, Selection))
    self.assertEquals('test_selection', selection.name)

  def testGetSelectionParamsFor(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals({'key':'value'},
                      self.portal_selections.getSelectionParamsFor('test_selection'))

  def testCallSelectionFor(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals(None,
                      self.portal_selections.callSelectionFor('not_found_selection'))
    # XXX more tests needed

  def testCheckedUids(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals([],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))
    self.portal_selections.setSelectionCheckedUidsFor('test_selection',
                                                      ['foo'])
    self.assertEquals(['foo'],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))
    self.portal_selections.updateSelectionCheckedUidList('test_selection',
                                                         ['foo'], ['bar'])
    self.assertEquals(['bar'],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))
    self.portal_selections.checkAll('test_selection',
                                    ['foo', 'baz'])
    self.assertEquals(sorted(['foo', 'bar', 'baz']),
                      sorted(self.portal_selections.getSelectionCheckedUidsFor('test_selection')))
    self.portal_selections.uncheckAll('test_selection',
                                    ['foo', 'bar'])
    self.assertEquals(['baz'],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))

  def testGetSelectionListUrlFor(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals('',
                      self.portal_selections.getSelectionListUrlFor('test_selection'))

  def testInvertMode(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.portal_selections.setSelectionInvertModeFor('test_selection', 1)
    self.assertEquals(1,
                      self.portal_selections.getSelectionInvertModeFor('test_selection'))
    self.assertEquals([],
                      self.portal_selections.getSelectionInvertModeUidListFor('test_selection'))

  def testSetSelectionToAll(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.portal_selections.checkAll('test_selection',
                                    ['foo', 'bar'])
    self.portal_selections.setSelectionToAll('test_selection')
    self.assertEquals(0,
                      self.portal_selections.getSelectionInvertModeFor('test_selection'))
    self.assertEquals({},
                      self.portal_selections.getSelectionParamsFor('test_selection'))
    self.assertEquals([],
                      self.portal_selections.getSelectionCheckedUidsFor('test_selection'))

  def testSortOrder(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.portal_selections.setSelectionSortOrder('test_selection',
                                                 [('title', 'ascending')])
    self.assertEquals([('title', 'ascending')],
                      self.portal_selections.getSelectionSortOrder('test_selection'))
    self.portal_selections.setSelectionQuickSortOrder('test_selection',
                                                      'title')
    self.assertEquals([('title', 'descending')],
                      self.portal_selections.getSelectionSortOrder('test_selection'))
    self.portal_selections.setSelectionQuickSortOrder('test_selection',
                                                      'date')
    self.assertEquals([('date', 'ascending')],
                      self.portal_selections.getSelectionSortOrder('test_selection'))

  def testColumns(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals([],
                      self.portal_selections.getSelectionColumns('test_selection'))
    self.assertEquals([('default_key', 'default_val')],
                      self.portal_selections.getSelectionColumns('test_selection', [('default_key', 'default_val')]))
    self.portal_selections.setSelectionColumns('test_selection',
                                                 [('key', 'val')])
    self.assertEquals([('key', 'val')],
                      self.portal_selections.getSelectionColumns('test_selection'))
    self.assertEquals([('key', 'val')],
                      self.portal_selections.getSelectionColumns('test_selection', [('default_key', 'default_val')]))

  def testStats(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals([' ', ' ', ' ', ' ', ' ', ' '],
                      self.portal_selections.getSelectionStats('test_selection'))
    self.portal_selections.setSelectionStats('test_selection',
                                                 [])
    self.assertEquals([],
                      self.portal_selections.getSelectionStats('test_selection'))

  def testView(self, quiet=quiet, run=run_all_test):
    if not run: return
    # XXX tests should be added

  def testPage(self, quiet=quiet, run=run_all_test):
    if not run: return
    # XXX tests should be added

  def testDomainSelection(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals('',
                      self.portal_selections.buildSQLJoinExpressionFromDomainSelection({}))
    self.assertEquals('',
                      self.portal_selections.buildSQLExpressionFromDomainSelection({}))
    from Products.ERP5Form.Selection import DomainSelection
    self.assertEquals('',
                      self.portal_selections.buildSQLJoinExpressionFromDomainSelection(DomainSelection({}).__of__(self.portal_selections)))
    category_tool = self.getCategoryTool()
    base = category_tool.newContent(portal_type = 'Base Category',
                                   id='test_base_cat')
    base_uid = base.getUid()
    self.assertEquals('category AS test_base_cat_category',
                      self.portal_selections.buildSQLJoinExpressionFromDomainSelection({'test_base_cat': ('portal_categories', 'test_base_cat')}))
    self.assertEquals('( catalog.uid = test_base_cat_category.uid AND (test_base_cat_category.category_uid = %d AND test_base_cat_category.base_category_uid = %d) )' % (base_uid, base_uid),
                      self.portal_selections.buildSQLExpressionFromDomainSelection({'test_base_cat': ('portal_categories', 'test_base_cat')}))
    test = base.newContent(portal_type = 'Category', id = 'test_cat')
    test_uid = test.getUid()
    self.assertEquals('category AS test_base_cat_category',
                      self.portal_selections.buildSQLJoinExpressionFromDomainSelection({'test_base_cat': ('portal_categories', 'test_base_cat/test_cat')}))
    self.assertEquals('( catalog.uid = test_base_cat_category.uid AND (test_base_cat_category.category_uid = %d AND test_base_cat_category.base_category_uid = %d) )' % (test_uid, base_uid),
                      self.portal_selections.buildSQLExpressionFromDomainSelection({'test_base_cat': ('portal_categories', 'test_base_cat/test_cat')}))
    self.assertEquals('( catalog.uid = test_base_cat_category.uid AND (test_base_cat_category.category_uid = %d AND test_base_cat_category.base_category_uid = %d AND test_base_cat_category.category_strict_membership = 1) )' % (test_uid, base_uid),
                      self.portal_selections.buildSQLExpressionFromDomainSelection({'test_base_cat': ('portal_categories', 'test_base_cat/test_cat')}, strict_membership = 1))

  def testDict(self, quiet=quiet, run=run_all_test):
    if not run: return
    self.assertEquals({},
                      self.portal_selections.getSelectionDomainDictFor('test_selection'))
    self.assertEquals({},
                      self.portal_selections.getSelectionReportDictFor('test_selection'))

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSelectionTool))
    return suite
