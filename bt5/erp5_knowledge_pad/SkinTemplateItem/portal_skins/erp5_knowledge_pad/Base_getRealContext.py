real_context = context
if real_context.isTempObject():
  real_context = real_context.getParentValue()

web_site_value = real_context.getWebSiteValue()
if web_site_value is not None and web_site_value.isTempObject():
  real_web_site_value = web_site_value.getParentValue()
  while real_web_site_value.isTempObject():
    real_web_site_value = real_web_site_value.getParentValue()
  web_site_url = web_site_value.getRelativeUrl()
  web_site_url_without_language = real_web_site_value.getRelativeUrl()
  real_context_url = real_context.getRelativeUrl()
  real_context_url_without_language = real_context_url.replace(web_site_url, web_site_url_without_language, 1)
  real_context = context.getPortalObject().restrictedTraverse(real_context_url_without_language)

return real_context
