reward_threshold = context.portal_preferences.getPreferredLoyaltyRewardThreshold()
record_currency = context.portal_preferences.getPreferredLoyaltyRecordCurrency()

search_kw = {"resource": record_currency,
             "group_by_node": True}
getResultValue = context.portal_catalog.getResultValue

for inventory in context.portal_simulation.getCurrentInventoryList(**search_kw):
  if inventory.total_price >= reward_threshold:
    node = getResultValue(uid=inventory.node_uid)
    if node.objectValues(portal_type='Loyalty Account') and not node.Person_getLoyaltyRewardTradeCondition():
      context.activate(tag=tag).Alarm_createOneTimeSaleTradeCondition(
                                     node_uid=inventory.node_uid,
                                     point=reward_threshold)

context.activate(after_tag=tag).getId()
