##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Yoshinori Okuji <yo@nexedi.com>
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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Utils import cartesianProduct
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestXMLMatrix(ERP5TypeTestCase):
  """
  Tests the Cell API
  """
  quiet = 1

  def getBusinessTemplateList(self):
    """
    Return the list of business templates.
    """
    return ('erp5_base', 'erp5_trade',)

  def getTitle(self):
    """
    Returns the title of the test
    """
    return "XMLMatrix"

  def afterSetUp(self, quiet=1, run=1):
    """
    Some pre-configuration
    """
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)
    portal = self.getPortal()
    module = portal.purchase_order_module
    if '1' not in module.objectIds():
      order = module.newContent(id='1', portal_type='Purchase Order')

  def test_01_RenameCellRange(self, quiet=quiet):
    """
    tests renameCellRange behaviour
    """
    if not quiet:
      ZopeTestCase._print('\nTest Rename Cell Range ')
    portal = self.getPortal()
    module = portal.purchase_order_module
    order = module._getOb('1')
    if order.hasContent('1'): order.deleteContent('1')
    matrix = order.newContent(id='1', portal_type='Purchase Order Line')

    cell_range = [['1', '2', '3'], ['a', 'b', 'c']]
    kwd = {'base_id' : 'quantity'}
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)

    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.newCell(portal_type="Purchase Order Cell",
                            *place, **kwd)
      cell.test_id = i
      i += 1

    cell_range = [['2', '3', '4'], ['b', 'c', 'd']]
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      self.assertNotEqual(cell, None)
      self.assertEqual(getattr(cell, 'test_id', None), i)
      i += 1

    cell_range = [['1', '2', '3', '4'], ['a', 'b', 'c', 'd']]
    value_list = (0, 1, 2, None, 3, 4, 5, None, 6, 7, 8, None, None, None, None, None)
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      if value_list[i] is None:
        self.assertEqual(cell, None)
      else:
        self.assertNotEqual(cell, None)
        self.assertEqual(getattr(cell, 'test_id', None), value_list[i])
      i += 1

    cell_range = [['1', '2'], ['a', 'b']]
    value_list = (0, 1, 3, 4)
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      self.assertNotEqual(cell, None)
      self.assertEqual(getattr(cell, 'test_id', None), value_list[i])
      i += 1

    cell_range = [['3'], ['a', 'b', 'c'], ['A', 'B', 'C']]
    value_list = (0, None, None, 1, None, None, None, None, None)
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      if value_list[i] is None:
        self.assertEqual(cell, None)
      else:
        self.assertNotEqual(cell, None)
        self.assertEqual(getattr(cell, 'test_id', None), value_list[i])
      i += 1

    cell_range = [['1', '2'], ['A', 'B']]
    value_list = (0, 1, None, None)
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      if value_list[i] is None:
        self.assertEqual(cell, None)
      else:
        self.assertNotEqual(cell, None)
        self.assertEqual(getattr(cell, 'test_id', None), value_list[i])
      i += 1

    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.newCell(portal_type="Purchase Order Cell",
                            *place, **kwd)
      cell.test_id = i
      i += 1

    cell_range = [['1', '2'], ['A', 'B'], ['a', 'b']]
    value_list = (0, None, 1, None, 2, None, 3, None)
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      if value_list[i] is None:
        self.assertEqual(cell, None)
      else:
        self.assertNotEqual(cell, None)
        self.assertEqual(getattr(cell, 'test_id', None), value_list[i])
      i += 1

  def checkSetCellRangeAndCatalog(self, active=1):
    """
    Tests if set Cell range do well catalog and uncatalog
    """
    portal = self.getPortal()
    module = portal.purchase_order_module
    if not active:
      # FIXME: deleting portal_activities prevent from running another test
      # after this one (because this methods commits the transaction)
      portal._delObject('portal_activities')
      module.recursiveImmediateReindexObject()
    else:
      module.recursiveReindexObject()
      get_transaction().commit()
      self.tic()
    catalog = portal.portal_catalog

    order = module._getOb('1')
    if order.hasContent('1'): order.deleteContent('1')
    matrix = order.newContent(id='1', portal_type='Purchase Order Line')
    url = matrix.getUrl()

    cell_range = [['1', '2', '3'], ['a', 'b', 'c']]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)

    for place in cartesianProduct(cell_range):
      cell = matrix.newCell(portal_type="Purchase Order Cell",
                            *place, **kwd)
    get_transaction().commit()
    self.tic()
    initial_cell_id_list = map(lambda x: x.getId(),matrix.objectValues())
    for id in initial_cell_id_list:
      cell_path = url + '/' + id
      self.assertEquals(catalog.hasPath(cell_path),True)

    cell_range = [['2', '3', '4'], ['b', 'c', 'd']]
    matrix.setCellRange(*cell_range, **kwd)
    # We must commit transaction in order to put cell reindexing in activity queue
    get_transaction().commit()
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    next_cell_id_list = map(lambda x: x.getId(),matrix.objectValues())
    LOG('checkSetCellRangeAndCatalog', 0, 'next_cell_id_list = %r, cell_range = %r' % (next_cell_id_list, cell_range))
    removed_id_list = filter(lambda x: x not in next_cell_id_list,initial_cell_id_list)
    self.tic()
    for id in next_cell_id_list:
      cell_path = url + '/' + id
      self.assertEquals(catalog.hasPath(cell_path),True)
    for id in removed_id_list:
      cell_path = url + '/' + id
      self.assertEquals(catalog.hasPath(cell_path),False)

    cell_range = [['0', '1'], ['a','b']]
    matrix.setCellRange(*cell_range, **kwd)
    get_transaction().commit()
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    next2_cell_id_list = map(lambda x: x.getId(),matrix.objectValues())
    removed_id_list = filter(lambda x: x not in next2_cell_id_list,next_cell_id_list)
    self.tic()
    for id in next2_cell_id_list:
      cell_path = url + '/' + id
      self.assertEquals(catalog.hasPath(cell_path),True)
    for id in removed_id_list:
      cell_path = url + '/' + id
      self.assertEquals(catalog.hasPath(cell_path),False)

    cell_range = [['0', '1'], ['a','b']]
    kwd = {'base_id' : 'movement'}
    matrix.setCellRange(*cell_range, **kwd)
    get_transaction().commit()
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)
    self.tic()
    for id in next2_cell_id_list:
      cell_path = url + '/' + id
      self.assertEquals(catalog.hasPath(cell_path),False)

  def test_02_SetCellRangeAndCatalogWithActivities(self, quiet=quiet):
    """
    Tests if set Cell range do well catalog and uncatalog, using activities
    """
    if not quiet:
      ZopeTestCase._print('\nTest Set Cell Range And Catalog With Activities ')
    self.checkSetCellRangeAndCatalog(active=1)

  

  def test_9999_SetCellRangeAndCatalogWithoutActivities(self, quiet=quiet):
    """
    Tests if set Cell range do well catalog and uncatalog, not using
    activities.
    WARNING this test removes activity tool from the test environment. All
    tests after this one will have no activity tool.
    """
    if not quiet:
      ZopeTestCase._print('\nTest Set Cell Range And Catalog Without Activities ')
    self.checkSetCellRangeAndCatalog(active=0)
  

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestXMLMatrix))
  return suite
