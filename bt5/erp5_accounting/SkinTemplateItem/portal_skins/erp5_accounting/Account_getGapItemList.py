"""Return a list of possible GAP categories for a given account.

if only_preferred_gap parameter is true, this will return only GAP
categories from the GAP set in preferences, otherwise it will return
categories from all available GAP.
"""

portal = context.getPortalObject()

def display(x):
  gap_id = x.getReference()
  if gap_id:
    return '%s - %s' % (
      gap_id,
      x.getTranslatedShortTitle() or x.getTranslatedTitle())
  return x.getIndentedTitle()


def getGapItemList(only_preferred_gap, gap_root=None):
  if only_preferred_gap and gap_root:
    return portal.portal_categories.resolveCategory(gap_root).getCategoryChildItemList(
        base=False,
        is_self_excluded=True,
        display_method=display,
        local_sort_id=('int_index', 'reference', 'id'))

  result = []
  for gap_root_title, gap_root in context.AccountModule_getAvailableGapList():
    if gap_root:
      result.append((gap_root_title, None))
      result.extend(
          portal.portal_categories.resolveCategory(gap_root).getCategoryChildItemList(
              base=False,
              is_self_excluded=True,
              display_method=display,
              display_none_category=False,
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
