'''Returns the currency that is used for this section category.
Returns None if no currency defined or if mixed currency are used.
'''

from Products.ERP5Type.Cache import CachingMethod

def getCurrencyForSectionCategory(section_category, section_category_strict):
  portal = context.getPortalObject()
  currency_set = set()
  for section_uid in portal.Base_getSectionUidListForSectionCategory(
      section_category, section_category_strict):
    if section_uid != -1:
      section, = portal.portal_catalog(uid=section_uid, limit=2)
      currency = section.getObject().getPriceCurrency()
      if currency:
        currency_set.add(currency)
  if len(currency_set) == 1:
    return currency_set.pop()

getCurrencyForSectionCategory = CachingMethod(
              getCurrencyForSectionCategory,
              id=script.getId(), cache_factory='erp5_content_long')

return getCurrencyForSectionCategory(section_category, section_category_strict)
