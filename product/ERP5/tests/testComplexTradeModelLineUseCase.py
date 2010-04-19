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

from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5.tests.testTradeModelLine import TestTradeModelLineMixin


class TestComplexTradeModelLineUseCase(TestTradeModelLineMixin):
  """This test provides several complex use cases which are seen in the normal
  shop and make sure that trade model line is capable of real business scene.
  """

  def createOrder(self):
    module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    return module.newContent(portal_type=self.order_portal_type,
        title=self.id())

  def createTradeCondition(self):
    module = self.portal.getDefaultModule(
        portal_type=self.trade_condition_portal_type)
    trade_condition = module.newContent(
        portal_type=self.trade_condition_portal_type,
        title=self.id())
    return trade_condition

  def getAmount(self, order, reference, return_object=False):
    amount_list = []
    for amount in order.getAggregatedAmountList():
      if amount.getProperty('reference') == reference:
        amount_list.append(amount)
    if return_object:
      return amount_list
    if amount_list:
      return sum(amount.getTotalPrice() for amount in amount_list)

  def appendBaseContributionCategory(self, document, new_category):
    base_contribution_value_list = document.getBaseContributionValueList()
    document.setBaseContributionValueList(
      base_contribution_value_list+[new_category])

  def beforeTearDown(self):
    # abort any transaction
    transaction.abort()
    # put non finished activities into ignored state
    activity_connection = self.portal.cmf_activity_sql_connection
    for table in 'message', 'message_queue':
      activity_connection.manage_test(
          'delete from %s where processing_node=-2' % table)

    def removeAll(*args):
      for container in args:
        container.manage_delObjects(ids=list(container.objectIds()))
    removeAll(self.portal.sale_order_module,
              self.portal.purchase_order_module,
              self.portal.sale_trade_condition_module,
              self.portal.purchase_trade_condition_module,
              self.portal.person_module,
              self.portal.organisation_module,
              self.portal.service_module,
              self.portal.product_module,
              self.portal.currency_module,
              self.portal.portal_categories.product_line,
              self.portal.portal_categories.base_amount,
              self.portal.portal_categories.trade_phase,
              self.portal.portal_categories.use,
              self.portal.portal_categories.quantity_unit,
              )

    self.stepTic()

  def afterSetUp(self):
    portal = self.portal

    # inherited method
    self.createCategories()

    self.stepTic()

    # add currency
    jpy = portal.currency_module.newContent(title='Yen', reference='JPY', base_unit_quantity='1')

    self.stepTic()

    # add organisations
    my_company = portal.organisation_module.newContent(title='My Company')
    client_1 = portal.organisation_module.newContent(title='Client 1')

    self.stepTic()

    # add base amount subcategories
    base_amount = portal.portal_categories.base_amount
    self.total_price_of_ordered_items = base_amount.newContent(id='total_price_of_ordered_items')
    self.discount_amount_of_non_vat_taxable = base_amount.newContent(id='discount_amount_of_non_vat_taxable')
    self.discount_amount_of_vat_taxable = base_amount.newContent(id='discount_amount_of_vat_taxable')
    self.vat_taxable = base_amount.newContent(id='vat_taxable')
    self.additional_charge = base_amount.newContent('additional_charge')
    self.total_price_without_vat = base_amount.newContent(id='total_price_without_vat')
    self.total_price_of_vat_taxable = base_amount.newContent(id='total_price_of_vat_taxable')
    self.discount_amount = base_amount.newContent(id='discount_amount')
    self.vat_amount = base_amount.newContent(id='vat_amount')
    self.total_price_with_vat = base_amount.newContent(id='total_price_with_vat')
    self.poster_present_1dvd = base_amount.newContent(id='poster_present_1dvd')
    self.poster_present_3cd = base_amount.newContent(id='poster_present_3cd')
    self.special_discount_3cd = base_amount.newContent(id='special_discount_3cd')
    # add product line subcategories
    product_line = portal.portal_categories.product_line
    audio = product_line.newContent(id='audio')
    audio_cd = audio.newContent(id='cd')
    video = product_line.newContent(id='video')
    video_dvd = video.newContent(id='dvd')
    other_product = product_line.newContent(id='other')
    # add a quantity unit subcategory
    self.unit = portal.portal_categories.quantity_unit.newContent(id='unit')

    self.stepTic()

    # create services
    self.service_vat = portal.service_module.newContent(title='VAT')
    self.service_discount = portal.service_module.newContent(title='DISCOUNT')
    self.service_shipping_fee = portal.service_module.newContent(title='SHIPPING FEE')

    self.stepTic()

    # create products
    def addProductDocument(title, product_line_value):
      return portal.product_module.newContent(
        title=title,
        product_line_value=product_line_value,
        quantity_unit_value=self.unit,
        base_contribution_value_list=[self.vat_taxable,
                                      self.total_price_of_ordered_items])

    self.music_album_1 = addProductDocument('Music Album 1', audio_cd)
    self.movie_dvd_1 = addProductDocument('Movie DVD 1', video_dvd)
    self.music_album_2 = addProductDocument('Movie Album 2', audio_cd)
    self.candy = addProductDocument('Candy', other_product)
    self.poster = addProductDocument('Poster', other_product)
    self.music_album_3 = addProductDocument('Movie Album 3', audio_cd)
    self.movie_dvd_2 = addProductDocument('Movie DVD 2', video_dvd)
    self.music_album_4 = addProductDocument('Movie Album 4', audio_cd)

    self.stepTic()

    # create a trade condition and add several common trade model lines in it.
    self.trade_condition = self.createTradeCondition()
    self.trade_condition.edit(
      source_section_value=my_company,
      source_value=my_company,
      source_decision_value=my_company,
      destination_section_value=client_1,
      destination_value=client_1,
      destination_decision_value=client_1,
      price_currency_value=jpy)
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Total Price Without VAT',
      reference='TOTAL_PRICE_WITHOUT_VAT',
      price=1,
      trade_phase=None,
      int_index=10,
      base_application_value_list=[self.discount_amount_of_non_vat_taxable,
                                   self.discount_amount_of_vat_taxable,
                                   self.total_price_of_ordered_items,
                                   self.additional_charge],
      base_contribution_value_list=[self.total_price_without_vat])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Total Price Of VAT Taxable',
      reference='TOTAL_PRICE_OF_VAT_TAXABLE',
      price=1,
      trade_phase=None,
      int_index=10,
      base_application_value_list=[self.discount_amount_of_vat_taxable,
                                   self.vat_taxable],
      base_contribution_value_list=[self.total_price_of_vat_taxable])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Discount Amount',
      reference='DISCOUNT_AMOUNT',
      resource_value=self.service_discount,
      price=1,
      trade_phase_value=portal.portal_categories.trade_phase.default.invoicing,
      int_index=10,
      base_application_value_list=[self.discount_amount_of_vat_taxable,
                                   self.discount_amount_of_non_vat_taxable],
      base_contribution_value_list=[self.discount_amount])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='VAT Amount',
      reference='VAT_AMOUNT',
      resource_value=self.service_vat,
      price=0.05,
      trade_phase_value=portal.portal_categories.trade_phase.default.invoicing,
      int_index=10,
      base_application_value_list=[self.discount_amount_of_vat_taxable,
                                   self.vat_taxable],
      base_contribution_value_list=[self.vat_amount])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Total Price With VAT',
      reference='TOTAL_PRICE_WITH_VAT',
      price=1,
      trade_phase=None,
      int_index=20,
      base_application_value_list=[self.vat_amount,
                                   self.total_price_without_vat],
      base_contribution_value_list=[self.total_price_with_vat])

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
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_getAmountProperty',
      'amount, base_application, amount_list, *args, **kw',
      """\
if base_application == 'base_amount/special_discount_3cd':
  total_quantity = sum([x.getQuantity() for x in amount_list
    if x.isMovement() and base_application in x.getBaseContributionList()])
  if total_quantity < 3:
    return 0
""")
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_AND_10PERCENT_DISCOUNT_OFF_THEM',
                     resource_value=self.service_discount,
                     price=-0.1,
                     trade_phase=None,
                     int_index=0,
                     base_application_value_list=[self.special_discount_3cd],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_1, self.special_discount_3cd)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_2, self.special_discount_3cd)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.candy,
                                    quantity=1,
                                    price=100)

    self.stepTic()

    # check the current amount
    self.portal.pdb()
    #self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 8100)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 405)
    #self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 8505)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)

    self.stepTic()

    # check again
    self.assertEqual(self.getAmount(order, '3CD_AND_10PERCENT_DISCOUNT_OFF_THEM'),
                     -1040)
    #self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 9460)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 473)
    #self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 9933)

  def test_usecase2(self):
    """
    Use case 2 : Buy 3 CDs or more, get 500 yen off.

    1 CD  5000 yen
    1 CD  3000 yen
    1 DVD 3000 yen
    1 CD  2400 yen
    discount 500 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CD500YenDiscount',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      """\
