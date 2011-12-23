# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#          Fabien Morin <fabien@nexedi.com>
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
import transaction
from Products.ERP5.tests.testTradeModelLine import TestTradeModelLineMixin


class TestComplexTradeModelLineUseCase(TestTradeModelLineMixin):
  """This test provides several complex use cases which are seen in the normal
  shop and make sure that trade model line is capable of real business scene.
  """

  def appendBaseContributionCategory(self, document, *new_category):
    document.setBaseContributionList(
      document.getBaseContributionList() + list(new_category))

  def createCategories(self):
    super(TestComplexTradeModelLineUseCase, self).createCategories()
    category_tool = self.portal.portal_categories
    self.createCategoriesInCategory(category_tool.base_amount, (
      'additional_charge',
      'discount_amount',
      'discount_amount_of_non_vat_taxable',
      'discount_amount_of_vat_taxable',
      'total_price_of_ordered_items',
      'total_price_of_vat_taxable',
      'total_price_without_vat',
      'total_price_with_vat',
      'vat_amount',
      'vat_taxable',
      ))
    self.createCategoriesInCategory(category_tool.product_line, (
      'audio', 'video', 'other'))
    self.createCategoriesInCategory(category_tool.product_line.audio, ('cd',))
    self.createCategoriesInCategory(category_tool.product_line.video, ('dvd',))
    self.createCategoriesInCategory(category_tool.quantity_unit, ('unit',))

  def afterSetUp(self):
    super(TestComplexTradeModelLineUseCase, self).afterSetUp()
    portal = self.portal

    # add currency
    jpy = portal.currency_module.newContent(title='Yen', reference='JPY',
                                            base_unit_quantity='1')
    # add organisations
    my_company = portal.organisation_module.newContent(title='My Company')
    client_1 = portal.organisation_module.newContent(title='Client 1')

    # create services
    self.service_vat = portal.service_module.newContent(title='VAT')
    self.service_discount = portal.service_module.newContent(title='DISCOUNT')
    self.service_shipping_fee = portal.service_module.newContent(title='SHIPPING FEE')

    # create products
    def addProductDocument(title, product_line):
      return portal.product_module.newContent(
        title=title,
        product_line=product_line,
        quantity_unit='unit',
        base_contribution_list=('base_amount/vat_taxable',
                                'base_amount/total_price_of_ordered_items'))
    self.music_album_1 = addProductDocument('Music Album 1', 'audio/cd')
    self.movie_dvd_1 = addProductDocument('Movie DVD 1', 'video/dvd')
    self.music_album_2 = addProductDocument('Movie Album 2', 'audio/cd')
    self.candy = addProductDocument('Candy', 'other')
    self.poster = addProductDocument('Poster', 'other')
    self.music_album_3 = addProductDocument('Movie Album 3', 'audio/cd')
    self.movie_dvd_2 = addProductDocument('Movie DVD 2', 'video/dvd')
    self.music_album_4 = addProductDocument('Movie Album 4', 'audio/cd')

    # create a trade condition with several common trade model lines
    self.trade_condition = self.createTradeCondition(
      self.createBusinessProcess(), (
      dict(title='Total Price Without VAT',
           reference='TOTAL_PRICE_WITHOUT_VAT',
           price=1,
           int_index=10,
           target_delivery=True,
           base_application_list=('base_amount/discount_amount_of_non_vat_taxable',
                                  'base_amount/discount_amount_of_vat_taxable',
                                  'base_amount/total_price_of_ordered_items',
                                  'base_amount/additional_charge'),
           base_contribution='base_amount/total_price_without_vat'),
      dict(title='Total Price Of VAT Taxable',
           reference='TOTAL_PRICE_OF_VAT_TAXABLE',
           price=1,
           int_index=10,
           target_delivery=True,
           base_application_list=('base_amount/discount_amount_of_vat_taxable',
                                  'base_amount/vat_taxable'),
           base_contribution='base_amount/total_price_of_vat_taxable'),
      dict(title='Discount Amount',
           reference='DISCOUNT_AMOUNT',
           resource_value=self.service_discount,
           price=1,
           trade_phase='default/invoicing',
           int_index=10,
           target_delivery=True,
           base_application_list=('base_amount/discount_amount_of_vat_taxable',
                                  'base_amount/discount_amount_of_non_vat_taxable'),
           base_contribution='base_amount/discount_amount'),
      dict(title='VAT Amount',
           reference='VAT_AMOUNT',
           resource_value=self.service_vat,
           price=0.05,
           trade_phase='default/invoicing',
           int_index=10,
           target_delivery=True,
           base_application_list=('base_amount/discount_amount_of_vat_taxable',
                                  'base_amount/vat_taxable'),
           base_contribution='base_amount/vat_amount'),
      dict(title='Total Price With VAT',
           reference='TOTAL_PRICE_WITH_VAT',
           price=1,
           int_index=20,
           target_delivery=True,
           base_application_list=('base_amount/vat_amount',
                                  'base_amount/total_price_without_vat'),
           base_contribution='base_amount/total_price_with_vat')
      ),
      source_section_value=my_company,
      source_value=my_company,
      source_decision_value=my_company,
      destination_section_value=client_1,
      destination_value=client_1,
      destination_decision_value=client_1,
      price_currency_value=jpy)

    self.stepTic()

  def test_usecase1(self):
    """
    Use case 1 : Buy 3 CDs or more, get 10% off them.

    1 CD   5000 yen
    1 CD   3000 yen
    1 Candy 100 yen
    1 CD   2400 yen
    discount (5000+3000+2400) * 0.1 = 1040 yen
    """
    special_discount = self.setBaseAmountQuantityMethod(
      'special_discount', """\
def getBaseAmountQuantity(delivery_amount, base_application, **kw):
  if delivery_amount.isDelivery():
    total_quantity = sum([movement.getQuantity()
      for movement in delivery_amount.getBaseAmountList()
      if base_application in movement.getBaseContributionList()])
    if total_quantity < 3:
      return 0
  return context.getBaseAmountQuantity(
    delivery_amount, base_application, **kw)
return getBaseAmountQuantity""")

    trade_condition = self.createTradeCondition(
      self.trade_condition, (
      dict(reference='SPECIAL_DISCOUNT_3CD_LINEAR',
           resource_value=self.service_discount,
           price=-0.1,
           int_index=0,
           target_delivery=True,
           base_application=special_discount,
           base_contribution='base_amount/discount_amount_of_vat_taxable'),
      ))

    order = self.createOrder(trade_condition, (
      dict(id='1', price=5000, quantity=1, resource_value=self.music_album_1),
      dict(id='2', price=3000, quantity=1, resource_value=self.music_album_2),
      dict(id='3', price=100, quantity=1, resource_value=self.candy),
      ))
    self.appendBaseContributionCategory(order['1'], special_discount)
    self.appendBaseContributionCategory(order['2'], special_discount)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_LINEAR=dict(total_price=0),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=8100),
      TOTAL_PRICE_WITH_VAT=dict(total_price=8505),
      VAT_AMOUNT=dict(total_price=405))

    # add one more cd, then total is 3. the special discount will be applied.
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=self.music_album_3,
                            quantity=1,
                            price=2400)
    self.appendBaseContributionCategory(line, special_discount)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_LINEAR=dict(total_price=-1040),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=9460),
      TOTAL_PRICE_WITH_VAT=dict(total_price=9933),
      VAT_AMOUNT=dict(total_price=473))

  def test_usecase2(self):
    """
    Use case 2 : Buy 3 CDs or more, get 500 yen off.

    1 CD  5000 yen
    1 CD  3000 yen
    1 DVD 3000 yen
    1 CD  2400 yen
    discount 500 yen
    """
    special_discount = self.setBaseAmountQuantityMethod(
      'special_discount', """\
return lambda delivery_amount, base_application, **kw: \\
  3 <= sum([movement.getQuantity()
            for movement in delivery_amount.getBaseAmountList()
            if base_application in movement.getBaseContributionList()])""")

    trade_condition = self.createTradeCondition(
      self.trade_condition, (
      dict(reference='SPECIAL_DISCOUNT_3CD_FIXED',
           resource_value=self.service_discount,
           price=-1,
           quantity=500,
           int_index=0,
           target_delivery=True,
           base_application=special_discount,
           base_contribution='base_amount/discount_amount_of_vat_taxable'),
      ))

    order = self.createOrder(trade_condition, (
      dict(id='1', price=5000, quantity=1, resource_value=self.music_album_1),
      dict(id='2', price=3000, quantity=1, resource_value=self.music_album_2),
      dict(id='3', price=3000, quantity=1, resource_value=self.movie_dvd_1),
      ))
    self.appendBaseContributionCategory(order['1'], special_discount)
    self.appendBaseContributionCategory(order['2'], special_discount)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_FIXED=dict(total_price=0),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=11000),
      TOTAL_PRICE_WITH_VAT=dict(total_price=11550),
      VAT_AMOUNT=dict(total_price=550))

    # add one more cd, then total is 3. the special discount will be applied.
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=self.music_album_3,
                            quantity=1,
                            price=2400)
    self.appendBaseContributionCategory(line, special_discount)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_FIXED=dict(total_price=-500),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=12900),
      TOTAL_PRICE_WITH_VAT=dict(total_price=13545),
      VAT_AMOUNT=dict(total_price=645))

  def test_usecase3(self):
    """
    Use case 3 : Buy 3 CDs or more, get 10% off total.

    1 CD  5000 yen
    1 DVD 3000 yen
    1 CD  3000 yen
    1 CD  2400 yen
    discount (5000+3000+3000+2400) * 0.1 = 1340 yen
    """
    special_discount = self.setBaseAmountQuantityMethod(
      'special_discount', """\
def getBaseAmountQuantity(delivery_amount, base_application, **kw):
  total_quantity = sum([movement.getQuantity()
    for movement in delivery_amount.getBaseAmountList()
    if base_application in movement.getBaseContributionList()])
  if total_quantity < 3:
    return 0
  return delivery_amount.getGeneratedAmountQuantity(
    'base_amount/total_price_of_ordered_items')
return getBaseAmountQuantity""")

    trade_condition = self.createTradeCondition(
      self.trade_condition, (
      dict(reference='SPECIAL_DISCOUNT_3CD_LINEAR',
           resource_value=self.service_discount,
           price=-0.1,
           int_index=0,
           target_delivery=True,
           base_application=special_discount,
           base_contribution='base_amount/discount_amount_of_vat_taxable'),
      ))

    order = self.createOrder(trade_condition, (
      dict(id='1', price=5000, quantity=1, resource_value=self.music_album_1),
      dict(id='2', price=3000, quantity=1, resource_value=self.movie_dvd_1),
      dict(id='3', price=3000, quantity=1, resource_value=self.music_album_2),
      ))
    self.appendBaseContributionCategory(order['1'], special_discount)
    self.appendBaseContributionCategory(order['3'], special_discount)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_LINEAR=dict(total_price=0),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=11000),
      TOTAL_PRICE_WITH_VAT=dict(total_price=11550),
      VAT_AMOUNT=dict(total_price=550))

    # add one more cd, then total is 3. the special discount will be applied.
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=self.music_album_3,
                            quantity=1,
                            price=2400)
    self.appendBaseContributionCategory(line, special_discount)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_LINEAR=dict(total_price=-1340),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=12060),
      TOTAL_PRICE_WITH_VAT=dict(total_price=12663),
      VAT_AMOUNT=dict(total_price=603))

  def test_usecase4(self):
    """
    Use case 4 : Buy 3 CDs or 1 DVD, get 1 poster free.

    2 CD     6000 yen
    1 DVD    3000 yen
    1 Poster    0 yen
    """
    total_quantity = """\
def getBaseAmountQuantity(delivery_amount, base_application, **kw):
  value = delivery_amount.getGeneratedAmountQuantity(base_application)
  if base_application in delivery_amount.getBaseContributionList():
    value += delivery_amount.getQuantity()
  return value
return getBaseAmountQuantity"""
    poster_present_1dvd = self.setBaseAmountQuantityMethod(
      'poster_present_1dvd', total_quantity)
    poster_present_3cd = self.setBaseAmountQuantityMethod(
      'poster_present_3cd', total_quantity)
    special_discount = self.setBaseAmountQuantityMethod(
      'special_discount', """\
return lambda delivery_amount, base_application, **kw: \\
  3 <= delivery_amount.getGeneratedAmountQuantity(%r) or \\
  1 <= delivery_amount.getGeneratedAmountQuantity(%r)"""
      % (poster_present_3cd, poster_present_1dvd))

    trade_condition = self.createTradeCondition(
      self.trade_condition, (
      dict(reference='SPECIAL_DISCOUNT_3CD_OR_1DVD_FIXED',
           resource_value=self.poster,
           price=0,
           int_index=0,
           target_delivery=True,
           base_application=special_discount),
      ))

    order = self.createOrder(trade_condition, (
      dict(id='1', price=3000, quantity=2, resource_value=self.music_album_4),
      ))
    self.appendBaseContributionCategory(order['1'], poster_present_3cd)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_OR_1DVD_FIXED=dict(total_price=None),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=6000),
      TOTAL_PRICE_WITH_VAT=dict(total_price=6300),
      VAT_AMOUNT=dict(total_price=300))

    # add 1 dvd, then 1 poster will be given.
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=self.movie_dvd_1,
                            quantity=1,
                            price=3000)
    self.appendBaseContributionCategory(line, poster_present_1dvd)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_OR_1DVD_FIXED=dict(total_price=None, quantity=1,
                                              resource_value=self.poster),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=9000),
      TOTAL_PRICE_WITH_VAT=dict(total_price=9450),
      VAT_AMOUNT=dict(total_price=450))

    # even if we buy 3 CDs and 1 DVD, only one poster will be given.
    line = order.newContent(portal_type=self.order_line_portal_type,
                            resource_value=self.music_album_3,
                            quantity=1,
                            price=2400)
    self.appendBaseContributionCategory(line, poster_present_3cd)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD_OR_1DVD_FIXED=dict(total_price=None, quantity=1,
                                              resource_value=self.poster),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=11400),
      TOTAL_PRICE_WITH_VAT=dict(total_price=11970),
      VAT_AMOUNT=dict(total_price=570))

  def test_usecase5(self):
    """
    Use case 5 : Buy 3 CDs or more, 1 highest priced DVD in ordered 15% off.

    1 DVD    3000 yen
    1 DVD    1000 yen
    2 CD    10000 yen
    1 CD     3000 yen
    discount 3000 * 0.15 = 450 yen
    """
    special_discount = self.setBaseAmountQuantityMethod(
      'special_discount', """\
def getBaseAmountQuantity(delivery_amount, base_application, **kw):
  highest_price = quantity = 0
  for movement in delivery_amount.getBaseAmountList():
    if base_application in movement.getBaseContributionList():
      quantity += movement.getQuantity()
    if movement.getResourceValue().getProductLine() == 'video/dvd':
      highest_price = max(highest_price, movement.getPrice())
  return quantity >= 3 and highest_price
return getBaseAmountQuantity""")

    trade_condition = self.createTradeCondition(
      self.trade_condition, (
      dict(reference='SPECIAL_DISCOUNT_3CD',
           resource_value=self.service_discount,
           price=-0.15,
           int_index=0,
           target_delivery=True,
           base_application=special_discount,
           base_contribution='base_amount/discount_amount_of_vat_taxable'),
      ))

    order = self.createOrder(trade_condition, (
      dict(id='1', price=3000, quantity=1, resource_value=self.movie_dvd_1),
      dict(id='2', price=1000, quantity=1, resource_value=self.movie_dvd_2),
      dict(id='3', price=5000, quantity=1, resource_value=self.music_album_1),
      dict(id='4', price=3000, quantity=1, resource_value=self.music_album_2),
      ))
    self.appendBaseContributionCategory(order['3'], special_discount)
    self.appendBaseContributionCategory(order['4'], special_discount)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD=dict(total_price=0),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=12000),
      TOTAL_PRICE_WITH_VAT=dict(total_price=12600),
      VAT_AMOUNT=dict(total_price=600))

    # add one more cd, then total is 3. the special discount will be applied.
    order['3'].setQuantity(2)
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      SPECIAL_DISCOUNT_3CD=dict(total_price=-450),
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=16550),
      TOTAL_PRICE_WITH_VAT=dict(total_price=17377.5),
      VAT_AMOUNT=dict(total_price=827.5))

  def test_usecase6(self):
    """
    Use case 6 : Add a shipping fee by TradeModelLine and VAT is charged to
    this fee.
    """
    fixed_quantity = self.setBaseAmountQuantityMethod('fixed_quantity', """\
return lambda *args, **kw: 1""")

    trade_condition = self.createTradeCondition(
      self.trade_condition, (
      dict(reference='SHIPPING_FEE',
           resource_value=self.service_discount,
           quantity=500,
           int_index=0,
           target_delivery=True,
           base_application=fixed_quantity,
           base_contribution_list=('base_amount/additional_charge',
                                   'base_amount/vat_taxable')),
      ))

    order = self.createOrder(trade_condition, (
      dict(id='1', price=3000, quantity=1, resource_value=self.movie_dvd_1),
      dict(id='2', price=1000, quantity=1, resource_value=self.movie_dvd_2),
      ))
    transaction.commit()
    self.getAggregatedAmountDict(order, partial_check=True,
      TOTAL_PRICE_WITHOUT_VAT=dict(total_price=4500),
      TOTAL_PRICE_WITH_VAT=dict(total_price=4725),
      VAT_AMOUNT=dict(total_price=225))


class TestComplexTradeModelLineUseCaseSale(TestComplexTradeModelLineUseCase):
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  trade_condition_portal_type = 'Sale Trade Condition'


class TestComplexTradeModelLineUseCasePurchase(TestComplexTradeModelLineUseCase):
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  trade_condition_portal_type = 'Purchase Trade Condition'


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestComplexTradeModelLineUseCaseSale))
  suite.addTest(unittest.makeSuite(TestComplexTradeModelLineUseCasePurchase))
  return suite
