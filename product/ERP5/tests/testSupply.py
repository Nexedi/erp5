# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
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

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from Products.ERP5Type.tests.utils import SubcontentReindexingWrapper
from DateTime import DateTime

class TestSupplyMixin:
  def getBusinessTemplateList(self):
    """
      List of needed Business Templates
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_dummy_movement', 'erp5_trade')

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    self.category_tool = self.getCategoryTool()
    self.domain_tool = self.getDomainTool()
    self.catalog_tool = self.getCatalogTool()

    if not hasattr(self.portal, 'testing_folder'):
      self.portal.newContent(portal_type='Folder',
                            id='testing_folder')
    self.folder = self.portal.testing_folder

  def beforeTearDown(self):
    module = self.portal.getDefaultModule(self.supply_portal_type)
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

class TestSaleSupply(TestSupplyMixin, SubcontentReindexingWrapper,
    ERP5TypeTestCase):
  """
    Test Supplies usage
  """
  run_all_test = 1

  supply_portal_type = 'Sale Supply'
  supply_line_portal_type = 'Sale Supply Line'
  supply_cell_portal_type = 'Sale Supply Cell'
  generic_supply_line_portal_type = 'Supply Line'
  generic_supply_cell_portal_type = 'Supply Cell'
  predicate_portal_type = 'Predicate'

  def getTitle(self):
    return "Sale Supply"

  @reindex
  def _makeMovement(self, **kw):
    """Creates a movement.
    """
    mvt = self.folder.newContent(portal_type='Dummy Movement')
    mvt.edit(**kw)
    return mvt

  @reindex
  def _makeSupply(self, **kw):
    """Creates a supply.
    """
    supply = self.portal \
      .getDefaultModule(portal_type=self.supply_portal_type) \
      .newContent(portal_type=self.supply_portal_type)
    supply.edit(**kw)
    return supply

  @reindex
  def _makeSupplyLine(self, supply, **kw):
    """Creates a supply line.
    """
    supply_line = supply.newContent(portal_type=self.supply_line_portal_type)
    supply_line.edit(**kw)
    return supply_line

  @reindex
  def _makeSupplyCell(self, supply_line, **kw):
    """Creates a supply cell.
    """
    supply_cell = supply_line.newContent(portal_type=self.supply_cell_portal_type)
    supply_cell.edit(**kw)
    return supply_cell

  def test_01_MovementAndSupplyModification(self, quiet=0, run=run_all_test):
    """
      Check that moving timeframe of supply
      and then setting movement into that timeframe works.
    """
    if not run: return
    
    # movement is in middle of timeframe...
    movement = self._makeMovement(start_date='2009/01/15')

    supply = self._makeSupply(start_date_range_min='2009/01/01',
                              start_date_range_max='2009/01/31')

    supply_line = self._makeSupplyLine(supply)
    supply_cell = self._makeSupplyCell(supply_line)
    self.tic()

    res_line = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_line_portal_type)
    res_cell = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_cell_portal_type)

    # ...and predicate shall be found
    self.assertSameSet(res_line, [supply_line])
    self.assertSameSet(res_cell, [supply_cell])

    # timeframe is moved out of movement date...
    supply.edit(start_date_range_min='2009/02/01',
                start_date_range_max='2009/02/28')

    self.tic()

    res_line = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_line_portal_type)
    res_cell = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_cell_portal_type)

    # ...and predicate shall NOT be found
    self.assertSameSet(res_line, [])
    self.assertSameSet(res_cell, [])

    # movement is going back into timeframe...
    movement.edit(start_date='2009/02/15')

    self.tic()

    res_line = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_line_portal_type)
    res_cell = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_cell_portal_type)

    # ...and predicate shall be found
    self.assertSameSet(res_line, [supply_line])
    self.assertSameSet(res_cell, [supply_cell])

  def test_02_checkLineIsReindexedOnSupplyChange(self, quiet=0, run=run_all_test):
    """
      Check that Supply Line is properly reindexed (in predicate table)
      when date is change on Supply.
    """
    if not run: return
    
    original_date = DateTime().earliestTime() # lower precision of date
    new_date = DateTime(original_date + 10)

    self.assertNotEquals(original_date, new_date)

    supply = self._makeSupply(start_date_range_min=original_date)
    supply_line = self._makeSupplyLine(supply)

    kw = {}
    kw['predicate.uid'] = supply_line.getUid()
    kw['select_expression'] = 'predicate.start_date_range_min'

    # check supply line in predicate table
    result = self.catalog_tool(**kw)
    self.assertEquals(1, len(result) )
    result = result[0]
    self.assertEquals(result.start_date_range_min, original_date.toZone('UTC'))

    # set new date on supply...
    supply.edit(start_date_range_min=new_date)
    self.tic()
    
    # ...and check supply line
    kw['predicate.uid'] = supply_line.getUid()
    result = self.catalog_tool(**kw)
    self.assertEquals(1, len(result) )
    result = result[0]
    self.assertEquals(result.start_date_range_min, new_date.toZone('UTC'))


  def test_03_SupplyLineApplied(self, quiet=0, run=run_all_test):
    """
      Test supply line being found.
      XXX: This tests fails for second run due to bug #1248.
    """
    if not run: return

    portal = self.portal
    original_date = DateTime().earliestTime()

    supply = self._makeSupply(start_date_range_min=original_date)
    supply_line = self._makeSupplyLine(supply)
    self.tic()

    # create Sale Order and check Supply Line settings when 
    # a Resource is set on Sale Order Line
    product = portal.product_module.newContent(portal_type="Product",
                                               title = "Product 1")
    sale_order = portal.sale_order_module.newContent(portal_type = 'Sale Order',
                                                     start_date = DateTime())
    sale_order_line = sale_order.newContent(portal_type = 'Sale Order Line')
    sale_order_line.setResource(product.getRelativeUrl())
    self.tic()
    supply_line_list = self.domain_tool.searchPredicateList(sale_order,
                                      portal_type=self.supply_line_portal_type)
    self.assertSameSet([supply_line], supply_line_list)

  def test_sourceDestinationReferenceOnSupplyLine(self):
    """
      Check that it's possible to set and get a source/destination_reference on
      supply_line
    """
    supply = self._makeSupply(start_date_range_min=DateTime())
    supply_line = self._makeSupplyLine(supply)
    supply_line.setSourceReference('my_source_reference')
    self.assertEquals(supply_line.getSourceReference(), 'my_source_reference')
    supply_line.setDestinationReference('my_destination_reference')
    self.assertEquals(supply_line.getDestinationReference(), 'my_destination_reference')

  def test_subcontent_reindexing_supply(self):
    """Tests, that modification on Supply are propagated to children"""
    supply = self.portal.getDefaultModule(self.supply_portal_type).newContent(
                              portal_type=self.supply_portal_type)
    supply_line = supply.newContent(portal_type=self.supply_line_portal_type)
    supply_cell = supply_line.newContent(
        portal_type=self.supply_cell_portal_type)
    supply_line_predicate = supply_line.newContent(
        portal_type=self.predicate_portal_type)

    generic_supply_line = supply.newContent(
        portal_type=self.generic_supply_line_portal_type)
    generic_supply_cell = generic_supply_line.newContent(
        portal_type=self.generic_supply_cell_portal_type)
    generic_supply_predicate = generic_supply_line.newContent(
        portal_type=self.predicate_portal_type)

    self._testSubContentReindexing(supply, [supply_line, supply_cell,
      supply_line_predicate, generic_supply_line, generic_supply_cell, generic_supply_predicate])

  def test_subcontent_reindexing_supply_line(self):
    """Tests, that modification on Supply Line are propagated to children"""
    supply = self.portal.getDefaultModule(self.supply_portal_type).newContent(
                              portal_type=self.supply_portal_type)
    supply_line = supply.newContent(portal_type=self.supply_line_portal_type)
    supply_cell = supply_line.newContent(
        portal_type=self.supply_cell_portal_type)
    supply_line_predicate = supply_line.newContent(
        portal_type=self.predicate_portal_type)

    generic_supply_line = supply.newContent(
        portal_type=self.generic_supply_line_portal_type)
    generic_supply_cell = generic_supply_line.newContent(
        portal_type=self.generic_supply_cell_portal_type)
    generic_supply_predicate = generic_supply_line.newContent(
        portal_type=self.predicate_portal_type)

    self._testSubContentReindexing(supply_line, [supply_cell,
      supply_line_predicate])

    self._testSubContentReindexing(generic_supply_line, [generic_supply_cell,
      generic_supply_predicate])

  def testSupplyCellPropertyAndAccessor(self, quiet=0, run=run_all_test):
    """
      Check that getter/setter and get/setProperty methods works the same
      on supply cell. This test is added due to a bug introduced by revision
      39918 of ERP5/Document/MappedValue.py.
    """
    supply = self._makeSupply()
    supply_line = self._makeSupplyLine(supply)
    supply_cell = self._makeSupplyCell(supply_line)

    # User uses matrixbox to enter cells(variated data) and
    # it uses mapped value and setProperty method. Catalog uses
    # getter method to index cells.
    supply_cell.setMappedValuePropertyList(
      ['description', 'destination_reference'])

    # test description property
    self.assertEqual(supply_cell.getDescription(None), None)
    self.assertEqual(supply_cell.getProperty('description', None), None)
    supply_cell.setDescription('apple')
    self.assertEqual(supply_cell.getDescription(), 'apple')
    self.assertEqual(supply_cell.getProperty('description'), 'apple')
    supply_cell.setProperty('description', 'lemon')
    self.assertEqual(supply_cell.getDescription(), 'lemon')
    self.assertEqual(supply_cell.getProperty('description'), 'lemon')

    self.tic()

    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), description='apple')), 0)
    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), description='lemon')), 1)

    # test destination_reference property which defines storage_id on
    # property sheet
    self.assertEqual(supply_cell.getDestinationReference(None), None)
    self.assertEqual(supply_cell.getProperty('destination_reference', None), None)
    supply_cell.setDestinationReference('orange')
    self.assertEqual(supply_cell.getDestinationReference(), 'orange')
    self.assertEqual(supply_cell.getProperty('destination_reference'), 'orange')
    supply_cell.setProperty('destination_reference', 'banana')
    self.assertEqual(supply_cell.getDestinationReference(), 'banana')
    self.assertEqual(supply_cell.getProperty('destination_reference'), 'banana')

    self.tic()

    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), destination_reference='orange')), 0)
    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), destination_reference='banana')), 1)


class TestPurchaseSupply(TestSaleSupply):
  """
    Test Purchase Supplies usage
  """
  run_all_test = 1

  supply_portal_type = 'Purchase Supply'
  supply_line_portal_type = 'Purchase Supply Line'
  supply_cell_portal_type = 'Purchase Supply Cell'

  def getTitle(self):
    return "Purchase Supply"

class TestInternalSupply(TestSaleSupply):
  """
    Test Internal Supplies usage
  """
  run_all_test = 1

  supply_portal_type = 'Internal Supply'
  supply_line_portal_type = 'Internal Supply Line'
  supply_cell_portal_type = 'Internal Supply Cell'

  def getTitle(self):
    return "Internal Supply"

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSaleSupply))
  suite.addTest(unittest.makeSuite(TestPurchaseSupply))
  suite.addTest(unittest.makeSuite(TestInternalSupply))
  return suite
