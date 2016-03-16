unit = context.getQuantityUnit()
quantity_unit = unit.rsplit("/", 1)[0]


category = context.portal_categories.getCategoryValue(quantity_unit, 'quantity_unit')

pref = context.portal_preferences.getPreference('preferred_category_child_item_list_method_id', 'getCategoryChildCompactLogicalPathItemList')

candidates = getattr(category, pref)(recursive=True, local_sort_id=('int_index', 'translated_title'), checked_permission='View')

return candidates
