"""
This script select the good base category according to the portal_type and if
the category is in variation range
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

base_category_list = [y for x, y in getIndividualVariationBaseCategoryList(portal_type)]

if context.getPortalType() == 'Apparel Model Colour Variation' and 'colour' in base_category_list:
  context.edit(variation_base_category_list=('colour',))
elif context.getPortalType() == 'Apparel Model Morphology Variation' and 'morphology' in base_category_list:
  context.edit(variation_base_category_list=('morphology',))
