oauth_login_list = []

portal_skin = context.getPortalObject().portal_skins

if getattr(portal_skin, "erp5_oauth_google_login", None) is not None:
  oauth_login_list.append("google")

return oauth_login_list
