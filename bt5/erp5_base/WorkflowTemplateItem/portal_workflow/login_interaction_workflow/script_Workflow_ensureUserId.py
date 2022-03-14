"""Make sure the user has a user id.

Persons that were created before user id were introduced may not have a user id already.
"""
user = state_change['object'].getParentValue()
if user.getPortalType() == 'Person' and not user.hasUserId():
  user.initUserId()
