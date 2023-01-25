"""Returns the item list of possible functions to use on accounting lines.
"""
portal = context.getPortalObject()

function_base_category = portal.portal_preferences.getPreferredAccountingTransactionLineFunctionBaseCategory()
if function_base_category:
  return getattr(portal.portal_categories.restrictedTraverse(function_base_category),
                  portal.portal_preferences.getPreference('preferred_category_child_item_list_method_id',
                        'getCategoryChildCompactLogicalPathItemList'))(
                              local_sort_id=('int_index', 'translated_title'),
                              checked_permission='View',
                              base=True)

return ()
