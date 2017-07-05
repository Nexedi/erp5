"""Return a list of possible GAP categories for a given account.

if only_preferred_gap parameter is true, this will return only GAP
categories from the GAP set in preferences, otherwise it will return
categories from all available GAP.
"""

portal = context.getPortalObject()

display_cache = {}
def display(x):
  if x not in display_cache:
    gap_id = x.getReference()
    if gap_id:
      display_cache[x] = '%s - %s' % (
        gap_id,
        x.getTranslatedShortTitle() or x.getTranslatedTitle())
    else:
      display_cache[x] = x.getIndentedTitle()

  return display_cache[x]

def getGapItemList(only_preferred_gap, gap_root=None):
  if only_preferred_gap:
    if gap_root:
      return portal.portal_categories.resolveCategory(gap_root).getCategoryChildItemList(
        base=False, is_self_excluded=True, display_method=display,
        local_sort_id=('int_index', 'reference', 'id'))

  result = []
  for country in portal.portal_categories.gap.contentValues():
    for gap_root in country.contentValues():
      result.extend(gap_root.getCategoryChildItemList(
        base=False, is_self_excluded=True, display_method=display,
        local_sort_id=('int_index', 'reference', 'id')))
  return result

from Products.ERP5Type.Cache import CachingMethod
getGapItemList = CachingMethod(
  getGapItemList,
  id='Account_getGapItemList.%s' % portal.Localizer.get_selected_language(),
  cache_factory='erp5_content_long')

return getGapItemList(
  only_preferred_gap=only_preferred_gap,
  gap_root=portal.portal_preferences.getPreferredAccountingTransactionGap())
