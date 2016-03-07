portal = context.getPortalObject()
preferred_language_list = portal.portal_preferences.getPreference('preferred_user_interface_language_list', None)

def getConfiguratorLanguageList():
  language_list = []
  for language in portal.Localizer.get_languages_map():
    title = portal.Localizer.erp5_ui.gettext(language['title'], lang=language['id'])
    if not preferred_language_list or language['id'] in preferred_language_list:
      language_list.append((title, language['id']))
  return language_list

from Products.ERP5Type.Cache import CachingMethod
return CachingMethod(getConfiguratorLanguageList,
    ("getConfiguratorLanguageList", ),cache_factory='erp5_ui_long')()
