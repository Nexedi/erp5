portal_categories = context.portal_categories
portal_preferences = context.portal_preferences
method_id = portal_preferences.getPreference('preferred_category_child_item_list_method_id', 'getCategoryChildCompactLogicalPathItemList')

item_list = getattr(portal_categories.use, method_id)(local_sort_id=('int_index', 'translated_title'), checked_permission='View')

resource = context.getResourceValue()
if resource is None:
  item_display_list = item_list
else:
  selected_use_list = [use_value.getCategoryRelativeUrl() for use_value in resource.getUseValueList() + context.getUseValueList()]
  item_display_list = [('', '')] + [item for item in item_list if item[1] in selected_use_list]

return item_display_list
