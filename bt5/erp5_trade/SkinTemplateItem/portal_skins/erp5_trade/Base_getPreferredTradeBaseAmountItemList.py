portal_categories = context.portal_categories
portal_preferences = context.portal_preferences
method_id = portal_preferences.getPreference('preferred_category_child_item_list_method_id', 'getCategoryChildCompactLogicalPathItemList')

item_list = getattr(portal_categories.base_amount, method_id)(local_sort_id=('int_index', 'translated_title'), checked_permission='View', base=1)
preferred_list = portal_preferences.getPreferredTradeBaseAmountList()

if not preferred_list and preferred_list != ['']:
  return item_list
else:
  return [item for item in item_list if item[1] in preferred_list]
