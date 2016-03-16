try:
  website = context.getWebSiteValue()
except AttributeError:
  website = None

if website is not None and website.isStaticLanguageSelection():
  # Web Mode
  referer_url = context.REQUEST.HTTP_REFERER
  default_language = context.getDefaultAvailableLanguage()
  current_language = context.Localizer.get_selected_language()
  web_site_url = context.getWebSiteValue().absolute_url()
  if web_site_url.endswith('/%s' % current_language):
    # Quick hack to handle acquisition of temp object
    # which is different in the case of a Web Site
    web_site_url = web_site_url[:-len(current_language) - 1]

  if current_language == select_language:
    redirect_url = referer_url
  elif current_language == default_language:
    redirect_url = referer_url.replace(web_site_url, '%s/%s' %
                            (web_site_url, select_language))
  elif select_language == default_language:
    redirect_url = referer_url.replace('%s/%s' % (web_site_url, current_language), web_site_url)
  else:
    redirect_url = referer_url.replace('%s/%s' % (web_site_url, current_language),
                                       '%s/%s' % (web_site_url, select_language))
  return context.REQUEST.RESPONSE.redirect(redirect_url)
else:
  # ERP5 Mode
  # XXX Localizer-dependent
  portal = context.getPortalObject()

  if select_language is None:
    select_language = context.REQUEST.form["Base_doLanguage"]

  if not select_language:
    select_language = portal.Localizer.get_selected_language()

  portal.Localizer.changeLanguage(select_language)
