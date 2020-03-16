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
    system_preference = portal.portal_preferences.default_system_preference
    system_preference.edit(
      preferred_loyalty_record_currency='currency_module/test_loyalty_record_currency',
      preferred_loyalty_reward_threshold=180,
      preferred_loyalty_reward_business_process='business_process_module/erp5_default_business_process',
      preferred_loyalty_reward_currency='currency_module/test_loyalty_reward_currency',
      preferred_loyalty_reward_price_='0.3',
      preferred_loyalty_reward_notification_message_reference='Loyalty_Notification',
      preferred_loyalty_reward_one_time_trade_condition_reference='STC-ONE-TIME',
      preferred_loyalty_reward_used_trade_condition_reference='STC-USED-ONE-TIME',
      preferred_loyalty_reward_trade_model_line_trade_phase = 'default/invoicing'
    )
    delete_id_list = []
    for loyalty_account in self.portal.person_module.test_sale_order_receiver.objectValues(portal_type='Loyalty Account'):
      delete_id_list.append(loyalty_account.getId())
    self.portal.person_module.test_sale_order_receiver.manage_delObjects(ids=delete_id_list)
    delivery_builder_list = self.portal.business_process_module.erp5_default_business_process.invoice.getDeliveryBuilderList()
    if 'portal_deliveries/loyalty_transaction_builder' not in delivery_builder_list:
      delivery_builder_list.append('portal_deliveries/loyalty_transaction_builder')
      self.portal.business_process_module.erp5_default_business_process.invoice.edit(
        delivery_builder_list=delivery_builder_list)
    if portal.portal_workflow.isTransitionPossible(system_preference, 'enable'):
      system_preference.enable()
    for loyalty_transaction_line in self.portal.portal_catalog(portal_type='Loyalty Transaction Line'):
      loyalty_transaction_line.edit(quantity=0)
    sale_trade_condition = self.portal.person_module.test_sale_order_receiver.Person_getLoyaltyRewardTradeCondition()
    if sale_trade_condition and portal.portal_workflow.isTransitionPossible(sale_trade_condition, 'invalidate'):
      sale_trade_condition.invalidate()
    for rule in self.portal.portal_rules.objectValues():
      if rule.getValidationState() != 'validated':
        rule.validate()

    self.tic()

  def failUnlessMailSentWithText(self, text, last_messages_amount=2,to=None):
    success = False
    last_message = self.portal.MailHost._last_message
    if text in last_message[-1]:
      if to and 0:
        for recipient in last_message[1]:
          if '"%s"' % to in recipient.replace('\\', ''):
            success = True
            break
      else:
        success = True
    self.assertTrue(success)

  def createSaleOrder(self, specialise='business_process_module/erp5_default_business_process'):
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

  def generateConfirmedLoyaltyTransaction(self):
    sale_order=self.createSaleOrder()
    self.deliverSaleOrder(sale_order)
    self.tic()
    self.portal.portal_alarms.loyalty_transaction_builder_alarm.activeSense()
    self.tic()
    return sale_order.getCausalityRelatedValue(portal_type='Loyalty Transaction')


  def test_loyalty_transaction_creation(self):
    loyalty_transaction = self.generateConfirmedLoyaltyTransaction()
    self.assertTrue(loyalty_transaction is not None)
    self.assertEqual(loyalty_transaction.getSimulationState(), 'confirmed')
    self.assertEqual(loyalty_transaction.getTotalQuantity(), 10*10)
    self.assertEqual(loyalty_transaction.getDestinationSection(), 'person_module/test_sale_order_receiver')
    self.assertEqual(loyalty_transaction.getDestination(), 'person_module/test_sale_order_receiver')
    self.assertEqual(loyalty_transaction.getSourceSection(), 'organisation_module/test_sale_order_supplier')
    self.assertEqual(loyalty_transaction.getSource(), 'organisation_module/test_sale_order_supplier')

  def test_loyalty_trade_condition_creation(self):
    loyalty_transaction = self.generateConfirmedLoyaltyTransaction()
    self.portal.portal_alarms.loyalty_deliver.activeSense()
    self.tic()
    self.assertEqual(loyalty_transaction.getSimulationState(), 'delivered')
    self.portal.portal_alarms.loyalty_reward_creation.activeSense()
    self.tic()
    sale_trade_condition = self.portal.person_module.test_sale_order_receiver.Person_getLoyaltyRewardTradeCondition()
    #loyalty is 100 < 150
    self.assertTrue(not sale_trade_condition)
    loyalty_transaction = self.generateConfirmedLoyaltyTransaction()
    self.portal.portal_alarms.loyalty_deliver.activeSense()
    self.tic()
    self.portal.portal_alarms.loyalty_reward_creation.activeSense()
    sale_trade_condition = self.portal.person_module.test_sale_order_receiver.Person_getLoyaltyRewardTradeCondition()
    # no loyalty account
    self.assertTrue(not sale_trade_condition)
    self.portal.person_module.test_sale_order_receiver.newContent(portal_type='Loyalty Account')
    self.tic()
    self.portal.portal_alarms.loyalty_reward_creation.activeSense()
    sale_trade_condition = self.portal.person_module.test_sale_order_receiver.Person_getLoyaltyRewardTradeCondition()
    self.assertEqual(sale_trade_condition.getSpecialise(), self.portal.portal_preferences.getPreferredLoyaltyRewardBusinessProcess())
    self.assertEqual(sale_trade_condition.getPriceCurrency(), self.portal.portal_preferences.getPreferredLoyaltyRewardCurrency())
    trade_model_line = sale_trade_condition.objectValues(portal_type='Trade Model Line')
    self.assertEqual(1, len(trade_model_line))
    trade_model_line = trade_model_line[0]
    self.assertEqual(trade_model_line.getPrice(), self.portal.portal_preferences.getPreferredLoyaltyRewardPrice())
    self.assertEqual(trade_model_line.getUse(), 'trade/discount_service')
    self.assertEqual(trade_model_line.getBaseApplication(), 'base_amount/discounted')
    loyalty_transaction = sale_trade_condition.getCausalityRelatedValue(portal_type='Loyalty Transaction')
    self.assertEqual(loyalty_transaction.getSimulationState(), 'delivered')
    self.assertEqual(loyalty_transaction.getTotalQuantity(), -self.portal.portal_preferences.getPreferredLoyaltyRewardThreshold())

  def test_loyalty_trade_condition_invalidation(self):
    self.generateConfirmedLoyaltyTransaction()
    self.generateConfirmedLoyaltyTransaction()
    self.portal.person_module.test_sale_order_receiver.newContent(portal_type='Loyalty Account')
    self.tic()
    self.portal.portal_alarms.loyalty_deliver.activeSense()
    self.tic()
    self.portal.portal_alarms.loyalty_reward_creation.activeSense()
    self.tic()
    sale_trade_condition = self.portal.person_module.test_sale_order_receiver.Person_getLoyaltyRewardTradeCondition()
    sale_order = self.createSaleOrder(specialise=sale_trade_condition.getRelativeUrl())
    sale_order.confirm()
    self.tic()
    self.portal.portal_alarms.loyalty_reward_invalidation.activeSense()
    self.tic()
    self.assertTrue(sale_trade_condition.getReference().startswith(self.portal.portal_preferences.getPreferredLoyaltyRewardUsedTradeConditionReference()))

  def test_notify_loyalty_reward(self):
    self.portal.notification_message_module.test_notification_message.edit(
      reference = self.portal.portal_preferences.getPreferredLoyaltyRewardNotificationMessageReference())
    self.generateConfirmedLoyaltyTransaction()
    self.generateConfirmedLoyaltyTransaction()
    self.portal.person_module.test_sale_order_receiver.newContent(portal_type='Loyalty Account')
    self.tic()
    self.portal.portal_alarms.loyalty_deliver.activeSense()
    self.tic()
    self.portal.portal_alarms.loyalty_reward_creation.activeSense()
    self.tic()
    self.failUnlessMailSentWithText('Congratulations',to=self.portal.person_module.test_sale_order_receiver.getTitle())