total_quantity = sum([movement.getQuantity() for movement in aggregated_movement_list])
if total_quantity >= 3:
  current_movement.setQuantity(-500)
  return current_movement
else:
  return None
""")
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_AND_500YEN_OFF',
                     resource_value=self.service_discount,
                     price=1,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CD500YenDiscount',
                     trade_phase=None,
                     int_index=0,
                     base_application_value_list=[self.special_discount_3cd],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_1, self.special_discount_3cd)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_2, self.special_discount_3cd)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 11000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 550)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 11550)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)
    # check again
    self.assertEqual(self.getAmount(order, '3CD_AND_500YEN_OFF'), -500)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 12900)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 645)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 13545)

  def test_usecase3(self):
    """
    Use case 3 : Buy 3 CDs or more, get 10% off total.

    1 CD  5000 yen
    1 DVD 3000 yen
    1 CD  3000 yen
    1 CD  2400 yen
    discount (5000+3000+3000+2400) * 0.1 = 1340 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CD10PercentDiscountFromTotal',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      '''\
special_discount_3cd = context.portal_categories.base_amount.special_discount_3cd
total_quantity = sum([movement.getQuantity() for movement in current_aggregated_amount_list
                      if special_discount_3cd in movement.getBaseContributionValueList()])
if total_quantity >= 3:
  return current_movement
