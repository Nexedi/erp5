# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from DateTime import DateTime
import six

class TestRealTimeInventoryAccountingMixin:
  def assertIterableLen(self, iterable, expected_len):
    if len(iterable) != expected_len:
      self.fail('Length of %s is not equal to %d' % (repr(iterable),
                                                     expected_len))

  def stepSelectSalePackingList1(self, sequence=None, sequence_list=None):
    sequence.edit(current_sale_packing_list=sequence['sale_packing_list_1'])

  def stepSelectPurchasePackingList1(self, sequence=None, sequence_list=None):
    sequence.edit(current_purchase_packing_list=sequence['purchase_packing_list_1'])

  def stepSelectInternalPackingList1(self, sequence=None, sequence_list=None):
    sequence.edit(current_internal_packing_list=sequence['internal_packing_list_1'])

  def stepSelectProductionPackingList1(self, sequence=None, sequence_list=None):
    sequence.edit(current_production_packing_list=sequence['production_packing_list_1'])

  def _transitAndCheck(self, document, workflow_method_id, expected_state):
    from Products.ERP5Type.Core.Workflow import ValidationFailed
    try:
      if workflow_method_id.endswith('_action'):
        self.portal.portal_workflow.doActionFor(document, workflow_method_id)
      else:
        getattr(document, workflow_method_id)()
    except ValidationFailed as error:
      self.fail("Transition '%s' on %r should have succeeded (%s)" % \
                  (workflow_method_id, document,
                   sorted([m.message for m in error.msg])))

    try:
      getState = document.getSimulationState
    except AttributeError:
      getState = document.getValidationState
    self.assertEqual(getState(), expected_state)
    self.tic()

  def stepConfirmSalePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_sale_packing_list']
    self._transitAndCheck(packing_list, 'confirm_action', 'confirmed')

  def stepStartSalePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_sale_packing_list']
    self._transitAndCheck(packing_list, 'start_action', 'started')

  def stepStopSalePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_sale_packing_list']
    self._transitAndCheck(packing_list, 'stop_action', 'stopped')

  def stepConfirmPurchasePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_purchase_packing_list']
    self._transitAndCheck(packing_list, 'confirm_action', 'confirmed')

  def stepStartPurchasePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_purchase_packing_list']
    self._transitAndCheck(packing_list, 'start_action', 'started')

  def stepStopPurchasePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_purchase_packing_list']
    self._transitAndCheck(packing_list, 'stop_action', 'stopped')

  def stepConfirmInternalPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_internal_packing_list']
    self._transitAndCheck(packing_list, 'confirm_action', 'confirmed')

  def stepStartInternalPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_internal_packing_list']
    self._transitAndCheck(packing_list, 'start_action', 'started')

  def stepStopInternalPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_internal_packing_list']
    self._transitAndCheck(packing_list, 'stop_action', 'stopped')

  def stepConfirmProductionPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_production_packing_list']
    self._transitAndCheck(packing_list, 'confirm_action', 'confirmed')

  def stepStartProductionPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_production_packing_list']
    self._transitAndCheck(packing_list, 'start_action', 'started')

  def stepStopProductionPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_production_packing_list']
    self._transitAndCheck(packing_list, 'stop_action', 'stopped')

  def _checkAndGetCausalityRelated(self,
                                   document,
                                   causality_related_portal_type,
                                   causality_related_list_expected_len):
    causality_related_list = document.getCausalityRelatedValueList(portal_type=causality_related_portal_type)
    self.assertIterableLen(causality_related_list, causality_related_list_expected_len)
    return causality_related_list

  def stepCheckAccountingTransactionNotGeneratedFromSalePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_sale_packing_list']
    self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 0)

  def stepCheckAccountingTransactionNotGeneratedFromPurchasePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_purchase_packing_list']
    self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 0)

  def stepCheckAccountingTransactionNotGeneratedFromInternalPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_internal_packing_list']
    self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 0)

  def stepCheckAccountingTransactionNotGeneratedFromProductionPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_production_packing_list']
    self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 0)

  def stepCheckThreeAccountingTransactionGeneratedFromSalePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_sale_packing_list']
    accounting_transaction_list = self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 3)
    sequence.edit(current_accounting_transaction_list=accounting_transaction_list)

  def stepCheckThreeAccountingTransactionGeneratedFromPurchasePackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_purchase_packing_list']
    accounting_transaction_list = self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 3)
    sequence.edit(current_accounting_transaction_list=accounting_transaction_list)

  def stepCheckTwoAccountingTransactionGeneratedFromInternalPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_internal_packing_list']
    accounting_transaction_list = self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 2)
    sequence.edit(current_accounting_transaction_list=accounting_transaction_list)

  def stepCheckTwoAccountingTransactionGeneratedFromProductionPackingList(self, sequence=None, sequence_list=None):
    packing_list = sequence['current_production_packing_list']
    accounting_transaction_list = self._checkAndGetCausalityRelated(packing_list, 'Accounting Transaction', 2)
    sequence.edit(current_accounting_transaction_list=accounting_transaction_list)

  def _checkDelivery(self,
                     delivery,
                     delivery_property_dict=None,
                     movement_property_dict_tuple=()):
    if delivery_property_dict is not None:
      for property_id, property_value in six.iteritems(delivery_property_dict):
        self.assertEqual(delivery.getProperty(property_id), property_value)

    if not movement_property_dict_tuple:
      return

    movement_list = delivery.getMovementList()
    self.assertIterableLen(movement_list, len(movement_property_dict_tuple))

    unmatched_movement_dict_list = []
    for movement in movement_list:
      for movement_property_dict in movement_property_dict_tuple:
        if 'portal_type' not in movement_property_dict:
          break
        elif movement.getPortalType() == movement_property_dict['portal_type']:
          break

      movement_dict = {}
      for property_id in movement_property_dict:
        movement_dict[property_id] = movement.getProperty(property_id)

      if movement_dict not in movement_property_dict_tuple:
        unmatched_movement_dict_list.append(movement_dict)

    if unmatched_movement_dict_list:
      from pprint import pformat
      raise AssertionError(
        "The following Movements does not exist on '%s':\n%s" % \
          (delivery.getRelativeUrl(),
           pformat(unmatched_movement_dict_list)))

