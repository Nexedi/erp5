# Proxy roles: Manager in case user cannot access their own document.
user = context.getPortalObject().portal_membership.getAuthenticatedMember()
user_value = user.getUserValue()
try:
  return user_value.getReference()
except AttributeError:
  return user.getId()
