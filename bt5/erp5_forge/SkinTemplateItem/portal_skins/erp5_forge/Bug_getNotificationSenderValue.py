sender =  context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()

if sender is None:
  sender = context.getDestinationValue()

if sender is None:
  sender = context.getSourceTradeValue()

return sender
