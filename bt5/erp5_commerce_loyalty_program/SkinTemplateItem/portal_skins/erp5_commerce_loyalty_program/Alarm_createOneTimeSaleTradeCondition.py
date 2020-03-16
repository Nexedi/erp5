from DateTime import DateTime
portal = context.getPortalObject()
node = portal.portal_catalog.getResultValue(uid=node_uid)
if node.getPortalType() != "Person":
  return None
preferences = portal.portal_preferences
new_id = context.generateNewId(id_group="one_time_sale_trade_condition",
                               default=1)
trade_condition = context.sale_trade_condition_module.newContent(
  portal_type="Sale Trade Condition",
  reference="%s-%s" % (preferences.getPreferredLoyaltyRewardOneTimeTradeConditionReference(), new_id),
  destination_section_uid=node_uid,
  destination_uid=node_uid,
  trade_condition_type="sale/onetime",
  specialise=preferences.getPreferredLoyaltyRewardBusinessProcess(),
  price_currency=preferences.getPreferredLoyaltyRewardCurrency(),
  )

discount_service = portal.portal_catalog.getResultValue(
                        portal_type="Service", reference="DISCOUNT",
                        validation_state=["validated", "published"])

price = preferences.getPreferredLoyaltyRewardPrice()
trade_condition.newContent(
             portal_type="Trade Model Line",
             resource_value=discount_service,
             title="Loyalty Discount",
             base_application="base_amount/discounted",
             use="trade/discount_service",
             trade_phase=preferences.getPreferredLoyaltyRewardTradeModelLineTradePhase(),
             price=price)

trade_condition.validate()

loyalty_transaction = portal.loyalty_transaction_module.newContent(
                 title="Loyalty Bonus with %s Discount for your next Sale" % price,
                 portal_type = "Loyalty Transaction",
                 causality = trade_condition.getRelativeUrl(),
                 destination_section_uid = node_uid,
                 destination_uid = node_uid)

loyalty_transaction.newContent(portal_type="Loyalty Transaction Line",
                               quantity=-float(point), price=1.0,
                               resource=preferences.getPreferredLoyaltyRecordCurrency())

loyalty_transaction.deliver()

tag = "notify_person_reward_%s" % (str(node_uid))
node.activate(tag=tag).Person_notifyLoyaltyReward(loyalty_transaction.getRelativeUrl())

return trade_condition
