portal = context.getPortalObject()
Localizer = portal.Localizer

for language in language_list:
  Localizer.manage_addLanguage(language)
  for catalog in Localizer.objectValues():
    catalog.manage_addLanguage(language)

portal.portal_caches.clearAllCache()
return 'New Languages Added.'