else:
  return None
''')
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_10PERCENT_OFF_FROM_TOTAL',
                     resource_value=self.service_discount,
                     price=-0.1,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CD10PercentDiscountFromTotal',
                     trade_phase=None,
                     int_index=0,
                     base_application_value_list=[self.total_price_of_ordered_items],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_1, self.special_discount_3cd)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_3, self.special_discount_3cd)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 11000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 550)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 11550)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)
    # check again
    self.assertEqual(self.getAmount(order, '3CD_10PERCENT_OFF_FROM_TOTAL'),
                     -1340)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 12060)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 603)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 12663)

  def test_usecase4(self):
    """
    Use case 4 : Buy 3 CDs or 1 DVD, get 1 poster free.

    2 CD     6000 yen
    1 DVD    3000 yen
    1 Poster    0 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CDOr1DVDForPoster',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      '''\
poster_present_3cd = context.portal_categories.base_amount.poster_present_3cd
poster_present_1dvd = context.portal_categories.base_amount.poster_present_1dvd

total_quantity_3cd = sum([movement.getQuantity() for movement in aggregated_movement_list
                          if poster_present_3cd in movement.getBaseContributionValueList()])
total_quantity_1dvd = sum([movement.getQuantity() for movement in aggregated_movement_list
                           if poster_present_1dvd in movement.getBaseContributionValueList()])
if (total_quantity_3cd >= 3 or total_quantity_1dvd >= 1):
  current_movement.setQuantity(1)
  return current_movement
else:
  return None
''')
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_OR_1DVD_GET_1_POSTER_FREE',
                     resource_value=self.poster,
                     price=0,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CDOr1DVDForPoster',
                     trade_phase=None,
                     base_application_value_list=[self.poster_present_1dvd,
                                                  self.poster_present_3cd])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_4,
                                    quantity=2,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_1, self.poster_present_3cd)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 6000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 300)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 6300)
    self.assertEqual(self.getAmount(order, '3CD_OR_1DVD_GET_1_POSTER_FREE'),
                     None)
    # add 1 dvd, then 1 poster will be given.
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_2, self.poster_present_1dvd)

    self.stepTic()
    
    # check again
    one_free_poster_amount_list = self.getAmount(
      order,
      '3CD_OR_1DVD_GET_1_POSTER_FREE',
      return_object=True)
    self.assertEqual(len(one_free_poster_amount_list), 1)
    one_free_poster_amount = one_free_poster_amount_list[0]
    self.assertEqual(one_free_poster_amount.getTotalPrice(), 0)
    self.assertEqual(one_free_poster_amount.getQuantity(), 1)
    self.assertEqual(one_free_poster_amount.getPrice(), 0)
    self.assertEqual(one_free_poster_amount.getResourceValue(), self.poster)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 9000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 450)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 9450)

    # even if we buy 3 CDs and 1 DVD, only one poster will be given.
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_3, self.poster_present_3cd)

    self.stepTic()

    # check again
    one_free_poster_amount_list = self.getAmount(order,
                                            '3CD_OR_1DVD_GET_1_POSTER_FREE',
                                            return_object=True)
    self.assertEqual(len(one_free_poster_amount_list), 1)
    one_free_poster_amount = one_free_poster_amount_list[0]
    self.assertEqual(one_free_poster_amount.getTotalPrice(), 0)
    self.assertEqual(one_free_poster_amount.getQuantity(), 1)
    self.assertEqual(one_free_poster_amount.getPrice(), 0)
    self.assertEqual(one_free_poster_amount.getResourceValue(), self.poster)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 11400)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 570)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 11970)

  def test_usecase5(self):
    """
    Use case 5 : Buy 3 CDs or more, 1 highest priced DVD in ordered 15% off.

    1 DVD    3000 yen
    1 DVD    1000 yen
    2 CD    10000 yen
    1 CD     3000 yen
    discount 3000 * 0.15 = 450 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CD15PercentDiscountOf1HighestPricedDVD',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      '''\
