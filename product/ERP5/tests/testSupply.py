##############################################################################
# -*- coding: utf8 -*-
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
from DateTime import DateTime

class TestSupplyMixin:

  supply_portal_type = 'Sale Supply'
  supply_line_portal_type = 'Sale Supply Line'
  supply_cell_portal_type = 'Sale Supply Cell'

  def getBusinessTemplateList(self):
    """
      List of needed Business Templates
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_dummy_movement', 'erp5_trade',)

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

class TestSaleSupply(TestSupplyMixin, ERP5TypeTestCase):
  """
    Test Supplies usage
  """
  run_all_test = 1

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
    get_transaction().commit()
    self.tic()

    res = self.domain_tool.searchPredicateList(movement,
                                      portal_type=self.supply_line_portal_type)
    
    # ...and predicate shall be found
    self.assertSameSet(res, [supply_line])
    
    # timeframe is moved out of movement date...
    supply.edit(start_date_range_min='2009/02/01',
                start_date_range_max='2009/02/28')

    get_transaction().commit()
    self.tic()
    
    res = self.domain_tool.searchPredicateList(movement,
                                      portal_type=self.supply_line_portal_type)

    # ...and predicate shall NOT be found
    self.assertSameSet(res, [])

    # movement is going back into timeframe...
    movement.edit(start_date='2009/02/15')

    get_transaction().commit()
    self.tic()

    res = self.domain_tool.searchPredicateList(movement,
                                      portal_type=self.supply_line_portal_type)

    # ...and predicate shall be found
    self.assertSameSet(res, [supply_line])

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
    get_transaction().commit()
    self.tic()
    
    # ...and check supply line
    kw['predicate.uid'] = supply_line.getUid()
    result = self.catalog_tool(**kw)
    self.assertEquals(1, len(result) )
    result = result[0]
    self.assertEquals(result.start_date_range_min, new_date.toZone('UTC'))
    
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSaleSupply))
  suite.addTest(unittest.makeSuite(TestPurchaseSupply))
  return suite
