# Proxy roles: Manager in case user cannot access their own document.
user = context.getPortalObject().portal_membership.getAuthenticatedMember()
login_value = user.getLoginValue()
try:
  return login_value.getReference()
except AttributeError:
  return user.getId()