total_quantity = sum([movement.getQuantity() for movement in aggregated_movement_list])
if total_quantity >= 3:
  price_dvd_list = []
  product_line_dvd = context.portal_categories.product_line.video.dvd
  for movement in current_aggregated_amount_list:
    resource = movement.getResourceValue()
    if resource.getProductLineValue() == product_line_dvd:
      price_dvd_list.append((movement.getPrice(), movement))
  if price_dvd_list:
    price_dvd_list.sort()
    highest_priced_dvd_movement = price_dvd_list[-1][1]
    total_price = highest_priced_dvd_movement.getTotalPrice()

    from Products.ERP5Type.Document import newTempSimulationMovement
    causality_value_list = list(aggregated_movement_list) + [highest_priced_dvd_movement]
    temporary_movement = newTempSimulationMovement(current_movement.getParentValue(), current_movement.getId())
    temporary_movement.edit(title=current_movement.getProperty('title'),
                            description=current_movement.getProperty('description'),
                            resource=current_movement.getProperty('resource'),
                            reference=current_movement.getProperty('reference'),
                            int_index=current_movement.getProperty('int_index'),
                            base_application_list=current_movement.getProperty('base_application_list'),
                            base_contribution_list=current_movement.getProperty('base_contribution_list'),
                            start_date=highest_priced_dvd_movement.getStartDate(),
                            stop_date=highest_priced_dvd_movement.getStopDate(),
                            create_line=current_movement.getProperty('is_create_line'),
                            trade_phase_list=current_movement.getTradePhaseList(),
                            causality_list=[movement.getRelativeUrl() for movement in causality_value_list])
    temporary_movement.setPrice(current_movement.getProperty('price'))
    temporary_movement.setQuantity(highest_priced_dvd_movement.getPrice())
    return temporary_movement
''')
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_AND_1HIGHEST_PRICED_DVD_15PERCENT_OFF',
                     resource_value=self.service_discount,
                     price=-0.15,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CD15PercentDiscountOf1HighestPricedDVD',
                     trade_phase=None,
                     int_index=0,
                     base_application_value_list=[self.special_discount_3cd],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_2,
                                    quantity=1,
                                    price=1000)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_3, self.special_discount_3cd)
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 12000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 600)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'),
                     12600)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_3.setQuantity(2)

    self.stepTic()

    # check again
    self.assertEqual(self.getAmount(order, '3CD_AND_1HIGHEST_PRICED_DVD_15PERCENT_OFF'),
                     -450)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 16550)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 827.5)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 17377.5)

  def test_usecase6(self):
    """
    Use case 6 : Add a shipping fee by TradeModelLine and VAT is charged to
    this fee.
    """
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='SHIPPING_FEE',
                     resource_value=self.service_shipping_fee,
                     price=1,
                     quantity=500,
                     target_level=TARGET_LEVEL_DELIVERY,
                     trade_phase=None,
                     int_index=0,
                     base_application_value_list=[],
                     base_contribution_value_list=[self.additional_charge,
                                                   self.vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_2,
                                    quantity=1,
                                    price=1000)

    self.stepTic()

    # check amounts
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 4500)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 225)
    self.assertEqual(
      len(self.getAmount(order, 'VAT_AMOUNT', return_object=True)),
      1)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 4725)

    # change trade model line and calculate vat price per movement
    order.newContent(portal_type='Trade Model Line',
                     title='VAT Amount',
                     reference='VAT_AMOUNT',
                     resource_value=self.service_vat,
                     price=0.05,
                     target_level=TARGET_LEVEL_MOVEMENT,
                     trade_phase_value=self.portal.portal_categories.trade_phase.default.invoicing,
                     int_index=10,
                     base_application_value_list=[self.discount_amount_of_vat_taxable,
                                                  self.vat_taxable],
                     base_contribution_value_list=[self.vat_amount])

    self.stepTic()

    # check amounts again
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 4500)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 225)
    self.assertEqual(
      len(self.getAmount(order, 'VAT_AMOUNT', return_object=True)),
      3)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 4725)


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
