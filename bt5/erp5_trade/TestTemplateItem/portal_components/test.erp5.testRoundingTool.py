# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi KK, Nexedi SA and Contributors. All Rights Reserved.
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


class TestRoundingTool(ERP5TypeTestCase):
  """
  Rounding Tool Test
  """

  def getTitle(self):
    return 'Rounding Tool Test'

  def getBusinessTemplateList(self):
    return ('erp5_base',
            'erp5_pdm',
            'erp5_simulation',
            'erp5_trade',
            )

  def afterSetUp(self):
    if getattr(self.portal, '_run_after_setup', None) is not None:
      return

    self.portal._run_after_setup = True

    user_folder = self.portal.acl_users
    user_folder._doAddUser('developer', '', ['Manager'], [])
    user_folder._doAddUser('assignor', '', ['Auditor', 'Author', 'Assignor'], [])
    self.tic()

  def testRoundValueMethod(self):
    """
    Test rounding method
    """
    rounding_tool = self.portal.portal_roundings
    rounding_model = rounding_tool.newContent(portal_type='Rounding Model')
    rounding_model.edit(decimal_rounding_option='ROUND_HALF_UP')

    rounding_model.edit(precision=0.01)
    self.assertEqual(rounding_model.roundValue(12.344), 12.34)
    self.assertEqual(rounding_model.roundValue(12.355), 12.36)
    rounding_model.edit(precision=0.1)
    self.assertEqual(rounding_model.roundValue(12.34), 12.3)
    self.assertEqual(rounding_model.roundValue(12.35), 12.4)
    rounding_model.edit(precision=1.0)
    self.assertEqual(rounding_model.roundValue(1.1), 1)
    self.assertEqual(rounding_model.roundValue(1.5), 2)
    rounding_model.edit(precision=10.0)
    self.assertEqual(rounding_model.roundValue(1.1), 0)
    self.assertEqual(rounding_model.roundValue(5.0), 10)
    rounding_model.edit(precision=100.0)
    self.assertEqual(rounding_model.roundValue(132), 100)
    self.assertEqual(rounding_model.roundValue(150), 200)

  def testBasicRounding(self):
    """
    Test basic features of rounding tool
    """
    rounding_tool = self.portal.portal_roundings

    self.loginByUserName('assignor')
    sale_order = self.portal.sale_order_module.newContent(portal_type='Sale Order')
    sale_order_line = sale_order.newContent(portal_type='Sale Order Line')

    self.tic()

    # check values of empty line
    self.assertEqual(sale_order_line.getPrice(), None)
    self.assertEqual(sale_order_line.getProperty('price'), None)
    self.assertEqual(sale_order_line.getQuantity(), 0.0)
    self.assertEqual(sale_order_line.getProperty('quantity'), 0.0)
    self.assertEqual(sale_order_line.getTotalPrice(), 0.0)
    self.assertEqual(sale_order_line.getProperty('total_price'), 0.0)

    self.loginByUserName('developer')
    # rounding model dummy never match to sale order line
    rounding_model_dummy= rounding_tool.newContent(portal_type='Rounding Model')
    rounding_model_dummy.edit(decimal_rounding_option='ROUND_DOWN',
                              precision=0.01,
                              rounded_property_id_list=['price',
                                                        'quantity',
                                                        'total_price'])
    rounding_model_dummy.setCriterionProperty('portal_type')
    rounding_model_dummy.setCriterion('portal_type', identity=['Web Page'],
                                      min='', max='')

    # add a rounding model for price of sale order line
    rounding_model_1 = rounding_tool.newContent(portal_type='Rounding Model')
    rounding_model_1.edit(decimal_rounding_option='ROUND_DOWN',
                          precision=0.01,
                          rounded_property_id_list=['price'])
    rounding_model_1.setCriterionProperty('portal_type')
    rounding_model_1.setCriterion('portal_type', identity=['Sale Order Line'],
                                  min='', max='')

    self.loginByUserName('assignor')
    rounding_model_dummy.validate()
    rounding_model_1.validate()

    self.tic()

    # rounding model does not do anything to empty values like None
    wrapped_line = rounding_tool.getRoundingProxy(sale_order_line, sale_order_line)
    self.assertEqual(wrapped_line.getPrice(), None)
    self.assertEqual(wrapped_line.getProperty('price'), None)
    self.assertEqual(wrapped_line.getQuantity(), 0.0)
    self.assertEqual(wrapped_line.getProperty('quantity'), 0.0)
    self.assertEqual(wrapped_line.getTotalPrice(), 0.0)
    self.assertEqual(wrapped_line.getProperty('total_price'), 0.0)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('price'), 0.01)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('quantity'), None)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('total_price'), None)

    self.tic()

    # set values
    sale_order_line.edit(price=123.456, quantity=78.91)

    self.tic()

    self.assertEqual(sale_order_line.getPrice(), 123.456)
    self.assertEqual(sale_order_line.getProperty('price'), 123.456)
    self.assertEqual(sale_order_line.getQuantity(), 78.91)
    self.assertEqual(sale_order_line.getProperty('quantity'), 78.91)
    self.assertEqual(sale_order_line.getTotalPrice(), 123.456*78.91)
    self.assertEqual(sale_order_line.getProperty('total_price'), 123.456*78.91)

    # check if price is rounded
    wrapped_line = rounding_tool.getRoundingProxy(sale_order_line, sale_order_line)
    self.assertEqual(wrapped_line.getPrice(), 123.45)
    self.assertEqual(wrapped_line.getProperty('price'), 123.45)
    self.assertEqual(wrapped_line.getQuantity(), 78.91)
    self.assertEqual(wrapped_line.getProperty('quantity'), 78.91)
    self.assertEqual(wrapped_line.getTotalPrice(), 123.45*78.91)
    self.assertEqual(wrapped_line.getProperty('total_price'), 123.45*78.91)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('price'), 0.01)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('quantity'), None)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('total_price'), None)

    # add a rounding model for quantity of any portal type
    self.loginByUserName('developer')
    rounding_model_2 = rounding_tool.newContent(portal_type='Rounding Model')
    rounding_model_2.edit(decimal_rounding_option='ROUND_UP',
                          precision=0.1,
                          rounded_property_id_list=['quantity'])

    self.tic()

    self.loginByUserName('assignor')

    # check if price and quantity are rounded
    # if rounding model is not validated, then it is not applied
    wrapped_line = rounding_tool.getRoundingProxy(sale_order_line, sale_order_line)
    self.assertEqual(wrapped_line.getPrice(), 123.45)
    self.assertEqual(wrapped_line.getProperty('price'), 123.45)
    self.assertEqual(wrapped_line.getQuantity(), 78.91)
    self.assertEqual(wrapped_line.getProperty('quantity'), 78.91)
    self.assertEqual(wrapped_line.getTotalPrice(), 123.45*78.91)
    self.assertEqual(wrapped_line.getProperty('total_price'), 123.45*78.91)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('price'), 0.01)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('quantity'), None)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('total_price'), None)

    # validate
    rounding_model_2.validate()

    self.tic()

    # check if price and quantity are rounded
    # now, rounding model is validated, so it is applied
    wrapped_line = rounding_tool.getRoundingProxy(sale_order_line, sale_order_line)
    self.assertEqual(wrapped_line.getPrice(), 123.45)
    self.assertEqual(wrapped_line.getProperty('price'), 123.45)
    self.assertEqual(wrapped_line.getQuantity(), 79.0)
    self.assertEqual(wrapped_line.getProperty('quantity'), 79.0)
    self.assertEqual(wrapped_line.getTotalPrice(), 123.45*79.0)
    self.assertEqual(wrapped_line.getProperty('total_price'), 123.45*79.0)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('price'), 0.01)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('quantity'), 0.1)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('total_price'), None)

    # add a rounding model for total price of any portal type
    self.loginByUserName('developer')
    rounding_model_3 = rounding_tool.newContent(portal_type='Rounding Model')
    rounding_model_3.edit(decimal_rounding_option='ROUND_UP',
                          precision=10,
                          rounded_property_id_list=['total_price'])

    self.loginByUserName('assignor')
    rounding_model_3.validate()

    self.tic()

    # check if price and quantity and total price are rounded
    wrapped_line = rounding_tool.getRoundingProxy(sale_order_line, sale_order_line)
    self.assertEqual(wrapped_line.getPrice(), 123.45)
    self.assertEqual(wrapped_line.getProperty('price'), 123.45)
    self.assertEqual(wrapped_line.getQuantity(), 79.0)
    self.assertEqual(wrapped_line.getProperty('quantity'), 79.0)
    self.assertEqual(wrapped_line.getTotalPrice(), 9760.0)
    self.assertEqual(wrapped_line.getProperty('total_price'), 9760.0)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('price'), 0.01)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('quantity'), 0.1)
    self.assertEqual(wrapped_line.getRoundingModelPrecision('total_price'), 10)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRoundingTool))
  return suite
