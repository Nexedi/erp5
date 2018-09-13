from Products.ERP5Type.Document import newTempBase

portal = context.getPortalObject()
result = []
portal_diff = portal.portal_diff

def beautifyChange(change_dict):
  return ["%s:%s" % (k, change_dict[k]) for k in sorted(change_dict.keys())]

try:
  history_size = portal.portal_preferences.getPreferredHtmlStyleZodbHistorySize()
except AttributeError:
  history_size = 50

history_list = context.Base_getPropertyChangeHistoryList(context, size=history_size, property_name=property_name)

for i in range(1, len(history_list)):
  dict1 = history_list[i]
  dict2 = history_list[i-1]
  tmp = newTempBase(context, '')
  diff_list = portal_diff.diffPortalObject(dict2, dict1).asBeautifiedJSONDiff()
  dict_ = dict2.copy()
  dict_['change'] = [l for l in diff_list if l['path'] == 'change'][0]['diff']
  tmp.edit(**dict_)

  result.append(tmp)

result.sort(key=lambda x: x.getProperty('datetime'), reverse=True)
return result
