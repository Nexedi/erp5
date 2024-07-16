if REQUEST is not None:
  # mini security
  return None
from Products.ERP5Type.Utils import str2bytes
return str2bytes(context.getPortalObject().portal_preferences.getPreferredBearerTokenKey() or '')
