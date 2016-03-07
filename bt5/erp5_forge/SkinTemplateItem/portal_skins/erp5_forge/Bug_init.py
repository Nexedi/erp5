# Define a Reporter as Source Trade
person =  context.ERP5Site_getAuthenticatedMemberPersonValue()

if person is not None:
  context.setSourceTradeValue(person)

# Define Reference from ID
bug_id = context.getId()
context.setReference("#%s" % bug_id)