class TestRealTimeInventoryAccounting(ERP5TypeTestCase, TestRealTimeInventoryAccountingMixin):
  def afterSetUp(self):
    category_tool = self.portal.portal_categories

    getattr(self.portal.portal_types, 'Accounting Transaction').setLedgerValueList(
      [category_tool.ledger.stock.achat,
       category_tool.ledger.stock.preparation,
       category_tool.ledger.stock.production,
       category_tool.ledger.stock.stock.entree,
       category_tool.ledger.stock.stock.sortie,
       category_tool.ledger.stock.transit.entree,
       category_tool.ledger.stock.transit.sortie,
       category_tool.ledger.stock.vente])

    if 'my_group' not in category_tool.group:
      category_tool.group.newContent(portal_type='Category',
                                     id='my_group',
                                     title='HOGE')

    if 'variation_cars' not in self.portal.account_module:
      self.portal.account_module.newContent(
        portal_type='Account',
        id='variation_cars',
        reference='VARIATION_CARS',
        title='Variation des stocks de véhicules',
        account_type_value=category_tool.account_type.expense,
        financial_section_value=category_tool.financial_section.expense.op_expense.other,
        gap_value=category_tool.gap.fr.pcg['6']['60']['603']['6037'])

    if 'stock_car_park' not in self.portal.account_module:
      self.portal.account_module.newContent(
        portal_type='Account',
        id='stock_car_park',
        reference='STOCK_CAR_PARK',
        title='Stock Parc Véhicules',
        account_type_value=category_tool.account_type.asset,
        financial_section_value=category_tool.financial_section.asset.current_assets.stock,
        gap_value=category_tool.gap.fr.pcg['3']['35']['355'])

    if 'stock_car_transit' not in self.portal.account_module:
      self.portal.account_module.newContent(
        portal_type='Account',
        id='stock_car_transit',
        reference='STOCK_CAR_TRANSIT',
        title='Stock Transit Véhicules',
        account_type_value=category_tool.account_type.asset,
        financial_section_value=category_tool.financial_section.asset.current_assets.stock,
        gap_value=category_tool.gap.fr.pcg['3']['35']['355'])

    if 'stock_car_workshop' not in self.portal.account_module:
      self.portal.account_module.newContent(
        portal_type='Account',
        id='stock_car_workshop',
        reference='STOCK_CAR_WORKSHOP',
        title='Stock Atelier Véhicules',
        account_type_value=category_tool.account_type.asset,
        financial_section_value=category_tool.financial_section.asset.current_assets.stock,
        gap_value=category_tool.gap.fr.pcg['3']['35']['355'])

    if 'variation_parts' not in self.portal.account_module:
      self.portal.account_module.newContent(
        portal_type='Account',
        id='variation_parts',
        reference='VARIATION_PARTS',
        title='Variation des stocks de pièces',
        account_type_value=category_tool.account_type.expense,
        financial_section_value=category_tool.financial_section.expense.op_expense.other,
        gap_value=category_tool.gap.fr.pcg['6']['60']['603']['6031'])

    if 'stock_parts_port' not in self.portal.account_module:
      self.portal.account_module.newContent(
        portal_type='Account',
        id='stock_parts_port',
        reference='STOCK_PARTS_PORT',
        title='Stock Parts Port',
        account_type_value=category_tool.account_type.asset,
        financial_section_value=category_tool.financial_section.asset.current_assets.stock,
        gap_value=category_tool.gap.fr.pcg['3']['32']['321'])

    if 'stock_parts_transit' not in self.portal.account_module:
      self.portal.account_module.newContent(
        portal_type='Account',
        id='stock_parts_transit',
        reference='STOCK_PARTS_TRANSIT',
        title='Stock Parts Transit',
        account_type_value=category_tool.account_type.asset,
        financial_section_value=category_tool.financial_section.asset.current_assets.stock,
        gap_value=category_tool.gap.fr.pcg['3']['32']['321'])

    try:
      currency_eur = self.portal.currency_module.EUR
    except AttributeError:
      currency_eur = self.portal.currency_module.newContent(
        portal_type='Currency',
        id='EUR',
        reference='EUR',
        title='Euro',
        base_unit_quantity=0.01)
    if currency_eur.getValidationState() != 'validated':
      currency_eur.validate()

    try:
      currency_dol = self.portal.currency_module.DOL
    except AttributeError:
      currency_dol = self.portal.currency_module.newContent(
        portal_type='Currency',
        id='DOL',
        reference='DOL',
        title='Dollar',
        base_unit_quantity=0.01)
    if currency_dol.getValidationState() != 'validated':
      currency_dol.validate()

    try:
      organisation_hoge = self.portal.organisation_module.hoge
    except AttributeError:
      organisation_hoge = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        id='hoge',
        title='HOGE',
        price_currency_value=currency_eur,
        group_value=category_tool.group.my_group,
        site_value=category_tool.site.main)
    if organisation_hoge.getValidationState() != 'validated':
      organisation_hoge.validate()

    try:
      organisation_client = self.portal.organisation_module.client
    except AttributeError:
      organisation_client = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        id='client',
        title='Client',
        price_currency_value=currency_eur,
        role_value=category_tool.role.client)
    if organisation_client.getValidationState() != 'validated':
      organisation_client.validate()

    try:
      organisation_supplier = self.portal.organisation_module.supplier
    except AttributeError:
      organisation_supplier = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        id='supplier',
        title='Supplier',
        role_value=category_tool.role.supplier)
    if organisation_supplier.getValidationState() != 'validated':
      organisation_supplier.validate()

    try:
      organisation_workshop = self.portal.organisation_module.workshop
    except AttributeError:
      organisation_workshop = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        id='workshop',
        title='Workshop')
    if organisation_workshop.getValidationState() != 'validated':
      organisation_workshop.validate()

    try:
      organisation_park = self.portal.organisation_module.park
    except AttributeError:
      organisation_park = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        id='park',
        title='Park')
    if organisation_park.getValidationState() != 'validated':
      organisation_park.validate()

    try:
      currency_dol_conversion_eur = currency_dol.CONV_EUR
    except AttributeError:
      currency_dol_conversion_eur = currency_dol.newContent(
        portal_type='Currency Exchange Line',
        id='CONV_EUR',
        title='Conversion Euro',
        start_date=DateTime('2017/01/01 00:00:00 GMT+9'),
        stop_date=DateTime('2021/01/01 00:00:00 GMT+9'),
        price_currency_value=currency_eur,
        source_value=organisation_hoge,
        base_price=0.95)
    if currency_dol_conversion_eur.getValidationState() != 'validated':
      currency_dol_conversion_eur.validate()

    try:
      stc = self.portal.sale_trade_condition_module.hoge
    except AttributeError:
      stc = self.portal.sale_trade_condition_module.newContent(
        portal_type='Sale Trade Condition',
        id='hoge',
        reference='STC-HOGE',
        title='HOGE Sale Trade Condition',
        source_value=organisation_hoge,
        source_section_value=organisation_hoge,
        price_currency_value=currency_eur,
        specialise_value=self.portal.business_process_module.bpm_sale_hoge)
    if stc.getValidationState() != 'validated':
      stc.validate()

    try:
      ptc = self.portal.purchase_trade_condition_module.hoge
    except AttributeError:
      ptc = self.portal.purchase_trade_condition_module.newContent(
        portal_type='Purchase Trade Condition',
        id='hoge',
        reference='PTC-HOGE',
        title='HOGE Purchase Trade Condition',
        destination_value=organisation_hoge,
        destination_section_value=organisation_hoge,
        price_currency_value=currency_eur,
        specialise_value=self.portal.business_process_module.bpm_purchase_hoge)
    if ptc.getValidationState() != 'validated':
      ptc.validate()

    try:
      itc = self.portal.internal_trade_condition_module.hoge
    except AttributeError:
      itc = self.portal.internal_trade_condition_module.newContent(
        portal_type='Internal Trade Condition',
        id='hoge',
        reference='ITC-HOGE',
        title='HOGE Internal Trade Condition',
        source_value=organisation_hoge,
        source_section_value=organisation_hoge,
        price_currency_value=currency_eur,
        specialise_value=self.portal.business_process_module.bpm_internal_hoge)
    if itc.getValidationState() != 'validated':
      itc.validate()

    try:
      product_big_b_car = self.portal.product_module.big_b_car
    except AttributeError:
      product_big_b_car = self.portal.product_module.newContent(
        portal_type='Product',
        id='big_b_car',
        title='Big B Car',
        reference='543216789',
        product_line_value=category_tool.product_line.component,
        use_value=category_tool.use.trade.purchase,
        quantity_unit_value=category_tool.quantity_unit.unit.piece)
    if product_big_b_car.getValidationState() != 'validated':
      product_big_b_car.validate()

    try:
      product_car_no_supply = self.portal.product_module.car_no_supply
    except AttributeError:
      product_car_no_supply = self.portal.product_module.newContent(
        portal_type='Product',
        id='car_no_supply',
        title='Car No Supply',
        reference='843326789',
        product_line_value=category_tool.product_line.component,
        use_value=category_tool.use.trade.purchase,
        quantity_unit_value=category_tool.quantity_unit.unit.piece)
    if product_car_no_supply.getValidationState() != 'validated':
      product_car_no_supply.validate()

    try:
      product_part_1 = self.portal.product_module.part_1
    except AttributeError:
      product_part_1 = self.portal.product_module.newContent(
        portal_type='Product',
        id='part_1',
        title='Part 1',
        reference='12345',
        product_line_value=category_tool.product_line.component,
        use_value=category_tool.use.trade.purchase,
        quantity_unit_value=category_tool.quantity_unit.unit.piece)
    if product_part_1.getValidationState() != 'validated':
      product_part_1.validate()

    try:
      product_part_2 = self.portal.product_module.part_2
    except AttributeError:
      product_part_2 = self.portal.product_module.newContent(
        portal_type='Product',
        id='part_2',
        title='Part 2',
        reference='67891',
        product_line_value=category_tool.product_line.component,
        use_value=category_tool.use.trade.purchase,
        quantity_unit_value=category_tool.quantity_unit.unit.piece)
    if product_part_2.getValidationState() != 'validated':
      product_part_2.validate()

    try:
      sale_supply = self.portal.sale_supply_module.hoge
    except AttributeError:
      sale_supply = self.portal.sale_supply_module.newContent(
        portal_type='Sale Supply',
        id='hoge',
        title='HOGE Sale Supply',
        start_date_range_min=DateTime('2018/01/01 00:00:00 GMT+9'),
        start_date_range_max=DateTime('2999/12/31 00:00:00 GMT+9'),
        source_section_value=organisation_hoge)
    if 'product_big_b_car' not in sale_supply:
      sale_supply.newContent(
        portal_type='Sale Supply Line',
        id='product_big_b_car',
        title=product_big_b_car.getTitle(),
        resource_value=product_big_b_car,
        base_price=18100)
    if sale_supply.getValidationState() != 'validated':
      sale_supply.validate()

    try:
      purchase_supply = self.portal.purchase_supply_module.hoge
    except AttributeError:
      purchase_supply = self.portal.purchase_supply_module.newContent(
        portal_type='Purchase Supply',
        id='hoge',
        title='HOGE Purchase Supply',
        start_date_range_min=DateTime('2018/01/01 00:00:00 GMT+9'),
        start_date_range_max=DateTime('2999/12/31 00:00:00 GMT+9'),
        destination_section_value=organisation_hoge)
    if 'product_part_1' not in purchase_supply:
      purchase_supply.newContent(
        portal_type='Purchase Supply Line',
        id='product_part_1',
        title=product_part_1.getTitle(),
        resource_value=product_part_1,
        base_price=9000)
    if purchase_supply.getValidationState() != 'validated':
      purchase_supply.validate()

    try:
      internal_supply = self.portal.internal_supply_module.hoge
    except AttributeError:
      internal_supply = self.portal.internal_supply_module.newContent(
        portal_type='Internal Supply',
        id='hoge',
        title='HOGE Internal Supply',
        start_date_range_min=DateTime('2018/01/01 00:00:00 GMT+9'),
        start_date_range_max=DateTime('2999/12/31 00:00:00 GMT+9'),
        source_section_value=organisation_hoge)
    if 'product_big_b_car' not in internal_supply:
      internal_supply.newContent(
        portal_type='Internal Supply Line',
        id='product_big_b_car',
        title=product_big_b_car.getTitle(),
        resource_value=product_big_b_car,
        base_price=4242)
    if internal_supply.getValidationState() != 'validated':
      internal_supply.validate()

    self.tic()

  def stepCallBuilder(self, sequence=None, sequence_list=None):
    self.portal.portal_deliveries.inventory_asset_price_accounting_transaction_builder.build()

  def stepTestSalePackingList_create(self, sequence=None, sequence_list=None):
    sale_packing_list = self.portal.sale_packing_list_module.newContent(
      portal_type='Sale Packing List',
      specialise_value=self.portal.sale_trade_condition_module.hoge,
      title='Vente depuis le Prac',
      start_date=DateTime('2018/01/30 00:00:00 GMT+9'),
      stop_date=DateTime('2018/01/31 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.hoge,
      source_section_value=self.portal.organisation_module.hoge,
      destination_value=self.portal.organisation_module.client,
      destination_section_value=self.portal.organisation_module.client,
      price_currency_value=self.portal.currency_module.DOL)

    sale_packing_list.newContent(
      portal_type='Sale Packing List Line',
      title='Vente voiture',
      int_index=1,
      resource_value=self.portal.product_module.big_b_car,
      price=17100,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.sale)

    sequence.edit(sale_packing_list_1=sale_packing_list)

  def stepTestSalePackingList_checkAllAccountingTransaction(self, sequence=None, sequence_list=None):
    accounting_transaction_list = sequence['current_accounting_transaction_list']
    for accounting_transaction in accounting_transaction_list:
      self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
      if accounting_transaction.getLedgerValue() == self.portal.portal_categories.ledger.stock.stock.sortie:
        self._checkDelivery(
          accounting_transaction,
          delivery_property_dict=dict(
            source_section_value=self.portal.organisation_module.hoge,
            resource_value=self.portal.currency_module.DOL,
            # start_date=stop_date=SPL.start_date
            start_date=DateTime('2018/01/30 00:00:00 GMT+9'),
            stop_date=DateTime('2018/01/30 00:00:00 GMT+9')),
          movement_property_dict_tuple=(
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.variation_cars,
                 # sum(SPLL.price)
                 quantity=-17100),
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.stock_car_park,
                 # sum(SPLL.price)
                 quantity=17100)))

      elif accounting_transaction.getLedgerValue() == self.portal.portal_categories.ledger.stock.transit.entree:
        self._checkDelivery(
          accounting_transaction,
          delivery_property_dict=dict(
            source_section_value=self.portal.organisation_module.hoge,
            resource_value=self.portal.currency_module.DOL,
            # start_date=stop_date=SPL.start_date
            start_date=DateTime('2018/01/30 00:00:00 GMT+9'),
            stop_date=DateTime('2018/01/30 00:00:00 GMT+9')),
          movement_property_dict_tuple=(
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.variation_cars,
                 # sum(SPLL.price)
                 quantity=-17100),
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.stock_car_transit,
                 # sum(SPLL.price)
                 quantity=17100)))

      # ledger/stock/transit/sortie
      else:
        self._checkDelivery(
          accounting_transaction,
          delivery_property_dict=dict(
            source_section_value=self.portal.organisation_module.hoge,
            resource_value=self.portal.currency_module.DOL,
            ledger_value=self.portal.portal_categories.ledger.stock.transit.sortie,
            # start_date=stop_date=SPL.stop_date
            start_date=DateTime('2018/01/31 00:00:00 GMT+9'),
            stop_date=DateTime('2018/01/31 00:00:00 GMT+9')),
          movement_property_dict_tuple=(
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.stock_car_transit,
                 # sum(SPLL.price)
                 quantity=-17100),
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.variation_cars,
                 # sum(SPLL.price)
                 quantity=17100)))

  def testSalePackingList(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestSalePackingList_create
      Tic
      SelectSalePackingList1
      ConfirmSalePackingList
      Tic
      StartSalePackingList
      Tic
      StopSalePackingList
      Tic
      CallBuilder
      Tic
      CheckThreeAccountingTransactionGeneratedFromSalePackingList
      TestSalePackingList_checkAllAccountingTransaction
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

  def stepTestSalePackingListNoPriceAndNoSupply_create(self, sequence=None, sequence_list=None):
    sale_packing_list = self.portal.sale_packing_list_module.newContent(
      portal_type='Sale Packing List',
      specialise_value=self.portal.sale_trade_condition_module.hoge,
      title='Vente depuis le Prac (No Price/Supply)',
      start_date=DateTime('2018/01/30 00:00:00 GMT+9'),
      stop_date=DateTime('2018/01/31 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.hoge,
      source_section_value=self.portal.organisation_module.hoge,
      destination_value=self.portal.organisation_module.client,
      destination_section_value=self.portal.organisation_module.client,
      price_currency_value=self.portal.currency_module.DOL)

    sale_packing_list.newContent(
      portal_type='Sale Packing List Line',
      title='Vente voiture',
      int_index=1,
      resource_value=self.portal.product_module.car_no_supply,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.sale)

    sequence.edit(sale_packing_list_1=sale_packing_list)

  def testSalePackingListNoPriceAndNoSupply(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestSalePackingListNoPriceAndNoSupply_create
      Tic
      SelectSalePackingList1
      ConfirmSalePackingList
      Tic
      StartSalePackingList
      Tic
      StopSalePackingList
      Tic
      CallBuilder
      Tic
      CheckAccountingTransactionNotGeneratedFromSalePackingList
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

  def stepTestPurchasePackingList_create(self, sequence=None, sequence_list=None):
    purchase_packing_list = self.portal.purchase_packing_list_module.newContent(
      portal_type='Purchase Packing List',
      specialise_value=self.portal.purchase_trade_condition_module.hoge,
      title='Reception Supplier',
      start_date=DateTime('2018/01/09 00:00:00 GMT+9'),
      stop_date=DateTime('2018/01/10 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.hoge,
      source_section_value=self.portal.organisation_module.supplier,
      destination_value=self.portal.organisation_module.supplier,
      destination_section_value=self.portal.organisation_module.hoge,
      price_currency_value=self.portal.currency_module.DOL)

    purchase_packing_list.newContent(
      portal_type='Purchase Packing List Line',
      int_index=1,
      resource_value=self.portal.product_module.part_1,
      price=8000,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.purchase)

    purchase_packing_list.newContent(
      portal_type='Purchase Packing List Line',
        int_index=2,
        resource_value=self.portal.product_module.part_2,
        price=6000,
        quantity=1,
        quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
        use_value=self.portal.portal_categories.use.trade.purchase)

    sequence.edit(purchase_packing_list_1=purchase_packing_list)

  def stepTestPurchasePackingList_checkAllAccountingTransaction(self, sequence=None, sequence_list=None):
    accounting_transaction_list = sequence['current_accounting_transaction_list']
    for accounting_transaction in accounting_transaction_list:
      self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
      if accounting_transaction.getLedgerValue() == self.portal.portal_categories.ledger.stock.stock.entree:
        self._checkDelivery(
        accounting_transaction,
        delivery_property_dict=dict(
          source_section_value=self.portal.organisation_module.hoge,
          resource_value=self.portal.currency_module.DOL,
          # start_date=stop_date=PPL.stop_date
          start_date=DateTime('2018/01/10 00:00:00 GMT+9'),
          stop_date=DateTime('2018/01/10 00:00:00 GMT+9')),
        movement_property_dict_tuple=(
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.stock_parts_port,
               quantity=-6000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.variation_parts,
               quantity=6000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.stock_parts_port,
               quantity=-8000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.variation_parts,
               quantity=8000)))

      elif accounting_transaction.getLedgerValue() == self.portal.portal_categories.ledger.stock.transit.entree:
        self._checkDelivery(
        accounting_transaction,
        delivery_property_dict=dict(
          source_section_value=self.portal.organisation_module.hoge,
          resource_value=self.portal.currency_module.DOL,
          # start_date=stop_date=PPL.start_date
          start_date=DateTime('2018/01/09 00:00:00 GMT+9'),
          stop_date=DateTime('2018/01/09 00:00:00 GMT+9')),
        movement_property_dict_tuple=(
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.stock_parts_transit,
               quantity=-6000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.variation_parts,
               quantity=6000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.stock_parts_transit,
               quantity=-8000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.variation_parts,
               quantity=8000)))

      # ledger/stock/transit/sortie
      else:
        self._checkDelivery(
        accounting_transaction,
        delivery_property_dict=dict(
          source_section_value=self.portal.organisation_module.hoge,
          resource_value=self.portal.currency_module.DOL,
          ledger_value=self.portal.portal_categories.ledger.stock.transit.sortie,
          # start_date=stop_date=PPL.stop_date
          start_date=DateTime('2018/01/10 00:00:00 GMT+9'),
          stop_date=DateTime('2018/01/10 00:00:00 GMT+9')),
        movement_property_dict_tuple=(
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.stock_parts_transit,
               quantity=6000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.variation_parts,
               quantity=-6000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.stock_parts_transit,
               quantity=8000),
          dict(portal_type='Accounting Transaction Line',
               source_value=self.portal.account_module.variation_parts,
               quantity=-8000)))

  def testPurchasePackingList(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestPurchasePackingList_create
      Tic
      SelectPurchasePackingList1
      ConfirmPurchasePackingList
      Tic
      StartPurchasePackingList
      Tic
      StopPurchasePackingList
      Tic
      CallBuilder
      Tic
      CheckThreeAccountingTransactionGeneratedFromPurchasePackingList
      TestPurchasePackingList_checkAllAccountingTransaction
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

  def stepTestPurchasePackingListNoPriceAndNoSupply_create(self, sequence=None, sequence_list=None):
    purchase_packing_list = self.portal.purchase_packing_list_module.newContent(
      portal_type='Purchase Packing List',
      specialise_value=self.portal.purchase_trade_condition_module.hoge,
      title='Reception Supplier (No Supply/Price)',
      start_date=DateTime('2018/01/09 00:00:00 GMT+9'),
      stop_date=DateTime('2018/01/10 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.hoge,
      source_section_value=self.portal.organisation_module.supplier,
      destination_value=self.portal.organisation_module.supplier,
      destination_section_value=self.portal.organisation_module.hoge,
      price_currency_value=self.portal.currency_module.DOL)

    purchase_packing_list.newContent(
      portal_type='Purchase Packing List Line',
      int_index=1,
      resource_value=self.portal.product_module.car_no_supply,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.purchase)

    sequence.edit(purchase_packing_list_1=purchase_packing_list)

  def testPurchasePackingListNoPriceAndNoSupply(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestPurchasePackingListNoPriceAndNoSupply_create
      Tic
      SelectPurchasePackingList1
      ConfirmPurchasePackingList
      Tic
      StartPurchasePackingList
      Tic
      StopPurchasePackingList
      Tic
      CallBuilder
      Tic
      CheckAccountingTransactionNotGeneratedFromPurchasePackingList
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

  def stepTestInternalPackingList_create(self, sequence=None, sequence_list=None):
    internal_packing_list = self.portal.internal_packing_list_module.newContent(
      portal_type='Internal Packing List',
      specialise_value=self.portal.internal_trade_condition_module.hoge,
      title='Transfert Workshop to Park',
      start_date=DateTime('2018/03/02 00:00:00 GMT+9'),
      stop_date=DateTime('2018/03/03 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.workshop,
      source_section_value=self.portal.organisation_module.hoge,
      destination_value=self.portal.organisation_module.park,
      destination_section_value=self.portal.organisation_module.hoge,
      price_currency_value=self.portal.currency_module.DOL)

    internal_packing_list.newContent(
      portal_type='Internal Packing List Line',
      int_index=1,
      resource_value=self.portal.product_module.big_b_car,
      price=4242,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.purchase)

    sequence.edit(internal_packing_list_1=internal_packing_list)

  def stepTestInternalPackingList_checkAllAccountingTransaction(self, sequence=None, sequence_list=None):
    accounting_transaction_list = sequence['current_accounting_transaction_list']
    for accounting_transaction in accounting_transaction_list:
      self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
      if accounting_transaction.getLedgerValue() == self.portal.portal_categories.ledger.stock.stock.entree:
        self._checkDelivery(
          accounting_transaction,
          delivery_property_dict=dict(
            source_section_value=self.portal.organisation_module.hoge,
            resource_value=self.portal.currency_module.DOL,
            # start_date=stop_date=IPL.stop_date
            start_date=DateTime('2018/03/03 00:00:00 GMT+9'),
            stop_date=DateTime('2018/03/03 00:00:00 GMT+9')),
          movement_property_dict_tuple=(
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.stock_car_park,
                 # sum(IPLL.price)
                 quantity=-4242),
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.variation_cars,
                 # sum(IPLL.price)
                 quantity=4242)))

      # ledger/stock/stock/sortie
      else:
        self._checkDelivery(
          accounting_transaction,
          delivery_property_dict=dict(
            source_section_value=self.portal.organisation_module.hoge,
            resource_value=self.portal.currency_module.DOL,
            ledger_value=self.portal.portal_categories.ledger.stock.stock.sortie,
            # start_date=stop_date=IPL.start_date
            start_date=DateTime('2018/03/02 00:00:00 GMT+9'),
            stop_date=DateTime('2018/03/02 00:00:00 GMT+9')),
          movement_property_dict_tuple=(
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.variation_cars,
                 # sum(IPLL.price)
                 quantity=-4242),
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.stock_car_workshop,
                 # sum(IPLL.price)
                 quantity=4242)))

  def testInternalPackingList(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestInternalPackingList_create
      Tic
      SelectInternalPackingList1
      ConfirmInternalPackingList
      Tic
      StartInternalPackingList
      Tic
      StopInternalPackingList
      Tic
      CallBuilder
      Tic
      CheckTwoAccountingTransactionGeneratedFromInternalPackingList
      TestInternalPackingList_checkAllAccountingTransaction
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

  def stepTestInternalPackingListNoPriceAndNoSupply_create(self, sequence=None, sequence_list=None):
    internal_packing_list = self.portal.internal_packing_list_module.newContent(
      portal_type='Internal Packing List',
      specialise_value=self.portal.internal_trade_condition_module.hoge,
      title='Transfer Workshop to Park (No Supply/Price)',
      start_date=DateTime('2018/03/02 00:00:00 GMT+9'),
      stop_date=DateTime('2018/03/02 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.workshop,
      source_section_value=self.portal.organisation_module.hoge,
      destination_value=self.portal.organisation_module.park,
      destination_section_value=self.portal.organisation_module.hoge,
      price_currency_value=self.portal.currency_module.DOL)

    internal_packing_list.newContent(
      portal_type='Internal Packing List Line',
      int_index=1,
      resource_value=self.portal.product_module.car_no_supply,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.purchase)

    sequence.edit(internal_packing_list_1=internal_packing_list)

  def testInternalPackingListNoPriceAndNoSupply(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestInternalPackingListNoPriceAndNoSupply_create
      Tic
      SelectInternalPackingList1
      ConfirmInternalPackingList
      Tic
      StartInternalPackingList
      Tic
      StopInternalPackingList
      Tic
      CallBuilder
      Tic
      CheckAccountingTransactionNotGeneratedFromInternalPackingList
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

  def stepTestProductionPackingList_create(self, sequence=None, sequence_list=None):
    production_packing_list = self.portal.production_packing_list_module.newContent(
      portal_type='Production Packing List',
      specialise_value=self.portal.business_process_module.bpm_internal_hoge,
      title='Transfert Workshop to Park',
      start_date=DateTime('2018/03/02 00:00:00 GMT+9'),
      stop_date=DateTime('2018/03/03 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.workshop,
      source_section_value=self.portal.organisation_module.hoge,
      destination_value=self.portal.organisation_module.park,
      destination_section_value=self.portal.organisation_module.hoge,
      price_currency_value=self.portal.currency_module.DOL)

    production_packing_list.newContent(
      portal_type='Production Packing List Line',
      int_index=1,
      resource_value=self.portal.product_module.big_b_car,
      price=4242,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.purchase)

    sequence.edit(production_packing_list_1=production_packing_list)

  def stepTestProductionPackingList_checkAllAccountingTransaction(self, sequence=None, sequence_list=None):
    accounting_transaction_list = sequence['current_accounting_transaction_list']
    for accounting_transaction in accounting_transaction_list:
      self.assertEqual(accounting_transaction.getSimulationState(), 'stopped')
      if accounting_transaction.getLedgerValue() == self.portal.portal_categories.ledger.stock.stock.entree:
        self._checkDelivery(
          accounting_transaction,
          delivery_property_dict=dict(
            source_section_value=self.portal.organisation_module.hoge,
            resource_value=self.portal.currency_module.DOL,
            # start_date=stop_date=IPL.stop_date
            start_date=DateTime('2018/03/03 00:00:00 GMT+9'),
            stop_date=DateTime('2018/03/03 00:00:00 GMT+9')),
          movement_property_dict_tuple=(
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.stock_car_park,
                 # sum(IPLL.price)
                 quantity=-4242),
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.variation_cars,
                 # sum(IPLL.price)
                 quantity=4242)))

      # ledger/stock/stock/sortie
      else:
        self._checkDelivery(
          accounting_transaction,
          delivery_property_dict=dict(
            source_section_value=self.portal.organisation_module.hoge,
            resource_value=self.portal.currency_module.DOL,
            ledger_value=self.portal.portal_categories.ledger.stock.stock.sortie,
            # start_date=stop_date=IPL.start_date
            start_date=DateTime('2018/03/02 00:00:00 GMT+9'),
            stop_date=DateTime('2018/03/02 00:00:00 GMT+9')),
          movement_property_dict_tuple=(
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.variation_cars,
                 # sum(IPLL.price)
                 quantity=-4242),
            dict(portal_type='Accounting Transaction Line',
                 source_value=self.portal.account_module.stock_car_workshop,
                 # sum(IPLL.price)
                 quantity=4242)))

  def testProductionPackingList(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestProductionPackingList_create
      Tic
      SelectProductionPackingList1
      ConfirmProductionPackingList
      Tic
      StartProductionPackingList
      Tic
      StopProductionPackingList
      Tic
      CallBuilder
      Tic
      CheckTwoAccountingTransactionGeneratedFromProductionPackingList
      TestProductionPackingList_checkAllAccountingTransaction
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

  def stepTestProductionPackingListNoPriceAndNoSupply_create(self, sequence=None, sequence_list=None):
    production_packing_list = self.portal.production_packing_list_module.newContent(
      portal_type='Production Packing List',
      specialise_value=self.portal.business_process_module.bpm_internal_hoge,
      title='Transfer Workshop to Park (No Supply/Price)',
      start_date=DateTime('2018/03/02 00:00:00 GMT+9'),
      stop_date=DateTime('2018/03/02 00:00:00 GMT+9'),
      source_value=self.portal.organisation_module.workshop,
      source_section_value=self.portal.organisation_module.hoge,
      destination_value=self.portal.organisation_module.park,
      destination_section_value=self.portal.organisation_module.hoge,
      price_currency_value=self.portal.currency_module.DOL)

    production_packing_list.newContent(
      portal_type='Production Packing List Line',
      int_index=1,
      resource_value=self.portal.product_module.car_no_supply,
      quantity=1,
      quantity_unit_value=self.portal.portal_categories.quantity_unit.unit.piece,
      use_value=self.portal.portal_categories.use.trade.purchase)

    sequence.edit(production_packing_list_1=production_packing_list)

  def testProductionPackingListNoPriceAndNoSupply(self):
    sequence_list = SequenceList()
    sequence_str = """
      TestProductionPackingListNoPriceAndNoSupply_create
      Tic
      SelectProductionPackingList1
      ConfirmProductionPackingList
      Tic
      StartProductionPackingList
      Tic
      StopProductionPackingList
      Tic
      CallBuilder
      Tic
      CheckAccountingTransactionNotGeneratedFromProductionPackingList
      """
    sequence_list.addSequenceString(sequence_str)
    sequence_list.play(self, quiet=0)

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestRealTimeInventoryAccounting))
  return suite
