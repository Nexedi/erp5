oauth_login_list = []

portal_skin = context.getPortalObject().portal_skins

if getattr(portal_skin, "erp5_oauth_google_login", None) is not None:
  connector = context.ERP5Site_getDefaultGoogleConnector()
  if connector is not None and connector.getClientId() is not None:
    oauth_login_list.append("google")

if getattr(portal_skin, "erp5_oauth_facebook_login", None) is not None:
  connector = context.ERP5Site_getDefaultFacebookConnector()
  if connector is not None and connector.getClientId() is not None:
    oauth_login_list.append("facebook")

if getattr(portal_skin, "erp5_openid_connect_client", None) is not None:
  oauth_login_list.append("openidconnect")

return oauth_login_list
