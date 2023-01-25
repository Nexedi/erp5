"""Returns the item list of possible fundings to use on accounting lines.
"""
portal = context.getPortalObject()

funding_base_category = portal.portal_preferences.getPreferredAccountingTransactionLineFundingBaseCategory()
if funding_base_category:
  return getattr(portal.portal_categories.restrictedTraverse(funding_base_category),
                  portal.portal_preferences.getPreference('preferred_category_child_item_list_method_id',
                        'getCategoryChildCompactLogicalPathItemList'))(
                              local_sort_id=('int_index', 'translated_title'),
                              checked_permission='View',
                              base=True)

return ()
