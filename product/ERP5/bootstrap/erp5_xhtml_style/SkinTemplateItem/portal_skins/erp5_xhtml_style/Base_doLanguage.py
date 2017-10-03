import re

try:
  website = context.getWebSiteValue()
except AttributeError:
  website = None

if website is not None and website.isStaticLanguageSelection():
  # Web Mode
  root_website = website.getOriginalDocument()
  default_language = root_website.getDefaultAvailableLanguage()
  root_website_url = root_website.constructUrlFor()
  website_url_pattern = r'^%s(?:%s)*(/|$)' % (
    re.escape(root_website_url),
    '|'.join('/' + re.escape(x) for x in root_website.getAvailableLanguageList()))
  referer_url = context.REQUEST.HTTP_REFERER
  if referer_url:
    if select_language == default_language:
      redirect_url = re.sub(website_url_pattern, root_website_url + r'\1', referer_url)
    else:
      redirect_url = re.sub(website_url_pattern, root_website_url + '/' + select_language + r'\1',
                            referer_url)
  else:
    if select_language == default_language:
      redirect_url = root_website_url
    else:
      redirect_url = root_website.constructUrlFor(document_reference=select_language)
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
