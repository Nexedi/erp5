kw = dict(limit=15)

if starts_with is not None and search_catalog_key is not None:
  kw[search_catalog_key] = "%s%%" % starts_with

if search_portal_type is not None:
  kw["portal_type"] = search_portal_type

result_dict_list = []
for brain in context.portal_catalog(**kw):
  obj = brain.getObject()

  # There may be objects with different Portal Types, so the only way seems
  # to call the script for each object... The returned dict should only contains
  # 'label' (first line displayed) and 'description' (optional: second line displayed)
  result_dict = obj.getTypeBasedMethod('getCompletionDict',
                                       fallback_script_id='Base_getCompletionDict')(obj)

  result_dict['value'] = obj.getProperty(search_catalog_key)
  result_dict_list.append(result_dict)

from json import dumps
return dumps(result_dict_list, indent=4)
