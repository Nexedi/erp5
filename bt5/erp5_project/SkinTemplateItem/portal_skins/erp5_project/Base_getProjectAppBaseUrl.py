url = context.getPortalObject().portal_preferences.getPreferredProjectManagementAppBaseUrl("")

if not url:
  #fallback to default url
  return "https://project.nexedi.net"

return url.rstrip('/')