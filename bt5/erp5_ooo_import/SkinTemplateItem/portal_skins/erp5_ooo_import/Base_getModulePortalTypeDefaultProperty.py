from past.builtins import cmp
forbidden_property = ('uid', 'portal_type',)
match_property_list = []


def extract_keyword(name):
  return [i.lower() for i in name.replace('_', ' ').split()]

def match(name, keyword_list):
  count = 0
  if name == keyword_list:
    return 1
  for i in keyword_list:
    if i in name:
      count += 1
  return count/float(len(name + keyword_list))

module = context
spreadsheet_column = cell.getProperty('spreadsheet_column')
if spreadsheet_column is None:
  return ''
spreadsheet_column_property_list = extract_keyword(spreadsheet_column)
for portal_type in module.allowedContentTypes():
  for property in portal_type.getInstancePropertyAndBaseCategorySet():
    if property not in forbidden_property:
      property_dict = {}
      key = '%s.%s' % (portal_type.id, property)
      rank = match(spreadsheet_column_property_list,
                   extract_keyword(property))
      property_dict['key'] = key
      property_dict['rank'] = rank
      if rank == 1:
        return key
      elif rank > 0:
        match_property_list.append(property_dict)

def comp(a, b):
  return cmp('%s%s' % ((1-a['rank']), a['key']),
             '%s%s' % ((1-b['rank']), b['key']))

if match_property_list:
  match_property_list.sort(comp)
  return match_property_list[0]['key']
return None
