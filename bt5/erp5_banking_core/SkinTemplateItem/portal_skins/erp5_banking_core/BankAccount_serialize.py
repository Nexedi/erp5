# Serialize operations for this bank account
# Lookup pending tagged indexations
tag = context.BankAccount_getMessageTag(context)
if context.getPortalObject().portal_activities.countMessageWithTag(tag):
  raise ValueError("There are operations pending for this account that prevent form calculating its position. Please try again later.")
# Create a tagged indexation
context.activate(tag=tag).getId()
# Serialize at ZODB level
context.serialize()
