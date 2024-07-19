if REQUEST is not None:
  # mini security
  return None
return (context.getPortalObject().portal_preferences.getPreferredBearerTokenKey() or '').encode('utf-8')
