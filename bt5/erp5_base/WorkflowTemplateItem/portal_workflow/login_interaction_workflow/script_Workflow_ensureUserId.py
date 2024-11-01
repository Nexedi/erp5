"""Make sure the user has a user id.

Persons (or other user types) that were created before user id were introduced may not have a user id already.
"""
user = state_change['object'].getParentValue()
if user.getPortalType() in user.getPortalUserTypeList() and not user.hasUserId():
  user.initUserId()
