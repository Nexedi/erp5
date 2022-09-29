from Products.ERP5Type.Cache import CachingMethod

cachedMethod = CachingMethod(context.ConfigurationTemplate_readOOCalcFile, script.getId())
result = {}
filename = "standard_default_accounts.ods"
object_list = cachedMethod(filename)

for item in object_list:
  for k in item.keys():
    if k.startswith('gap_'):
      gap_id = k[len('gap_'):]
      account_list = result.setdefault(gap_id, [])
      new_item = item.copy()
      new_item['gap'] = new_item.pop(k)
      if ('title_%s' % gap_id) in new_item:
        new_item['title'] = new_item['title_%s' % gap_id]

      # clean all localisation columns
      for k in list(new_item.keys()):
        if k.startswith('gap_') or k.startswith('title_'):
          new_item.pop(k)

      account_list.append(new_item)
      continue

return result
