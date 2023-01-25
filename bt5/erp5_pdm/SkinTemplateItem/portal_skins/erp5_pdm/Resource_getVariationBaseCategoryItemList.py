"""
This script returns the list of base categories on the preferred
variations for services. It is intended to be used
by ListField instances.
"""

portal_type = context.getPortalType()

from Products.ERP5Type.Cache import CachingMethod

#xxx default preference value [] for fix a bug
method_name = 'getPreferred%sVariationBaseCategoryList' % portal_type.replace(' ', '')
method = getattr(context.portal_preferences, method_name)
url_list = method([])

def getVariationsBaseCategoryList(portal_type):
  result = []
  for url in url_list:
    base_category = context.portal_categories[url]
    result.append((base_category.getTranslatedTitle(), base_category.getRelativeUrl()))
  return result

getVariationsBaseCategoryList = CachingMethod(getVariationsBaseCategoryList,
    id=(script.id, context.Localizer.get_selected_language(), url_list),
    cache_factory='erp5_ui_long')

return getVariationsBaseCategoryList(portal_type)
