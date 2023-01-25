from Products.ERP5Type.Utils import sortValueList

def getCategoryMappingChildValueList(category_mapping, sort_on=None, sort_order=None,
                  is_self_excluded=1,local_sort_method=None,
                  local_sort_id=None, **kw):
  if is_self_excluded:
    value_list = []
  else:
    value_list = [category_mapping]
  allowed_type_list = ["Integration Base Category Mapping","Integration Category Mapping"]
  child_value_list = category_mapping.objectValues(portal_type=allowed_type_list)
  if local_sort_id:
    if isinstance(local_sort_id, (tuple, list)):
      def sort_method(a, b):
        for sort_id in local_sort_id:
          diff = cmp(a.getProperty(sort_id, 0), b.getProperty(sort_id, 0))
          if diff != 0:
            return diff
        return 0
      local_sort_method = sort_method
    else:
      local_sort_method = lambda a, b: cmp(a.getProperty(local_sort_id, 0),
                                          b.getProperty(local_sort_id, 0))
  if local_sort_method:
    # sort objects at the current level
    child_value_list = list(child_value_list)
    child_value_list.sort(local_sort_method)
  # get recursive child value list
  for c in child_value_list:
    value_list.extend(getCategoryMappingChildValueList(c,
                                  is_self_excluded=0,
                                  local_sort_id=local_sort_id,
                                  local_sort_method=local_sort_method))

  return sortValueList(value_list, sort_on, sort_order, **kw)


return getCategoryMappingChildValueList(context, sort_on=sort_on, sort_order=sort_order,
                                        local_sort_method=local_sort_method,
                                        local_sort_id=local_sort_id, **kw)
