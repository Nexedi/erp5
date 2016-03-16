default_method_name = 'getCategoryChildTranslatedCompactLogicalPathItemList'
method_name = context.portal_preferences.getPreference('preferred_category_child_item_list_method_id', default=default_method_name)

if not translate:
  method_name = method_name.replace('Translated', '')

if translate:
  if 'Compact' in method_name:
    local_sort_id_list = ('int_index', 'translated_short_title')
  else:
    local_sort_id_list = ('int_index', 'translated_title')
else:
  if 'Compact' in method_name:
    local_sort_id_list = ('int_index', 'short_title')
  else:
    local_sort_id_list = ('int_index', 'title')

method = getattr(base_category, method_name)

return method(local_sort_id=local_sort_id_list, checked_permission='View', **kw)
