"""
This script returns the list of base categories on the preferred
variations for services. It is intended to be used
by ListField instances.
"""

portal_type = context.getPortalType()
if portal_type in context.getPortalVariationTypeList():
  portal_type = context.getParentValue().getPortalType()

from Products.ERP5Type.Cache import CachingMethod

#xxx default preference value [] for fix a bug
method_name = 'getPreferred%sIndividualVariationBaseCategoryList' % portal_type.replace(' ', '')
method = getattr(context.portal_preferences, method_name)
url_list = method([])

def getIndividualVariationBaseCategoryList(portal_type):
  result = []
  for url in url_list:
    base_category = context.portal_categories[url]
    result.append((base_category.getTranslatedTitle(), base_category.getRelativeUrl()))
  return result

getIndividualVariationBaseCategoryList = CachingMethod(getIndividualVariationBaseCategoryList,
    id=(script.id, context.Localizer.get_selected_language(), url_list),
    cache_factory='erp5_ui_long')

return getIndividualVariationBaseCategoryList(portal_type)
