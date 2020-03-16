portal = context.getPortalObject()
one_time_trade_condition_reference= portal.portal_preferences.getPreferredLoyaltyRewardOneTimeTradeConditionReference()

search_kw = {"default_destination_uid": context.getUid(),
             "portal_type": "Sale Trade Condition",
             "reference": one_time_trade_condition_reference + '-%',
             "validation_state": "validated"}

return context.portal_catalog.getResultValue(**search_kw)
