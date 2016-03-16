from Products.ERP5Type.Cache import CachingMethod


def getLanguageList(site):
  language_list = [('', ''),]
  # First check if there is a specific method
  if getattr(site, "IntegrationSite_getPluginLanguageList", None):
    language_list += [(l.title,l.id) for l in getattr(site, 'IntegrationSite_getPluginLanguageList')()]
  else:
    # Otherwise use list from localizer
    language_list += [(x["name"], x["code"]) for x in site.Localizer.get_all_languages()]
  return language_list


getLanguageList = CachingMethod(getLanguageList, \
                                id = 'IntegrationSite_getLanguageList', \
                                cache_factory = 'erp5_ui_long')


return getLanguageList(context)
