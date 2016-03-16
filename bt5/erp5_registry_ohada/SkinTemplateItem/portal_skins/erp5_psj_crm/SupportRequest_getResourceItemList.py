"""
This script returns the list of items based on the preferred
resources for events. It is intended to be used
by ListField instances.
"""

from Products.ERP5Type.Cache import CachingMethod

def getResourceItemList():
  result = []
  url_list = context.portal_preferences.getPreferredSupportRequestResourceList()
  for url in url_list:
    resource_value = context.getPortalObject().restrictedTraverse(url)
    result.append((resource_value.getTranslatedTitle(), resource_value.getRelativeUrl()))
  return result

getResourceItemList = CachingMethod(getResourceItemList, 
      id=(script.id, context.Localizer.get_selected_language()), 
      cache_factory='erp5_ui_long')
                                 
return getResourceItemList()
