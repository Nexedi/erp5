kw = {"resource": context.portal_preferences.getPreferredLoyaltyRecordCurrency(),
      "node_uid": context.getUid()}

return context.portal_simulation.getCurrentInventory(**kw)
