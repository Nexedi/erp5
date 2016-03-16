sender =  context.ERP5Site_getAuthenticatedMemberPersonValue()

if sender is None:
  sender = context.getDestinationValue()

if sender is None:
  sender = context.getSourceTradeValue()

return sender
