##############################################################################
#
# Copyright (c) 2002-2020 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime


class testCommerceLoyaltyProgram(ERP5TypeTestCase):
  """
  Test Commerce Loyalty
  """

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return (
      'erp5_base',
      'erp5_commerce_loyalty_program',
      'erp5_simulation_test',
      'erp5_configurator_standard_trade_template'
    )

  def afterSetUp(self):
    portal = self.getPortalObject()
    self.portal = portal
    delivery_builder_list = self.portal.business_process_module.erp5_default_business_process.invoice.getDeliveryBuilderList()
    if 'portal_deliveries/loyalty_transaction_builder' not in delivery_builder_list:
      delivery_builder_list.append('portal_deliveries/loyalty_transaction_builder')
      self.portal.business_process_module.erp5_default_business_process.invoice.edit(
        delivery_builder_list=delivery_builder_list)
    for loyalty_transaction_line in self.portal.portal_catalog(portal_type='Loyalty Transaction Line'):
      loyalty_transaction_line.edit(quantity=0)
    for rule in self.portal.portal_rules.objectValues():
      if rule.getValidationState() != 'validated':
        rule.validate()
    self.tic()


  def createSaleOrder(self, specialise='sale_trade_condition_module/test_loyalty_program'):
    sale_order = self.portal.sale_order_module.newContent(
      portal_type='Sale Order',
      destination_section = 'person_module/test_sale_order_receiver',
      destination ='person_module/test_sale_order_receiver',
      source_section='organisation_module/test_sale_order_supplier',
      source='organisation_module/test_sale_order_supplier',
      start_date=DateTime(),
      stop_date=DateTime(),
      specialise = specialise
    )
    sale_order.newContent(
      portal_type='Sale Order Line',
      resource='product_module/test_product',
      price=10,
      quantity=10
    )
    return sale_order

  def deliverSaleOrder(self, sale_order):
    sale_order.confirm()
    self.tic()
    self.portal.portal_alarms.packing_list_builder_alarm.activeSense()
    self.tic()
    sale_packing_list = sale_order.getCausalityRelatedValue(portal_type='Sale Packing List')
    self.assertTrue(sale_packing_list is not None)
    sale_packing_list.start()
    sale_packing_list.stop()
    sale_packing_list.deliver()
    return sale_packing_list

  def generateLoyaltyTransaction(self):
    sale_order=self.createSaleOrder()
    self.deliverSaleOrder(sale_order)
    self.tic()
    self.portal.portal_alarms.loyalty_transaction_builder_alarm.activeSense()
    self.tic()
    return sale_order.getCausalityRelatedValue(portal_type='Loyalty Transaction')

  def createLoyaltyAccountIfNotExisted(self, user):
    if not user.objectValues(portal_type='Loyalty Account'):
      return user.newContent(portal_type='Loyalty Account')

  def test_no_loyalty_point_if_no_loyalty_account(self):
    delete_id_list = []
    for loyalty_account in self.portal.person_module.test_sale_order_receiver.objectValues(portal_type='Loyalty Account'):
      delete_id_list.append(loyalty_account.getId())
    self.portal.person_module.test_sale_order_receiver.manage_delObjects(ids=delete_id_list)
    self.tic()
    sale_order=self.createSaleOrder()
    self.deliverSaleOrder(sale_order)
    self.tic()
    self.portal.portal_alarms.loyalty_transaction_builder_alarm.activeSense()
    self.tic()
    loyalty_transaction = sale_order.getCausalityRelatedValue(portal_type='Loyalty Transaction')
    self.assertEqual(loyalty_transaction, None)
    self.assertEqual(self.portal.person_module.test_sale_order_receiver.Person_getTotalLoyaltyPoint(), 0)

  def test_collect_loyalty_point_fixed_quantity(self):
    self.createLoyaltyAccountIfNotExisted(self.portal.person_module.test_sale_order_receiver)
    # if specify quantity is defined, only get such quantity
    self.portal.sale_trade_condition_module.default_loyalty_program.collect_point.setLoyaltyPointQuantity(10)
    self.tic()
    loyalty_transaction = self.generateLoyaltyTransaction()
    self.assertTrue(loyalty_transaction is not None)
    self.assertEqual(self.portal.person_module.test_sale_order_receiver.Person_getTotalLoyaltyPoint(), 10)

  def test_collect_loyalty_point_percentage(self):
    self.createLoyaltyAccountIfNotExisted(self.portal.person_module.test_sale_order_receiver)
    # if specify quantity is defined, only get such quantity
    self.portal.sale_trade_condition_module.default_loyalty_program.collect_point.setLoyaltyPointQuantity(0)
    self.portal.sale_trade_condition_module.default_loyalty_program.collect_point.setLoyaltyPointPrice(0.5)
    self.tic()
    loyalty_transaction = self.generateLoyaltyTransaction()
    self.assertTrue(loyalty_transaction is not None)
    self.assertEqual(self.portal.person_module.test_sale_order_receiver.Person_getTotalLoyaltyPoint(), 100*0.5)

  def test_use_loyalty_point(self):
    # initialise loyalty point to 50
    self.createLoyaltyAccountIfNotExisted(self.portal.person_module.test_sale_order_receiver)
    self.portal.sale_trade_condition_module.default_loyalty_program.collect_point.setLoyaltyPointQuantity(0)
    self.portal.sale_trade_condition_module.default_loyalty_program.collect_point.setLoyaltyPointPrice(0.5)
    self.tic()
    self.generateLoyaltyTransaction()
    self.tic()
    #spend 10 point for coupon, and %10 of sale order price point for discount
    self.portal.sale_trade_condition_module.default_loyalty_program.coupon.setLoyaltyPointQuantity(-10)
    self.portal.sale_trade_condition_module.default_loyalty_program.discount.setLoyaltyPointQuantity(0)
    self.portal.sale_trade_condition_module.default_loyalty_program.discount.setLoyaltyPointPrice(-0.1)
    self.tic()
    self.generateLoyaltyTransaction()
    self.tic()
    self.assertEqual(self.portal.person_module.test_sale_order_receiver.Person_getTotalLoyaltyPoint(), 100*0.5 + 100*0.5 - 10 - 100*0.1)
