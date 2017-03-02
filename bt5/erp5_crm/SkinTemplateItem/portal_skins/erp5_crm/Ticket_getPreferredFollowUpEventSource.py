"""Returns the default sender for response events.

This script is here so that we can easily customized depending on the context event, ticket or user preferences.
"""

if context.hasSource():
  return context.getSource()
logged_in_user = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if logged_in_user is not None:
  return logged_in_user.getRelativeUrl()
return ''
