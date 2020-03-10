one_time_reference = context.portal_preferences.getPreferredLoyaltyRewardOneTimeTradeConditionReference()
used_reference = context.portal_preferences.getPreferredLoyaltyRewardUsedTradeConditionReference()

search_kw = {
  "portal_type": "Sale Order",
  "simulation_state": ["confirmed", "ordered", "planned"],
  "default_specialise_reference": one_time_reference + '-%',
  "default_specialise_validation_state": 'validated'
}

for sale_order in context.portal_catalog(**search_kw):
  trade_condition = sale_order.getSpecialiseValue()
  reference = trade_condition.getReference()
  new_reference = "%s-%s" % (used_reference, reference.split("-")[-1])
  trade_condition.setReference(new_reference)
