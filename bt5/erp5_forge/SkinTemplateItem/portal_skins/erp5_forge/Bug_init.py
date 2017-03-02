# Define a Reporter as Source Trade
person =  context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()

if person is not None:
  context.setSourceTradeValue(person)

# Define Reference from ID
bug_id = context.getId()
context.setReference("#%s" % bug_id)
