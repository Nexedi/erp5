# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi KK, Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import unittest
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.CMFCore.exceptions import AccessControl_Unauthorized


class TestPDMWithSecurity(ERP5TypeTestCase):
  """
  Test PDM with Security
  """

  def getTitle(self):
    return 'Test PDM with Security'

  def getBusinessTemplateList(self):

    return ('erp5_base',
            'erp5_pdm',
            )

  def afterSetUp(self):
    if getattr(self.portal, '_run_after_setup', None) is not None:
      return


    self.portal._run_after_setup = True

    user_folder = self.getPortal().acl_users
    user_folder._doAddUser('author', '', ['Auditor', 'Author'], [])
    user_folder._doAddUser('assignor', '', ['Auditor', 'Author', 'Assignor'], [])
    user_folder._doAddUser('assignee', '', ['Auditor', 'Author', 'Assignee'], [])

    self.tic()

  def testValidatedProductCanContainMeasure(self):
    """
    Make sure that validated product can contain measure.
    """
    self.loginByUserName('author')
    product = self.portal.product_module.newContent(portal_type='Product',
                                                    title='Chair')

    self.tic()

    # Author try to add a measure to validated product and succeed.
    product.newContent(portal_type='Measure')

    self.tic()

    self.assertEqual(len(product.contentValues(portal_type='Measure')), 1)

    self.loginByUserName('assignor')
    self.portal.portal_workflow.doActionFor(product, 'validate_action')

    self.tic()

    self.assertEqual(product.getValidationState(), 'validated')

    # Change to author and try to add a measure to validated product and fail.
    self.loginByUserName('author')
    self.assertRaises(AccessControl_Unauthorized,
                      product.newContent, portal_type='Measure')

    # Change to assignee and try to add a measure to validated product and succeed.
    self.loginByUserName('assignee')
    product.newContent(portal_type='Measure')

    self.tic()

    self.assertEqual(len(product.contentValues(portal_type='Measure')),
                     2)

class DefaultSupplyLineTestCase(ERP5TypeTestCase):
  def _makeOne(self):
    raise NotImplementedError()

  def afterSetUp(self):
    super(DefaultSupplyLineTestCase, self).afterSetUp()
    if self.portal.portal_categories.quantity_unit.get('time') is None:
      self.portal.portal_categories.quantity_unit.newContent(id='time')
    if self.portal.portal_categories.quantity_unit.time.get('hour') is None:
      self.portal.portal_categories.quantity_unit.time.newContent(id='hour')
    self.resource = self._makeOne()

  def test_purchase_supply_line(self):
    self.resource.edit(purchase_supply_line_base_price=123)
    self.assertEqual(self.resource.getPurchaseSupplyLineBasePrice(), 123)
    self.resource.edit(purchase_supply_line_priced_quantity=2)
    self.assertEqual(self.resource.getPurchaseSupplyLinePricedQuantity(), 2)
    self.resource.edit(purchase_supply_line_quantity_unit='time/hour')
    self.assertEqual(
        self.resource.getPurchaseSupplyLineQuantityUnitValue(),
        self.portal.portal_categories.quantity_unit.time.hour)
    self.assertEqual(
        self.resource.default_psl.getPortalType(), 'Purchase Supply Line')

  def test_internal_supply_line(self):
    self.resource.edit(internal_supply_line_base_price=123)
    self.assertEqual(self.resource.getInternalSupplyLineBasePrice(), 123)
    self.resource.edit(internal_supply_line_priced_quantity=2)
    self.assertEqual(self.resource.getInternalSupplyLinePricedQuantity(), 2)
    self.resource.edit(internal_supply_line_quantity_unit='time/hour')
    self.assertEqual(
        self.resource.getInternalSupplyLineQuantityUnitValue(),
        self.portal.portal_categories.quantity_unit.time.hour)
    self.assertEqual(
        self.resource.default_isl.getPortalType(), 'Internal Supply Line')

  def test_sale_supply_line(self):
    self.resource.edit(sale_supply_line_base_price=123)
    self.assertEqual(self.resource.getSaleSupplyLineBasePrice(), 123)
    self.resource.edit(sale_supply_line_priced_quantity=2)
    self.assertEqual(self.resource.getSaleSupplyLinePricedQuantity(), 2)
    self.resource.edit(sale_supply_line_quantity_unit='time/hour')
    self.assertEqual(
        self.resource.getSaleSupplyLineQuantityUnitValue(),
        self.portal.portal_categories.quantity_unit.time.hour)
    self.assertEqual(
        self.resource.default_ssl.getPortalType(), 'Sale Supply Line')


class TestProductDefaultSupplyLine(DefaultSupplyLineTestCase):
  def _makeOne(self):
    return self.portal.product_module.newContent(portal_type='Product')


class TestServiceDefaultSupplyLine(DefaultSupplyLineTestCase):
  def _makeOne(self):
    return self.portal.service_module.newContent(portal_type='Service')


class TestComponentDefaultSupplyLine(DefaultSupplyLineTestCase):
  def _makeOne(self):
    return self.portal.component_module.newContent(portal_type='Component')


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPDMWithSecurity))
  suite.addTest(unittest.makeSuite(TestProductDefaultSupplyLine))
  suite.addTest(unittest.makeSuite(TestServiceDefaultSupplyLine))
  suite.addTest(unittest.makeSuite(TestComponentDefaultSupplyLine))
  return suite
