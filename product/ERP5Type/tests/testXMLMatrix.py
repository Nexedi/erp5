#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5Type.Utils import cartesianProduct
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager

class TestXMLMatrix(ERP5TypeTestCase):

  # Some helper methods

  #def afterSetUp(self):

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.
    """
    return ('erp5_common', 'erp5_delivery')

  def afterSetUp(self, quiet=1, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('manager', '', ['Manager'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)
    portal = self.getPortal()
    portal.portal_types.constructContent(type_name='Purchase Order Module',
                                         container=portal,
                                         id='purchase_order')
    module = portal.purchase_order
    order = module.newContent(id='1', portal_type='Purchase Order')

  def testRenameCellRange(self):
    # Test if renameCellRange works in XMLMatrix.
    portal = self.getPortal()
    module = portal.purchase_order
    order = module._getOb('1')
    if order.hasContent('1'): order.deleteContent('1')
    matrix = order.newContent(id='1', portal_type='Purchase Order Line')

    cell_range = [['1', '2', '3'], ['a', 'b', 'c']]
    kwd = {'base_id' : 'quantity'}
    matrix.renameCellRange(*cell_range, **kwd)
    self.assertEqual(matrix.getCellRange(**kwd), cell_range)

    i = 0
    for place in cartesianProduct(cell_range):
      cell = matrix.newCell(*place, **kwd)
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
      cell = matrix.newCell(*place, **kwd)
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


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestXMLMatrix))
        return suite
