"""
  Returns a list of function wich are defined in the subordinated organisation if any
  and extend it with all possible functions.
"""

portal = context.getPortalObject()
category_child_item_list_method_id = portal.portal_preferences.getPreference(
                        'preferred_category_child_item_list_method_id',
                        'getCategoryChildTranslatedCompactLogicalPathItemList')

if 'Translated' in category_child_item_list_method_id:
  if 'Compact' in category_child_item_list_method_id:
    local_sort_id_list = ('int_index', 'translated_short_title')
  else:
    local_sort_id_list = ('int_index', 'translated_title')
else:
  if 'Compact' in category_child_item_list_method_id:
    local_sort_id_list = ('int_index', 'short_title')
  else:
    local_sort_id_list = ('int_index', 'title')

result = []

if context.getSubordination():
  subordination_value = context.getSubordinationValue()
  if subordination_value is not None:
    function_value = subordination_value.getFunctionValue()
    if function_value is not None:
      result.extend(getattr(function_value, category_child_item_list_method_id)(
                    local_sort_id=local_sort_id_list, disable_node=True))

result.extend(getattr(
         portal.portal_categories.function,
         category_child_item_list_method_id)(
              local_sort_id=local_sort_id_list, disable_node=True))

return result
