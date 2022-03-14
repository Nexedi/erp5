test_list = []

test_dict = {'objective time to view object form': 'view_object',
             'time to view object form with many lines': 'view_100_lines',
             'time to view proxyfield form': 'view_proxyfield',
             'add =': 'add_%u',
             'tic =': 'tic_%u',
             'view =': 'view_%u',
             }

for result_line in context.objectValues(portal_type='Test Result Line'):
  test = {}
  object_count = None
  stdout = result_line.getProperty('stdout') or ''
  if stdout:
    for line in result_line.getProperty('stdout').splitlines():
      for k, v in list(test_dict.items()):
        if k in line:
          test['%' in v and v % object_count or v] = \
            float(line.split('<')[1].strip())
          break
      else:
        if line.startswith('nb objects ='):
          object_count = int(line.split()[-1])
    test_list.append(test)

return test_list
