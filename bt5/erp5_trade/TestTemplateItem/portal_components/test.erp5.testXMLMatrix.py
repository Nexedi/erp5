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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import LogInterceptor
from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5Type.XMLMatrix import XMLMatrix
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import PROBLEM


class TestXMLMatrix(ERP5TypeTestCase, LogInterceptor):
  """
  Tests the Cell API
  """
  def getBusinessTemplateList(self):
    """
    Return the list of business templates.
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade',)

  def getTitle(self):
    """
    Returns the title of the test
    """
    return "XMLMatrix"

  def afterSetUp(self):
    """
    Some pre-configuration
    """
    uf = self.portal.acl_users
    uf._doAddUser('manager', '', ['Manager'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)
    module = self.portal.purchase_order_module
    order = module.newContent(portal_type='Purchase Order')
    self.matrix = order.newContent(portal_type='Purchase Order Line')
    self._catch_log_errors(ignored_level=PROBLEM)

  portal_activities_backup = None

  def beforeTearDown(self):
    self._ignore_log_errors()
    if self.portal_activities_backup is not None:
      self.portal._setObject('portal_activities',
                             self.portal_activities_backup)
      self.commit()
      del self.portal_activities_backup
    return super(TestXMLMatrix, self).beforeTearDown()


  def test_01_RenameCellRange(self):
    """
    tests renameCellRange behaviour
    """
    matrix = self.matrix

    cell_range = [['1', '2', '3'], ['a', 'b', 'c']]
    kwd = {'base_id' : 'quantity'}
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))

    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.newCell(portal_type="Purchase Order Cell",
                            *place, **kwd)
      cell.test_id = i
      i += 1

    cell_range = [['2', '3', '4'], ['b', 'c', 'd']]
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      self.assertNotEqual(cell, None)
      self.assertEqual(getattr(cell, 'test_id', None), i)
      i += 1

    cell_range = [['1', '2', '3', '4'], ['a', 'b', 'c', 'd']]
    value_list = (0, 1, 2, None, 3, 4, 5, None, 6, 7, 8, None, None, None, None, None)
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
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
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      self.assertNotEqual(cell, None)
      self.assertEqual(getattr(cell, 'test_id', None), value_list[i])
      i += 1

    cell_range = [['3'], ['a', 'b', 'c'], ['A', 'B', 'C']]
    value_list = (0, None, None, 1, None, None, None, None, None)
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
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
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
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
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.getCell(*place, **kwd)
      if value_list[i] is None:
        self.assertEqual(cell, None)
      else:
        self.assertNotEqual(cell, None)
        self.assertEqual(getattr(cell, 'test_id', None), value_list[i])
      i += 1

    # now commit transaction to make sure there are no activities for cells
    # that no longer exists.
    self.tic()

  def test_02_SetCellRangeAndCatalogWithActivities(self):
    """
    Tests if set Cell range do well catalog and uncatalog
    """
    portal = self.portal
    catalog = portal.portal_catalog

    matrix = self.matrix
    url = matrix.getUrl()

    cell_range = [['1', '2', '3'], ['a', 'b', 'c']]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))

    for place in cartesianProduct(cell_range):
      matrix.newCell(portal_type="Purchase Order Cell",
                            *place, **kwd)
    self.tic()
    initial_cell_id_list = list(matrix.objectIds())
    for id_ in initial_cell_id_list:
      self.assertTrue(catalog.hasPath(url + '/' + id_))

    cell_range = [['2', '3', '4'], ['b', 'c', 'd']]
    matrix.setCellRange(*cell_range, **kwd)
    # We must commit transaction in order to put cell reindexing in activity queue
    self.commit()
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    next_cell_id_list = list(matrix.objectIds())
    # the cells on coordinates 2b, 3b, 3b and 3c are kept
    self.assertEqual(4, len(next_cell_id_list))
    for coord in [['2', 'b'],
                  ['2', 'c'],
                  ['3', 'b'],
                  ['3', 'c']]:
      self.assertNotEqual(None, matrix.getCell(*coord, **kwd))

    removed_id_list = [x for x in initial_cell_id_list if x not in next_cell_id_list]
    self.tic()
    for id_ in next_cell_id_list:
      self.assertTrue(catalog.hasPath(url + '/' + id_))
    for id_ in removed_id_list:
      self.assertFalse(catalog.hasPath(url + '/' + id_))

    cell_range = [['0', '1'], ['a','b']]
    matrix.setCellRange(*cell_range, **kwd)
    self.commit()
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    next2_cell_id_list = list(matrix.objectIds())
    removed_id_list = [x for x in next_cell_id_list if x not in next2_cell_id_list]
    self.tic()
    for id_ in next2_cell_id_list:
      self.assertTrue(catalog.hasPath(url + '/' + id_))
    for id_ in removed_id_list:
      self.assertFalse(catalog.hasPath(url + '/' + id_))

    cell_range = [['0', '1'], ['a','b']]
    kwd = {'base_id' : 'movement'}
    matrix.setCellRange(*cell_range, **kwd)
    self.commit()
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    self.tic()
    for id_ in next2_cell_id_list:
      self.assertFalse(catalog.hasPath(url + '/' + id_))

    # create some cells
    cell1 = matrix.newCell(*['0', 'a'], **kwd)
    cell1_path = cell1.getPath()
    cell2 = matrix.newCell(*['1', 'a'], **kwd)
    cell2_path = cell2.getPath()
    self.commit()

    # if we keep the same range, nothing happens
    matrix.setCellRange(*cell_range, **kwd)
    self.commit()
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    self.assertEqual(len(matrix.getCellValueList(**kwd)), 2)
    self.tic()

    self.assertTrue(catalog.hasPath(matrix.getPath()))
    self.assertTrue(catalog.hasPath(cell1_path))
    self.assertTrue(catalog.hasPath(cell2_path))

    # now set other ranges
    cell_range = [['0', '2'], ['a', ], ['Z']]
    matrix.setCellRange(*cell_range, **kwd)
    self.commit()
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    self.tic()

    # in this case, cells has been removed
    self.assertEqual(matrix.getCellValueList(**kwd), [])

    self.assertTrue(catalog.hasPath(matrix.getPath()))
    self.assertFalse(catalog.hasPath(cell1_path))
    self.assertFalse(catalog.hasPath(cell2_path))

    # create cells in this new range
    cell1 = matrix.newCell(*['0', 'a', 'Z'], **kwd)
    cell1_path = cell1.getPath()
    cell2 = matrix.newCell(*['2', 'a', 'Z'], **kwd)
    cell2_path = cell2.getPath()
    self.commit()

    cell_range = [['1', '2'], ['a', ], ['X']]
    matrix.setCellRange(*cell_range, **kwd)
    self.commit()
    self.assertEqual(list(map(set, matrix.getCellRange(**kwd))), list(map(set, cell_range)))
    self.tic()

    # in this case, cells has been removed
    self.assertEqual(matrix.getCellValueList(**kwd), [])

    self.assertTrue(catalog.hasPath(matrix.getPath()))
    self.assertFalse(catalog.hasPath(cell1_path))
    self.assertFalse(catalog.hasPath(cell2_path))

  def test_add_dimension(self):
    matrix = self.matrix

    cell_range = [['1', ]]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)

    matrix.newCell(*['1',], **kwd)
    self.tic()

    cell_range = [['1', ], ['a', ]]
    matrix.setCellRange(*cell_range, **kwd)
    self.assertEqual(0, len(matrix.getCellValueList(**kwd)))
    matrix.newCell(*['1', 'a'], **kwd)
    self.tic()

  def test_del_dimension(self):
    matrix = self.matrix

    cell_range = [['1', ], ['a', ]]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)

    for place in cartesianProduct(cell_range):
      matrix.newCell(*place, **kwd)
    self.tic()

    cell_range = [['1', ]]
    matrix.setCellRange(*cell_range, **kwd)
    self.assertEqual(0, len(matrix.getCellValueList(**kwd)))
    self.tic()

  def test_increase_dimension(self):
    matrix = self.matrix

    cell_range = [['1', ], ['a', ]]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)

    for place in cartesianProduct(cell_range):
      matrix.newCell(*place, **kwd)
    cell = matrix.getCell(*['1', 'a'], **kwd)
    self.tic()

    cell_range = [['1', '2', ], ['a']]
    matrix.setCellRange(*cell_range, **kwd)
    self.assertEqual(1, len(matrix.getCellValueList(**kwd)))
    # previous cell is kept
    self.assertEqual(cell, matrix.getCell(*['1', 'a'], **kwd))
    self.tic()
    # the cell is still in catalog
    self.assertEqual(cell,
        self.portal.portal_catalog.getObject(cell.getUid()))

  def test_decrease_dimension(self):
    matrix = self.matrix

    cell_range = [['1', '2'], ['a', ]]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)

    for place in cartesianProduct(cell_range):
      matrix.newCell(*place, **kwd)
    cell = matrix.getCell(*['1', 'a'], **kwd)
    self.tic()

    cell_range = [['1', ], ['a']]
    matrix.setCellRange(*cell_range, **kwd)
    self.assertEqual(1, len(matrix.getCellValueList(**kwd)))
    # previous cell is kept
    self.assertEqual(cell, matrix.getCell(*['1', 'a'], **kwd))
    self.tic()
    # the cell is still in catalog
    self.assertEqual(cell,
        self.portal.portal_catalog.getObject(cell.getUid()))

  def test_decrease_and_increase_dimension(self):
    matrix = self.matrix

    cell_range = [['1', '2'], ['a', ]]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)

    for place in cartesianProduct(cell_range):
      matrix.newCell(*place, **kwd)
    cell = matrix.getCell(*['1', 'a'], **kwd)
    self.tic()

    cell_range = [['1', ], ['a', 'b']]
    matrix.setCellRange(*cell_range, **kwd)
    self.assertEqual(1, len(matrix.getCellValueList(**kwd)))
    # previous cell is kept
    self.assertEqual(cell, matrix.getCell(*['1', 'a'], **kwd))
    self.tic()
    # the cell is still in catalog
    self.assertEqual(cell,
        self.portal.portal_catalog.getObject(cell.getUid()))

  def test_change_dimension_cell_change_id(self):
    # The dimension change, a cell is kept, but receives a new ID because its
    # coordinate changes
    matrix = self.matrix

    cell_range = [['1', '2',], ['a', 'b',]]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)

    for place in cartesianProduct(cell_range):
      matrix.newCell(*place, **kwd)

    cell = matrix.getCell('2', 'b', **kwd)
    self.assertEqual('quantity_1_1', cell.getId())
    cell.setTitle('This one')
    self.tic()

    cell_range = [['2', '3', ], ['b', 'c',]]
    matrix.setCellRange(*cell_range, **kwd)
    self.commit()
    self.assertNotIn('quantity_0_1', matrix.objectIds())

    cell = matrix.getCell('2', 'b', **kwd)
    self.assertEqual('quantity_1_1', cell.getId())
    self.assertEqual('This one', cell.getTitle())

    self.tic()

    # the cell is still in catalog
    self.assertEqual(cell,
        self.portal.portal_catalog.getObject(cell.getUid()))

  def test_change_dimension_and_check_consistency(self):
    # make sure _checkConsistency does not complain about a cell
    # having an id outside the len of the dimension after a dimension
    # change if id is within acceptable values
    matrix = self.matrix

    cell_range = [['1', '2',], ['a', 'b',]]
    kwd = {'base_id' : 'quantity'}
    matrix.setCellRange(*cell_range, **kwd)

    for place in cartesianProduct(cell_range):
      matrix.newCell(*place, **kwd)

    cell = matrix.getCell('2', 'b', **kwd)
    self.assertEqual('quantity_1_1', cell.getId())
    cell.setTitle('This one')
    self.tic()

    cell_range = [['2', ], ['b',]]
    matrix.setCellRange(*cell_range, **kwd)
    self.tic()
    self.assertEqual(set(["quantity_1_1"]), set([
      x.getId() for x in matrix.objectValues()]))

    cell = matrix.getCell('2', 'b', **kwd)
    self.assertEqual('quantity_1_1', cell.getId())
    self.assertEqual('This one', cell.getTitle())

    self.assertEqual(XMLMatrix._checkConsistency(matrix), [])
    cell.setId('quantity_2_1')
    error_list = XMLMatrix._checkConsistency(matrix)
    self.assertEqual(1, len(error_list))
    self.assertTrue(error_list[0][3].find("is out of bound") > 0)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestXMLMatrix))
  return suite
